<template>
  <div class="conversations-page">
    <el-row :gutter="20">
      <!-- 会话列表 -->
      <el-col :span="8">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>💬 会话列表</span>
              <el-select v-model="selectedAccount" placeholder="选择账号" style="width: 150px;" @change="loadConversations">
                <el-option v-for="acc in accounts" :key="acc.id" :label="acc.name" :value="acc.id" />
              </el-select>
            </div>
          </template>

          <el-input
            v-model="searchKeyword"
            placeholder="搜索会话"
            prefix-icon="Search"
            clearable
            style="margin-bottom: 15px;"
          />

          <div class="conversation-list" v-loading="loading">
            <div
              v-for="conv in filteredConversations"
              :key="conv.conversation_id"
              class="conversation-item"
              :class="{ active: currentConv?.conversation_id === conv.conversation_id }"
              @click="selectConversation(conv)"
            >
              <div class="conversation-avatar">
                <el-avatar :size="40">{{ conv.user_name?.charAt(0) || 'U' }}</el-avatar>
              </div>
              <div class="conversation-info">
                <div class="conversation-header">
                  <span class="conversation-name">{{ conv.user_name || '未知用户' }}</span>
                  <span class="conversation-time">{{ formatTime(conv.last_message_time) }}</span>
                </div>
                <div class="conversation-preview">
                  {{ conv.last_message || '暂无消息' }}
                </div>
              </div>
            </div>

            <el-empty v-if="conversations.length === 0" description="暂无会话" />
          </div>
        </el-card>
      </el-col>

      <!-- 聊天窗口 -->
      <el-col :span="16">
        <el-card v-if="currentConv" class="chat-card">
          <template #header>
            <div class="chat-header">
              <div class="chat-user-info">
                <el-avatar :size="36">{{ currentConv.user_name?.charAt(0) || 'U' }}</el-avatar>
                <div class="chat-user-details">
                  <div class="chat-user-name">{{ currentConv.user_name }}</div>
                  <div class="chat-user-status">在线</div>
                </div>
              </div>
              <div class="chat-actions">
                <el-button type="primary" size="small" @click="showQuickReply">
                  <el-icon><ChatDotRound /></el-icon>
                  快捷回复
                </el-button>
              </div>
            </div>
          </template>

          <div class="chat-messages" ref="messagesContainer">
            <div
              v-for="msg in messages"
              :key="msg.id"
              class="message"
              :class="msg.sender_type"
            >
              <div class="message-avatar">
                <el-avatar :size="40">{{ msg.sender_name?.charAt(0) || 'U' }}</el-avatar>
              </div>
              <div class="message-content">
                <div class="message-bubble">
                  {{ msg.content }}
                </div>
                <div class="message-time">{{ formatTime(msg.created_at) }}</div>
              </div>
            </div>
          </div>

          <div class="chat-input">
            <el-input
              v-model="messageInput"
              type="textarea"
              :rows="3"
              placeholder="输入消息..."
              @keyup.enter.ctrl="sendMessage"
            />
            <div class="chat-input-actions">
              <el-button @click="selectImage">
                <el-icon><Picture /></el-icon>
                图片
              </el-button>
              <el-button type="primary" @click="sendMessage" :loading="sending">
                <el-icon><Promotion /></el-icon>
                发送
              </el-button>
            </div>
          </div>
        </el-card>

        <el-empty v-else description="请选择一个会话" />
      </el-col>
    </el-row>

    <!-- 快捷回复对话框 -->
    <el-dialog v-model="quickReplyVisible" title="快捷回复" width="500px">
      <el-select v-model="selectedQuickReply" placeholder="选择快捷回复" style="width: 100%;" @change="applyQuickReply">
        <el-option
          v-for="reply in quickReplies"
          :key="reply.id"
          :label="reply.name"
          :value="reply.content"
        >
          <span>{{ reply.name }}</span>
          <span style="float: right; color: #8492a6; font-size: 13px">{{ reply.content }}</span>
        </el-option>
      </el-select>
      <template #footer>
        <el-button @click="quickReplyVisible = false">取消</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import { useAccountStore } from '@/store/account'

const accountStore = useAccountStore()
const loading = ref(false)
const sending = ref(false)
const selectedAccount = ref(null)
const searchKeyword = ref('')
const currentConv = ref(null)
const messageInput = ref('')
const quickReplyVisible = ref(false)
const selectedQuickReply = ref('')

const accounts = computed(() => accountStore.accounts)
const conversations = ref([])
const messages = ref([])

