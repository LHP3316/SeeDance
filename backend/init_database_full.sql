-- ==========================================
-- SeeDance 后台管理系统 - 数据库初始化脚本
-- ==========================================
-- 创建日期: 2026-04-21
-- 数据库: MySQL 8.0+
-- 字符集: utf8mb4
-- ==========================================

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ==========================================
-- 1. 创建数据库和用户
-- ==========================================
CREATE DATABASE IF NOT EXISTS seedance_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'seedance'@'localhost' IDENTIFIED BY 'seedance123';
GRANT ALL PRIVILEGES ON seedance_db.* TO 'seedance'@'localhost';
FLUSH PRIVILEGES;

USE seedance_db;

-- ==========================================
-- 2. 用户表 (users)
-- ==========================================
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users`  (
  `id` int(0) NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `username` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '用户名',
  `password_hash` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '密码哈希值',
  `role` enum('super_admin','admin') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'admin' COMMENT '角色：super_admin-超级管理员，admin-管理员',
  `is_active` tinyint(1) NOT NULL DEFAULT 1 COMMENT '是否启用：1-启用，0-禁用',
  `created_at` datetime(0) NOT NULL DEFAULT CURRENT_TIMESTAMP(0) COMMENT '创建时间',
  `updated_at` datetime(0) NOT NULL DEFAULT CURRENT_TIMESTAMP(0) ON UPDATE CURRENT_TIMESTAMP(0) COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `username`(`username`) USING BTREE,
  INDEX `idx_username`(`username`) USING BTREE,
  INDEX `idx_role`(`role`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '用户表' ROW_FORMAT = Dynamic;

-- ==========================================
-- 3. 素材表 (materials)
-- ==========================================
DROP TABLE IF EXISTS `materials`;
CREATE TABLE `materials`  (
  `id` int(0) NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '素材名称',
  `type` enum('image','video') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '素材类型：image-图片，video-视频',
  `file_path` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '文件存储路径',
  `file_url` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '文件访问URL',
  `file_size` bigint(0) NULL DEFAULT NULL COMMENT '文件大小（字节）',
  `width` int(0) NULL DEFAULT NULL COMMENT '图片/视频宽度',
  `height` int(0) NULL DEFAULT NULL COMMENT '图片/视频高度',
  `duration` float NULL DEFAULT NULL COMMENT '视频时长（秒）',
  `source` enum('generated','manual') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'manual' COMMENT '来源：generated-系统生成，manual-手动上传',
  `task_id` int(0) NULL DEFAULT NULL COMMENT '关联任务ID',
  `execution_id` int(0) NULL DEFAULT NULL COMMENT '关联执行记录ID',
  `created_by` int(0) NULL DEFAULT NULL COMMENT '创建者ID',
  `jimeng_uri` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '即梦平台URI',
  `created_at` datetime(0) NOT NULL DEFAULT CURRENT_TIMESTAMP(0) COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_type`(`type`) USING BTREE,
  INDEX `idx_source`(`source`) USING BTREE,
  INDEX `idx_task_id`(`task_id`) USING BTREE,
  INDEX `idx_created_by`(`created_by`) USING BTREE,
  CONSTRAINT `materials_ibfk_1` FOREIGN KEY (`task_id`) REFERENCES `tasks` (`id`) ON DELETE SET NULL ON UPDATE RESTRICT,
  CONSTRAINT `materials_ibfk_2` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE SET NULL ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '素材表' ROW_FORMAT = Dynamic;

