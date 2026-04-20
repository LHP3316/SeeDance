"""
任务执行器 - 定时检测并执行任务
功能：
1. 定时检测任务列表（可配置间隔）
2. 检查任务执行时间是否到达
3. 调用即梦AI API执行任务
4. 保存生成的图片/视频
5. 更新任务状态
6. 详细日志记录

使用方法：
# 在WSL Ubuntu环境中运行：
conda activate video
cd /mnt/d/Project/seedance

# 单次执行（测试）
python task_executor.py --once

# 持续运行（默认5分钟间隔）
python task_executor.py

# 自定义间隔（10分钟）
python task_executor.py --interval 600
"""

import os
import sys
import time
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

# 添加项目根目录和backend目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(project_root, 'backend')

# 确保backend目录在路径中（用于导入models和config）
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models.task import Task
from backend.models.task_execution import TaskExecution
from backend.models.material import Material
from backend.config import settings
from backend.database import Base
from jimeng_api_client import JimengAPIClient

# 配置日志
LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# 创建logger
logger = logging.getLogger("TaskExecutor")
logger.setLevel(logging.DEBUG)

# 清除已有的handler（避免重复添加）
logger.handlers.clear()

# 文件处理器 - 实时写入
file_handler = logging.FileHandler(
    LOG_DIR / f"task_executor_{datetime.now().strftime('%Y%m%d')}.log",
    encoding='utf-8'
)
file_handler.setLevel(logging.DEBUG)
file_handler.flush = lambda: file_handler.stream.flush()  # 确保立即刷新
file_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s'
)
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

# 控制台处理器 - 实时输出
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.flush = lambda: console_handler.stream.flush()  # 确保立即刷新
console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)


def flush_logs():
    """强制刷新所有日志处理器，确保日志立即写入文件"""
    for handler in logger.handlers:
        handler.flush()


