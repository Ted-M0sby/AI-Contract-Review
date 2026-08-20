<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeft, FileText, UploadCloud } from '@lucide/vue'
import { uploadContract } from '../api/contract'

const router = useRouter()
const form = ref({
  title: '',
  contract_type: 'housing_lease',
  file: null,
})
const fileName = ref('')
const error = ref('')
const loading = ref(false)

function handleFileChange(event) {
  const file = event.target.files?.[0]
  form.value.file = file || null
  fileName.value = file?.name || ''
}

async function handleUpload() {
  error.value = ''

  if (!form.value.title || !form.value.file) {
    error.value = '请填写合同名称并选择文件'
    return
  }

  const ext = form.value.file.name.split('.').pop()?.toLowerCase()
  if (!['pdf', 'docx', 'txt'].includes(ext)) {
    error.value = '当前仅支持 PDF、DOCX、TXT 文件'
    return
  }

  loading.value = true
  try {
    const response = await uploadContract(form.value)
    await router.push(`/contracts/${response.contract_id}`)
  } catch (requestError) {
    error.value = requestError.message || '合同上传失败，请稍后重试'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <section class="page-header">
    <div>
      <span class="eyebrow">合同上传</span>
      <h1>上传房屋租赁合同</h1>
      <p>第一版仅支持房屋租赁合同，文件类型限制为 PDF、DOCX、TXT。</p>
    </div>
  </section>

  <section class="form-surface">
    <form class="wide-form" @submit.prevent="handleUpload">
      <div class="form-section-title">
        <span><FileText /></span>
        <div><strong>合同文件信息</strong><small>填写名称并选择需要审查的合同</small></div>
      </div>
      <label class="field">
        <span>合同名称</span>
        <input v-model.trim="form.title" type="text" placeholder="例如：北京市住房租赁合同" />
      </label>

      <label class="field">
        <span>合同类型</span>
        <select v-model="form.contract_type">
          <option value="housing_lease">房屋租赁合同</option>
        </select>
      </label>

      <label class="upload-box">
        <input type="file" accept=".pdf,.docx,.txt" @change="handleFileChange" />
        <span class="upload-icon"><UploadCloud /></span>
        <strong>{{ fileName || '选择合同文件' }}</strong>
        <span>支持 PDF、DOCX、TXT</span>
      </label>

      <p v-if="error" class="form-error">{{ error }}</p>

      <div class="form-actions">
        <button class="button button-secondary" type="button" @click="router.push('/contracts')"><ArrowLeft />返回列表</button>
        <button class="button button-primary" type="submit" :disabled="loading">
          <UploadCloud v-if="!loading" />{{ loading ? '上传中...' : '上传合同' }}
        </button>
      </div>
    </form>
  </section>
</template>
