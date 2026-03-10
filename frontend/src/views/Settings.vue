<template>
  <div class="settings-page">
    <el-card>
      <template #header><span>系统设置</span></template>
      <el-form label-width="120px">
        <el-form-item label="服务地址">
          <el-input v-model="settings.host" />
        </el-form-item>
        <el-form-item label="服务端口">
          <el-input-number v-model="settings.port" :min="1000" :max="65535" />
        </el-form-item>
        <el-form-item label="日志级别">
          <el-select v-model="settings.logLevel">
            <el-option label="DEBUG" value="DEBUG" />
            <el-option label="INFO" value="INFO" />
            <el-option label="WARNING" value="WARNING" />
            <el-option label="ERROR" value="ERROR" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="saveSettings">保存设置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const settings = ref({ host: '0.0.0.0', port: 8080, logLevel: 'INFO' })

const saveSettings = () => {
  ElMessage.success('设置保存成功')
}
</script>

<style scoped>
.settings-page { padding: 20px; }
</style>
