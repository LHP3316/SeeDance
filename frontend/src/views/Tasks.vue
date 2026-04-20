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

    <!-- 创建图片任务对话框 -->
    <el-dialog
      v-model="imageDialogVisible"
      title="新建图片任务"
      width="800px"
      :close-on-click-modal="false"
    >
      <el-form :model="imageForm" :rules="imageRules" ref="imageFormRef" label-width="100px">
        <el-form-item label="任务名称" prop="name">
          <el-input v-model="imageForm.name" placeholder="请输入任务名称" />
        </el-form-item>
        
        <el-form-item label="选择模型" prop="model">
          <el-select v-model="imageForm.model" placeholder="请选择模型" style="width: 100%">
            <el-option-group label="Seedream系列">
              <el-option label="图片5.0 Lite - 指令响应更精准" value="jimeng_5_0_lite" />
              <el-option label="图片4.6 - 人像一致性更好" value="jimeng_4_6" />
            </el-option-group>
            <el-option-group label="经典系列">
              <el-option label="图片4.5 - 强化一致性" value="jimeng_4_5" />
              <el-option label="图片4.1 - 专业创意美学" value="jimeng_4_1" />
              <el-option label="图片4.0 - 支持多参考图" value="jimeng_4_0" />
              <el-option label="图片3.1 - 美学多样性" value="jimeng_3_1" />
              <el-option label="图片3.0 - 影视级质感" value="jimeng_3_0" />
            </el-option-group>
          </el-select>
        </el-form-item>

        <el-form-item label="图片比例" prop="ratio">
          <el-radio-group v-model="imageForm.ratio" class="ratio-group">
            <el-radio-button label="智能">智能</el-radio-button>
            <el-radio-button label="21:9">21:9</el-radio-button>
            <el-radio-button label="16:9">16:9</el-radio-button>
            <el-radio-button label="3:2">3:2</el-radio-button>
            <el-radio-button label="4:3">4:3</el-radio-button>
            <el-radio-button label="1:1">1:1</el-radio-button>
            <el-radio-button label="3:4">3:4</el-radio-button>
            <el-radio-button label="2:3">2:3</el-radio-button>
            <el-radio-button label="9:16">9:16</el-radio-button>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="分辨率" prop="resolution">
          <el-radio-group v-model="imageForm.resolution">
            <el-radio-button label="2K">高清 2K</el-radio-button>
            <el-radio-button label="4K">超清 4K</el-radio-button>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="上传图片">
          <el-upload
            ref="uploadRef"
            :action="uploadUrl"
            :headers="uploadHeaders"
            :on-success="handleUploadSuccess"
            :on-remove="handleRemoveFile"
            :file-list="imageForm.uploadedFiles"
            multiple
            :limit="5"
            list-type="picture-card"
            accept="image/*"
          >
            <el-icon><Plus /></el-icon>
          </el-upload>
          <div class="upload-tip">支持jpg/png格式，最多5张</div>
        </el-form-item>

        <el-form-item label="提示词" prop="prompt">
          <div class="prompt-container" @click.stop>
            <el-input
              v-model="imageForm.prompt"
              type="textarea"
              :rows="5"
              placeholder="请输入图片描述，输入 @ 可引用已上传的图片"
              @input="handlePromptInput"
              ref="promptInputRef"
              style="width: 100%"
            />
            
            <!-- @图片选择下拉框 -->
            <div 
              v-if="showImagePicker" 
              class="image-picker-dropdown"
              :style="pickerStyle"
              @click.stop
            >
              <div class="picker-header">
                <span>选择图片</span>
                <el-icon class="close-btn" @click="closeImagePicker"><Close /></el-icon>
              </div>
              <div class="picker-list">
                <div 
                  v-for="(file, index) in imageForm.uploadedFiles" 
                  :key="file.uid"
                  class="picker-item"
                  @click="insertImageTag(index)"
                >
                  <el-image
                    :src="file.url"
                    class="picker-image"
                    fit="cover"
                  />
                  <span class="picker-name">{{ file.name }}</span>
                </div>
                <div v-if="imageForm.uploadedFiles.length === 0" class="empty-tip">
                  <el-icon :size="40"><Picture /></el-icon>
                  <p>暂无图片，请先上传</p>
                </div>
              </div>
            </div>
          </div>
          
          <div v-if="imageForm.uploadedFiles.length > 0" class="image-tags">
            <span class="tag-label">已上传图片：</span>
            <span
              v-for="(file, index) in imageForm.uploadedFiles"
              :key="file.uid"
              class="image-tag-text"
            >
              @{{ file.name }}
              <el-icon class="remove-icon" @click="handleRemoveTag(index)"><Close /></el-icon>
            </span>
          </div>
        </el-form-item>

        <el-form-item label="执行时间">
          <el-date-picker
            v-model="imageForm.scheduledTime"
            type="datetime"
            placeholder="选择日期时间（可选）"
            :disabled-date="disabledDate"
            :disabled-hours="disabledHours"
            :disabled-minutes="disabledMinutes"
            :disabled-seconds="disabledSeconds"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DD HH:mm:ss"
            clearable
            style="width: 100%"
          />
          <div class="time-tip">不选择则立即执行</div>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="imageDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCreateImageTask" :loading="creating">
          创建任务
        </el-button>
      </template>
    </el-dialog>

    <!-- 创建视频任务对话框 -->
    <el-dialog
      v-model="videoDialogVisible"
      title="新建视频任务"
      width="600px"
    >
      <el-form :model="videoForm" label-width="100px">
        <el-form-item label="任务名称">
          <el-input v-model="videoForm.name" placeholder="请输入任务名称" />
        </el-form-item>
        
        <el-form-item label="提示词">
          <el-input
            v-model="videoForm.prompt"
            type="textarea"
            :rows="4"
            placeholder="请输入视频描述"
          />
        </el-form-item>

        <el-form-item label="选择模型">
          <el-select v-model="videoForm.model" placeholder="请选择模型" style="width: 100%">
            <el-option label="即梦视频2.0" value="jimeng_video_v2" />
            <el-option label="即梦视频1.5" value="jimeng_video_v1_5" />
            <el-option label="高清视频生成" value="hd_video_gen" />
          </el-select>
        </el-form-item>

        <el-form-item label="视频比例">
          <el-select v-model="videoForm.ratio" placeholder="请选择比例" style="width: 100%">
            <el-option label="16:9" value="16:9" />
            <el-option label="9:16" value="9:16" />
            <el-option label="1:1" value="1:1" />
          </el-select>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="videoDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCreateVideoTask" :loading="creating">
          创建任务
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getTasks, deleteTask, runTask, createTask } from '@/api/task'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Close, Picture } from '@element-plus/icons-vue'

