<template>
  <div class="layout-container">
    <!-- 左侧边栏 -->
    <aside class="sidebar">
      <div class="logo-area">
        <div class="logo-box">RAG</div>
        <span class="logo-text">智能知识库</span>
      </div>
      
      <nav class="nav-menu">
        <div class="nav-item active">
          <span class="icon">📚</span> 知识库管理
        </div>
        <div class="nav-item">
          <span class="icon">💬</span> 智能问答
        </div>
        <div class="nav-item">
          <span class="icon">⚙️</span> 系统设置
        </div>
      </nav>
    </aside>

    <!-- 右侧主内容区 -->
    <main class="main-content">
      <!-- 顶部导航 -->
      <header class="top-bar">
        <h2 class="page-title">知识库管理</h2>
        <div class="user-profile">
          <span>{{ username }}</span>
          <el-button type="danger" plain size="small" @click="handleLogout">退出登录</el-button>
        </div>
      </header>

      <!-- 内容看板 -->
      <div class="content-area">
        <div class="welcome-card">
          <h1>你好，{{ username }} 👋</h1>
          <p>准备好构建你的第一个 RAG 应用了吗？</p>
          <el-button type="primary" size="large" style="margin-top: 20px;" class="create-btn">
            + 创建新知识库
          </el-button>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const username = ref('')

onMounted(() => {
  username.value = localStorage.getItem('username') || '管理员'
})

const handleLogout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('username')
  router.push('/login')
}
</script>

<style scoped>
.layout-container {
  display: flex;
  height: 100vh;
  background-color: #fafafa;
}

/* 侧边栏 */
.sidebar {
  width: 240px;
  background-color: #ffffff;
  border-right: 1px solid #e4e4e7;
  display: flex;
  flex-direction: column;
}

.logo-area {
  height: 64px;
  display: flex;
  align-items: center;
  padding: 0 24px;
  border-bottom: 1px solid #e4e4e7;
}

.logo-box {
  background: #18181b;
  color: white;
  font-size: 12px;
  font-weight: bold;
  padding: 4px 8px;
  border-radius: 6px;
  margin-right: 12px;
}

.logo-text {
  font-weight: 600;
  font-size: 16px;
  color: #18181b;
}

.nav-menu {
  padding: 16px 12px;
  flex: 1;
}

.nav-item {
  padding: 10px 12px;
  margin-bottom: 4px;
  border-radius: 8px;
  cursor: pointer;
  color: #52525b;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 12px;
}

.nav-item:hover {
  background-color: #f4f4f5;
  color: #18181b;
}

.nav-item.active {
  background-color: #f4f4f5;
  color: #18181b;
  font-weight: 600;
}

/* 右侧区域 */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.top-bar {
  height: 64px;
  background: #ffffff;
  border-bottom: 1px solid #e4e4e7;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32px;
}

.page-title {
  font-size: 18px;
  font-weight: 600;
  color: #18181b;
  margin: 0;
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 16px;
  color: #52525b;
  font-size: 14px;
}

.content-area {
  padding: 32px;
  flex: 1;
  overflow-y: auto;
}

.welcome-card {
  background: #ffffff;
  border-radius: 12px;
  padding: 48px;
  border: 1px solid #e4e4e7;
  box-shadow: 0 1px 3px rgba(0,0,0,0.02);
  text-align: center;
}

.welcome-card h1 {
  font-size: 24px;
  color: #18181b;
  margin-top: 0;
}

.welcome-card p {
  color: #71717a;
}

.create-btn {
  background-color: #18181b;
  border-color: #18181b;
  border-radius: 8px;
}
</style>