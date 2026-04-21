"""
数据库迁移：为task_images表添加reference_name字段
"""
from sqlalchemy import text
from database import engine

def migrate():
    """添加reference_name字段"""
    with engine.connect() as conn:
        # 检查字段是否已存在
        result = conn.execute(text("""
            SELECT COUNT(*) 
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'task_images' 
            AND COLUMN_NAME = 'reference_name'
        """))
        
        exists = result.scalar() > 0
        
        if not exists:
            print("添加reference_name字段到task_images表...")
            conn.execute(text("""
                ALTER TABLE task_images 
                ADD COLUMN reference_name VARCHAR(200) NULL COMMENT '图片引用名称'
            """))
            conn.commit()
            print("✓ reference_name字段添加成功")
        else:
            print("✓ reference_name字段已存在，跳过")

if __name__ == "__main__":
    try:
        migrate()
        print("迁移完成！")
    except Exception as e:
        print(f"迁移失败: {e}")
        raise
