<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, FileText, Send, ShieldCheck } from '@lucide/vue'
import { getContract, getReview, sendContractDingTalk } from '../api/contract'
import RiskCard from '../components/RiskCard.vue'

const route = useRoute()
const router = useRouter()
const contract = ref(null)
const review = ref(null)
const loading = ref(true)
const error = ref('')
const dingtalkLoading = ref(false)
const dingtalkMessage = ref('')
const dingtalkError = ref('')

const riskMap = {
  high: '高风险',
  medium: '中风险',
  low: '低风险',
}

const counts = computed(() => {
  const result = { high: 0, medium: 0, low: 0 }
  const levels = [
    ...(review.value?.risks || []).map((item) => item.risk_level),
    ...(review.value?.missing_items || []).map((item) => item.risk_level),
    ...(review.value?.conflicts || []).map((item) => item.risk_level),
  ]

  levels.forEach((level) => {
    if (result[level] !== undefined) result[level] += 1
  })

  return result
})

onMounted(async () => {
  try {
    const [contractResponse, reviewResponse] = await Promise.all([
      getContract(route.params.id),
      getReview(route.params.id),
    ])
    contract.value = contractResponse.data
    review.value = reviewResponse.data
  } catch (requestError) {
    error.value = requestError.message || 'AI 审查结果加载失败，请稍后重试'
  } finally {
    loading.value = false
  }
})

async function handleSendDingTalk() {
  if (!contract.value) return

  dingtalkLoading.value = true
  dingtalkMessage.value = ''
  dingtalkError.value = ''

  try {
    const response = await sendContractDingTalk(contract.value.id)
    dingtalkMessage.value = response.message || '已发送至钉钉群'
  } catch (requestError) {
    dingtalkError.value = requestError.message || '钉钉发送失败，请稍后重试'
  } finally {
    dingtalkLoading.value = false
  }
}
</script>

<template>
  <div v-if="loading" class="empty-state">正在加载 AI 审查结果...</div>
  <div v-else-if="error" class="empty-state">
    <p class="form-error">{{ error }}</p>
    <button class="button button-secondary" type="button" @click="router.push('/contracts')">返回合同列表</button>
  </div>
  <div v-else-if="!contract || !review" class="empty-state">未找到审查结果</div>
  <template v-else>
    <section class="page-header">
      <div>
        <span class="eyebrow">AI 审查结果</span>
        <h1>{{ contract.title }}</h1>
        <p>{{ review.contract_type_name }} · AI 类型置信度 {{ Math.round(review.contract_confidence * 100) }}%</p>
      </div>
      <div class="header-actions">
        <button class="button button-accent" type="button" :disabled="dingtalkLoading" @click="handleSendDingTalk">
          <Send v-if="!dingtalkLoading" />{{ dingtalkLoading ? '发送中...' : '发送钉钉复核' }}
        </button>
        <button class="button button-secondary" type="button" @click="router.push(`/contracts/${contract.id}`)"><ArrowLeft />返回详情</button>
      </div>
    </section>

    <p v-if="dingtalkMessage" class="form-message">{{ dingtalkMessage }}</p>
    <p v-if="dingtalkError" class="form-error">{{ dingtalkError }}</p>

    <section class="review-summary">
      <div class="summary-main">
        <span class="summary-icon"><ShieldCheck /></span>
        <span class="risk-pill" :class="`risk-${review.overall_risk}`">{{ riskMap[review.overall_risk] }}</span>
        <h2>{{ review.review_summary }}</h2>
        <p>{{ review.summary }}</p>
      </div>
      <div class="risk-counts">
        <div class="count-box risk-high">
          <strong>{{ counts.high }}</strong>
          <span>高风险数量</span>
        </div>
        <div class="count-box risk-medium">
          <strong>{{ counts.medium }}</strong>
          <span>中风险数量</span>
        </div>
        <div class="count-box risk-low">
          <strong>{{ counts.low }}</strong>
          <span>低风险数量</span>
        </div>
      </div>
    </section>

    <section class="review-layout">
      <article class="document-panel compact">
        <header>
          <h2><FileText />合同原文</h2>
          <span>{{ contract.contract_type_name }}</span>
        </header>
        <pre>{{ contract.content }}</pre>
      </article>

      <div class="review-panel">
        <section>
          <h2>风险列表</h2>
          <div class="risk-list">
            <RiskCard v-for="risk in review.risks" :key="risk.risk_id" :risk="risk" />
          </div>
        </section>

        <section v-if="review.missing_items?.length" class="review-subsection">
          <h2>缺失事项</h2>
          <article v-for="item in review.missing_items" :key="item.title" class="simple-finding">
            <span class="risk-pill" :class="`risk-${item.risk_level}`">{{ riskMap[item.risk_level] }}</span>
            <h3>{{ item.title }}</h3>
            <p>{{ item.reason }}</p>
          </article>
        </section>

        <section v-if="review.conflicts?.length" class="review-subsection">
          <h2>冲突条款</h2>
          <article v-for="item in review.conflicts" :key="item.title" class="simple-finding">
            <span class="risk-pill" :class="`risk-${item.risk_level}`">{{ riskMap[item.risk_level] }}</span>
            <h3>{{ item.title }}</h3>
            <p>{{ item.location_a }}：{{ item.text_a }}</p>
            <p>{{ item.location_b }}：{{ item.text_b }}</p>
          </article>
        </section>

        <section v-if="review.positive_findings?.length" class="review-subsection">
          <h2>正向发现</h2>
          <ul class="positive-list">
            <li v-for="item in review.positive_findings" :key="item">{{ item }}</li>
          </ul>
        </section>
      </div>
    </section>
  </template>
</template>
