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
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="type" label="类型" width="100" />
        <el-table-column prop="created_at" label="上传时间" width="180" />
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button type="danger" size="small" @click="handleDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getMaterials, deleteMaterial } from '@/api/material'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const materialList = ref([])
const uploadUrl = 'http://localhost:8000/api/materials/upload'
const uploadHeaders = {
  Authorization: `Bearer ${localStorage.getItem('token')}`
}

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
</style>
