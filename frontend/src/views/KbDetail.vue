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
        <div class="nav-item active"><span class="icon">📄</span> 文档管理</div>
      </nav>
    </aside>

    <main class="main-content">
      <header class="top-bar">
        <div style="display: flex; align-items: center; gap: 16px;">
          <el-button @click="router.push('/dashboard')">← 返回</el-button>
          <h2 class="page-title">知识库文档管理</h2>
          <!-- 👇 新增的对话按钮 -->
          <el-button type="primary" @click="router.push(`/chat/${kbId}`)" style="background-color: #18181b; border-color: #18181b;">
            💬 开始对话
          </el-button>
        </div>
      </header>

      <div class="content-area">
        <!-- 上传区域 -->
        <el-card class="upload-card" shadow="never">
          <div class="upload-header">
            <h3>上传新文档</h3>
            <p>支持 PDF、DOCX、TXT 格式</p>
          </div>
            <el-upload
            class="upload-demo"
            drag
            multiple
            accept=".txt,.pdf,.docx"
            :action="uploadUrl"
            :headers="uploadHeaders"
            :data="{ kbId: kbId }"
            :show-file-list="true"
            :on-success="handleUploadSuccess"
            :on-error="handleUploadError"
            :before-upload="beforeUpload"
            >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">
              将文件拖到此处，或 <em>点击上传</em>
            </div>
          </el-upload>
        </el-card>

        <!-- 列表区域 -->
        <el-card class="list-card" shadow="never" style="margin-top: 24px;">
          <template #header>
            <div class="card-header">
              <span>已上传文档</span>
              <el-button text type="primary" @click="fetchDocs">刷新列表</el-button>
            </div>
          </template>
          
          <el-table :data="docList" style="width: 100%" v-loading="loading">
            <el-table-column prop="filename" label="文件名" min-width="200" />
            <el-table-column label="状态" width="120">
              <template #default="scope">
                <el-tag v-if="scope.row.status === 'PROCESSING'" type="warning">处理中</el-tag>
                <el-tag v-else-if="scope.row.status === 'AVAILABLE'" type="success">可用</el-tag>
                <el-tag v-else type="danger">失败</el-tag>
                <el-button 
                  v-if="scope.row.status === 'FAILED' || scope.row.status === 'PROCESSING'" 
                  type="primary" 
                  link 
                  size="small"
                  @click="handleRetry(scope.row.id)"
                >
                  重试
                </el-button>


              </template>
            </el-table-column>
            <el-table-column prop="createdAt" label="上传时间" width="200">
              <template #default="scope">
                {{ new Date(scope.row.createdAt).toLocaleString() }}
              </template>
            </el-table-column>

              <el-table-column label="操作" width="100">
              <template #default="scope">
                <el-button 
                  type="danger" link size="small"
                  @click="handleDelete(scope.row.id, scope.row.filename)"
                >
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import request from '../utils/request'

const route = useRoute()
const router = useRouter()
const kbId = route.params.id

const docList = ref([])
const loading = ref(false)

// 上传配置
const uploadUrl = 'http://localhost:18080/api/documents/upload'
const uploadHeaders = computed(() => {
  return {
    Authorization: `Bearer ${localStorage.getItem('token')}`
  }
})

const beforeUpload = (file: File) => {
  const isAllowed = ['pdf', 'docx', 'txt'].includes(file.name.split('.').pop()?.toLowerCase() || '')
  if (!isAllowed) {
    ElMessage.error('只能上传 PDF, DOCX, TXT 文件')
    return false
  }
  
  // 👇 新增：限制文件不能超过 100MB（你可以根据自己电脑配置调整）
  const isLt100M = file.size / 1024 / 1024 < 100
  if (!isLt100M) {
    ElMessage.error('文件大小不能超过 100MB，请拆分后再上传')
    return false
  }
  
  return true
}

const handleUploadSuccess = (res: any) => {
  if (res.code === 200) {
    ElMessage.success('有文件上传成功，正在处理...')
    // 延迟 1 秒刷新列表，避免并发上传时接口被打爆
    setTimeout(() => {
      fetchDocs()
    }, 1000)
  } else {
    ElMessage.error(res.message || '上传失败')
  }
}

const handleUploadError = () => {
  ElMessage.error('网络错误，上传失败')
}

// 获取文档列表
const fetchDocs = async () => {
  loading.value = true
  try {
    const res: any = await request.get(`/documents/list/${kbId}`)
    if (res.code === 200) {
      docList.value = res.data
    }
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const handleRetry = async (docId: number) => {
  try {
    const res: any = await request.post(`/documents/${docId}/retry`)
    if (res.code === 200) {
      ElMessage.success('已重新发起处理，请稍后刷新')
      fetchDocs()
    } else {
      ElMessage.error(res.message)
    }
  } catch (error) {
    ElMessage.error('重试失败')
  }
}

const handleDelete = async (docId: number, filename: string) => {
  try {
    await ElMessageBox.confirm(`确定要删除文件 "${filename}" 吗？删除后无法恢复。`, '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })
    
    const res: any = await request.delete(`/documents/${docId}`)
    if (res.code === 200) {
      ElMessage.success('删除成功')
      fetchDocs()
    } else {
      ElMessage.error(res.message || '删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error(error)
      ElMessage.error('删除请求失败')
    }
  }
}

onMounted(() => {
  fetchDocs()
})
</script>

<style scoped>
/* 复用之前的布局样式 */
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

.content-area { padding: 32px; flex: 1; overflow-y: auto; }
.upload-card { border-radius: 12px; border: 1px solid #e4e4e7; }
.upload-header { margin-bottom: 16px; }
.upload-header h3 { margin: 0 0 4px 0; font-size: 16px; color: #18181b; }
.upload-header p { margin: 0; font-size: 13px; color: #71717a; }
.list-card { border-radius: 12px; border: 1px solid #e4e4e7; }
.card-header { display: flex; justify-content: space-between; align-items: center; font-weight: 600; color: #18181b; }
</style>