<template>
  <div class="tasks">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>任务列表</span>
          <div>
            <el-button type="success" @click="showCreateDialog('image')">新建图片任务</el-button>
            <el-button type="primary" @click="showCreateDialog('video')">新建视频任务</el-button>
          </div>
        </div>
      </template>
      
      <el-table :data="taskList" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="任务名称" />
        <el-table-column prop="type" label="类型" width="100" />
        <el-table-column prop="status" label="状态" width="100" />
        <el-table-column prop="model" label="模型" width="150" />
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button size="small" @click="handleRun(row.id)">执行</el-button>
            <el-button type="danger" size="small" @click="handleDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getTasks, deleteTask, runTask } from '@/api/task'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const taskList = ref([])

const fetchTasks = async () => {
  loading.value = true
  try {
    const res = await getTasks({ page: 1, page_size: 20 })
    taskList.value = res.items || []
  } finally {
    loading.value = false
  }
}

const showCreateDialog = (type) => {
  ElMessage.info(`${type === 'image' ? '图片' : '视频'}任务创建功能开发中`)
}

const handleRun = async (id) => {
  await runTask(id)
  ElMessage.success('任务已启动')
  fetchTasks()
}

const handleDelete = async (id) => {
  await ElMessageBox.confirm('确定删除?', '提示')
  await deleteTask(id)
  ElMessage.success('删除成功')
  fetchTasks()
}

onMounted(fetchTasks)
</script>

<style scoped>
.tasks {
  padding: 20px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
