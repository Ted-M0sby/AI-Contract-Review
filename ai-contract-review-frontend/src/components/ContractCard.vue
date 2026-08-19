<script setup>
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import { ArrowRight, FileText, ScanSearch, Sparkles } from '@lucide/vue'

const props = defineProps({
  contract: {
    type: Object,
    required: true,
  },
})

const statusMap = {
  pending: '待审查',
  reviewing: '审查中',
  reviewed: '已审查',
  failed: '审查失败',
}

const riskMap = {
  high: '高风险',
  medium: '中风险',
  low: '低风险',
}

const statusText = computed(() => statusMap[props.contract.status] || props.contract.status)
const riskText = computed(() => props.contract.overall_risk ? riskMap[props.contract.overall_risk] : '未生成')
</script>

<template>
  <article class="contract-card">
    <div class="contract-card-main">
      <div class="contract-title-row">
        <span class="file-icon"><FileText /></span>
        <div>
          <h3>{{ contract.title }}</h3>
          <p>{{ contract.contract_type_name }}</p>
        </div>
      </div>
      <div class="tag-row">
        <span class="status-pill" :class="`status-${contract.status}`">{{ statusText }}</span>
        <span class="risk-pill" :class="contract.overall_risk ? `risk-${contract.overall_risk}` : 'risk-empty'">
          {{ riskText }}
        </span>
      </div>
    </div>

    <dl class="meta-grid">
      <div>
        <dt>上传时间</dt>
        <dd>{{ contract.created_at }}</dd>
      </div>
      <div>
        <dt>合同类型</dt>
        <dd>{{ contract.contract_type }}</dd>
      </div>
    </dl>

    <div class="card-actions">
      <RouterLink class="button button-secondary" :to="`/contracts/${contract.id}`"><ScanSearch />查看详情</RouterLink>
      <RouterLink
        class="button button-accent"
        :class="{ disabled: contract.status !== 'reviewed' }"
        :to="contract.status === 'reviewed' ? `/contracts/${contract.id}/review` : `/contracts/${contract.id}`"
      >
        <Sparkles v-if="contract.status === 'reviewed'" /><ArrowRight v-else />查看审查结果
      </RouterLink>
    </div>
  </article>
</template>
