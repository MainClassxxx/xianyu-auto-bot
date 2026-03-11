<template>
  <div class="notifications-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>🔔 通知管理</span>
          <el-button type="primary" @click="showAddChannel">
            <el-icon><Plus /></el-icon>
            添加渠道
          </el-button>
        </div>
      </template>

      <el-table :data="channels" v-loading="loading" style="width: 100%">
        <el-table-column prop="name" label="渠道名称" width="150" />
        <el-table-column prop="channel_type" label="类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getTypeTag(row.channel_type)">
              {{ getTypeText(row.channel_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="webhook_url" label="Webhook URL" min-width="300" show-overflow-tooltip />
        <el-table-column prop="enabled" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.enabled ? 'success' : 'info'">
              {{ row.enabled ? '已启用' : '已禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="toggleChannel(row)">
              {{ row.enabled ? '禁用' : '启用' }}
            </el-button>
            <el-button type="warning" size="small" @click="testChannel(row)">测试</el-button>
            <el-button type="danger" size="small" @click="deleteChannel(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 添加渠道对话框 -->
    <el-dialog v-model="dialogVisible" title="添加通知渠道" width="500px">
      <el-form :model="channelForm" label-width="100px">
        <el-form-item label="渠道名称" required>
          <el-input v-model="channelForm.name" placeholder="例如：飞书通知" />
        </el-form-item>
        <el-form-item label="渠道类型" required>
          <el-select v-model="channelForm.channel_type" placeholder="请选择" style="width: 100%;">
            <el-option label="飞书" value="feishu" />
            <el-option label="钉钉" value="dingtalk" />
            <el-option label="企业微信" value="wechat" />
            <el-option label="Telegram" value="telegram" />
          </el-select>
        </el-form-item>
        <el-form-item label="Webhook URL" required v-if="channelForm.channel_type">
          <el-input
            v-model="channelForm.webhook_url"
            type="textarea"
            :rows="3"
            placeholder="输入 Webhook URL"
          />
          <el-link type="primary" style="margin-top: 5px;" @click="quickSetupFeishu">
            快速配置飞书 Webhook
          </el-link>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitChannel">确定</el-button>
      </template>
    </el-dialog>

    <!-- 飞书配置指引 -->
    <el-dialog v-model="feishuGuideVisible" title="飞书 Webhook 配置指引" width="600px">
      <div class="feishu-guide">
        <h4>📝 配置步骤：</h4>
        <ol>
          <li>打开飞书群聊 → 右上角设置 → 机器人</li>
          <li>点击「添加机器人」→ 选择「自定义机器人」</li>
          <li>设置机器人名称（如：闲鱼机器人）</li>
          <li>复制 Webhook 地址</li>
          <li>粘贴到上方输入框</li>
        </ol>

        <h4>⚠️ 注意事项：</h4>
        <ul>
          <li>Webhook 地址是敏感信息，请妥善保管</li>
          <li>一个 Webhook 只能用于一个群聊</li>
          <li>可以随时禁用或删除</li>
        </ul>

        <el-alert
          title="💡 提示"
          description="配置完成后，系统会自动发送订单通知、发货通知、每小时报告等"
          type="info"
          :closable="false"
          show-icon
        />
      </div>
      <template #footer>
        <el-button type="primary" @click="feishuGuideVisible = false">我知道了</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'

const loading = ref(false)
const dialogVisible = ref(false)
const feishuGuideVisible = ref(false)
const submitting = ref(false)

const channels = ref([])

const channelForm = reactive({
  name: '',
  channel_type: '',
  webhook_url: ''
})

onMounted(() => {
  loadChannels()
})

async function loadChannels() {
  loading.value = true
  try {
    const response = await axios.get('http://localhost:8080/api/notifications/channels')
    channels.value = response.data || []
  } catch (error) {
    ElMessage.error('加载通知渠道失败：' + error.message)
  } finally {
    loading.value = false
  }
}

function showAddChannel() {
  channelForm.name = ''
  channelForm.channel_type = ''
  channelForm.webhook_url = ''
  dialogVisible.value = true
}

function getTypeTag(type) {
  const tags = {
    'feishu': 'primary',
    'dingtalk': 'warning',
    'wechat': 'success',
    'telegram': 'info'
  }
  return tags[type] || 'info'
}

function getTypeText(type) {
  const texts = {
    'feishu': '飞书',
    'dingtalk': '钉钉',
    'wechat': '企业微信',
    'telegram': 'Telegram'
  }
  return texts[type] || type
}

async function submitChannel() {
  if (!channelForm.name || !channelForm.channel_type || !channelForm.webhook_url) {
    ElMessage.warning('请填写完整信息')
    return
  }

  submitting.value = true
  try {
    await axios.post('http://localhost:8080/api/notifications/channels', channelForm)
    ElMessage.success('添加成功')
    dialogVisible.value = false
    loadChannels()
  } catch (error) {
    ElMessage.error('添加失败：' + error.message)
  } finally {
    submitting.value = false
  }
}

async function toggleChannel(channel) {
  try {
    await axios.post(`http://localhost:8080/api/notifications/channels/${channel.id}/toggle`)
    ElMessage.success(`${channel.enabled ? '禁用' : '启用'}成功`)
    loadChannels()
  } catch (error) {
    ElMessage.error('操作失败：' + error.message)
  }
}

async function testChannel(channel) {
  try {
    await axios.post('http://localhost:8080/api/notifications/test', {
      channel_id: channel.id,
      message: '这是一条测试消息'
    })
    ElMessage.success('测试消息已发送')
  } catch (error) {
    ElMessage.error('测试失败：' + error.message)
  }
}

async function deleteChannel(channel) {
  try {
    await ElMessageBox.confirm(
      `确定要删除"${channel.name}"吗？`,
      '警告',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
    )

    await axios.delete(`http://localhost:8080/api/notifications/channels/${channel.id}`)
    ElMessage.success('删除成功')
    loadChannels()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败：' + error.message)
    }
  }
}

function quickSetupFeishu() {
  feishuGuideVisible.value = true
}
</script>

<style scoped>
.notifications-page {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.feishu-guide {
  padding: 20px;
}

.feishu-guide h4 {
  margin: 15px 0 10px;
  color: #303133;
}

.feishu-guide ol,
.feishu-guide ul {
  padding-left: 20px;
  color: #606266;
  line-height: 2;
}

.feishu-guide li {
  margin-bottom: 5px;
}
</style>
