<template>
  <div class="dashboard">
    <section class="headline">
      <div>
        <h2>控制台总览</h2>
        <p>今天也适合多跑几组风格实验，数据会自动同步到这里。</p>
      </div>
      <div class="quick-actions">
        <el-button type="primary" @click="goTo('/tasks')">新建任务</el-button>
        <el-button @click="goTo('/materials')">管理素材</el-button>
        <el-button @click="goTo('/system')">系统设置</el-button>
      </div>
    </section>

    <el-row :gutter="16" class="stats-row">
      <el-col :xs="24" :sm="12" :lg="6" v-for="card in statCards" :key="card.key">
        <el-card class="stat-panel" shadow="hover">
          <div class="stat-card" :class="card.key">
            <div class="stat-title">{{ card.title }}</div>
            <div class="stat-value">{{ card.value }}</div>
            <div class="stat-note">{{ card.note }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" class="content-row">
      <el-col :xs="24" :lg="14">
        <el-card class="block-card" shadow="never">
          <template #header>
            <div class="block-header">
              <span>任务健康度</span>
              <el-tag type="info">实时</el-tag>
            </div>
          </template>
          <div class="health-item">
            <div class="health-top">
              <span>完成率</span>
              <strong>{{ completionRate }}%</strong>
            </div>
            <el-progress :percentage="completionRate" :stroke-width="10" color="#2f8cff" />
          </div>
          <div class="health-item">
            <div class="health-top">
              <span>运行占比</span>
              <strong>{{ runningRate }}%</strong>
            </div>
            <el-progress :percentage="runningRate" :stroke-width="10" color="#ff9f43" />
          </div>
          <div class="status-strip">
            <div class="status-chip queued">排队中 {{ statusSummary.queued }}</div>
            <div class="status-chip running">执行中 {{ statusSummary.running }}</div>
            <div class="status-chip failed">失败 {{ statusSummary.failed }}</div>
          </div>
        </el-card>

        <el-card class="block-card" shadow="never">
          <template #header>
            <div class="block-header">
              <span>最近任务</span>
              <el-button text type="primary" @click="goTo('/tasks')">查看全部</el-button>
            </div>
          </template>
          <el-table :data="recentTasks" size="small" empty-text="暂无任务" style="width: 100%">
            <el-table-column prop="name" label="任务名" min-width="180" show-overflow-tooltip />
            <el-table-column prop="type" label="类型" width="90" />
            <el-table-column label="状态" width="110">
              <template #default="{ row }">
                <el-tag :type="statusTagType(row.status)">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="创建时间" width="170">
              <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="10">
        <el-card class="block-card" shadow="never">
          <template #header>
            <div class="block-header">
              <span>最近素材</span>
              <el-button text type="primary" @click="goTo('/materials')">进入素材库</el-button>
            </div>
          </template>
          <div class="material-grid" v-if="recentMaterials.length">
            <div class="material-item" v-for="item in recentMaterials" :key="item.id">
              <div class="material-preview">
                <img v-if="item.type === 'image'" :src="getImageUrl(item.file_url)" :alt="item.name" />
                <video v-else :src="getImageUrl(item.file_url)" muted></video>
              </div>
              <div class="material-info">
                <div class="name" :title="item.name">{{ item.name }}</div>
                <div class="meta">{{ item.type }} · {{ formatDate(item.created_at) }}</div>
              </div>
            </div>
          </div>
          <el-empty v-else description="暂无素材" :image-size="80" />
        </el-card>

        <el-card class="block-card ideas" shadow="never">
          <template #header>
            <div class="block-header">
              <span>灵感备忘</span>
              <el-tag type="success">建议</el-tag>
            </div>
          </template>
          <ul class="idea-list">
            <li>用同一提示词批量试 3 种模型，保留最优风格做模板。</li>
            <li>素材命名加场景前缀，后续检索效率会明显提升。</li>
            <li>先跑 1:1 小图确认风格，再放大分辨率节省时长。</li>
          </ul>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { getTasks } from '@/api/task'
import { getMaterials } from '@/api/material'

const router = useRouter()

const stats = ref({
  totalTasks: 0,
  runningTasks: 0,
  completedTasks: 0,
  totalMaterials: 0
})

const statusSummary = ref({
  queued: 0,
  running: 0,
  failed: 0
})

const recentTasks = ref([])
const recentMaterials = ref([])

const completionRate = computed(() => {
  if (!stats.value.totalTasks) return 0
  return Math.round((stats.value.completedTasks / stats.value.totalTasks) * 100)
})

const runningRate = computed(() => {
  if (!stats.value.totalTasks) return 0
  return Math.round((stats.value.runningTasks / stats.value.totalTasks) * 100)
})

const statCards = computed(() => [
  { key: 'total', title: '总任务数', value: stats.value.totalTasks, note: '包含全部未删除任务' },
  { key: 'running', title: '进行中', value: stats.value.runningTasks, note: '正在执行与排队中的任务' },
  { key: 'completed', title: '已完成', value: stats.value.completedTasks, note: `完成率 ${completionRate.value}%` },
  { key: 'materials', title: '素材总数', value: stats.value.totalMaterials, note: '图片与视频素材总和' }
])

const loadDashboard = async () => {
  const tinyPage = { page: 1, page_size: 1 }

  const [
    totalTasksRes,
    runningTasksRes,
    completedTasksRes,
    queuedTasksRes,
    failedTasksRes,
    totalMaterialsRes,
    recentTasksRes,
    recentMaterialsRes
  ] = await Promise.allSettled([
    getTasks(tinyPage),
    getTasks({ ...tinyPage, status: 'running' }),
    getTasks({ ...tinyPage, status: 'completed' }),
    getTasks({ ...tinyPage, status: 'queued' }),
    getTasks({ ...tinyPage, status: 'failed' }),
    getMaterials(tinyPage),
    getTasks({ page: 1, page_size: 5 }),
    getMaterials({ page: 1, page_size: 6 })
  ])

  stats.value.totalTasks = totalTasksRes.status === 'fulfilled' ? (totalTasksRes.value.total || 0) : 0
  stats.value.runningTasks = runningTasksRes.status === 'fulfilled' ? (runningTasksRes.value.total || 0) : 0
  stats.value.completedTasks = completedTasksRes.status === 'fulfilled' ? (completedTasksRes.value.total || 0) : 0
  stats.value.totalMaterials = totalMaterialsRes.status === 'fulfilled' ? (totalMaterialsRes.value.total || 0) : 0

  statusSummary.value.queued = queuedTasksRes.status === 'fulfilled' ? (queuedTasksRes.value.total || 0) : 0
  statusSummary.value.running = runningTasksRes.status === 'fulfilled' ? (runningTasksRes.value.total || 0) : 0
  statusSummary.value.failed = failedTasksRes.status === 'fulfilled' ? (failedTasksRes.value.total || 0) : 0

  recentTasks.value = recentTasksRes.status === 'fulfilled' ? (recentTasksRes.value.items || []) : []
  recentMaterials.value = recentMaterialsRes.status === 'fulfilled' ? (recentMaterialsRes.value.items || []) : []
}

const formatDate = (value) => {
  if (!value) return '-'
  return String(value).replace('T', ' ').slice(0, 16)
}

const statusTagType = (status) => {
  const map = {
    completed: 'success',
    running: 'warning',
    queued: 'info',
    failed: 'danger'
  }
  return map[status] || 'info'
}

const goTo = (path) => {
  router.push(path)
}

const getImageUrl = (url) => {
  // 后端已经返回完整URL，直接返回
  return url || ''
}

onMounted(loadDashboard)
</script>

<style scoped>
.dashboard {
  padding: 20px;
  min-height: calc(100vh - 60px);
  background:
    radial-gradient(circle at 10% 0%, rgba(57, 122, 255, 0.08), transparent 38%),
    radial-gradient(circle at 85% 20%, rgba(7, 197, 255, 0.08), transparent 36%),
    #f3f5f8;
}

.headline {
  margin-bottom: 16px;
  padding: 16px 18px;
  border-radius: 12px;
  background: linear-gradient(120deg, #ffffff 0%, #f8fbff 60%, #edf3ff 100%);
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.headline h2 {
  margin: 0;
  color: #1f2d3d;
}

.headline p {
  margin: 8px 0 0;
  color: #6b7a90;
  font-size: 13px;
}

.quick-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.stats-row {
  margin-bottom: 16px;
}

.stat-panel {
  border: 1px solid #e9eef7;
  border-radius: 12px;
}

.stat-card {
  text-align: center;
  padding: 8px 0;
  position: relative;
}

.stat-card::before {
  content: '';
  position: absolute;
  left: 20%;
  right: 20%;
  top: 0;
  height: 3px;
  border-radius: 99px;
}

.stat-card.total::before {
  background: linear-gradient(90deg, #2f8cff, #6db3ff);
}

.stat-card.running::before {
  background: linear-gradient(90deg, #ff9f43, #ffc76a);
}

.stat-card.completed::before {
  background: linear-gradient(90deg, #15b87a, #42d19a);
}

.stat-card.materials::before {
  background: linear-gradient(90deg, #7a5cff, #9f89ff);
}

.stat-title {
  color: #7a889f;
  font-size: 13px;
  margin-top: 8px;
}

.stat-value {
  color: #1d2a39;
  font-size: 36px;
  line-height: 1.25;
  font-weight: 700;
}

.stat-note {
  color: #96a2b6;
  font-size: 12px;
}

.content-row {
  margin-bottom: 4px;
}

.block-card {
  border-radius: 12px;
  border: 1px solid #e8edf5;
  margin-bottom: 16px;
}

.block-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.health-item {
  margin-bottom: 14px;
}

.health-top {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
  color: #5f6d82;
}

.health-top strong {
  color: #1d2a39;
}

.status-strip {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
  margin-top: 14px;
}

.status-chip {
  text-align: center;
  font-size: 12px;
  padding: 8px 6px;
  border-radius: 10px;
  border: 1px solid transparent;
}

.status-chip.queued {
  background: #eef5ff;
  color: #2f8cff;
  border-color: #dbe9ff;
}

.status-chip.running {
  background: #fff5e9;
  color: #cf7d17;
  border-color: #ffe4bf;
}

.status-chip.failed {
  background: #fff0f0;
  color: #d84d4d;
  border-color: #ffd9d9;
}

.material-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.material-item {
  display: flex;
  gap: 10px;
  border: 1px solid #eef1f6;
  border-radius: 10px;
  padding: 8px;
}

.material-preview {
  width: 58px;
  height: 58px;
  border-radius: 8px;
  overflow: hidden;
  background: #f1f4f9;
  flex-shrink: 0;
}

.material-preview img,
.material-preview video {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.material-info {
  min-width: 0;
}

.material-info .name {
  font-size: 13px;
  color: #2a3648;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.material-info .meta {
  margin-top: 4px;
  font-size: 12px;
  color: #95a1b2;
}

.ideas {
  background: linear-gradient(150deg, #ffffff, #f7fbff);
}

.idea-list {
  margin: 0;
  padding-left: 18px;
  color: #4f5f75;
  line-height: 1.85;
}

@media (max-width: 992px) {
  .headline {
    flex-direction: column;
    align-items: flex-start;
  }

  .material-grid {
    grid-template-columns: 1fr;
  }
}
</style>
