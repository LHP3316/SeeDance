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
            <el-option-group label="最新版本">
              <el-option label="图片5.0 - 最新最强模型" value="5.0" />
              <el-option label="图片4.6" value="4.6" />
              <el-option label="图片4.5" value="4.5" />
            </el-option-group>
            <el-option-group label="经典版本">
              <el-option label="图片4.1 - 专业创意美学" value="4.1" />
              <el-option label="图片4.0 - 支持多参考图" value="4.0" />
              <el-option label="图片3.1 - 美学多样性" value="3.1" />
              <el-option label="图片3.0 - 影视级质感" value="3.0" />
              <el-option label="图片2.1" value="2.1" />
              <el-option label="图片2.0" value="2.0" />
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
            :on-exceed="handleExceed"
            :file-list="imageForm.uploadedFiles"
            multiple
            :limit="5"
            list-type="picture-card"
            accept="image/*"
            :class="{ 'hide-upload': imageForm.uploadedFiles.length >= 5 }"
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

        <el-form-item label="执行时间" prop="scheduledTime">
          <el-date-picker
            v-model="imageForm.scheduledTime"
            type="datetime"
            placeholder="选择日期时间"
            :disabled-date="disabledDate"
            :disabled-hours="disabledHours"
            :disabled-minutes="disabledMinutes"
            :disabled-seconds="disabledSeconds"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DD HH:mm:ss"
            style="width: 100%"
          />
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
      width="700px"
    >
      <el-form :model="videoForm" :rules="videoRules" ref="videoFormRef" label-width="100px">
        <el-form-item label="任务名称" prop="name">
          <el-input v-model="videoForm.name" placeholder="请输入任务名称" />
        </el-form-item>
        
        <el-form-item label="选择模型" prop="model">
          <el-select v-model="videoForm.model" placeholder="请选择模型" style="width: 100%">
            <el-option-group label="Seedance 2.0系列">
              <el-option label="Seedance 2.0 Fast VIP - 极速推理，会员专属通道" value="s2.0" />
              <el-option label="Seedance 2.0 VIP - 全模态能力，会员专属通道" value="s2.0p" />
              <el-option label="Seedance 2.0 Fast - 高性价比" value="s2.0_fast" />
              <el-option label="Seedance 2.0 - 全能王者" value="s2.0_standard" />
            </el-option-group>
          </el-select>
        </el-form-item>

        <el-form-item label="视频比例" prop="ratio">
          <el-radio-group v-model="videoForm.ratio" class="ratio-group">
            <el-radio-button label="16:9">16:9</el-radio-button>
            <el-radio-button label="9:16">9:16</el-radio-button>
            <el-radio-button label="1:1">1:1</el-radio-button>
            <el-radio-button label="4:3">4:3</el-radio-button>
            <el-radio-button label="3:4">3:4</el-radio-button>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="视频时长" prop="duration">
          <el-select v-model="videoForm.duration" placeholder="请选择时长" style="width: 100%">
            <el-option label="请选择" :value="null" disabled />
            <el-option label="4秒" :value="4" />
            <el-option label="5秒" :value="5" />
            <el-option label="6秒" :value="6" />
            <el-option label="7秒" :value="7" />
            <el-option label="8秒" :value="8" />
            <el-option label="9秒" :value="9" />
            <el-option label="10秒" :value="10" />
            <el-option label="11秒" :value="11" />
            <el-option label="12秒" :value="12" />
            <el-option label="13秒" :value="13" />
            <el-option label="14秒" :value="14" />
            <el-option label="15秒" :value="15" />
          </el-select>
        </el-form-item>

        <el-form-item label="上传图片">
          <el-upload
            ref="videoUploadRef"
            :action="uploadUrl"
            :headers="uploadHeaders"
            :on-success="handleVideoUploadSuccess"
            :on-remove="handleVideoRemoveFile"
            :on-exceed="handleVideoExceed"
            :file-list="videoForm.uploadedFiles"
            multiple
            :limit="12"
            list-type="picture-card"
            accept="image/*"
            :class="{ 'hide-upload': videoForm.uploadedFiles.length >= 12 }"
          >
            <el-icon><Plus /></el-icon>
          </el-upload>
          <div class="upload-tip">支持jpg/png格式，最多12张</div>
        </el-form-item>

        <el-form-item label="提示词" prop="prompt">
          <div class="prompt-container" @click.stop>
            <el-input
              v-model="videoForm.prompt"
              type="textarea"
              :rows="5"
              placeholder="请输入视频描述，输入 @ 可引用已上传的图片"
              @input="handleVideoPromptInput"
              ref="videoPromptInputRef"
              style="width: 100%"
            />
            
            <!-- @图片选择下拉框 -->
            <div 
              v-if="showVideoImagePicker" 
              class="image-picker-dropdown"
              :style="videoPickerStyle"
              @click.stop
            >
              <div class="picker-header">
                <span>选择图片</span>
                <el-icon class="close-btn" @click="closeVideoImagePicker"><Close /></el-icon>
              </div>
              <div class="picker-list">
                <div 
                  v-for="(file, index) in videoForm.uploadedFiles" 
                  :key="file.uid"
                  class="picker-item"
                  @click="insertVideoImageTag(index)"
                >
                  <el-image
                    :src="file.url"
                    class="picker-image"
                    fit="cover"
                  />
                  <span class="picker-name">{{ file.name }}</span>
                </div>
                <div v-if="videoForm.uploadedFiles.length === 0" class="empty-tip">
                  <el-icon :size="40"><Picture /></el-icon>
                  <p>暂无图片，请先上传</p>
                </div>
              </div>
            </div>
          </div>
          
          <div v-if="videoForm.uploadedFiles.length > 0" class="image-tags">
            <span class="tag-label">已上传图片：</span>
            <span
              v-for="(file, index) in videoForm.uploadedFiles"
              :key="file.uid"
              class="image-tag-text"
            >
              @{{ file.name }}
              <el-icon class="remove-icon" @click="handleRemoveVideoTag(index)">
                <Close />
              </el-icon>
            </span>
          </div>
        </el-form-item>

        <el-form-item label="执行时间" prop="scheduledTime">
          <el-date-picker
            v-model="videoForm.scheduledTime"
            type="datetime"
            placeholder="选择日期时间"
            :disabled-date="disabledVideoDate"
            :disabled-hours="disabledVideoHours"
            :disabled-minutes="disabledVideoMinutes"
            :disabled-seconds="disabledVideoSeconds"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DD HH:mm:ss"
            style="width: 100%"
          />
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
  prompt: [{ required: true, message: '请输入提示词', trigger: 'blur' }],
  scheduledTime: [{ required: true, message: '请选择执行时间', trigger: 'change' }]
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
  ratio: '16:9',
  duration: null,
  scheduledTime: '',
  uploadedFiles: []
})

