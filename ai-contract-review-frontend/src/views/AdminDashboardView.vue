<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import * as echarts from 'echarts'
import { BarChart3, FileText, RefreshCw, ShieldCheck, UsersRound } from '@lucide/vue'
import { getAdminOverview } from '../api/admin'

const overview = ref(null)
const loading = ref(true)
const error = ref('')
const riskChartRef = ref(null)
const statusChartRef = ref(null)
const scaleChartRef = ref(null)
let riskChart = null
let statusChart = null
let scaleChart = null

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

const riskColors = {
  high: '#6d28d9',
  medium: '#a855f7',
  low: '#c084fc',
}

const statusColors = {
  pending: '#8a5cf6',
  reviewing: '#2e63d6',
  reviewed: '#0c8878',
  failed: '#e86d49',
}

const statusStats = computed(() => overview.value?.status_stats || {})
const riskStats = computed(() => overview.value?.risk_stats || {})
const recentContracts = computed(() => overview.value?.recent_contracts || [])
const totalRiskCount = computed(() => (
  Number(riskStats.value.high || 0)
  + Number(riskStats.value.medium || 0)
  + Number(riskStats.value.low || 0)
))
const totalStatusCount = computed(() => (
  Number(statusStats.value.pending || 0)
  + Number(statusStats.value.reviewing || 0)
  + Number(statusStats.value.reviewed || 0)
  + Number(statusStats.value.failed || 0)
))

const metricCards = computed(() => [
  {
    label: '用户总数',
    value: overview.value?.user_count || 0,
    icon: UsersRound,
  },
  {
    label: '合同总数',
    value: overview.value?.contract_count || 0,
    icon: FileText,
  },
  {
    label: '已审查',
    value: statusStats.value.reviewed || 0,
    icon: ShieldCheck,
  },
  {
    label: '审查失败',
    value: statusStats.value.failed || 0,
    icon: BarChart3,
  },
])

const riskPieData = computed(() => {
  const data = ['high','medium','low'].map((level) => ({
    name: riskMap[level],
    value: Number(riskStats.value[level] || 0),
    realValue: Number(riskStats.value[level] || 0),
    itemStyle: { color: riskColors[level] },
  }))

  if (!data.some((item) => item.value > 0)) {
    return data.map((item) => ({
      ...item,
      value: 1,
    }))
  }

  return data
})

const statusPieData = computed(() => {
  const data = ['pending','reviewing','reviewed','failed'].map((status) => ({
    name: statusMap[status],
    value: Number(statusStats.value[status] || 0),
    itemStyle: { color: statusColors[status] },
  }))

  if (!data.some((item) => item.value > 0)) {
    return [{ name: '暂无状态数据', value: 1, itemStyle: { color: '#eef1f3' } }]
  }

  return data
})

const scalePieData = computed(() => {
  const data = [
    { name: '用户总数', value: Number(overview.value?.user_count || 0), itemStyle: { color: '#7c3aed' } },
    { name: '合同总数', value: Number(overview.value?.contract_count || 0), itemStyle: { color: '#0c8878' } },
  ]

  if (!data.some((item) => item.value > 0)) {
    return [{ name: '暂无系统数据', value: 1, itemStyle: { color: '#eef1f3' } }]
  }

  return data
})

function resizeCharts() {
  ;[riskChart,statusChart,scaleChart].forEach((item) => {
    if (item) item.resize()
  })
}

function disposeCharts() {
  ;[riskChart,statusChart,scaleChart].forEach((item) => {
    if (item) item.dispose()
  })
  riskChart = null
  statusChart = null
  scaleChart = null
}

function renderPieChart(chartRef,chartInstance,name,data) {
  if (!chartRef.value || !overview.value) return chartInstance

  const currentChart = chartInstance || echarts.init(chartRef.value)
  currentChart.setOption({
    color: data.map((item) => item.itemStyle.color),
    tooltip: {
      trigger: 'item',
      formatter(item) {
        const value = item.data.realValue ?? item.value
        return `${item.name}：${value}`
      },
    },
    legend: {
      bottom: 0,
      left: 'center',
      itemWidth: 10,
      itemHeight: 10,
      textStyle: {
        color: '#68747d',
      },
    },
    series: [
      {
        name,
        type: 'pie',
        radius: '68%',
        center: ['50%','43%'],
        avoidLabelOverlap: true,
        itemStyle: {
          borderColor: '#ffffff',
          borderWidth: 3,
        },
        label: {
          color: '#35434d',
          formatter(item) {
            const value = item.data.realValue ?? item.value
            return `${item.name}\n${value}`
          },
        },
        labelLine: {
          length: 12,
          length2: 8,
        },
        data,
      },
    ],
  })
  return currentChart
}

