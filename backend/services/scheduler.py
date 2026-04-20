from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from database import SessionLocal
from models.task import Task, TaskStatusEnum


scheduler = BackgroundScheduler()


def init_scheduler():
    """初始化调度器"""
    db = SessionLocal()
    try:
        tasks = db.query(Task).filter(
            Task.schedule_type == "cron",
            Task.is_deleted == False
        ).all()
        
        for task in tasks:
            if task.cron_expression:
                scheduler.add_job(
                    execute_task,
                    CronTrigger.from_crontab(task.cron_expression),
                    args=[task.id],
                    id=f"task_{task.id}"
                )
        
        scheduler.start()
    finally:
        db.close()


def execute_task(task_id: int):
    """执行任务"""
    # TODO: 实现任务执行逻辑
    pass


def add_task_job(task_id: int, cron_expression: str):
    """添加任务调度"""
    scheduler.add_job(
        execute_task,
        CronTrigger.from_crontab(cron_expression),
        args=[task_id],
        id=f"task_{task_id}"
    )


def remove_task_job(task_id: int):
    """移除任务调度"""
    job_id = f"task_{task_id}"
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)
