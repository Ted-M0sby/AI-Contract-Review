<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { FileText, Sparkles } from '@lucide/vue'
import { getContract, startReview } from '../api/contract'

const route = useRoute()
const router = useRouter()
const contract = ref(null)
const loading = ref(true)
const reviewing = ref(false)
const error = ref('')

const statusMap = {
  pending: '待审查',
  reviewing: '审查中',
  reviewed: '已审查',
  failed: '审查失败',
}

const statusText = computed(() => contract.value ? statusMap[contract.value.status] || contract.value.status : '')

onMounted(async () => {
  try {
    const response = await getContract(route.params.id)
    contract.value = response.data
  } catch (requestError) {
    error.value = requestError.message || '合同详情加载失败，请稍后重试'
  } finally {
    loading.value = false
  }
})

async function handleStartReview() {
  if (!contract.value) return

  reviewing.value = true
  error.value = ''
  contract.value.status = 'reviewing'

  try {
    const response = await startReview(contract.value.id)
    if (response.code !== 200) {
      error.value = response.message || '发起审查失败'
      return
    }
    contract.value.status = 'reviewed'
    router.push(`/contracts/${contract.value.id}/review`)
  } finally {
    reviewing.value = false
  }
}
</script>

<template>
  <div v-if="loading" class="empty-state">正在加载合同详情...</div>
  <div v-else-if="error && !contract" class="empty-state">
    <p class="form-error">{{ error }}</p>
    <button class="button button-secondary" type="button" @click="router.push('/contracts')">返回合同列表</button>
  </div>
  <div v-else-if="!contract" class="empty-state">未找到该合同</div>
  <template v-else>
    <section class="page-header">
      <div>
        <span class="eyebrow">合同详情</span>
        <h1>{{ contract.title }}</h1>
        <p>{{ contract.contract_type_name }} · 上传时间：{{ contract.created_at }}</p>
      </div>
      <button class="button button-accent" type="button" :disabled="reviewing" @click="handleStartReview">
        <Sparkles v-if="!reviewing" />{{ reviewing ? 'AI 审查中...' : '开始 AI 审查' }}
      </button>
    </section>

    <section class="detail-layout">
      <aside class="info-panel">
        <div class="panel-title"><FileText /><strong>合同信息</strong></div>
        <dl class="info-list">
          <div>
            <dt>合同类型</dt>
            <dd>{{ contract.contract_type_name }}</dd>
          </div>
          <div>
            <dt>内部类型</dt>
            <dd>{{ contract.contract_type }}</dd>
          </div>
          <div>
            <dt>审查状态</dt>
            <dd>
              <span class="status-pill" :class="`status-${contract.status}`">{{ statusText }}</span>
            </dd>
          </div>
          <div v-if="contract.original_filename || contract.file_name">
            <dt>上传文件</dt>
            <dd>{{ contract.original_filename || contract.file_name }}</dd>
          </div>
        </dl>
        <p v-if="reviewing" class="reviewing-note">AI 正在审查合同，预计约 2 秒后进入结果页。</p>
        <p v-if="error" class="form-error">{{ error }}</p>
      </aside>

      <article class="document-panel">
        <header>
          <h2>合同正文</h2>
          <span>合同原文</span>
        </header>
        <pre v-if="contract.content">{{ contract.content }}</pre>
        <div v-else class="empty-state">后端暂未返回可展示的合同正文</div>
      </article>
    </section>
  </template>
</template>
