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
      <header class="top-bar">
        <h2 class="page-title">知识库管理</h2>
        <div class="user-profile">
          <span>{{ username }}</span>
          <el-button type="danger" plain size="small" @click="handleLogout">退出登录</el-button>
        </div>
      </header>

      <div class="content-area">
        <div class="action-bar">
          <div class="empty-space"></div>
          <el-button type="primary" class="create-btn" @click="showCreateDialog = true">
            + 创建知识库
          </el-button>
        </div>

        <!-- 知识库列表 (网格布局) -->
        <div v-if="kbList.length > 0" class="kb-grid">
          <div v-for="kb in kbList" :key="kb.id" class="kb-card">
            <div class="kb-icon">📁</div>
            <div class="kb-info">
              <h3 class="kb-name">{{ kb.name }}</h3>
              <p class="kb-desc">{{ kb.description || '暂无描述' }}</p>
            </div>
            <div class="kb-footer">
              <span class="kb-date">{{ formatDate(kb.createdAt) }}</span>
              <el-button size="small" text type="primary" @click="goToDetail(kb.id)">进入 -></el-button>
            </div>
          </div>
        </div>

        <!-- 空状态 -->
        <el-empty v-else description="还没有知识库，创建一个开始吧！" />
      </div>
    </main>

    <!-- 创建知识库弹窗 -->
    <el-dialog v-model="showCreateDialog" title="创建新知识库" width="400px" :close-on-click-modal="false">
      <el-form :model="createForm" label-position="top">
        <el-form-item label="知识库名称 (必填)">
          <el-input v-model="createForm.name" placeholder="例如：产品操作手册" />
        </el-form-item>
        <el-form-item label="描述 (选填)">
          <el-input v-model="createForm.description" type="textarea" :rows="3" placeholder="简要说明一下这个知识库..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showCreateDialog = false">取消</el-button>
          <el-button type="primary" :loading="creating" @click="handleCreate">确认创建</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import request from '../utils/request'

const router = useRouter()
const username = ref('')
const kbList = ref<any[]>([])

// 弹窗控制
const showCreateDialog = ref(false)
const creating = ref(false)
const createForm = ref({ name: '', description: '' })

onMounted(() => {
  username.value = localStorage.getItem('username') || '管理员'
  fetchKbList()
})

// 获取列表
const fetchKbList = async () => {
  try {
    const res: any = await request.get('/knowledge-bases')
    if (res.code === 200) {
      kbList.value = res.data
    }
  } catch (error) {
    console.error('获取列表失败', error)
  }
}

// 创建知识库
const handleCreate = async () => {
  if (!createForm.value.name) {
    ElMessage.warning('请输入知识库名称')
    return
  }
  
  creating.value = true
  try {
    const res: any = await request.post('/knowledge-bases', createForm.value)
    if (res.code === 200) {
      ElMessage.success('创建成功')
      showCreateDialog.value = false
      createForm.value = { name: '', description: '' }
      fetchKbList() // 刷新列表
    } else {
      ElMessage.error(res.message)
    }
  } catch (error) {
    console.error(error)
  } finally {
    creating.value = false
  }
}

const handleLogout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('username')
  router.push('/login')
}

// 跳转到文档详情页
const goToDetail = (id: number) => {
  router.push(`/kb/${id}`)
}

// 日期格式化
const formatDate = (dateStr: string) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString()
}
</script>

<style scoped>
.layout-container { display: flex; height: 100vh; background-color: #fafafa; }

/* 侧边栏 */
.sidebar { width: 240px; background-color: #ffffff; border-right: 1px solid #e4e4e7; display: flex; flex-direction: column; }
.logo-area { height: 64px; display: flex; align-items: center; padding: 0 24px; border-bottom: 1px solid #e4e4e7; }
.logo-box { background: #18181b; color: white; font-size: 12px; font-weight: bold; padding: 4px 8px; border-radius: 6px; margin-right: 12px; }
.logo-text { font-weight: 600; font-size: 16px; color: #18181b; }
.nav-menu { padding: 16px 12px; flex: 1; }
.nav-item { padding: 10px 12px; margin-bottom: 4px; border-radius: 8px; cursor: pointer; color: #52525b; font-size: 14px; font-weight: 500; display: flex; align-items: center; gap: 12px; transition: all 0.2s; }
.nav-item:hover { background-color: #f4f4f5; color: #18181b; }
.nav-item.active { background-color: #f4f4f5; color: #18181b; font-weight: 600; }

/* 右侧区域 */
.main-content { flex: 1; display: flex; flex-direction: column; }
.top-bar { height: 64px; background: #ffffff; border-bottom: 1px solid #e4e4e7; display: flex; align-items: center; justify-content: space-between; padding: 0 32px; }
.page-title { font-size: 18px; font-weight: 600; color: #18181b; margin: 0; }
.user-profile { display: flex; align-items: center; gap: 16px; color: #52525b; font-size: 14px; }

.content-area { padding: 32px; flex: 1; overflow-y: auto; }
.action-bar { display: flex; justify-content: space-between; margin-bottom: 24px; }
.create-btn { background-color: #18181b; border-color: #18181b; border-radius: 8px; }

/* 知识库网格 */
.kb-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; }
.kb-card {
  background: #ffffff;
  border: 1px solid #e4e4e7;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  transition: all 0.2s;
  box-shadow: 0 1px 3px rgba(0,0,0,0.02);
}
.kb-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px -8px rgba(0,0,0,0.1);
  border-color: #d4d4d8;
}
.kb-icon { font-size: 32px; margin-bottom: 16px; }
.kb-info { flex: 1; margin-bottom: 16px; }
.kb-name { font-size: 16px; font-weight: 600; color: #18181b; margin: 0 0 8px 0; }
.kb-desc { font-size: 14px; color: #71717a; margin: 0; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.kb-footer { display: flex; justify-content: space-between; align-items: center; border-top: 1px solid #f4f4f5; padding-top: 12px; margin-top: auto; }
.kb-date { font-size: 12px; color: #a1a1aa; }
</style>