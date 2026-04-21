#!/usr/bin/env python3
"""批量创建前端文件"""
from pathlib import Path

base_dir = Path(__file__).parent / "frontend" / "src"

frontend_files = {
    "api/request.js": '''import axios from 'axios'
import { ElMessage } from 'element-plus'

const request = axios.create({
  baseURL: '/api',
  timeout: 30000
})

request.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

request.interceptors.response.use(
  response => response.data,
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    ElMessage.error(error.response?.data?.detail || '请求失败')
    return Promise.reject(error)
  }
)

export default request
''',

    "api/auth.js": '''import request from './request'

export const login = (data) => request.post('/auth/login', data, {
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
})

export const getUserInfo = () => request.get('/auth/me')
''',

    "api/task.js": '''import request from './request'

export const getTasks = (params) => request.get('/tasks/', { params })
export const createTask = (data) => request.post('/tasks/', data)
export const updateTask = (id, data) => request.put(`/tasks/${id}`, data)
export const deleteTask = (id) => request.delete(`/tasks/${id}`)
export const runTask = (id) => request.post(`/tasks/${id}/run`)
''',

    "api/material.js": '''import request from './request'

export const getMaterials = (params) => request.get('/materials/', { params })
export const uploadMaterial = (formData) => request.post('/materials/upload', formData, {
  headers: { 'Content-Type': 'multipart/form-data' }
})
export const deleteMaterial = (id) => request.delete(`/materials/${id}`)
''',

    "api/system.js": '''import request from './request'

export const getSessionId = () => request.get('/system/session')
export const updateSessionId = (sessionid) => request.put('/system/session', { sessionid })
export const getUsers = (params) => request.get('/system/users', { params })
export const createUser = (data) => request.post('/system/users', data)
export const deleteUser = (id) => request.delete(`/system/users/${id}`)
export const getSystemLogs = (params) => request.get('/system/logs', { params })
''',

    "stores/user.js": '''import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref(JSON.parse(localStorage.getItem('user') || 'null'))

  function setToken(newToken) {
    token.value = newToken
    localStorage.setItem('token', newToken)
  }

  function setUserInfo(info) {
    userInfo.value = info
    localStorage.setItem('user', JSON.stringify(info))
  }

  function logout() {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  return { token, userInfo, setToken, setUserInfo, logout }
})
''',

    "layouts/MainLayout.vue": '''<template>
  <el-container class="layout-container">
    <el-aside width="200px">
      <div class="logo">SeeDance</div>
      <el-menu
        :default-active="route.path"
        router
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
      >
        <el-menu-item index="/dashboard">
          <el-icon><DataLine /></el-icon>
          <span>数据统计</span>
        </el-menu-item>
        <el-menu-item index="/tasks">
          <el-icon><List /></el-icon>
          <span>任务管理</span>
        </el-menu-item>
        <el-menu-item index="/materials">
          <el-icon><Picture /></el-icon>
          <span>素材库</span>
        </el-menu-item>
        <el-menu-item index="/system">
          <el-icon><Setting /></el-icon>
          <span>系统管理</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    
    <el-container>
      <el-header>
        <div class="header-right">
          <el-dropdown>
            <span class="user-info">
              <el-icon><User /></el-icon>
              {{ userStore.userInfo?.username || 'Admin' }}
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="handleLogout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'
import { DataLine, List, Picture, Setting, User } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.layout-container {
  height: 100vh;
}
.el-aside {
  background-color: #304156;
}
.logo {
  height: 60px;
  line-height: 60px;
  text-align: center;
  color: #fff;
  font-size: 20px;
  font-weight: bold;
}
.el-header {
  background-color: #fff;
  box-shadow: 0 1px 4px rgba(0,21,41,.08);
  display: flex;
  justify-content: flex-end;
  align-items: center;
}
.user-info {
  cursor: pointer;
}
.el-main {
  background-color: #f0f2f5;
}
</style>
''',

    "views/Login.vue": '''<template>
  <div class="login-container">
    <el-card class="login-card">
      <h2>SeeDance 后台管理</h2>
      <el-form :model="loginForm" @submit.prevent="handleLogin">
        <el-form-item>
          <el-input v-model="loginForm.username" placeholder="用户名" prefix-icon="User" />
        </el-form-item>
        <el-form-item>
          <el-input v-model="loginForm.password" type="password" placeholder="密码" prefix-icon="Lock" show-password />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" native-type="submit" :loading="loading" style="width: 100%">登录</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { login } from '@/api/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)

const loginForm = reactive({
  username: '',
  password: ''
})

const handleLogin = async () => {
  loading.value = true
  try {
    const res = await login(loginForm)
    userStore.setToken(res.access_token)
    userStore.setUserInfo(res.user)
    ElMessage.success('登录成功')
    router.push('/dashboard')
  } catch (error) {
    console.error('登录失败:', error)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
.login-card {
  width: 400px;
  padding: 20px;
}
h2 {
  text-align: center;
  margin-bottom: 30px;
  color: #303133;
}
</style>
''',

    "views/Dashboard.vue": '''<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card>
          <div class="stat-card">
            <div class="stat-title">总任务数</div>
            <div class="stat-value">{{ stats.totalTasks }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <div class="stat-card">
            <div class="stat-title">进行中</div>
            <div class="stat-value">{{ stats.runningTasks }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <div class="stat-card">
            <div class="stat-title">已完成</div>
            <div class="stat-value">{{ stats.completedTasks }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <div class="stat-card">
            <div class="stat-title">素材总数</div>
            <div class="stat-value">{{ stats.totalMaterials }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const stats = ref({
  totalTasks: 0,
  runningTasks: 0,
  completedTasks: 0,
  totalMaterials: 0
})

onMounted(() => {
  // TODO: 加载统计数据
})
</script>

<style scoped>
.dashboard {
  padding: 20px;
}
.stat-card {
  text-align: center;
}
.stat-title {
  color: #909399;
  font-size: 14px;
  margin-bottom: 10px;
}
.stat-value {
  color: #303133;
  font-size: 32px;
  font-weight: bold;
}
</style>
''',

    "views/Materials.vue": '''<template>
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
''',

    "views/Tasks.vue": '''<template>
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
''',

    "style.css": '''* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
'''
}

# 创建所有文件
created = 0
for filepath, content in frontend_files.items():
    full_path = base_dir / filepath
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(content, encoding='utf-8')
    created += 1
    print(f"✓ {filepath}")

print(f"\n✅ 共创建 {created} 个前端文件")
