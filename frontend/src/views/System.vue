<template>
  <div class="system">
    <el-tabs v-model="activeTab">
      <!-- API配置 -->
      <el-tab-pane label="API配置" name="api">
        <el-card>
          <template #header>
            <span>即梦API配置</span>
          </template>
          <el-form :model="apiForm" label-width="120px">
            <el-form-item label="SessionID">
              <el-input v-model="apiForm.sessionid" type="password" show-password />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveApiConfig" :loading="saving">保存配置</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>
      
      <!-- 用户管理 -->
      <el-tab-pane v-if="isSuperAdmin" label="用户管理" name="users">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>用户列表</span>
              <el-button type="primary" size="small" @click="showUserDialog = true">
                <el-icon><Plus /></el-icon>
                添加用户
              </el-button>
            </div>
          </template>
          
          <el-table :data="visibleUserList" v-loading="userLoading">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="username" label="用户名" />
            <el-table-column prop="role" label="角色">
              <template #default="{ row }">
                <el-tag :type="row.role === 'super_admin' ? 'danger' : 'primary'">
                  {{ row.role === 'super_admin' ? '超级管理员' : '管理员' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="is_active" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.is_active ? 'success' : 'info'">
                  {{ row.is_active ? '启用' : '禁用' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="180" />
            <el-table-column label="操作" width="150">
              <template #default="{ row }">
                <el-button size="small" @click="editUser(row)">编辑</el-button>
                <el-button v-if="row.role !== 'super_admin'" size="small" type="danger" @click="deleteUser(row.id)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>
      
      <!-- 系统日志 -->
      <el-tab-pane label="系统日志" name="logs">
        <el-card>
          <template #header>
            <span>系统日志</span>
          </template>
          
          <el-table :data="logList" v-loading="logLoading" max-height="600">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="level" label="级别" width="100">
              <template #default="{ row }">
                <el-tag :type="getLogLevelType(row.level)">
                  {{ row.level.toUpperCase() }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="module" label="模块" width="120" />
            <el-table-column prop="message" label="消息" show-overflow-tooltip />
            <el-table-column prop="created_at" label="时间" width="180" />
          </el-table>
        </el-card>
      </el-tab-pane>
    </el-tabs>
    
    <!-- 添加用户对话框 -->
    <el-dialog v-model="showUserDialog" title="添加用户" width="500px">
      <el-form :model="userForm" label-width="100px">
        <el-form-item label="用户名" required>
          <el-input v-model="userForm.username" />
        </el-form-item>
        <el-form-item label="密码" required>
          <el-input v-model="userForm.password" type="password" show-password />
        </el-form-item>
        <el-form-item label="角色" required>
          <el-input value="管理员" disabled />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showUserDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreateUser" :loading="userCreating">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { getSessionId, updateSessionId, getUsers, createUser, deleteUser as deleteUserApi, getSystemLogs } from '@/api/system'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'

const activeTab = ref('api')
const saving = ref(false)
const userLoading = ref(false)
const userCreating = ref(false)
const logLoading = ref(false)
const showUserDialog = ref(false)

const apiForm = reactive({
  sessionid: ''
})

const userList = ref([])
const isSuperAdmin = computed(() => {
  const user = JSON.parse(localStorage.getItem('user') || 'null')
  return user?.role === 'super_admin'
})
const visibleUserList = computed(() => userList.value.filter((item) => item.role !== 'super_admin'))
const userForm = reactive({
  username: '',
  password: '',
  role: 'admin'
})

const logList = ref([])

const fetchApiConfig = async () => {
  try {
    const res = await getSessionId()
    apiForm.sessionid = res.sessionid || ''
  } catch (error) {
    console.error('获取API配置失败:', error)
  }
}

const saveApiConfig = async () => {
  saving.value = true
  try {
    await updateSessionId(apiForm.sessionid)
    ElMessage.success('保存成功')
  } catch (error) {
    console.error('保存失败:', error)
  } finally {
    saving.value = false
  }
}

const fetchUsers = async () => {
  if (!isSuperAdmin.value) return
  userLoading.value = true
  try {
    const res = await getUsers({ page: 1, page_size: 100 })
    userList.value = res.items || res
  } catch (error) {
    console.error('获取用户列表失败:', error)
  } finally {
    userLoading.value = false
  }
}

const handleCreateUser = async () => {
  if (!userForm.username || !userForm.password) {
    ElMessage.warning('请填写完整信息')
    return
  }
  
  userCreating.value = true
  try {
    await createUser({
      username: userForm.username,
      password: userForm.password,
      role: 'admin'
    })
    ElMessage.success('创建成功')
    showUserDialog.value = false
    userForm.username = ''
    userForm.password = ''
    fetchUsers()
  } catch (error) {
    console.error('创建用户失败:', error)
  } finally {
    userCreating.value = false
  }
}

const editUser = (row) => {
  ElMessage.info('编辑功能开发中')
}

const deleteUser = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除此用户吗？', '提示', { type: 'warning' })
    await deleteUserApi(id)
    ElMessage.success('删除成功')
    fetchUsers()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除用户失败:', error)
    }
  }
}

const fetchLogs = async () => {
  logLoading.value = true
  try {
    const res = await getSystemLogs({ page: 1, page_size: 50 })
    logList.value = res.items || res
  } catch (error) {
    console.error('获取日志失败:', error)
  } finally {
    logLoading.value = false
  }
}

const getLogLevelType = (level) => {
  const typeMap = {
    debug: 'info',
    info: 'success',
    warning: 'warning',
    error: 'danger'
  }
  return typeMap[level] || 'info'
}

onMounted(() => {
  fetchApiConfig()
  if (isSuperAdmin.value) {
    fetchUsers()
  } else if (activeTab.value === 'users') {
    activeTab.value = 'api'
  }
  fetchLogs()
})
</script>

<style scoped>
.system {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
