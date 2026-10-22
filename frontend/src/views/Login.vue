<template>
  <div class="login-wrapper">
    <div class="login-card">
      <div class="header">
        <div class="logo-icon">
          <!-- 简单用 SVG 模拟一个高质感 Icon -->
          <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
          </svg>
        </div>
        <h1 class="title">欢迎回来</h1>
        <p class="subtitle">登录到您的 RAG 智能知识库系统</p>
      </div>

      <el-form :model="form" class="login-form" @keyup.enter="handleLogin">
        <div class="input-group">
          <label>账号</label>
          <el-input v-model="form.username" placeholder="请输入管理员账号" size="large" />
        </div>
        <div class="input-group">
          <label>密码</label>
          <el-input v-model="form.password" type="password" placeholder="请输入密码" size="large" show-password />
        </div>
        
        <el-button type="primary" size="large" class="submit-btn" :loading="loading" @click="handleLogin">
          登录系统
        </el-button>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import request from '../utils/request'

const router = useRouter()
const loading = ref(false)
const form = ref({
  username: 'admin',
  password: '123456'
})

const handleLogin = async () => {
  if (!form.value.username || !form.value.password) {
    ElMessage.warning('请填写完整信息')
    return
  }
  
  loading.value = true
  try {
    const res: any = await request.post('/auth/login', form.value)
    if (res.code === 200) {
      ElMessage.success('验证成功')
      localStorage.setItem('token', res.data.token)
      localStorage.setItem('username', res.data.username)
      router.push('/dashboard')
    } else {
      ElMessage.error(res.message || '登录失败')
    }
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-wrapper {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #fafafa; /* 极浅灰背景 */
  background-image: radial-gradient(#e5e7eb 1px, transparent 1px);
  background-size: 20px 20px; /* 细节点阵背景 */
}

.login-card {
  width: 420px;
  background: #ffffff;
  padding: 48px;
  border-radius: 16px;
  box-shadow: 0 10px 40px -10px rgba(0, 0, 0, 0.08), 0 0 1px rgba(0,0,0,0.1);
  border: 1px solid #f0f0f0;
}

.header {
  text-align: center;
  margin-bottom: 36px;
}

.logo-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 56px;
  height: 56px;
  background: #18181b; /* 极简黑 */
  color: #ffffff;
  border-radius: 14px;
  margin-bottom: 20px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.title {
  font-size: 24px;
  font-weight: 600;
  color: #18181b;
  margin: 0 0 8px 0;
  letter-spacing: -0.5px;
}

.subtitle {
  font-size: 14px;
  color: #71717a;
  margin: 0;
}

.input-group {
  margin-bottom: 20px;
}

.input-group label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: #3f3f46;
  margin-bottom: 8px;
}

:deep(.el-input__wrapper) {
  box-shadow: 0 0 0 1px #e4e4e7 inset;
  border-radius: 8px;
  padding: 8px 12px;
  transition: all 0.2s;
}

:deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px #18181b inset; /* 聚焦时变成极简黑，告别默认蓝色 */
}

.submit-btn {
  width: 100%;
  margin-top: 12px;
  background-color: #18181b;
  border-color: #18181b;
  border-radius: 8px;
  font-weight: 500;
  letter-spacing: 0.5px;
  transition: all 0.2s;
}

.submit-btn:hover {
  background-color: #27272a;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}
</style>