const loading = ref(false)
const creating = ref(false)
const taskList = ref([])

// 图片任务相关
const imageDialogVisible = ref(false)
const imageFormRef = ref(null)
const uploadUrl = 'http://localhost:8000/api/materials/upload'
const uploadHeaders = {
  Authorization: `Bearer ${localStorage.getItem('token')}`
}

// 表单验证规则
const imageRules = {
  name: [{ required: true, message: '请输入任务名称', trigger: 'blur' }],
  model: [{ required: true, message: '请选择模型', trigger: 'change' }],
  ratio: [{ required: true, message: '请选择图片比例', trigger: 'change' }],
  resolution: [{ required: true, message: '请选择分辨率', trigger: 'change' }],
  prompt: [{ required: true, message: '请输入提示词', trigger: 'blur' }]
}

const imageForm = ref({
  name: '',
  model: '',
  ratio: '1:1',
  resolution: '2K',
  prompt: '',
  uploadedFiles: [],
  scheduledTime: ''
})

// @图片选择器相关
const showImagePicker = ref(false)
const pickerStyle = ref({})
const promptInputRef = ref(null)
const lastAtPosition = ref(null)

// 视频任务相关
const videoDialogVisible = ref(false)
const videoForm = ref({
  name: '',
  prompt: '',
  model: '',
  ratio: '16:9'
})

// 时间限制函数
const now = new Date()
const disabledDate = (time) => {
  return time.getTime() < Date.now() - 8.64e7 // 8.64e7 = 1天的毫秒数，允许今天
}

const disabledHours = () => {
  const selectedDate = imageForm.value.scheduledTime?.split(' ')[0]
  const today = new Date().toISOString().split('T')[0]
  
  if (selectedDate === today) {
    const currentHour = new Date().getHours()
    return Array.from({ length: 24 }, (_, i) => i).filter(h => h < currentHour)
  }
  return []
}

