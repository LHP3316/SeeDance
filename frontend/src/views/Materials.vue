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
      
      <!-- 矩阵卡片布局 -->
      <div class="materials-grid" v-loading="loading">
        <div 
          v-for="item in materialList" 
          :key="item.id" 
          class="material-card"
          @click="previewMaterial(item)"
        >
          <!-- 图片预览 -->
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
            
            <!-- 悬停遮罩 -->
            <div class="card-overlay">
              <el-button type="primary" size="small" @click.stop="previewMaterial(item)">
                <el-icon><ZoomIn /></el-icon>
                查看
              </el-button>
              <el-button type="danger" size="small" @click.stop="handleDelete(item.id)">
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
            </div>
          </div>
          
          <!-- 卡片信息 -->
          <div class="card-info">
            <div class="card-name" :title="item.name">{{ item.name }}</div>
            <div class="card-meta">
              <el-tag :type="item.type === 'image' ? 'success' : 'primary'" size="small">
                {{ item.type === 'image' ? '图片' : '视频' }}
              </el-tag>
              <span class="card-time">{{ formatDate(item.created_at) }}</span>
            </div>
          </div>
        </div>
        
        <!-- 空状态 -->
        <el-empty v-if="!loading && materialList.length === 0" description="暂无素材，请上传" />
      </div>
    </el-card>

    <!-- 图片预览对话框 -->
    <el-dialog
      v-model="previewVisible"
      :title="currentMaterial?.name || '图片预览'"
      width="900px"
      :close-on-click-modal="true"
      class="preview-dialog"
    >
      <div class="preview-container">
        <el-image
          :src="getImageUrl(previewUrl)"
          fit="contain"
          style="width: 100%; max-height: 70vh;"
          :preview-src-list="[getImageUrl(previewUrl)]"
        />
      </div>
      <div class="preview-info">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="文件名">{{ currentMaterial?.name }}</el-descriptions-item>
          <el-descriptions-item label="类型">
            <el-tag :type="currentMaterial?.type === 'image' ? 'success' : 'primary'">
              {{ currentMaterial?.type === 'image' ? '图片' : '视频' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="上传时间">{{ currentMaterial?.created_at }}</el-descriptions-item>
          <el-descriptions-item label="文件路径">{{ currentMaterial?.file_path }}</el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getMaterials, deleteMaterial } from '@/api/material'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Picture, VideoPlay, ZoomIn, Delete, Loading } from '@element-plus/icons-vue'

const loading = ref(false)
const materialList = ref([])
const uploadUrl = 'http://localhost:8000/api/materials/upload'
const uploadHeaders = {
  Authorization: `Bearer ${localStorage.getItem('token')}`
}

// 预览相关
const previewVisible = ref(false)
const previewUrl = ref('')
const currentMaterial = ref(null)

// 获取完整的图片URL
const getImageUrl = (url) => {
  if (!url) return ''
  // 如果是相对路径，添加后端地址
  if (url.startsWith('/uploads/')) {
    return `http://localhost:8000${url}`
  }
  // 如果已经是完整URL，直接返回
  if (url.startsWith('http://') || url.startsWith('https://')) {
    return url
  }
  // 其他情况，添加后端地址
  return `http://localhost:8000${url.startsWith('/') ? '' : '/'}${url}`
}

// 格式化日期
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
    const res = await getMaterials({ page: 1, page_size: 50 })
    materialList.value = res.items || []
    console.log('素材列表:', materialList.value)
  } finally {
    loading.value = false
  }
}

const handleUploadSuccess = () => {
  ElMessage.success('上传成功')
  fetchMaterials()
}

const previewMaterial = (material) => {
  currentMaterial.value = material
  previewUrl.value = material.file_url
  previewVisible.value = true
}

const handleDelete = async (id) => {
  try {
    await ElMessageBox.confirm('确定删除此素材？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await deleteMaterial(id)
    ElMessage.success('删除成功')
    fetchMaterials()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
    }
  }
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

/* 矩阵布局 */
.materials-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
  padding: 10px 0;
  min-height: 400px;
}

/* 卡片样式 */
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

/* 图片区域 */
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

/* 加载状态 */
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

/* 悬停遮罩 */
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

/* 卡片信息 */
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

/* 预览对话框 */
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

/* 响应式 */
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