// 视频表单验证规则
const videoRules = {
  name: [{ required: true, message: '请输入任务名称', trigger: 'blur' }],
  model: [{ required: true, message: '请选择模型', trigger: 'change' }],
  ratio: [{ required: true, message: '请选择视频比例', trigger: 'change' }],
  duration: [{ required: true, message: '请选择视频时长', trigger: 'change' }],
  prompt: [{ required: true, message: '请输入提示词', trigger: 'blur' }],
  scheduledTime: [{ required: true, message: '请选择执行时间', trigger: 'change' }]
}

// 视频表单ref
const videoFormRef = ref(null)

// 视频@图片选择器相关
const showVideoImagePicker = ref(false)
const videoPickerStyle = ref({})
const videoPromptInputRef = ref(null)
const lastVideoAtPosition = ref(0)

// 视频时间限制函数
const disabledVideoDate = (time) => {
  return time.getTime() < Date.now() - 8.64e7
}

const disabledVideoHours = () => {
  const selectedDate = videoForm.value.scheduledTime?.split(' ')[0]
  const today = new Date().toISOString().split('T')[0]
  
  if (selectedDate === today) {
    const currentHour = new Date().getHours()
    return Array.from({ length: 24 }, (_, i) => i).filter(h => h < currentHour)
  }
  return []
}

const disabledVideoMinutes = (selectedHour) => {
  const selectedDate = videoForm.value.scheduledTime?.split(' ')[0]
  const today = new Date().toISOString().split('T')[0]
  const currentHour = new Date().getHours()
  
  if (selectedDate === today && selectedHour === currentHour) {
    const currentMinute = new Date().getMinutes()
    return Array.from({ length: 60 }, (_, i) => i).filter(m => m < currentMinute)
  }
  return []
}

const disabledVideoSeconds = (selectedHour, selectedMinute) => {
  const selectedDate = videoForm.value.scheduledTime?.split(' ')[0]
  const today = new Date().toISOString().split('T')[0]
  const currentHour = new Date().getHours()
  const currentMinute = new Date().getMinutes()
  
  if (selectedDate === today && selectedHour === currentHour && selectedMinute === currentMinute) {
    const currentSecond = new Date().getSeconds()
    return Array.from({ length: 60 }, (_, i) => i).filter(s => s < currentSecond)
  }
  return []
}

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
    if (videoFormRef.value) {
      videoFormRef.value.resetFields()
    }
    videoForm.value = {
      name: '',
      prompt: '',
      model: '',
      ratio: '16:9',
      duration: null,
      scheduledTime: '',
      uploadedFiles: []
    }
    showVideoImagePicker.value = false
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

