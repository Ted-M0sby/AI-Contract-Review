<script setup>
import { computed } from 'vue'
import { RouterLink, RouterView, useRouter } from 'vue-router'
import { FileText, LayoutDashboard, LogOut, ShieldCheck, UploadCloud, UserRound } from '@lucide/vue'

const router = useRouter()
const email = computed(() => localStorage.getItem('email') || 'demo@qq.com')

function logout() {
  localStorage.removeItem('user_id')
  localStorage.removeItem('email')
  router.push('/login')
}
</script>

<template>
  <div class="app-shell">
    <aside class="sidebar">
      <RouterLink class="brand" to="/contracts">
        <span class="brand-mark"><ShieldCheck /></span>
        <span>
          <strong>智审合同</strong>
          <small>房屋租赁审查</small>
        </span>
      </RouterLink>

      <nav class="side-nav" aria-label="主导航">
        <span class="nav-caption">合同工作台</span>
        <RouterLink to="/contracts"><LayoutDashboard /><span>我的合同</span></RouterLink>
        <RouterLink to="/contracts/upload"><UploadCloud /><span>上传合同</span></RouterLink>
      </nav>

      <div class="sidebar-user">
        <div class="user-profile">
          <span class="user-avatar"><UserRound /></span>
          <span>
            <small>当前用户</small>
            <strong>{{ email }}</strong>
          </span>
        </div>
        <button class="button button-ghost full" type="button" @click="logout"><LogOut />退出登录</button>
      </div>
    </aside>

    <section class="workspace">
      <header class="topbar">
        <div class="topbar-context"><FileText /><span>房屋租赁合同审查工作台</span></div>
        <div class="service-state"><span></span>AI 审查服务</div>
      </header>
      <main class="main-panel">
        <RouterView />
      </main>
    </section>
  </div>
</template>