const quickReplies = ref([
  { id: 1, name: '欢迎语', content: '您好，欢迎光临！请问有什么可以帮您？' },
  { id: 2, name: '发货通知', content: '您好，您的商品已发货，请注意查收！' },
  { id: 3, name: '感谢购买', content: '感谢您的购买，祝您生活愉快！' }
])

const filteredConversations = computed(() => {
  if (!searchKeyword.value) return conversations.value
  return conversations.value.filter(conv =>
    conv.user_name?.toLowerCase().includes(searchKeyword.value.toLowerCase())
  )
})

onMounted(() => {
  accountStore.fetchAccounts()
})

async function loadConversations() {
  if (!selectedAccount.value) {
    conversations.value = []
    return
  }

  loading.value = true
  try {
    const response = await axios.get('http://localhost:8080/api/conversations', {
      params: { account_id: selectedAccount.value }
    })
    conversations.value = response.data || []
  } catch (error) {
    ElMessage.error('加载会话失败：' + error.message)
  } finally {
    loading.value = false
  }
}

function selectConversation(conv) {
  currentConv.value = conv
  loadMessages(conv.conversation_id)
}

async function loadMessages(conversationId) {
  try {
    const response = await axios.get(`http://localhost:8080/api/conversations/${conversationId}/messages`)
    messages.value = response.data || []
    
    // 滚动到底部
    setTimeout(() => {
      const container = document.querySelector('.chat-messages')
      if (container) {
        container.scrollTop = container.scrollHeight
      }
    }, 100)
  } catch (error) {
    ElMessage.error('加载消息失败：' + error.message)
  }
}

async function sendMessage() {
  if (!messageInput.value.trim() || !currentConv.value) {
    ElMessage.warning('请输入消息内容')
    return
  }

  sending.value = true
  try {
    await axios.post(
      `http://localhost:8080/api/conversations/${currentConv.value.conversation_id}/messages`,
      { content: messageInput.value },
      { params: { account_id: selectedAccount.value } }
    )
    
    messages.value.push({
      content: messageInput.value,
      sender_type: 'me',
      created_at: new Date().toISOString()
    })
    
    messageInput.value = ''
    
    // 滚动到底部
    setTimeout(() => {
      const container = document.querySelector('.chat-messages')
      if (container) {
        container.scrollTop = container.scrollHeight
      }
    }, 100)
  } catch (error) {
    ElMessage.error('发送失败：' + error.message)
  } finally {
    sending.value = false
  }
}

function showQuickReply() {
  quickReplyVisible.value = true
}

function applyQuickReply(content) {
  messageInput.value = content
  quickReplyVisible.value = false
}

function formatTime(time) {
  if (!time) return ''
  const date = new Date(time)
  const now = new Date()
  const diff = now - date
  
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  
  return date.toLocaleDateString('zh-CN', { month: 'numeric', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

function selectImage() {
  ElMessage.info('图片功能开发中')
}
</script>

<style scoped>
.conversations-page {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.conversation-list {
  max-height: 600px;
  overflow-y: auto;
}

.conversation-item {
  display: flex;
  align-items: center;
  padding: 12px;
  cursor: pointer;
  border-radius: 8px;
  transition: background-color 0.3s;
}

.conversation-item:hover {
  background-color: #f5f7fa;
}

.conversation-item.active {
  background-color: #e6f7ff;
}

.conversation-avatar {
  margin-right: 12px;
}

.conversation-info {
  flex: 1;
  overflow: hidden;
}

.conversation-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.conversation-name {
  font-weight: 600;
  color: #303133;
}

.conversation-time {
  font-size: 12px;
  color: #909399;
}

.conversation-preview {
  font-size: 13px;
  color: #909399;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.chat-card {
  height: calc(100vh - 140px);
  display: flex;
  flex-direction: column;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chat-user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.chat-user-name {
  font-weight: 600;
  color: #303133;
}

.chat-user-status {
  font-size: 12px;
  color: #67C23A;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background-color: #f5f7fa;
}

.message {
  display: flex;
  margin-bottom: 20px;
}

.message.me {
  flex-direction: row-reverse;
}

.message-avatar {
  flex-shrink: 0;
}

.message-content {
  max-width: 60%;
  margin: 0 12px;
}

.message-bubble {
  padding: 12px 16px;
  border-radius: 12px;
  background-color: #fff;
  color: #303133;
  word-wrap: break-word;
}

.message.me .message-bubble {
  background-color: #409EFF;
  color: #fff;
}

.message-time {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
  text-align: right;
}

.chat-input {
  border-top: 1px solid #e6e6e6;
  padding: 15px;
  background-color: #fff;
}

.chat-input-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 10px;
}
</style>
