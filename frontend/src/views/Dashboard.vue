<template>
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
