<template>
  <div class="materials">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>素材库</span>
          <el-upload
            :action="uploadUrl"
            :headers="uploadHeaders"
            :on-success="handleUploadSuccess"
            :show-file-list="false"
          >
            <el-button type="primary">上传素材</el-button>
          </el-upload>
        </div>
      </template>

      <div class="materials-grid" v-loading="loading">
        <div
          v-for="item in materialList"
          :key="item.id"
          class="material-card"
          @click="previewMaterial(item)"
        >
          <div class="card-image">
            <el-image
              v-if="item.type === 'image'"
              :src="getImageUrl(item.file_url)"
              fit="cover"
              class="material-image"
              lazy
            >
              <template #error>
                <div class="image-error">
                  <el-icon :size="40"><Picture /></el-icon>
                  <span>加载失败</span>
                </div>
              </template>
              <template #placeholder>
                <div class="image-loading">
                  <el-icon class="is-loading" :size="30"><Loading /></el-icon>
                </div>
              </template>
            </el-image>
            <div v-else class="video-placeholder">
              <el-icon :size="50"><VideoPlay /></el-icon>
              <span>视频文件</span>
            </div>

            <div class="card-overlay">
              <el-button type="primary" size="small" @click.stop="previewMaterial(item)">
                <el-icon><ZoomIn /></el-icon>
                查看大图
              </el-button>
            </div>
          </div>

          <div class="card-info">
            <div class="card-name" :title="getDisplayName(item)">{{ getDisplayName(item) }}</div>
            <div class="card-meta">
              <el-tag :type="item.type === 'image' ? 'success' : 'primary'" size="small">
                {{ item.type === 'image' ? '图片' : '视频' }}
              </el-tag>
              <span class="card-time">{{ formatDate(item.created_at) }}</span>
            </div>
          </div>
        </div>

        <el-empty v-if="!loading && materialList.length === 0" description="暂无素材，请先上传" />
      </div>

      <!-- 分页 -->
      <div class="pagination-container" v-if="total > 0">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[12, 24, 36, 48]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <el-dialog
      v-model="previewVisible"
      :title="getDisplayName(currentMaterial) || '素材预览'"
      width="900px"
      :close-on-click-modal="true"
      class="preview-dialog"
    >
      <div class="preview-container">
        <el-image
          :src="getImageUrl(previewUrl)"
          fit="contain"
          style="width: 100%; max-height: 70vh"
          :preview-src-list="[getImageUrl(previewUrl)]"
        />
      </div>
      <div class="preview-info">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="文件名">{{ getDisplayName(currentMaterial) }}</el-descriptions-item>
          <el-descriptions-item label="类型">
            <el-tag :type="currentMaterial?.type === 'image' ? 'success' : 'primary'">
              {{ currentMaterial?.type === 'image' ? '图片' : '视频' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="上传时间">{{ formatDate(currentMaterial?.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="文件路径">{{ currentMaterial?.file_path }}</el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getMaterials } from '@/api/material'
import { ElMessage } from 'element-plus'
import { Picture, VideoPlay, ZoomIn, Loading } from '@element-plus/icons-vue'

const loading = ref(false)
const materialList = ref([])
const uploadUrl = 'http://localhost:8000/api/materials/upload'
const uploadHeaders = {
  Authorization: `Bearer ${localStorage.getItem('token')}`
}

// 分页相关
const currentPage = ref(1)
const pageSize = ref(12)
const total = ref(0)

const previewVisible = ref(false)
const previewUrl = ref('')
const currentMaterial = ref(null)

const getImageUrl = (url) => {
  if (!url) return ''
  if (url.startsWith('/uploads/')) return `http://localhost:8000${url}`
  if (url.startsWith('http://') || url.startsWith('https://')) return url
  return `http://localhost:8000${url.startsWith('/') ? '' : '/'}${url}`
}

const extractNameFromPath = (value) => {
  if (!value) return ''
  const normalized = String(value).replace(/\\/g, '/')
  const filename = normalized.split('/').pop() || ''
  try {
    return decodeURIComponent(filename)
  } catch {
    return filename
  }
}

const getDisplayName = (material) => {
  if (!material) return ''
  return (
    extractNameFromPath(material.name) ||
    extractNameFromPath(material.file_path) ||
    extractNameFromPath(material.file_url) ||
    '-'
  )
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const fetchMaterials = async () => {
  loading.value = true
  try {
    const res = await getMaterials({ page: currentPage.value, page_size: pageSize.value })
    materialList.value = res.items || []
    total.value = res.total || 0
  } finally {
    loading.value = false
  }
}

const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1 // 改变每页数量时重置到第一页
  fetchMaterials()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  fetchMaterials()
}

const handleUploadSuccess = () => {
  ElMessage.success('上传成功')
  currentPage.value = 1 // 上传后回到第一页
  fetchMaterials()
}

const previewMaterial = (material) => {
  currentMaterial.value = material
  previewUrl.value = material.file_url
  previewVisible.value = true
}

onMounted(fetchMaterials)
</script>

<style scoped>
.materials {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.materials-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
  padding: 10px 0;
  min-height: 400px;
}

.material-card {
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  cursor: pointer;
  position: relative;
}

.material-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 20px 0 rgba(0, 0, 0, 0.15);
}

.card-image {
  position: relative;
  width: 100%;
  height: 200px;
  background: #f5f7fa;
  overflow: hidden;
}

.material-image {
  width: 100%;
  height: 100%;
  transition: transform 0.3s ease;
}

.material-card:hover .material-image {
  transform: scale(1.05);
}

.image-loading,
.image-error,
.video-placeholder {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
  background: #f5f7fa;
  color: #909399;
  gap: 10px;
}

.image-error span,
.video-placeholder span {
  font-size: 12px;
}

.card-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 10px;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.material-card:hover .card-overlay {
  opacity: 1;
}

.card-info {
  padding: 12px;
}

.card-name {
  font-size: 14px;
  color: #303133;
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-time {
  font-size: 12px;
  color: #909399;
}

.preview-dialog :deep(.el-dialog__body) {
  padding: 20px;
}

.preview-container {
  display: flex;
  justify-content: center;
  align-items: center;
  background: #f5f7fa;
  padding: 20px;
  border-radius: 4px;
  min-height: 400px;
}

.preview-info {
  margin-top: 20px;
}

.pagination-container {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 20px;
  padding: 20px 0;
}

@media (max-width: 768px) {
  .materials-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 15px;
  }

  .card-image {
    height: 150px;
  }
}
</style>
