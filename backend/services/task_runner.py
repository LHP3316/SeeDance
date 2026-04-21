from database import SessionLocal
from models.task import Task, TaskStatusEnum
from models.task_execution import TaskExecution, ExecutionStatusEnum
from services.jimeng_service import jimeng_service
from datetime import datetime


class TaskRunner:
    """任务执行器"""
    
    def run_task(self, task_id: int):
        """执行任务"""
        db = SessionLocal()
        try:
            task = db.query(Task).filter(Task.id == task_id).first()
            if not task:
                return
            
            # 创建执行记录
            execution = TaskExecution(
                task_id=task_id,
                status=ExecutionStatusEnum.running
            )
            db.add(execution)
            db.commit()
            
            # 更新任务状态
            task.status = TaskStatusEnum.running
            task.run_count += 1
            db.commit()
            
            # TODO: 执行实际任务逻辑
            
            # 更新执行结果
            execution.status = ExecutionStatusEnum.success
            execution.finished_at = datetime.now()
            db.commit()
            
        except Exception as e:
            # 记录错误
            if 'execution' in locals():
                execution.status = ExecutionStatusEnum.failed
                execution.error_message = str(e)
                db.commit()
        finally:
            db.close()


task_runner = TaskRunner()
