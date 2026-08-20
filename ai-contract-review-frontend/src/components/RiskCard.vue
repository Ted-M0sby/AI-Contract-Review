<script setup>
import { computed } from 'vue'
import { BookOpenText, FileText, Scale, Sparkles } from '@lucide/vue'

const props = defineProps({
  risk: {
    type: Object,
    required: true,
  },
})

const riskMap = {
  high: '高风险',
  medium: '中风险',
  low: '低风险',
}

const levelText = computed(() => riskMap[props.risk.risk_level] || props.risk.risk_level)
const confidenceText = computed(() => `${Math.round((props.risk.confidence || 0) * 100)}%`)
const evidenceSourceText = computed(() => {
  const sources = (props.risk.evidence || [])
    .map((item) => item.source_name || item.source_type)
    .filter(Boolean)
  const uniqueSources = [...new Set(sources)]

  if (uniqueSources.length <= 3) {
    return uniqueSources.join('、')
  }

  return `${uniqueSources.slice(0, 3).join('、')} 等 ${uniqueSources.length} 个来源`
})
</script>

<template>
  <article class="risk-card" :class="`risk-card-${risk.risk_level}`">
    <header class="risk-card-header">
      <div>
        <span class="subtle">{{ risk.risk_id }} · {{ risk.category }}</span>
        <h3>{{ risk.title }}</h3>
      </div>
      <span class="risk-pill" :class="`risk-${risk.risk_level}`">{{ levelText }}</span>
    </header>

    <div class="risk-section">
      <h4><FileText />原合同条款</h4>
      <p class="quote-text">{{ risk.original_text }}</p>
    </div>

    <div class="risk-section">
      <h4><Scale />风险原因</h4>
      <p>{{ risk.reason }}</p>
    </div>

    <div class="risk-section">
      <h4><Sparkles />修改建议</h4>
      <p>{{ risk.suggestion }}</p>
    </div>

    <div class="risk-section recommended">
      <h4><BookOpenText />建议修改后条款</h4>
      <p>{{ risk.recommended_clause }}</p>
    </div>

    <div class="risk-footer">
      <span>AI 置信度：{{ confidenceText }}</span>
      <span v-if="evidenceSourceText">来源：{{ evidenceSourceText }}</span>
    </div>
  </article>
</template>
