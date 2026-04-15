<template>
  <section class="faq-assistant glass-card">
    <div class="faq-assistant__head">
      <div class="faq-assistant__identity">
        <div class="faq-assistant__avatar">
          <span class="faq-assistant__avatar-core"></span>
        </div>
        <div class="faq-assistant__identity-copy">
          <span class="brand-chip">平台问答助手</span>
          <small>帮助用户理解平台功能、入口与基本操作</small>
        </div>
      </div>

      <div class="faq-assistant__signal">
        <span class="faq-assistant__dot"></span>
        <span>{{ modeLabel }}</span>
      </div>
    </div>

    <div class="faq-assistant__quick">
      <button
        v-for="question in starterQuestions"
        :key="question"
        class="faq-assistant__quick-chip"
        type="button"
        @click="submitQuestion(question)"
      >
        {{ question }}
      </button>
    </div>

    <div ref="timelineRef" class="faq-assistant__timeline">
      <article
        v-for="message in messages"
        :key="message.id"
        class="faq-message"
        :class="`faq-message--${message.role}`"
      >
        <span class="faq-message__role">{{ message.role === 'assistant' ? '助手' : '你' }}</span>
        <div
          v-if="message.role === 'assistant'"
          class="faq-message__content"
          v-html="renderAssistantContent(message.content)"
        ></div>
        <p v-else class="faq-message__content">{{ message.content }}</p>

        <div v-if="message.actions?.length" class="faq-message__actions">
          <button
            v-for="action in message.actions"
            :key="`${message.id}-${action.label}`"
            class="secondary-btn faq-message__action-btn"
            type="button"
            @click="goToAction(action)"
          >
            {{ action.label }}
          </button>
        </div>
      </article>
    </div>

    <form class="faq-assistant__composer" @submit.prevent="submitQuestion()">
      <input
        v-model="draft"
        class="faq-assistant__input"
        type="text"
        maxlength="120"
        placeholder="例如：我该如何发起一次情景推演？"
      />
      <button class="primary-btn faq-assistant__send" type="submit" :disabled="sending || !draft.trim()">
        {{ sending ? '发送中...' : '发送' }}
      </button>
    </form>
  </section>
</template>

<script setup>
import { computed, nextTick, ref } from 'vue'
import { useRouter } from 'vue-router'

import { askFaqAssistant } from '../api/platform.js'

const router = useRouter()

const starterQuestions = ref([
  '工作台里怎么查看历史季度？',
  '怎样发起一次情景推演？',
  '模型结果页主要看什么？',
  '我应该先进入哪一个入口？',
])

const messages = ref([
  {
    id: 'welcome',
    role: 'assistant',
    content:
      '我可以帮助你快速了解工作台、季度切换、情景推演、模型结果和平台入口。你也可以直接点下方常见问题开始。',
    actions: [],
  },
])

const mode = ref('guidance')
const sending = ref(false)
const draft = ref('')
const timelineRef = ref(null)

const modeLabel = computed(() => (mode.value === 'llm' ? '智能问答已启用' : '平台功能快速指引'))

function escapeHtml(value) {
  return value
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;')
}

function renderAssistantContent(content) {
  let html = escapeHtml(content || '')

  html = html.replace(/\*\*(.+?)\*\*/gs, '<strong>$1</strong>')
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>')
  html = html.replace(/\n/g, '<br />')

  return html
}

function scrollTimelineToBottom() {
  if (!timelineRef.value) return
  timelineRef.value.scrollTop = timelineRef.value.scrollHeight
}

function buildHistoryPayload() {
  return messages.value
    .filter((item) => item.role === 'user' || item.role === 'assistant')
    .slice(-6)
    .map((item) => ({
      role: item.role,
      content: item.content,
    }))
}