-- ==========================================
-- 4. 任务表 (tasks)
-- ==========================================
DROP TABLE IF EXISTS `tasks`;
CREATE TABLE `tasks`  (
  `id` int(0) NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '任务名称',
  `type` enum('image','video') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '任务类型：image-图片任务，video-视频任务',
  `prompt` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '提示词',
  `model` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '模型名称',
  `ratio` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '画幅比例（如 16:9, 4:3, 1:1）',
  `duration` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '视频时长（如 "4s", "5s"）',
  `resolution` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '分辨率（如 2K, 4K）',
  `image_size` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '图片尺寸',
  `params` json NULL COMMENT '扩展参数（JSON格式）',
  `status` enum('pending','queued','running','completed','failed') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'pending' COMMENT '任务状态：pending-待执行，queued-已排队，running-执行中，completed-已完成，failed-失败',
  `schedule_type` enum('manual','once','cron') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'manual' COMMENT '调度类型：manual-手动，once-一次性，cron-定时任务',
  `cron_expression` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT 'Cron表达式',
  `scheduled_time` datetime(0) NULL DEFAULT NULL COMMENT '计划执行时间',
  `next_run_time` datetime(0) NULL DEFAULT NULL COMMENT '下次执行时间',
  `last_run_time` datetime(0) NULL DEFAULT NULL COMMENT '上次执行时间',
  `run_count` int(0) NOT NULL DEFAULT 0 COMMENT '执行次数',
  `error_message` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL COMMENT '错误信息',
  `image_material_id` int(0) NULL DEFAULT NULL COMMENT '生成的图片素材ID',
  `video_material_id` int(0) NULL DEFAULT NULL COMMENT '生成的视频素材ID',
  `is_deleted` tinyint(1) NOT NULL DEFAULT 0 COMMENT '是否删除：1-已删除，0-未删除',
  `created_by` int(0) NOT NULL COMMENT '创建者ID',
  `created_at` datetime(0) NOT NULL DEFAULT CURRENT_TIMESTAMP(0) COMMENT '创建时间',
  `updated_at` datetime(0) NOT NULL DEFAULT CURRENT_TIMESTAMP(0) ON UPDATE CURRENT_TIMESTAMP(0) COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_status`(`status`) USING BTREE,
  INDEX `idx_type`(`type`) USING BTREE,
  INDEX `idx_schedule_type`(`schedule_type`) USING BTREE,
  INDEX `idx_created_by`(`created_by`) USING BTREE,
  INDEX `idx_is_deleted`(`is_deleted`) USING BTREE,
  CONSTRAINT `tasks_ibfk_1` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '任务表' ROW_FORMAT = Dynamic;

-- ==========================================
-- 5. 任务图片关联表 (task_images)
-- ==========================================
DROP TABLE IF EXISTS `task_images`;
CREATE TABLE `task_images`  (
  `id` int(0) NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `task_id` int(0) NOT NULL COMMENT '任务ID',
  `image_id` int(0) NOT NULL COMMENT '素材ID',
  `image_url` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '图片URL',
  `description` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '图片描述',
  `sort_order` int(0) NOT NULL DEFAULT 0 COMMENT '排序顺序',
  `created_at` datetime(0) NOT NULL DEFAULT CURRENT_TIMESTAMP(0) COMMENT '创建时间',
  `reference_name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '图片引用名称',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_task_id`(`task_id`) USING BTREE,
  INDEX `idx_image_id`(`image_id`) USING BTREE,
  CONSTRAINT `task_images_ibfk_1` FOREIGN KEY (`task_id`) REFERENCES `tasks` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '任务图片关联表' ROW_FORMAT = Dynamic;

-- ==========================================
-- 6. 任务执行记录表 (task_executions)
-- ==========================================
DROP TABLE IF EXISTS `task_executions`;
CREATE TABLE `task_executions`  (
  `id` int(0) NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `task_id` int(0) NOT NULL COMMENT '任务ID',
  `status` enum('running','success','failed') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '执行状态：running-执行中，success-成功，failed-失败',
  `started_at` datetime(0) NOT NULL COMMENT '开始时间',
  `completed_at` datetime(0) NULL DEFAULT NULL COMMENT '完成时间',
  `duration_seconds` int(0) NULL DEFAULT NULL COMMENT '执行时长（秒）',
  `history_id` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '即梦平台历史记录ID',
  `error_message` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL COMMENT '错误信息',
  `output_files` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL COMMENT '生成的文件路径列表（JSON格式）',
  `result_data` json NULL COMMENT '执行结果数据（JSON格式）',
  `created_at` datetime(0) NOT NULL DEFAULT CURRENT_TIMESTAMP(0) COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_task_id`(`task_id`) USING BTREE,
  INDEX `idx_status`(`status`) USING BTREE,
  INDEX `idx_started_at`(`started_at`) USING BTREE,
  CONSTRAINT `task_executions_ibfk_1` FOREIGN KEY (`task_id`) REFERENCES `tasks` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '任务执行记录表' ROW_FORMAT = Dynamic;

-- ==========================================
-- 7. 系统配置表 (system_configs)
-- ==========================================
DROP TABLE IF EXISTS `system_configs`;
CREATE TABLE `system_configs`  (
  `id` int(0) NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `key` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '配置键',
  `value` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '配置值',
  `description` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '配置描述',
  `updated_by` int(0) NULL DEFAULT NULL COMMENT '更新者ID',
  `updated_at` datetime(0) NOT NULL DEFAULT CURRENT_TIMESTAMP(0) ON UPDATE CURRENT_TIMESTAMP(0) COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `key`(`key`) USING BTREE,
  INDEX `idx_key`(`key`) USING BTREE,
  INDEX `updated_by`(`updated_by`) USING BTREE,
  CONSTRAINT `system_configs_ibfk_1` FOREIGN KEY (`updated_by`) REFERENCES `users` (`id`) ON DELETE SET NULL ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '系统配置表' ROW_FORMAT = Dynamic;

-- ==========================================
-- 8. 系统日志表 (system_logs)
-- ==========================================
DROP TABLE IF EXISTS `system_logs`;
CREATE TABLE `system_logs`  (
  `id` int(0) NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `level` enum('debug','info','warning','error') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'info' COMMENT '日志级别：debug-调试，info-信息，warning-警告，error-错误',
  `module` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '模块名称',
  `message` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '日志消息',
  `user_id` int(0) NULL DEFAULT NULL COMMENT '用户ID',
  `created_at` datetime(0) NOT NULL DEFAULT CURRENT_TIMESTAMP(0) COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_level`(`level`) USING BTREE,
  INDEX `idx_module`(`module`) USING BTREE,
  INDEX `idx_created_at`(`created_at`) USING BTREE,
  INDEX `user_id`(`user_id`) USING BTREE,
  CONSTRAINT `system_logs_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '系统日志表' ROW_FORMAT = Dynamic;

-- ==========================================
-- 初始化数据
-- ==========================================

-- 插入默认管理员账号（密码：admin123）
INSERT INTO `users` (`username`, `password_hash`, `role`, `is_active`) VALUES 
('admin', '$2b$12$UvSSdnWNoNqcoBRhWA.TneAj9438J.wCtEbd5Mu39ubIWCIn3wzaW', 'super_admin', 1);

-- 插入默认系统配置
INSERT INTO `system_configs` (`key`, `value`, `description`) VALUES 
('jimeng_session_id', '', '即梦API SessionID');

SET FOREIGN_KEY_CHECKS = 1;

-- ==========================================
-- 数据库初始化完成
-- ==========================================
