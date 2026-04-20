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

# 文件处理器
file_handler = logging.FileHandler(
    LOG_DIR / f"task_executor_{datetime.now().strftime('%Y%m%d')}.log",
    encoding='utf-8'
)
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s'
)
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

# 控制台处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)


class TaskExecutor:
    """任务执行器"""
    
    def __init__(self):
        """初始化执行器"""
        # 数据库连接
        self.engine = create_engine(settings.resolved_database_url)
        self.Session = sessionmaker(bind=self.engine)
        
        # 即梦API客户端
        self.jimeng_client = JimengAPIClient(sessionid=settings.SESSION_ID)
        
        # 输出目录
        self.output_dir = Path(__file__).parent / "output"
        self.output_dir.mkdir(exist_ok=True)
        
        logger.info("=" * 60)
        logger.info("任务执行器初始化完成")
        logger.info(f"输出目录: {self.output_dir}")
        logger.info("=" * 60)
    
    def get_pending_tasks(self) -> List[Task]:
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
            tasks = session.query(Task).filter(
                Task.status == 'pending',
                Task.scheduled_time <= now,
                Task.is_deleted == False
            ).all()
            
            logger.info(f"查询到 {len(tasks)} 个待执行任务")
            return tasks
            
        except Exception as e:
            logger.error(f"查询待执行任务失败: {e}")
            return []
        finally:
            session.close()
    
    def execute_image_task(self, task: Task) -> Dict:
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
        logger.info(f"  - 提示词: {task.prompt[:50]}...")
        
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
                
                # ========== 测试模式：模拟API调用 ==========
                logger.info("[测试模式] 模拟API调用，不实际请求即梦API")
                import time
                time.sleep(2)  # 模拟API请求时间
                
                # 模拟API返回结果
                api_result = {
                    "success": True,
                    "history_id": f"test_history_{task.id}_{int(time.time())}",
                    "urls": [
                        f"https://example.com/test_image_{task.id}_0.png",
                        f"https://example.com/test_image_{task.id}_1.png"
                    ],
                    "error": None
                }
                
                logger.info(f"[测试模式] 模拟API调用成功，生成 {len(api_result['urls'])} 张图片")
                # ============================================
                
                # 正式环境时取消下面的注释，删除上面的模拟代码
                # api_result = self.jimeng_client.generate_text_to_image(
                #     prompt=task.prompt,
                #     model=task.model,
                #     ratio=task.ratio
                # )
                
                result["api_response"] = api_result
                
                if api_result.get("success"):
                    result["success"] = True
                    result["history_id"] = api_result.get("history_id")
                    result["image_urls"] = api_result.get("urls", [])
                    
                    logger.info(f"API调用成功，生成 {len(result['image_urls'])} 张图片")
                    
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
            
        except Exception as e:
            result["error"] = str(e)
            logger.error(f"执行图片任务异常: {e}", exc_info=True)
        
        return result
    
    def execute_video_task(self, task: Task) -> Dict:
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
        logger.info(f"  - 提示词: {task.prompt[:50]}...")
        
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
                
                # ========== 测试模式：模拟API调用 ==========
                logger.info("[测试模式] 模拟API调用，不实际请求即梦API")
                import time
                time.sleep(3)  # 模拟API请求时间（视频通常更慢）
                
                # 模拟API返回结果
                api_result = {
                    "success": True,
                    "history_id": f"test_history_{task.id}_{int(time.time())}",
                    "url": f"https://example.com/test_video_{task.id}.mp4",
                    "error": None
                }
                
                logger.info(f"[测试模式] 模拟API调用成功，视频URL: {api_result['url']}")
                # ============================================
                
                # 正式环境时取消下面的注释，删除上面的模拟代码
                # api_result = self.jimeng_client.generate_text_to_video(
                #     prompt=task.prompt,
                #     model=task.model,
                #     ratio=task.ratio,
                #     duration=task.duration or 4
                # )
                
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
        # ========== 测试模式：创建模拟文件 ==========
        logger.info(f"[测试模式] 模拟保存图片: {url}")
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = "".join(c for c in task_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"task{task_id}_{safe_name}_{timestamp}_{index}_TEST.png"
        filepath = self.output_dir / filename
        
        # 创建一个测试文件
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"测试文件 - 任务ID: {task_id}\n")
                f.write(f"任务名称: {task_name}\n")
                f.write(f"图片索引: {index}\n")
                f.write(f"原始URL: {url}\n")
                f.write(f"创建时间: {timestamp}\n")
                f.write(f"\n这是测试模式创建的模拟文件，实际运行时会是真实的图片。\n")
            
            logger.info(f"[测试模式] 测试图片文件创建成功: {filepath}")
            return str(filepath)
        except Exception as e:
            logger.error(f"[测试模式] 创建测试文件失败: {e}")
            return None
        # ============================================
        
        # 正式环境时取消下面的注释，删除上面的模拟代码
        # import requests
        # 
        # try:
        #     logger.info(f"正在下载图片: {url}")
        #     response = requests.get(url, timeout=120)
        #     response.raise_for_status()
        #     
        #     # 生成文件名
        #     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        #     safe_name = "".join(c for c in task_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        #     filename = f"task{task_id}_{safe_name}_{timestamp}_{index}.png"
        #     filepath = self.output_dir / filename
        #     
        #     # 保存文件
        #     with open(filepath, 'wb') as f:
        #         f.write(response.content)
        #     
        #     logger.info(f"图片保存成功: {filepath}")
        #     return str(filepath)
        #     
        # except Exception as e:
        #     logger.error(f"下载图片失败: {e}")
        #     return None
    
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
        # ========== 测试模式：创建模拟文件 ==========
        logger.info(f"[测试模式] 模拟保存视频: {url}")
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = "".join(c for c in task_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"task{task_id}_{safe_name}_{timestamp}_TEST.mp4"
        filepath = self.output_dir / filename
        
        # 创建一个测试文件
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"测试文件 - 任务ID: {task_id}\n")
                f.write(f"任务名称: {task_name}\n")
                f.write(f"原始URL: {url}\n")
                f.write(f"创建时间: {timestamp}\n")
                f.write(f"\n这是测试模式创建的模拟文件，实际运行时会是真实的视频。\n")
            
            logger.info(f"[测试模式] 测试视频文件创建成功: {filepath}")
            return str(filepath)
        except Exception as e:
            logger.error(f"[测试模式] 创建测试文件失败: {e}")
            return None
        # ============================================
        
        # 正式环境时取消下面的注释，删除上面的模拟代码
        # import requests
        # 
        # try:
        #     logger.info(f"正在下载视频: {url}")
        #     response = requests.get(url, timeout=300)
        #     response.raise_for_status()
        #     
        #     # 生成文件名
        #     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        #     safe_name = "".join(c for c in task_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        #     filename = f"task{task_id}_{safe_name}_{timestamp}.mp4"
        #     filepath = self.output_dir / filename
        #     
        #     # 保存文件
        #     with open(filepath, 'wb') as f:
        #         f.write(response.content)
        #     
        #     logger.info(f"视频保存成功: {filepath}")
        #     return str(filepath)
        #     
        # except Exception as e:
        #     logger.error(f"下载视频失败: {e}")
        #     return None
    
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
    
    def execute_task(self, task: Task):
        """
        执行单个任务
        
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
            
            # 执行任务
            if task.type == "image":
                result = self.execute_image_task(task)
            elif task.type == "video":
                result = self.execute_video_task(task)
            else:
                logger.error(f"未知的任务类型: {task.type}")
                result = {"success": False, "error": f"未知的任务类型: {task.type}"}
            
            # 更新任务状态
            if result["success"]:
                self.update_task_status(task.id, "completed")
                logger.info(f"✓ 任务 [ID:{task.id}] 执行成功")
            else:
                self.update_task_status(task.id, "failed", result.get("error"))
                logger.error(f"✗ 任务 [ID:{task.id}] 执行失败: {result.get('error')}")
            
            # 记录执行结果
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # 保存执行日志
            self.save_execution_log(task, result, start_time, end_time)
            
            logger.info("-" * 60)
            logger.info(f"任务执行完成 [ID:{task.id}]")
            logger.info(f"  - 状态: {'成功' if result['success'] else '失败'}")
            logger.info(f"  - 耗时: {duration:.2f}秒")
            if result.get('saved_files'):
                logger.info(f"  - 保存文件: {result['saved_files']}")
            elif result.get('saved_file'):
                logger.info(f"  - 保存文件: {result['saved_file']}")
            else:
                logger.info(f"  - 保存文件: 无")
            logger.info("-" * 60)
            
        except Exception as e:
            logger.error(f"任务执行异常 [ID:{task.id}]: {e}", exc_info=True)
            self.update_task_status(task.id, "failed", str(e))
    
    def run_once(self):
        """执行一次任务检测和执行"""
        logger.info("\n" + "=" * 60)
        logger.info(f"开始任务检测 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 60)
        
        try:
            # 获取待执行任务
            tasks = self.get_pending_tasks()
            
            if not tasks:
                logger.info("暂无待执行任务")
                return
            
            # 执行每个任务
            for task in tasks:
                self.execute_task(task)
                
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
