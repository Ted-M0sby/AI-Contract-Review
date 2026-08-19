<script setup>
import { onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { FileText, UploadCloud } from '@lucide/vue'
import { getContracts } from '../api/contract'
import ContractCard from '../components/ContractCard.vue'

const contracts = ref([])
const loading = ref(true)
const error = ref('')
const email = ref(localStorage.getItem('email') || '')
const userId = ref(localStorage.getItem('user_id') || '')

async function loadContracts() {
  loading.value = true
  error.value = ''

  try {
    const response = await getContracts()
    contracts.value = response.data || []
  } catch (requestError) {
    contracts.value = []
    error.value = requestError.message || '合同列表加载失败，请稍后重试'
  } finally {
    loading.value = false
  }
}

onMounted(loadContracts)
</script>

<template>
  <section class="page-header">
    <div>
      <span class="eyebrow">合同工作台</span>
      <h1>我的合同</h1>
      <p>当前用户：{{ email }} · 用户 ID：{{ userId }}</p>
    </div>
    <RouterLink class="button button-primary" to="/contracts/upload"><UploadCloud />上传合同</RouterLink>
  </section>

  <section class="content-band">
    <div v-if="loading" class="empty-state">正在加载合同列表...</div>
    <div v-else-if="error" class="empty-state">
      <p class="form-error">{{ error }}</p>
      <button class="button button-secondary" type="button" @click="loadContracts">重新加载</button>
    </div>
    <div v-else-if="!contracts.length" class="empty-state">
      还没有合同，请先上传一份房屋租赁合同。
    </div>
    <template v-else>
      <div class="list-toolbar">
        <div><FileText /><strong>合同档案</strong><span>共 {{ contracts.length }} 份</span></div>
        <span>按上传时间展示</span>
      </div>
      <div class="contract-grid">
        <ContractCard v-for="contract in contracts" :key="contract.id" :contract="contract" />
      </div>
    </template>
  </section>
</template>