async function submitQuestion(predefinedQuestion = '') {
  const question = (predefinedQuestion || draft.value).trim()
  if (!question || sending.value) return
  const history = buildHistoryPayload()

  messages.value.push({
    id: `user-${Date.now()}`,
    role: 'user',
    content: question,
    actions: [],
  })
  draft.value = ''
  sending.value = true
  await nextTick()
  scrollTimelineToBottom()

  try {
    const payload = await askFaqAssistant(question, history)
    mode.value = payload.mode || 'guidance'
    starterQuestions.value = payload.starter_questions?.length ? payload.starter_questions : starterQuestions.value
    messages.value.push({
      id: `assistant-${Date.now()}`,
      role: 'assistant',
      content: payload.message || '我已经收到你的问题，你可以继续问我平台功能和入口使用。',
      actions: payload.suggested_actions || [],
    })
  } catch (error) {
    console.error('Failed to get FAQ assistant reply:', error)
    mode.value = 'guidance'
    messages.value.push({
      id: `assistant-${Date.now()}`,
      role: 'assistant',
      content:
        '我先按平台内置指引回答：如果你要看地图和季度变化，请进入工作台；如果你要看模型表现，请打开模型结果页；如果你要做区域干预对比，请进入工作台后启动情景推演。',
      actions: [
        { label: '进入工作台', route: '/workspace' },
        { label: '查看模型结果', route: '/evidence' },
        { label: '查看使用引导', route: '/guide' },
      ],
    })
  } finally {
    sending.value = false
    await nextTick()
    scrollTimelineToBottom()
  }
}

function goToAction(action) {
  router.push({
    path: action.route || '/',
    query: action.query || undefined,
  })
}
</script>

<style scoped>
.faq-assistant {
  display: grid;
  grid-template-rows: auto auto minmax(170px, 1fr) auto;
  gap: 14px;
  padding: 20px 22px;
  width: min(100%, 100%);
  min-height: 400px;
  align-content: start;
  border-radius: 30px;
  background:
    radial-gradient(circle at 10% 0%, rgba(95, 208, 209, 0.1), transparent 24%),
    radial-gradient(circle at 100% 0%, rgba(79, 191, 127, 0.14), transparent 26%),
    linear-gradient(180deg, rgba(12, 31, 47, 0.92), rgba(7, 20, 33, 0.97));
}

.faq-assistant::after {
  content: '';
  position: absolute;
  inset: 0;
  pointer-events: none;
  border-radius: inherit;
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.07), transparent 18%),
    linear-gradient(315deg, rgba(95, 208, 209, 0.09), transparent 26%);
  opacity: 0.8;
}

.faq-assistant__head {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 12px;
  align-items: center;
  position: relative;
  z-index: 1;
}

.faq-assistant__identity {
  display: flex;
  align-items: center;
  gap: 14px;
  min-width: 0;
}

.faq-assistant__avatar {
  position: relative;
  width: 52px;
  height: 52px;
  border-radius: 20px;
  flex: 0 0 auto;
  background: linear-gradient(145deg, rgba(13, 42, 62, 0.96), rgba(7, 22, 35, 0.9));
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.06),
    0 12px 24px rgba(0, 0, 0, 0.22);
}

.faq-assistant__avatar-core {
  position: absolute;
  inset: 12px;
  border-radius: 16px;
  background:
    radial-gradient(circle at 35% 35%, rgba(255, 255, 255, 0.3), transparent 26%),
    linear-gradient(135deg, var(--brand-sea), var(--brand-eco));
  box-shadow:
    0 0 20px rgba(95, 208, 209, 0.28),
    0 0 34px rgba(79, 191, 127, 0.18);
}

.faq-assistant__identity-copy {
  display: grid;
  gap: 6px;
}

.faq-assistant__identity-copy small {
  color: var(--text-muted);
  line-height: 1.55;
}

.faq-assistant__signal {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border-radius: 999px;
  background: rgba(5, 18, 30, 0.58);
  border: 1px solid rgba(95, 208, 209, 0.14);
  color: var(--text-secondary);
  font-size: 12px;
  white-space: nowrap;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04);
}

.faq-assistant__dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--brand-sea), var(--brand-eco));
  box-shadow: 0 0 16px rgba(95, 208, 209, 0.48);
}

.faq-assistant__quick {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  position: relative;
  z-index: 1;
  min-width: 0;
}

.faq-assistant__quick-chip {
  padding: 9px 14px;
  border-radius: 16px;
  border: 1px solid rgba(95, 208, 209, 0.12);
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.05), rgba(255, 255, 255, 0.02)),
    rgba(255, 255, 255, 0.02);
  color: var(--text-secondary);
  cursor: pointer;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04);
  transition: transform 0.2s ease, border-color 0.2s ease, color 0.2s ease, background 0.2s ease;
}