const disabledMinutes = (selectedHour) => {
  const selectedDate = imageForm.value.scheduledTime?.split(' ')[0]
  const today = new Date().toISOString().split('T')[0]
  const currentHour = new Date().getHours()
  
  if (selectedDate === today && selectedHour === currentHour) {
    const currentMinute = new Date().getMinutes()
    return Array.from({ length: 60 }, (_, i) => i).filter(m => m < currentMinute)
  }
  return []
}

const disabledSeconds = (selectedHour, selectedMinute) => {
  const selectedDate = imageForm.value.scheduledTime?.split(' ')[0]
  const today = new Date().toISOString().split('T')[0]
  const currentHour = new Date().getHours()
  const currentMinute = new Date().getMinutes()
  
  if (selectedDate === today && selectedHour === currentHour && selectedMinute === currentMinute) {
    const currentSecond = new Date().getSeconds()
    return Array.from({ length: 60 }, (_, i) => i).filter(s => s < currentSecond)
  }
  return []
}

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
  if (type === 'image') {
    imageForm.value = {
      name: '',
      model: '',
      ratio: '1:1',
      resolution: '2K',
      prompt: '',
      uploadedFiles: [],
      scheduledTime: ''
    }
    imageDialogVisible.value = true
  } else {
    videoForm.value = {
      name: '',
      prompt: '',
      model: '',
      ratio: '16:9'
    }
    videoDialogVisible.value = true
  }
}

const handleUploadSuccess = (response, file) => {
  ElMessage.success('上传成功')
  // 添加已上传的文件标记，使用真实文件名
  imageForm.value.uploadedFiles.push({
    uid: file.uid,
    name: response.name,  // 使用真实文件名（UUID格式）
    url: response.file_url
  })
}

const handleRemoveFile = (file) => {
  const index = imageForm.value.uploadedFiles.findIndex(f => f.uid === file.uid)
  if (index > -1) {
    imageForm.value.uploadedFiles.splice(index, 1)
  }
}

const handleRemoveTag = (index) => {
  imageForm.value.uploadedFiles.splice(index, 1)
}

const handlePromptInput = (value) => {
  // 检测最后输入的字符是否是@
  if (value && value.endsWith('@')) {
    // 显示图片选择器
    showImagePicker.value = true
    lastAtPosition.value = value.length - 1
    
    // 计算下拉框位置
    setTimeout(() => {
      calculatePickerPosition()
    }, 0)
  } else if (showImagePicker.value) {
    // 如果输入了其他字符，隐藏选择器
    // 但如果是在@后输入空格，也隐藏
    const lastChar = value ? value[value.length - 1] : ''
    if (lastChar === ' ' || !value.endsWith('@')) {
      showImagePicker.value = false
    }
  }
}

const calculatePickerPosition = () => {
  // 简单定位，显示在输入框下方
  pickerStyle.value = {
    position: 'absolute',
    top: '100%',
    left: '0',
    marginTop: '4px',
    zIndex: 2000
  }
}

const insertImageTag = (index) => {
  const file = imageForm.value.uploadedFiles[index]
  if (!file) return
  
  // 在@位置插入图片名称
  const prompt = imageForm.value.prompt
  const atPos = prompt.lastIndexOf('@')
  
  if (atPos !== -1) {
    // 替换@为@图片名
    const before = prompt.substring(0, atPos)
    const after = prompt.substring(atPos + 1)
    imageForm.value.prompt = `${before}@${file.name}${after}`
  }
  
  // 隐藏选择器
  showImagePicker.value = false
  
  // 聚焦回输入框
  setTimeout(() => {
    if (promptInputRef.value) {
      promptInputRef.value.focus()
    }
  }, 100)
}

const closeImagePicker = () => {
  showImagePicker.value = false
  // 移除末尾的@
  if (imageForm.value.prompt && imageForm.value.prompt.endsWith('@')) {
    imageForm.value.prompt = imageForm.value.prompt.slice(0, -1)
  }
  // 聚焦回输入框
  setTimeout(() => {
    if (promptInputRef.value) {
      promptInputRef.value.focus()
    }
  }, 100)
}

