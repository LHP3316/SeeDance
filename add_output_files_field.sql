-- 为 task_executions 表添加 output_files 字段
-- 用于保存任务执行后生成的文件路径（JSON格式）

ALTER TABLE task_executions 
ADD COLUMN output_files TEXT NULL COMMENT '生成的文件路径列表（JSON格式）' 
AFTER error_message;

-- 验证字段是否添加成功
SELECT COLUMN_NAME, COLUMN_TYPE, COLUMN_COMMENT 
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_SCHEMA = DATABASE() 
  AND TABLE_NAME = 'task_executions' 
  AND COLUMN_NAME = 'output_files';
