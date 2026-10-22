<template>
  <div class="layout-container">
    <aside class="sidebar">
      <div class="logo-area">
        <div class="logo-box">RAG</div>
        <span class="logo-text">智能知识库</span>
      </div>
      <nav class="nav-menu">
        <div class="nav-item" @click="router.push('/dashboard')">
          <span class="icon">📚</span> 知识库管理
        </div>
        <div class="nav-item active"><span class="icon">💬</span> 智能问答</div>
      </nav>
    </aside>

    <main class="main-content">
      <header class="top-bar">
        <div style="display: flex; align-items: center; gap: 16px;">
          <el-button @click="router.push('/dashboard')">← 返回</el-button>
          <h2 class="page-title">知识库智能问答</h2>
        </div>
      </header>

      <div class="chat-area">
        <!-- 消息列表 -->
        <div class="message-list" ref="msgListRef">
          <div v-if="messages.length === 0" class="empty-state">
            <h2>👋 你好，我是知识库助手</h2>
            <p>你可以问我关于当前知识库中的任何问题，我会基于你的文档回答。</p>
          </div>
          
          <div v-for="(msg, index) in messages" :key="index" :class="['message-row', msg.role]">
            <div class="avatar">{{ msg.role === 'user' ? '😎' : '🤖' }}</div>
            <div class="bubble-container">
              <div class="bubble">{{ msg.content }}</div>
              <!-- 展示引用 -->
              <div v-if="msg.references && msg.references.length > 0" class="references">
                <p class="ref-title">📚 参考来源：</p>
                <el-collapse>
                  <el-collapse-item v-for="(ref, i) in msg.references" :key="i" :title="`引用片段 ${i+1}`">
                    <div class="ref-text">{{ ref.text }}</div>
                  </el-collapse-item>
                </el-collapse>
              </div>
            </div>
          </div>
          
          <div v-if="loading" class="message-row assistant">
            <div class="avatar">🤖</div>
            <div class="bubble">正在检索知识库并思考... ⏳</div>
          </div>
        </div>

        <!-- 输入框区域 -->
        <div class="input-area">
          <el-input 
            v-model="question" 
            placeholder="输入你的问题，按 Enter 发送..."
            size="large"
            @keyup.enter="sendMessage"
            :disabled="loading"
          >
            <template #append>
              <el-button @click="sendMessage" :loading="loading" type="primary" style="background:#18181b;">发送</el-button>
            </template>
          </el-input>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import request from '../utils/request'

const route = useRoute()
const router = useRouter()
const kbId = route.params.id // 从路由获取当前知识库ID

const question = ref('')
const loading = ref(false)
const messages = ref<any[]>([])
const msgListRef = ref<HTMLElement | null>(null)

const scrollToBottom = async () => {
  await nextTick()
  if (msgListRef.value) {
    msgListRef.value.scrollTop = msgListRef.value.scrollHeight
  }
}

const sendMessage = async () => {
  if (!question.value.trim()) return
  
  const userQ = question.value
  messages.value.push({ role: 'user', content: userQ })
  question.value = ''
  loading.value = true
  scrollToBottom()

  try {
    // 注意：这里是用 Form 格式发送，所以用 request 模拟表单提交
    const params = new URLSearchParams()
    params.append('question', userQ)
    params.append('kbId', kbId as string)

    const res: any = await request.post('/documents/chat', params, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    })
    
    if (res.code === 200 && res.data.code === 200) {
      const aiData = res.data.data
      messages.value.push({
        role: 'assistant',
        content: aiData.answer,
        references: aiData.references
      })
    } else {
      ElMessage.error('问答处理失败')
    }
  } catch (error) {
    console.error(error)
    ElMessage.error('请求超时或出错')
  } finally {
    loading.value = false
    scrollToBottom()
  }
}
</script>

<style scoped>
/* 基础布局 */
.layout-container { display: flex; height: 100vh; background-color: #fafafa; }
.sidebar { width: 240px; background-color: #ffffff; border-right: 1px solid #e4e4e7; display: flex; flex-direction: column; }
.logo-area { height: 64px; display: flex; align-items: center; padding: 0 24px; border-bottom: 1px solid #e4e4e7; }
.logo-box { background: #18181b; color: white; font-size: 12px; font-weight: bold; padding: 4px 8px; border-radius: 6px; margin-right: 12px; }
.logo-text { font-weight: 600; font-size: 16px; color: #18181b; }
.nav-menu { padding: 16px 12px; flex: 1; }
.nav-item { padding: 10px 12px; margin-bottom: 4px; border-radius: 8px; cursor: pointer; color: #52525b; font-size: 14px; font-weight: 500; display: flex; align-items: center; gap: 12px; transition: all 0.2s; }
.nav-item:hover { background-color: #f4f4f5; color: #18181b; }
.nav-item.active { background-color: #f4f4f5; color: #18181b; font-weight: 600; }

.main-content { flex: 1; display: flex; flex-direction: column; }
.top-bar { height: 64px; background: #ffffff; border-bottom: 1px solid #e4e4e7; display: flex; align-items: center; padding: 0 32px; }
.page-title { font-size: 18px; font-weight: 600; color: #18181b; margin: 0; }

/* 聊天区样式 */
.chat-area { flex: 1; display: flex; flex-direction: column; padding: 24px; overflow: hidden; max-width: 900px; margin: 0 auto; width: 100%; }
.message-list { flex: 1; overflow-y: auto; padding-bottom: 24px; display: flex; flex-direction: column; gap: 20px; }
.empty-state { text-align: center; color: #71717a; margin-top: 100px; }
.empty-state h2 { color: #18181b; font-size: 24px; }

.message-row { display: flex; gap: 16px; max-width: 85%; }
.message-row.user { flex-direction: row-reverse; align-self: flex-end; }
.message-row.assistant { align-self: flex-start; }

.avatar { width: 36px; height: 36px; border-radius: 50%; background: #f4f4f5; display: flex; align-items: center; justify-content: center; font-size: 18px; flex-shrink: 0; border: 1px solid #e4e4e7;}
.message-row.user .avatar { background: #18181b; color: white; border: none; }

.bubble-container { display: flex; flex-direction: column; gap: 8px; width: 100%; }
.bubble { padding: 12px 16px; border-radius: 12px; font-size: 15px; line-height: 1.6; word-break: break-word; }
.message-row.assistant .bubble { background: #ffffff; border: 1px solid #e4e4e7; color: #18181b; border-top-left-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.02); }
.message-row.user .bubble { background: #18181b; color: #ffffff; border-top-right-radius: 4px; }

.references { background: #fafafa; border: 1px solid #e4e4e7; border-radius: 8px; padding: 12px; margin-top: 8px;}
.ref-title { margin: 0 0 8px 0; font-size: 13px; color: #71717a; font-weight: 600; }
.ref-text { font-size: 13px; color: #52525b; line-height: 1.5; white-space: pre-wrap; }

/* 输入区 */
.input-area { margin-top: 16px; }
</style>