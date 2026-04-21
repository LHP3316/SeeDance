-- 为 tasks 表添加 history_record_id 字段
-- 用于保存即梦平台的历史记录ID，方便后续查询和轮询

ALTER TABLE `tasks` 
ADD COLUMN `history_record_id` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '即梦平台历史记录ID' AFTER `video_material_id`;

-- 添加索引（可选，方便查询）
ALTER TABLE `tasks` 
ADD INDEX `idx_history_record_id`(`history_record_id`) USING BTREE;
