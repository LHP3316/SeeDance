-- 创建数据库
CREATE DATABASE IF NOT EXISTS seedance_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建用户
CREATE USER IF NOT EXISTS 'seedance'@'localhost' IDENTIFIED BY 'seedance123';
GRANT ALL PRIVILEGES ON seedance_db.* TO 'seedance'@'localhost';
FLUSH PRIVILEGES;

-- 为已存在的表添加缺失字段（如果字段已存在会跳过）
ALTER TABLE materials ADD COLUMN IF NOT EXISTS original_name VARCHAR(200) NULL COMMENT '原始文件名';
ALTER TABLE task_images ADD COLUMN IF NOT EXISTS reference_name VARCHAR(200) NULL COMMENT '图片引用名称';

-- 修改tasks表的duration字段类型：从Integer改为String，支持存储"4s"、"5s"等格式
ALTER TABLE tasks MODIFY COLUMN duration VARCHAR(20) NULL COMMENT '视频时长(如 "4s", "5s")';