class TaskExecutor:
    """任务执行器"""
    
    def __init__(self):
        """初始化执行器"""
        # 数据库连接
        self.engine = create_engine(settings.resolved_database_url)
        
        # 解决表重复定义问题：重新创建Base
        from sqlalchemy.orm import declarative_base
        TaskBase = declarative_base()
        
        # 重新声明Task模型（避免与database.py中的Base冲突）
        from sqlalchemy import Column, Integer, String, DateTime, Text, Enum as SQLEnum
        from sqlalchemy.sql import func
        from enum import Enum
        
        class TaskStatusEnum(str, Enum):
            pending = "pending"
            running = "running"
            completed = "completed"
            failed = "failed"
            cancelled = "cancelled"
        
        class Task(TaskBase):
            __tablename__ = "tasks"
            __table_args__ = {'extend_existing': True}
            
            id = Column(Integer, primary_key=True, index=True)
            name = Column(String(200), nullable=False)
            type = Column(String(50), nullable=False)  # image or video
            prompt = Column(Text, nullable=False)
            model = Column(String(50), nullable=False)
            ratio = Column(String(20), nullable=False)
            duration = Column(Integer, nullable=True)  # 视频时长（秒）
            resolution = Column(String(20), nullable=True)  # 分辨率 2k/4k
            image_size = Column(String(20), nullable=True)  # 图片尺寸
            params = Column(String(1000), nullable=True)  # 扩展参数JSON
            status = Column(SQLEnum(TaskStatusEnum), default=TaskStatusEnum.pending)
            schedule_type = Column(String(50), nullable=True)  # manual/scheduled
            cron_expression = Column(String(100), nullable=True)
            scheduled_time = Column(DateTime, nullable=True)
            next_run_time = Column(DateTime, nullable=True)
            last_run_time = Column(DateTime, nullable=True)
            run_count = Column(Integer, default=0)
            is_deleted = Column(Integer, default=0)  # 数据库中是Boolean/TinyInt
            error_message = Column(Text, nullable=True)
            image_material_id = Column(Integer, nullable=True)
            video_material_id = Column(Integer, nullable=True)
            created_by = Column(Integer, nullable=False)
            created_at = Column(DateTime, server_default=func.now())
            updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
        
        self.Session = sessionmaker(bind=self.engine)
        self.Task = Task  # 保存Task类供后续使用
        
        # 从数据库读取SessionID
        session_id = self._get_session_id_from_db()
        if not session_id:
            logger.error("未找到SessionID配置，请在后台管理系统中配置")
            raise ValueError("SessionID未配置")
        
        logger.info(f"从数据库加载SessionID: {session_id[:10]}...")
        
        # 即梦API客户端
        self.jimeng_client = JimengAPIClient(sessionid=session_id)
        
        # 输出目录
        self.output_dir = Path(__file__).parent / "output"
        self.output_dir.mkdir(exist_ok=True)
        
        logger.info("=" * 60)
        logger.info("任务执行器初始化完成")
        logger.info(f"输出目录: {self.output_dir}")
        logger.info("=" * 60)
    
    def _get_session_id_from_db(self) -> Optional[str]:
        """
        从数据库读取SessionID配置
        
        Returns:
            SessionID字符串或None
        """
        try:
            session = self.Session()
            try:
                # 直接使用SQL查询，避免模型导入冲突
                from sqlalchemy import text
                
                # 注意：key是MySQL保留字，需要用反引号包裹
                # 先尝试 jimeng_session_id（新格式）
                result = session.execute(
                    text("SELECT `value` FROM system_configs WHERE `key` = 'jimeng_session_id'")
                )
                row = result.fetchone()
                
                if row and row[0]:
                    session_id = row[0].strip()
                    logger.info(f"成功从数据库读取SessionID (jimeng_session_id)")
                    return session_id
                
                # 如果没找到，尝试 jimeng_sessionid（旧格式）
                logger.info("未找到jimeng_session_id，尝试jimeng_sessionid...")
                result = session.execute(
                    text("SELECT `value` FROM system_configs WHERE `key` = 'jimeng_sessionid'")
                )
                row = result.fetchone()
                
                if row and row[0]:
                    session_id = row[0].strip()
                    logger.info(f"成功从数据库读取SessionID (jimeng_sessionid)")
                    return session_id
                
                logger.warning("数据库中未找到SessionID配置")
                return None
            finally:
                session.close()
        except Exception as e:
            logger.error(f"从数据库读取SessionID失败: {e}")
            return None
    
    def get_pending_tasks(self):
        """
        获取待执行的任务
        
        Returns:
            待执行的任务列表
        """
        session = self.Session()
        try:
            now = datetime.now()
            
            # 查询条件：
            # 1. 状态为 pending
            # 2. scheduled_time 已到达或已过
            # 3. 未删除
            tasks = session.query(self.Task).filter(
                self.Task.status == 'pending',
                self.Task.scheduled_time <= now,
                self.Task.is_deleted == False
            ).all()
            
            logger.info(f"查询到 {len(tasks)} 个待执行任务")
            flush_logs()  # 立即写入日志
            return tasks
            
        except Exception as e:
            logger.error(f"查询待执行任务失败: {e}")
            return []
        finally:
            session.close()
    
    def execute_image_task(self, task) -> Dict:
        """
        执行图片任务
        
        Args:
            task: 任务对象
            
        Returns:
            执行结果
        """
        logger.info(f"开始执行图片任务 [ID:{task.id}] - {task.name}")
        logger.info(f"  - 模型: {task.model}")
        logger.info(f"  - 比例: {task.ratio}")
        logger.info(f"  - 提示词: {task.prompt}")  # 完整显示提示词
        
        result = {
            "success": False,
            "history_id": None,
            "image_urls": [],
            "saved_files": [],
            "error": None,
            "api_response": None
        }
        
        try:
            # 判断是文生图还是图生图
            if task.image_material_id:
                # 图生图
                logger.info("检测到参考图片，使用图生图模式")
                # TODO: 实现图生图逻辑
                result["error"] = "图生图功能待实现"
            else:
                # 文生图
                logger.info("使用文生图模式")
                
                # 调用即梦API
                api_result = self.jimeng_client.generate_text_to_image(
                    prompt=task.prompt,
                    model=task.model,
                    ratio=task.ratio
                )
                
                result["api_response"] = api_result
                
                if api_result.get("success"):
                    result["success"] = True
                    result["history_id"] = api_result.get("history_id")
                    result["image_urls"] = api_result.get("urls", [])
                    
                    logger.info(f"API调用成功，生成 {len(result['image_urls'])} 张图片")
                    logger.info(f"  - 图片URL列表:")
                    for idx, img_url in enumerate(result['image_urls'], 1):
                        logger.info(f"    [{idx}] {img_url}")
                    
                    # 下载并保存图片
                    for idx, img_url in enumerate(result["image_urls"]):
                        saved_path = self._download_and_save_image(
                            url=img_url,
                            task_id=task.id,
                            task_name=task.name,
                            index=idx
                        )
                        if saved_path:
                            result["saved_files"].append(saved_path)
                            logger.info(f"  ✓ 图片已保存: {saved_path}")
                else:
                    result["error"] = api_result.get("error", "API调用失败")
                    logger.error(f"API调用失败: {result['error']}")
                    logger.error(f"  - 完整API响应: {json.dumps(api_result, ensure_ascii=False, indent=2)}")
            
        except Exception as e:
            result["error"] = str(e)
            logger.error(f"执行图片任务异常: {e}", exc_info=True)
        
        return result
    
    def execute_video_task(self, task) -> Dict:
        """
        执行视频任务
        
        Args:
            task: 任务对象
            
        Returns:
            执行结果
        """
        logger.info(f"开始执行视频任务 [ID:{task.id}] - {task.name}")
        logger.info(f"  - 模型: {task.model}")
        logger.info(f"  - 比例: {task.ratio}")
        logger.info(f"  - 时长: {task.duration}秒")
        logger.info(f"  - 提示词: {task.prompt}")  # 完整显示提示词
        
        result = {
            "success": False,
            "history_id": None,
            "video_url": None,
            "saved_file": None,
            "error": None,
            "api_response": None
        }
        
        try:
            # 判断任务类型
            if task.image_material_id:
                # 多图视频
                logger.info("检测到参考图片，使用多图视频模式")
                # TODO: 实现多图视频逻辑
                result["error"] = "多图视频功能待实现"
            else:
                # 文生视频
                logger.info("使用文生视频模式")
                
                # 调用即梦API
                api_result = self.jimeng_client.generate_text_to_video(
                    prompt=task.prompt,
                    model=task.model,
                    ratio=task.ratio,
                    duration=task.duration or 4
                )
                
                result["api_response"] = api_result
                
                if api_result.get("success"):
                    result["success"] = True
                    result["history_id"] = api_result.get("history_id")
                    result["video_url"] = api_result.get("url")
                    
                    logger.info(f"API调用成功，视频URL: {result['video_url']}")
                    
                    # 下载并保存视频
                    if result["video_url"]:
                        saved_path = self._download_and_save_video(
                            url=result["video_url"],
                            task_id=task.id,
                            task_name=task.name
                        )
                        if saved_path:
                            result["saved_file"] = saved_path
                            logger.info(f"  ✓ 视频已保存: {saved_path}")
                else:
                    result["error"] = api_result.get("error", "API调用失败")
                    logger.error(f"API调用失败: {result['error']}")
                    logger.error(f"  - 完整API响应: {json.dumps(api_result, ensure_ascii=False, indent=2)}")
            
        except Exception as e:
            result["error"] = str(e)
            logger.error(f"执行视频任务异常: {e}", exc_info=True)
        
        return result
    
    def _download_and_save_image(self, url: str, task_id: int, task_name: str, index: int) -> Optional[str]:
        """
        下载并保存图片
        
        Args:
            url: 图片URL
            task_id: 任务ID
            task_name: 任务名称
            index: 图片索引
            
        Returns:
            保存的文件路径
        """
        import requests
        
        try:
            logger.info(f"正在下载图片: {url}")
            response = requests.get(url, timeout=120)
            response.raise_for_status()
            
            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = "".join(c for c in task_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"task{task_id}_{safe_name}_{timestamp}_{index}.png"
            filepath = self.output_dir / filename
            
            # 保存文件
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"图片保存成功: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"下载图片失败: {e}")
            return None
    
    def _download_and_save_video(self, url: str, task_id: int, task_name: str) -> Optional[str]:
        """
        下载并保存视频
        
        Args:
            url: 视频URL
            task_id: 任务ID
            task_name: 任务名称
            
        Returns:
            保存的文件路径
        """
        import requests
        
        try:
            logger.info(f"正在下载视频: {url}")
            response = requests.get(url, timeout=300)
            response.raise_for_status()
            
            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = "".join(c for c in task_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"task{task_id}_{safe_name}_{timestamp}.mp4"
            filepath = self.output_dir / filename
            
            # 保存文件
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"视频保存成功: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"下载视频失败: {e}")
            return None
    
    def update_task_status(self, task_id: int, status: str, error_message: Optional[str] = None):
        """
        更新任务状态
        
        Args:
            task_id: 任务ID
            status: 新状态
            error_message: 错误信息（如果有）
        """
        session = self.Session()
        try:
            task = session.query(Task).filter(Task.id == task_id).first()
            if task:
                task.status = status
                task.last_run_time = datetime.now()
                task.run_count += 1
                
                if error_message:
                    task.error_message = error_message
                
                session.commit()
                logger.info(f"任务 [ID:{task_id}] 状态已更新为: {status}")
            else:
                logger.warning(f"未找到任务 [ID:{task_id}]")
                
        except Exception as e:
            session.rollback()
            logger.error(f"更新任务状态失败: {e}")
        finally:
            session.close()
    
    def save_execution_log(self, task: Task, result: Dict, start_time: datetime, end_time: datetime):
        """
        保存执行日志到数据库
        
        Args:
            task: 任务对象
            result: 执行结果
            start_time: 开始时间
            end_time: 结束时间
        """
        session = self.Session()
        try:
            duration = int((end_time - start_time).total_seconds())
            
            execution = TaskExecution(
                task_id=task.id,
                status="success" if result["success"] else "failed",
                started_at=start_time,
                completed_at=end_time,  # 使用completed_at而不是finished_at
                duration_seconds=duration,
                history_id=result.get("history_id"),
                error_message=result.get("error")
            )
            
            session.add(execution)
            session.commit()
            
            logger.info(f"执行日志已保存 [Task:{task.id}, Execution:{execution.id}]")
            
        except Exception as e:
            session.rollback()
            logger.error(f"保存执行日志失败: {e}")
        finally:
            session.close()
    
    def execute_task(self, task):
        """
        执行单个任务
        注意：此方法如果失败会抛出异常，由调用方处理
        
        Args:
            task: 任务对象
        """
        logger.info("=" * 60)
        logger.info(f"开始执行任务 [ID:{task.id}] - {task.name}")
        logger.info(f"任务类型: {task.type}")
        logger.info(f"计划执行时间: {task.scheduled_time}")
        logger.info("=" * 60)
        
        start_time = datetime.now()
        
        try:
            # 更新任务状态为 running
            self.update_task_status(task.id, "running")
            flush_logs()  # 立即写入日志
            
            # 执行任务
            if task.type == "image":
                result = self.execute_image_task(task)
            elif task.type == "video":
                # 视频任务需要特别注意：可能包含长时间轮询
                logger.info("⚠ 视频任务将进入轮询等待状态，期间不会执行其他任务")
                result = self.execute_video_task(task)
            else:
                raise ValueError(f"未知的任务类型: {task.type}")
            
            # 检查执行结果
            if not result.get("success"):
                raise Exception(result.get("error", "任务执行失败"))
            
            flush_logs()  # 立即写入日志
            
            # 更新任务状态为 completed
            self.update_task_status(task.id, "completed")
            logger.info(f"✓ 任务 [ID:{task.id}] 执行成功")
            flush_logs()  # 立即写入日志
            
            # 保存执行日志
            end_time = datetime.now()
            self.save_execution_log(task, result, start_time, end_time)
            
            # 记录执行结果
            duration = (end_time - start_time).total_seconds()
            
            logger.info("-" * 60)
            logger.info(f"任务执行完成 [ID:{task.id}]")
            logger.info(f"  - 状态: 成功")
            logger.info(f"  - 耗时: {duration:.2f}秒")
            if result.get('saved_files'):
                logger.info(f"  - 保存文件: {result['saved_files']}")
            elif result.get('saved_file'):
                logger.info(f"  - 保存文件: {result['saved_file']}")
            else:
                logger.info(f"  - 保存文件: 无")
            logger.info("-" * 60)
            flush_logs()  # 立即写入日志
            
        except Exception as e:
            # 重新抛出异常，让调用方处理
            logger.error(f"任务执行异常 [ID:{task.id}]: {e}")
            flush_logs()  # 立即写入日志
            raise
    
    def run_once(self):
        """
        执行一次任务检测和执行
        单线程顺序执行，按scheduled_time排序
        """
        logger.info("\n" + "=" * 60)
        logger.info(f"开始任务检测 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 60)
        flush_logs()  # 立即写入日志
        
        try:
            # 获取待执行任务
            tasks = self.get_pending_tasks()
            
            if not tasks:
                logger.info("暂无待执行任务")
                return
            
            # 按scheduled_time排序（最早的先执行）
            tasks.sort(key=lambda t: t.scheduled_time)
            
            logger.info(f"找到 {len(tasks)} 个待执行任务，按执行时间排序")
            
            # 单线程顺序执行每个任务
            for idx, task in enumerate(tasks, 1):
                logger.info(f"\n{'='*60}")
                logger.info(f"准备执行第 {idx}/{len(tasks)} 个任务 [ID:{task.id}]")
                logger.info(f"计划执行时间: {task.scheduled_time}")
                logger.info(f"{'='*60}")
                
                try:
                    # 执行单个任务（如果失败会抛出异常）
                    self.execute_task(task)
                    logger.info(f"✓ 任务 [ID:{task.id}] 执行完成\n")
                    flush_logs()  # 立即写入日志
                    
                except Exception as e:
                    # 任务执行失败，记录错误并继续下一个
                    logger.error(f"✗ 任务 [ID:{task.id}] 执行失败: {e}")
                    logger.error(f"错误详情: {str(e)}", exc_info=True)
                    logger.info(f"→ 跳过当前任务，继续执行下一个任务\n")
                    flush_logs()  # 立即写入日志
                    
                    # 更新任务状态为failed
                    try:
                        self.update_task_status(task.id, "failed", str(e))
                    except Exception as update_error:
                        logger.error(f"更新任务状态失败: {update_error}")
                    
                    continue  # 继续下一个任务
                
        except Exception as e:
            logger.error(f"任务检测执行失败: {e}", exc_info=True)
    
    def run_continuous(self, interval: int = 300):
        """
        持续运行任务检测
        
        Args:
            interval: 检测间隔（秒），默认300秒（5分钟）
        """
        logger.info(f"启动持续任务检测，间隔: {interval}秒")
        logger.info("按 Ctrl+C 停止")
        
        try:
            while True:
                self.run_once()
                
                logger.info(f"等待 {interval}秒后进行下次检测...")
                time.sleep(interval)
                
        except KeyboardInterrupt:
            logger.info("\n收到停止信号，任务执行器已退出")
        except Exception as e:
            logger.error(f"持续运行异常: {e}", exc_info=True)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="SeeDance 任务执行器")
    parser.add_argument(
        "--interval",
        type=int,
        default=300,
        help="任务检测间隔（秒），默认300秒（5分钟）"
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="只执行一次检测，不持续运行"
    )
    
    args = parser.parse_args()
    
    # 创建执行器
    executor = TaskExecutor()
    
    if args.once:
        logger.info("执行单次任务检测")
        executor.run_once()
    else:
        logger.info(f"启动持续任务检测（间隔: {args.interval}秒）")
        executor.run_continuous(interval=args.interval)


if __name__ == "__main__":
    main()
