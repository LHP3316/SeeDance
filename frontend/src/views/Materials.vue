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
      
      <el-table :data="materialList" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column label="预览" width="120">
          <template #default="{ row }">
            <el-image
              v-if="row.type === 'image'"
              :src="row.file_url"
              :preview-src-list="[row.file_url]"
              style="width: 80px; height: 80px; cursor: pointer;"
              fit="cover"
              preview-teleported
            >
              <template #error>
                <div class="image-error">
                  <el-icon><Picture /></el-icon>
                </div>
              </template>
            </el-image>
            <el-icon v-else style="font-size: 40px; color: #909399;">
              <VideoPlay />
            </el-icon>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="row.type === 'image' ? 'success' : 'primary'">
              {{ row.type === 'image' ? '图片' : '视频' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="上传时间" width="180" />
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button 
              v-if="row.type === 'image'" 
              type="primary" 
              size="small" 
              @click="previewImage(row)"
            >
              查看
            </el-button>
            <el-button type="danger" size="small" @click="handleDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 图片预览对话框 -->
    <el-dialog
      v-model="previewVisible"
      title="图片预览"
      width="800px"
      :close-on-click-modal="true"
    >
      <div class="preview-container">
        <el-image
          :src="previewUrl"
          fit="contain"
          style="width: 100%; max-height: 70vh;"
        />
      </div>
      <div class="preview-info">
        <p><strong>文件名：</strong>{{ currentMaterial?.name }}</p>
        <p><strong>上传时间：</strong>{{ currentMaterial?.created_at }}</p>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getMaterials, deleteMaterial } from '@/api/material'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Picture, VideoPlay } from '@element-plus/icons-vue'

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

const fetchMaterials = async () => {
  loading.value = true
  try {
    const res = await getMaterials({ page: 1, page_size: 20 })
    materialList.value = res.items || []
  } finally {
    loading.value = false
  }
}

const handleUploadSuccess = () => {
  ElMessage.success('上传成功')
  fetchMaterials()
}

const previewImage = (material) => {
  currentMaterial.value = material
  previewUrl.value = material.file_url
  previewVisible.value = true
}

const handleDelete = async (id) => {
  await ElMessageBox.confirm('确定删除?', '提示')
  await deleteMaterial(id)
  ElMessage.success('删除成功')
  fetchMaterials()
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
.image-error {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 80px;
  height: 80px;
  background: #f5f7fa;
  color: #909399;
  font-size: 24px;
}
.preview-container {
  display: flex;
  justify-content: center;
  align-items: center;
  background: #f5f7fa;
  padding: 20px;
  border-radius: 4px;
}
.preview-info {
  margin-top: 20px;
  padding: 15px;
  background: #f9f9f9;
  border-radius: 4px;
}
.preview-info p {
  margin: 8px 0;
  color: #606266;
}
</style>
