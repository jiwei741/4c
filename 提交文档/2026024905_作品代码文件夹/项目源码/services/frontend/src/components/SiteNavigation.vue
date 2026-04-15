<template>
  <header class="site-nav" :class="{ compact }">
    <div class="site-nav__inner page-section">
      <RouterLink class="site-nav__brand" to="/">
        <span class="site-nav__mark">天穹智算</span>
        <span class="site-nav__sub">Regional Carbon Sink Intelligence</span>
      </RouterLink>
      <nav class="site-nav__links">
        <RouterLink to="/" class="site-nav__link">首页</RouterLink>
        <RouterLink to="/workspace" class="site-nav__link">工作台</RouterLink>
        <RouterLink to="/evidence" class="site-nav__link">模型结果</RouterLink>
      </nav>
      <RouterLink to="/workspace" class="site-nav__cta">进入平台</RouterLink>
    </div>
  </header>
</template>

<script setup>
import { RouterLink } from 'vue-router'

defineProps({
  compact: {
    type: Boolean,
    default: false,
  },
})
</script>

<style scoped>
.site-nav {
  position: sticky;
  top: 0;
  z-index: 50;
  padding: 18px 0;
  backdrop-filter: blur(14px);
  background: linear-gradient(180deg, rgba(4, 14, 23, 0.9), rgba(4, 14, 23, 0.54));
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.site-nav.compact {
  padding: 14px 0;
}

.site-nav__inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
}

.site-nav__brand {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.site-nav__mark {
  font-size: 20px;
  font-weight: 700;
  letter-spacing: 0.08em;
}

.site-nav__sub {
  color: var(--text-muted);
  font-size: 12px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.site-nav__links {
  display: flex;
  align-items: center;
  gap: 18px;
}

.site-nav__link {
  color: var(--text-secondary);
  min-height: 42px;
  padding: 0 16px;
  border-radius: 14px;
  border: 1px solid transparent;
  font-size: 15px;
  font-weight: 600;
  transition: background 0.2s ease, color 0.2s ease, border-color 0.2s ease, transform 0.2s ease, box-shadow 0.2s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.site-nav__link.router-link-active {
  color: var(--text-primary);
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(91, 198, 219, 0.18);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.06);
}

.site-nav__link:hover {
  transform: translateY(-1px);
  border-color: rgba(120, 220, 167, 0.18);
}

.site-nav__cta {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 50px;
  padding: 0 24px;
  border-radius: 18px;
  background: linear-gradient(135deg, var(--brand-sea), var(--brand-eco));
  color: white;
  font-weight: 700;
  font-size: 15px;
}

@media (max-width: 900px) {
  .site-nav__inner {
    flex-wrap: wrap;
  }

  .site-nav__links {
    width: 100%;
    justify-content: center;
    flex-wrap: wrap;
  }

  .site-nav__cta {
    width: 100%;
  }
}
</style>
