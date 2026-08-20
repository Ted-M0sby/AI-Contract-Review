<script setup>
import { onBeforeUnmount, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { ArrowRight, ShieldCheck } from '@lucide/vue'
import { register, sendCode } from '../api/auth'

const router = useRouter()
const form = ref({
  email: '',
  code: '',
  password: '',
  confirmPassword: '',
})
const countdown = ref(0)
const message = ref('')
const error = ref('')
const loading = ref(false)
const sendingCode = ref(false)
let timer = null

async function handleSendCode() {
  error.value = ''
  message.value = ''

  if (!form.value.email) {
    error.value = '请先填写 QQ 邮箱'
    return
  }

  sendingCode.value = true
  try {
    const response = await sendCode({ email: form.value.email })
    message.value = response.message || '验证码已发送'
    countdown.value = 60
    timer = window.setInterval(() => {
      countdown.value -= 1
      if (countdown.value <= 0) {
        window.clearInterval(timer)
        timer = null
      }
    }, 1000)
  } catch (requestError) {
    error.value = requestError.message || '验证码发送失败，请稍后重试'
  } finally {
    sendingCode.value = false
  }
}

async function handleRegister() {
  error.value = ''
  message.value = ''

  if (!form.value.email || !form.value.code || !form.value.password || !form.value.confirmPassword) {
    error.value = '请完整填写注册信息'
    return
  }

  if (form.value.password !== form.value.confirmPassword) {
    error.value = '两次输入的密码不一致'
    return
  }

  loading.value = true
  try {
    const response = await register(form.value)
    message.value = response.message || '注册成功，即将返回登录页'
    window.setTimeout(() => router.push('/login'), 700)
  } catch (requestError) {
    error.value = requestError.message || '注册失败，请检查验证码和注册信息'
  } finally {
    loading.value = false
  }
}

onBeforeUnmount(() => {
  if (timer) {
    window.clearInterval(timer)
  }
})
</script>

<template>
  <main class="auth-page">
    <section class="auth-panel">
      <div class="auth-copy">
        <div class="auth-identity"><span><ShieldCheck /></span><strong>智审合同</strong></div>
        <span class="eyebrow">创建 Demo 账号</span>
        <h1>用 QQ 邮箱完成账号注册</h1>
        <p>验证码由真实后端发送，注册成功后即可登录合同工作台。</p>
      </div>

      <form class="auth-card" @submit.prevent="handleRegister">
        <div class="form-heading">
          <span>创建工作台账号</span>
          <h2>注册</h2>
        </div>
        <label class="field">
          <span>QQ 邮箱</span>
          <input v-model.trim="form.email" type="email" placeholder="example@qq.com" autocomplete="email" />
        </label>
        <div class="field code-field">
          <label>
            <span>验证码</span>
            <input v-model.trim="form.code" type="text" placeholder="请输入验证码" />
          </label>
          <button class="button button-secondary" type="button" :disabled="countdown > 0 || sendingCode" @click="handleSendCode">
            {{ sendingCode ? '发送中...' : countdown > 0 ? `重新发送(${countdown}s)` : '发送验证码' }}
          </button>
        </div>
        <label class="field">
          <span>密码</span>
          <input v-model="form.password" type="password" placeholder="请输入密码" autocomplete="new-password" />
        </label>
        <label class="field">
          <span>确认密码</span>
          <input v-model="form.confirmPassword" type="password" placeholder="请再次输入密码" autocomplete="new-password" />
        </label>
        <p v-if="error" class="form-error">{{ error }}</p>
        <p v-if="message" class="form-message">{{ message }}</p>
        <button class="button button-primary full" type="submit" :disabled="loading">
          {{ loading ? '注册中...' : '注册' }}<ArrowRight v-if="!loading" />
        </button>
        <RouterLink class="text-link centered" to="/login">返回登录</RouterLink>
      </form>
    </section>
  </main>
</template>