function renderCharts() {
  if (!overview.value) return

  riskChart = renderPieChart(riskChartRef,riskChart,'风险等级',riskPieData.value)
  statusChart = renderPieChart(statusChartRef,statusChart,'审查状态',statusPieData.value)
  scaleChart = renderPieChart(scaleChartRef,scaleChart,'系统规模',scalePieData.value)
}

async function loadOverview() {
  disposeCharts()
  loading.value = true
  error.value = ''

  try {
    const response = await getAdminOverview()
    overview.value = response.data
  } catch (requestError) {
    overview.value = null
    error.value = requestError.message || '管理员看板加载失败，请稍后重试'
  } finally {
    loading.value = false
  }

  if (overview.value && !error.value) {
    await nextTick()
    renderCharts()
  }
}

onMounted(() => {
  loadOverview()
  window.addEventListener('resize',resizeCharts)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize',resizeCharts)
  disposeCharts()
})
</script>

<template>
  <section class="page-header">
    <div>
      <span class="eyebrow">管理员看板</span>
      <h1>系统运行概览</h1>
      <p>查看用户、合同、审查状态和风险分布。</p>
    </div>
    <button class="button button-secondary" type="button" :disabled="loading" @click="loadOverview">
      <RefreshCw />{{ loading ? '加载中...' : '刷新数据' }}
    </button>
  </section>

  <section class="content-band">
    <div v-if="loading" class="empty-state">正在加载管理员看板...</div>
    <div v-else-if="error" class="empty-state">
      <p class="form-error">{{ error }}</p>
      <button class="button button-secondary" type="button" @click="loadOverview">重新加载</button>
    </div>
    <template v-else-if="overview">
      <div class="admin-metrics">
        <article v-for="item in metricCards" :key="item.label" class="admin-metric">
          <span><component :is="item.icon" /></span>
          <div>
            <strong>{{ item.value }}</strong>
            <small>{{ item.label }}</small>
          </div>
        </article>
      </div>

      <div class="admin-chart-grid">
        <article class="admin-panel">
          <header class="admin-panel-header">
            <div>
              <h2>风险等级分布</h2>
              <p>共 {{ totalRiskCount }} 份合同生成风险等级</p>
            </div>
          </header>
          <div ref="riskChartRef" class="admin-chart"></div>
        </article>

        <article class="admin-panel">
          <header class="admin-panel-header">
            <div>
              <h2>审查状态</h2>
              <p>共 {{ totalStatusCount }} 份合同进入系统流程</p>
            </div>
          </header>
          <div ref="statusChartRef" class="admin-chart"></div>
        </article>

        <article class="admin-panel">
          <header class="admin-panel-header">
            <div>
              <h2>系统数据规模</h2>
              <p>用户和合同数量对比</p>
            </div>
          </header>
          <div ref="scaleChartRef" class="admin-chart"></div>
        </article>
      </div>

      <article class="admin-panel">
        <header class="list-toolbar">
          <div><FileText /><strong>最近合同</strong><span>最多显示 20 条</span></div>
          <span>按上传时间展示</span>
        </header>
        <div class="admin-table-wrap">
          <table class="admin-table">
            <thead>
              <tr>
                <th>合同名称</th>
                <th>用户邮箱</th>
                <th>合同类型</th>
                <th>审查状态</th>
                <th>综合风险</th>
                <th>上传时间</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="contract in recentContracts" :key="contract.id">
                <td>{{ contract.title }}</td>
                <td>{{ contract.user_email || '-' }}</td>
                <td>{{ contract.contract_type_name || contract.contract_type }}</td>
                <td><span class="status-pill" :class="`status-${contract.status}`">{{ statusMap[contract.status] || contract.status }}</span></td>
                <td>
                  <span class="risk-pill" :class="contract.overall_risk ? `risk-${contract.overall_risk}` : 'risk-empty'">
                    {{ contract.overall_risk ? riskMap[contract.overall_risk] : '未生成' }}
                  </span>
                </td>
                <td>{{ contract.created_at }}</td>
              </tr>
              <tr v-if="!recentContracts.length">
                <td colspan="6">暂无合同数据</td>
              </tr>
            </tbody>
          </table>
        </div>
      </article>
    </template>
  </section>
</template>
