-- 创建数据库
CREATE DATABASE IF NOT EXISTS seedance_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建用户
CREATE USER IF NOT EXISTS 'seedance'@'localhost' IDENTIFIED BY 'seedance123';
GRANT ALL PRIVILEGES ON seedance_db.* TO 'seedance'@'localhost';
FLUSH PRIVILEGES;