.faq-assistant__quick-chip:hover {
  transform: translateY(-1px);
  border-color: rgba(95, 208, 209, 0.26);
  background: linear-gradient(180deg, rgba(31, 143, 188, 0.14), rgba(79, 191, 127, 0.08));
  color: var(--text-primary);
}

.faq-assistant__timeline {
  display: grid;
  gap: 8px;
  min-height: 180px;
  max-height: 250px;
  overflow: auto;
  padding-right: 8px;
  position: relative;
  z-index: 1;
  scrollbar-width: thin;
  scrollbar-color: rgba(95, 208, 209, 0.72) rgba(6, 19, 31, 0.64);
}

.faq-assistant__composer,
.faq-assistant__quick,
.faq-assistant__timeline,
.faq-assistant__head {
  width: 100%;
}

.faq-assistant__timeline,
.faq-assistant__composer {
  max-width: 100%;
}

.faq-assistant__timeline::-webkit-scrollbar {
  width: 12px;
}

.faq-assistant__timeline::-webkit-scrollbar-track {
  border-radius: 999px;
  background: linear-gradient(180deg, rgba(6, 19, 31, 0.78), rgba(10, 26, 40, 0.64));
  border: 1px solid rgba(255, 255, 255, 0.04);
}

.faq-assistant__timeline::-webkit-scrollbar-thumb {
  border-radius: 999px;
  background: linear-gradient(180deg, rgba(31, 143, 188, 0.92), rgba(79, 191, 127, 0.88));
  border: 2px solid rgba(6, 19, 31, 0.8);
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.06);
}

.faq-message {
  display: grid;
  gap: 8px;
  padding: 12px 14px 12px;
  border-radius: 22px;
  border: 1px solid rgba(255, 255, 255, 0.07);
  position: relative;
}

.faq-message--assistant {
  background:
    radial-gradient(circle at 0% 0%, rgba(31, 143, 188, 0.14), transparent 28%),
    rgba(5, 17, 28, 0.76);
  border-top-left-radius: 10px;
}

.faq-message--user {
  background:
    radial-gradient(circle at 100% 0%, rgba(79, 191, 127, 0.12), transparent 26%),
    rgba(16, 43, 63, 0.64);
  border-top-right-radius: 10px;
}

.faq-message__role {
  color: var(--text-muted);
  font-size: 12px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.faq-message__content {
  color: var(--text-primary);
  line-height: 1.75;
  white-space: pre-wrap;
}

.faq-message__content :deep(strong) {
  color: #f3fbff;
  font-weight: 700;
}

.faq-message__content :deep(code) {
  display: inline-block;
  padding: 2px 8px;
  margin: 0 2px;
  border-radius: 999px;
  background: rgba(8, 26, 40, 0.92);
  border: 1px solid rgba(95, 208, 209, 0.14);
  color: #8ddcf4;
  font-family: 'JetBrains Mono', 'Cascadia Code', Consolas, monospace;
  font-size: 0.92em;
}

.faq-message__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.faq-message__action-btn {
  min-height: 42px;
  padding: 0 16px;
  border-radius: 14px;
}

.faq-assistant__composer {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 8px;
  margin-top: auto;
  position: relative;
  z-index: 1;
}

.faq-assistant__input {
  width: 100%;
  min-height: 48px;
  padding: 0 16px;
  border-radius: 18px;
  border: 1px solid rgba(95, 208, 209, 0.14);
  background:
    linear-gradient(180deg, rgba(4, 15, 25, 0.92), rgba(7, 20, 32, 0.86)),
    rgba(4, 15, 25, 0.8);
  color: var(--text-primary);
  outline: none;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04);
}

.faq-assistant__input:focus {
  border-color: rgba(95, 208, 209, 0.32);
  box-shadow:
    0 0 0 3px rgba(31, 143, 188, 0.12),
    0 10px 22px rgba(0, 0, 0, 0.18);
}

.faq-assistant__send {
  min-width: 96px;
}
</style>
