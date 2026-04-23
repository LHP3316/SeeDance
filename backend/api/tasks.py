from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from models.task import Task, TaskStatusEnum, ScheduleTypeEnum
from models.task_image import TaskImage
from schemas.task import TaskCreate, TaskUpdate, TaskResponse, ExecutionResponse
from core.deps import get_current_user, require_admin
from models.user import User

router = APIRouter(prefix="/tasks", tags=["任务管理"])


@router.get("/", response_model=dict)
async def list_tasks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    type: Optional[str] = None,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取任务列表"""
    try:
        query = db.query(Task).filter(Task.is_deleted == False)
        
        if type:
            query = query.filter(Task.type == type)
        if status:
            query = query.filter(Task.status == status)
        
        total = query.count()
        tasks = query.order_by(Task.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
        
        # 将Task对象转换为字典
        from schemas.task import TaskResponse
        from models.task_execution import TaskExecution
        import json
        
        task_items = []
        for task in tasks:
            task_dict = TaskResponse.model_validate(task).model_dump()
            
            # 如果任务已完成，获取执行结果
            if task.status == TaskStatusEnum.completed:
                # 查询最新的成功执行记录
                execution = db.query(TaskExecution).filter(
                    TaskExecution.task_id == task.id,
                    TaskExecution.status == 'success'
                ).order_by(TaskExecution.created_at.desc()).first()
                
                if execution and execution.output_files:
                    try:
                        # 解析output_files JSON
                        output_files = json.loads(execution.output_files)
                        task_dict['output_files'] = output_files
                        
                        # 区分图片和视频
                        task_dict['output_images'] = [f for f in output_files if f.endswith(('.png', '.jpg', '.jpeg', '.gif'))]
                        task_dict['output_videos'] = [f for f in output_files if f.endswith(('.mp4', '.avi', '.mov'))]
                    except:
                        task_dict['output_files'] = []
                        task_dict['output_images'] = []
                        task_dict['output_videos'] = []
                else:
                    task_dict['output_files'] = []
                    task_dict['output_images'] = []
                    task_dict['output_videos'] = []
            
            task_items.append(task_dict)
        
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "items": task_items
        }
    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        print(f"任务列表查询错误: {error_detail}")
        raise HTTPException(status_code=500, detail=error_detail)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取任务详情"""
    task = db.query(Task).filter(Task.id == task_id, Task.is_deleted == False).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return task


@router.post("/", response_model=TaskResponse)
async def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """创建任务"""
    task = Task(
        name=task_data.name,
        type=task_data.type,
        prompt=task_data.prompt,
        model=task_data.model,
        ratio=task_data.ratio,
        duration=task_data.duration,
        resolution=task_data.resolution,
        image_size=task_data.image_size,
        schedule_type=task_data.schedule_type,
        cron_expression=task_data.cron_expression,
        scheduled_time=task_data.scheduled_time,
        created_by=current_user.id
    )
    
    db.add(task)
    db.flush()
    
    # 添加关联图片（方式1：通过image_ids）
    if task_data.images:
        for idx, img_ref in enumerate(task_data.images):
            task_image = TaskImage(
                task_id=task.id,
                image_id=img_ref.image_id,
                reference_name=img_ref.reference_name,
                sort_order=idx
            )
            db.add(task_image)
    
    # 添加关联图片（方式2：通过image_urls）
    if task_data.image_urls:
        from models.material import Material
        for idx, img_url in enumerate(task_data.image_urls):
            # 根据URL查找素材
            material = db.query(Material).filter(Material.file_url == img_url).first()
            if material:
                task_image = TaskImage(
                    task_id=task.id,
                    image_id=material.id,
                    image_url=img_url,  # 保存图片URL
                    reference_name=material.name,
                    sort_order=idx
                )
                db.add(task_image)
    
    db.commit()
    db.refresh(task)
    return task


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """更新任务"""
    task = db.query(Task).filter(Task.id == task_id, Task.is_deleted == False).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    # 执行中的任务不可修改
    if task.status == TaskStatusEnum.running:
        raise HTTPException(status_code=400, detail="执行中的任务不可修改")
    
    update_data = task_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)
    
    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """软删除任务"""
    task = db.query(Task).filter(Task.id == task_id, Task.is_deleted == False).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    # 只有pending状态的任务可以删除
    if task.status != TaskStatusEnum.pending:
        raise HTTPException(status_code=400, detail="只有待执行的任务可以删除")
    
    task.is_deleted = True
    db.commit()
    return {"message": "任务已删除"}


@router.post("/{task_id}/run")
async def run_task(
    task_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """手动触发任务执行"""
    task = db.query(Task).filter(Task.id == task_id, Task.is_deleted == False).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    if task.status == TaskStatusEnum.running:
        raise HTTPException(status_code=400, detail="任务正在执行中")
    
    task.status = TaskStatusEnum.queued
    db.commit()
    
    return {"message": "任务已加入队列"}


@router.get("/{task_id}/executions", response_model=dict)
async def get_executions(
    task_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取任务执行记录"""
    from models.task_execution import TaskExecution
    
    query = db.query(TaskExecution).filter(TaskExecution.task_id == task_id)
    total = query.count()
    executions = query.order_by(TaskExecution.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": executions
    }
