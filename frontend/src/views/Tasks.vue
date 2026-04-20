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

    <!-- 创建任务对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogType === 'image' ? '新建图片任务' : '新建视频任务'"
      width="600px"
    >
      <el-form :model="taskForm" label-width="100px">
        <el-form-item label="任务名称">
          <el-input v-model="taskForm.name" placeholder="请输入任务名称" />
        </el-form-item>
        
        <el-form-item label="提示词">
          <el-input
            v-model="taskForm.prompt"
            type="textarea"
            :rows="4"
            placeholder="请输入图片描述"
          />
        </el-form-item>

        <el-form-item label="选择模型">
          <el-select v-model="taskForm.model" placeholder="请选择模型" style="width: 100%">
            <el-option
              v-for="model in modelList"
              :key="model.value"
              :label="model.label"
              :value="model.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="图片比例">
          <el-select v-model="taskForm.ratio" placeholder="请选择比例" style="width: 100%">
            <el-option label="1:1" value="1:1" />
            <el-option label="16:9" value="16:9" />
            <el-option label="9:16" value="9:16" />
            <el-option label="4:3" value="4:3" />
            <el-option label="3:4" value="3:4" />
          </el-select>
        </el-form-item>

        <el-form-item label="参考图片" v-if="dialogType === 'image'">
          <el-select
            v-model="taskForm.image_urls"
            multiple
            placeholder="选择参考图片（可选）"
            style="width: 100%"
          >
            <el-option
              v-for="img in materialList"
              :key="img.id"
              :label="img.name"
              :value="img.file_url"
            >
              <div style="display: flex; align-items: center;">
                <el-image
                  :src="img.file_url"
                  style="width: 40px; height: 40px; margin-right: 8px;"
                  fit="cover"
                />
                <span>{{ img.name }}</span>
              </div>
            </el-option>
          </el-select>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCreateTask" :loading="creating">
          创建任务
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getTasks, deleteTask, runTask, createTask } from '@/api/task'
import { getMaterials } from '@/api/material'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const creating = ref(false)
const taskList = ref([])
const materialList = ref([])
const dialogVisible = ref(false)
const dialogType = ref('image')

// 图片模型列表
const imageModels = [
  { label: '即梦4.0', value: 'jimeng_v4' },
  { label: '即梦3.0', value: 'jimeng_v3' },
  { label: '高美学质量v5', value: 'high_aes_general_v5_0_pro' },
  { label: '专业渲染v2', value: 'professional_render_v2' },
]

// 视频模型列表
const videoModels = [
  { label: '即梦视频2.0', value: 'jimeng_video_v2' },
  { label: '即梦视频1.5', value: 'jimeng_video_v1_5' },
  { label: '高清视频生成', value: 'hd_video_gen' },
]

const modelList = ref([])

const taskForm = ref({
  name: '',
  prompt: '',
  model: '',
  ratio: '1:1',
  image_urls: []
})

const fetchTasks = async () => {
  loading.value = true
  try {
    const res = await getTasks({ page: 1, page_size: 20 })
    taskList.value = res.items || []
  } finally {
    loading.value = false
  }
}

const fetchMaterials = async () => {
  try {
    const res = await getMaterials({ page: 1, page_size: 100 })
    materialList.value = (res.items || []).filter(m => m.type === 'image')
  } catch (error) {
    console.error('获取素材列表失败:', error)
  }
}

const showCreateDialog = (type) => {
  dialogType.value = type
  modelList.value = type === 'image' ? imageModels : videoModels
  taskForm.value = {
    name: '',
    prompt: '',
    model: '',
    ratio: type === 'image' ? '1:1' : '16:9',
    image_urls: []
  }
  dialogVisible.value = true
}

const handleCreateTask = async () => {
  if (!taskForm.value.name || !taskForm.value.prompt || !taskForm.value.model) {
    ElMessage.warning('请填写完整信息')
    return
  }

  creating.value = true
  try {
    await createTask({
      ...taskForm.value,
      type: dialogType.value
    })
    ElMessage.success('任务创建成功')
    dialogVisible.value = false
    fetchTasks()
  } catch (error) {
    console.error('创建任务失败:', error)
  } finally {
    creating.value = false
  }
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

onMounted(() => {
  fetchTasks()
  fetchMaterials()
})
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