const handleCreateImageTask = async () => {
  // 表单验证
  if (!imageFormRef.value) return
  
  try {
    await imageFormRef.value.validate()
  } catch (error) {
    return
  }
  
  creating.value = true
  try {
    // 提取提示词中@引用的图片URL
    const imageUrls = imageForm.value.uploadedFiles.map(f => f.url)
    
    await createTask({
      name: imageForm.value.name,
      type: 'image',
      prompt: imageForm.value.prompt,
      model: imageForm.value.model,
      ratio: imageForm.value.ratio,
      resolution: imageForm.value.resolution,
      image_urls: imageUrls,
      scheduled_time: imageForm.value.scheduledTime || null
    })
    
    ElMessage.success('任务创建成功')
    imageDialogVisible.value = false
    fetchTasks()
  } catch (error) {
    console.error('创建任务失败:', error)
  } finally {
    creating.value = false
  }
}

const handleCreateVideoTask = async () => {
  if (!videoForm.value.name || !videoForm.value.prompt || !videoForm.value.model) {
    ElMessage.warning('请填写完整信息')
    return
  }

  creating.value = true
  try {
    await createTask({
      ...videoForm.value,
      type: 'video'
    })
    ElMessage.success('任务创建成功')
    videoDialogVisible.value = false
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
  
  // 添加全局点击事件，点击外部关闭下拉框
  document.addEventListener('click', () => {
    if (showImagePicker.value) {
      showImagePicker.value = false
      // 移除末尾的@
      if (imageForm.value.prompt && imageForm.value.prompt.endsWith('@')) {
        imageForm.value.prompt = imageForm.value.prompt.slice(0, -1)
      }
    }
  })
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

.ratio-group {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.upload-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 8px;
}

.time-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.image-tags {
  margin-top: 8px;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 4px;
}

.tag-label {
  font-size: 12px;
  color: #606266;
  margin-right: 4px;
}

.image-tag-text {
  display: inline-flex;
  align-items: center;
  padding: 4px 8px;
  background: #f0f9ff;
  border: 1px solid #b3d8ff;
  border-radius: 4px;
  font-size: 12px;
  color: #409eff;
  cursor: default;
  transition: all 0.2s;
}

.image-tag-text:hover {
  background: #e6f7ff;
  border-color: #66b1ff;
}

.remove-icon {
  margin-left: 4px;
  cursor: pointer;
  font-size: 14px;
  color: #909399;
  transition: color 0.2s;
}

.remove-icon:hover {
  color: #f56c6c;
}

/* 提示词容器 */
.prompt-container {
  position: relative;
  width: 100%;
}

.prompt-container :deep(.el-textarea) {
  width: 100%;
  min-width: 500px;
}

.prompt-container :deep(.el-textarea__inner) {
  width: 100% !important;
}

/* 图片选择下拉框 */
.image-picker-dropdown {
  position: absolute;
  background: #fff;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  min-width: 300px;
  max-width: 500px;
  max-height: 300px;
  overflow: hidden;
  z-index: 2000;
}

.picker-header {
  padding: 10px 12px;
  background: #f5f7fa;
  border-bottom: 1px solid #e4e7ed;
  font-size: 13px;
  font-weight: 500;
  color: #303133;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.close-btn {
  cursor: pointer;
  font-size: 16px;
  color: #909399;
  transition: color 0.2s;
}

.close-btn:hover {
  color: #f56c6c;
}

.picker-list {
  max-height: 240px;
  overflow-y: auto;
  padding: 8px;
}

.picker-item {
  display: flex;
  align-items: center;
  padding: 8px;
  cursor: pointer;
  border-radius: 4px;
  transition: background 0.2s;
  margin-bottom: 4px;
}

.picker-item:hover {
  background: #f5f7fa;
}

.picker-item:last-child {
  margin-bottom: 0;
}

.picker-image {
  width: 50px;
  height: 50px;
  border-radius: 4px;
  margin-right: 12px;
  flex-shrink: 0;
}

.picker-name {
  flex: 1;
  font-size: 13px;
  color: #606266;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 滚动条样式 */
.picker-list::-webkit-scrollbar {
  width: 6px;
}

.picker-list::-webkit-scrollbar-thumb {
  background: #c0c4cc;
  border-radius: 3px;
}

.picker-list::-webkit-scrollbar-thumb:hover {
  background: #909399;
}

/* 空状态提示 */
.empty-tip {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: #909399;
}

.empty-tip .el-icon {
  margin-bottom: 12px;
}

.empty-tip p {
  margin: 0;
  font-size: 14px;
  color: #909399;
}
</style>
