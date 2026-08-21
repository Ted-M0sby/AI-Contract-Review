<script setup>
import { ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { ArrowRight, ShieldCheck } from '@lucide/vue'
import { login } from '../api/auth'

const route = useRoute()
const router = useRouter()

const form = ref({
  email: '',
  password: '',
})
const loading = ref(false)
const error = ref('')

async function handleLogin() {
  error.value = ''

  if (!form.value.email || !form.value.password) {
    error.value = '请填写 QQ 邮箱和密码'
    return
  }

  loading.value = true
  try {
    const response = await login(form.value)
    const userId = response.user_id ?? response.data?.user_id
    if (userId == null) {
      throw new Error('登录成功，但后端未返回 user_id')
    }

    const role = response.role || response.data?.role || 'user'
    const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : ''
    localStorage.setItem('user_id', String(userId))
    localStorage.setItem('email', response.email || response.data?.email || form.value.email)
    localStorage.setItem('role', role)
    await router.push(role === 'admin' ? (redirect.startsWith('/admin') ? redirect : '/admin') : (redirect && !redirect.startsWith('/admin') ? redirect : '/contracts'))
  } catch (requestError) {
    error.value = requestError.message || '登录失败，请稍后重试'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <main class="auth-page">
    <section class="auth-panel">
      <div class="auth-copy">
        <div class="auth-identity"><span><ShieldCheck /></span><strong>智审合同</strong></div>
        <span class="eyebrow">AI 合同审查</span>
        <p>面向房屋租赁合同的风险识别、条款核查与修改建议工作台。</p>
      </div>

      <form class="auth-card" @submit.prevent="handleLogin">
        <div class="form-heading">
          <span>欢迎回来</span>
          <h2>账号登录</h2>
        </div>
        <label class="field">
          <span>QQ 邮箱</span>
          <input v-model.trim="form.email" type="email" placeholder="example@qq.com" autocomplete="email" />
        </label>
        <label class="field">
          <span>密码</span>
          <input v-model="form.password" type="password" placeholder="请输入密码" autocomplete="current-password" />
        </label>
        <p v-if="error" class="form-error">{{ error }}</p>
        <button class="button button-primary full" type="submit" :disabled="loading">
          {{ loading ? '登录中...' : '登录' }}<ArrowRight v-if="!loading" />
        </button>
        <RouterLink class="text-link centered" to="/register">没有账号？去注册</RouterLink>
      </form>
    </section>
  </main>
</template>