const handleExceed = (files) => {
  ElMessage.warning(`最多只能上传5张图片，已选择${files.length}张`)
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
  if (!videoFormRef.value) return
  
  try {
    await videoFormRef.value.validate()
  } catch (error) {
    return
  }

  creating.value = true
  try {
    await createTask({
      name: videoForm.value.name,
      type: 'video',
      prompt: videoForm.value.prompt,
      model: videoForm.value.model,
      ratio: videoForm.value.ratio,
      duration: videoForm.value.duration,
      scheduled_time: videoForm.value.scheduledTime,
      image_urls: videoForm.value.uploadedFiles.map(f => f.url)
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

// 视频上传相关函数
const handleVideoUploadSuccess = (response, file) => {
  ElMessage.success('上传成功')
  videoForm.value.uploadedFiles.push({
    uid: file.uid,
    name: response.name,
    url: response.file_url
  })
}

const handleVideoExceed = (files) => {
  ElMessage.warning(`最多只能上传12张图片，已选择${files.length}张`)
}

const handleVideoRemoveFile = (file) => {
  const index = videoForm.value.uploadedFiles.findIndex(f => f.uid === file.uid)
  if (index > -1) {
    videoForm.value.uploadedFiles.splice(index, 1)
  }
}

const handleRemoveVideoTag = (index) => {
  videoForm.value.uploadedFiles.splice(index, 1)
}

// 视频@图片选择器函数
const handleVideoPromptInput = (value) => {
  if (value && value.endsWith('@')) {
    showVideoImagePicker.value = true
    lastVideoAtPosition.value = value.length - 1
    setTimeout(() => {
      calculateVideoPickerPosition()
    }, 0)
  } else if (showVideoImagePicker.value) {
    const lastChar = value ? value[value.length - 1] : ''
    if (lastChar === ' ' || !value.endsWith('@')) {
      showVideoImagePicker.value = false
    }
  }
}

const calculateVideoPickerPosition = () => {
  if (!videoPromptInputRef.value) return
  
  const textarea = videoPromptInputRef.value.$el.querySelector('textarea')
  if (!textarea) return
  
  const cursorPosition = lastVideoAtPosition.value
  const textBeforeCursor = videoForm.value.prompt.substring(0, cursorPosition)
  
  const tempDiv = document.createElement('div')
  tempDiv.style.cssText = `
    position: absolute;
    visibility: hidden;
    white-space: pre-wrap;
    word-wrap: break-word;
    font: ${window.getComputedStyle(textarea).font};
    width: ${textarea.offsetWidth}px;
    padding: ${window.getComputedStyle(textarea).padding};
  `
  tempDiv.textContent = textBeforeCursor
  document.body.appendChild(tempDiv)
  
  const lines = tempDiv.innerHTML.split('\n')
  const currentLineIndex = lines.length - 1
  const lineHeight = parseInt(window.getComputedStyle(textarea).lineHeight)
  const paddingTop = parseInt(window.getComputedStyle(textarea).paddingTop)
  
  const topOffset = textarea.offsetTop + paddingTop + (currentLineIndex * lineHeight) + lineHeight
  const leftOffset = textarea.offsetLeft + (textarea.scrollWidth / 2) - 150
  
  document.body.removeChild(tempDiv)
  
  videoPickerStyle.value = {
    position: 'absolute',
    top: `${topOffset}px`,
    left: `${Math.max(0, leftOffset)}px`,
    zIndex: 2000,
    width: '300px',
    maxHeight: '200px',
    overflowY: 'auto'
  }
}

const closeVideoImagePicker = () => {
  showVideoImagePicker.value = false
  if (videoForm.value.prompt && videoForm.value.prompt.endsWith('@')) {
    videoForm.value.prompt = videoForm.value.prompt.slice(0, -1)
  }
}

const insertVideoImageTag = (index) => {
  const file = videoForm.value.uploadedFiles[index]
  const prompt = videoForm.value.prompt
  const atPos = prompt.lastIndexOf('@')
  
  if (atPos !== -1) {
    const before = prompt.substring(0, atPos)
    const after = prompt.substring(atPos + 1)
    videoForm.value.prompt = `${before}@${file.name}${after}`
  }
  
  showVideoImagePicker.value = false
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

/* 隐藏上传按钮 */
.hide-upload :deep(.el-upload--picture-card) {
  display: none !important;
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
