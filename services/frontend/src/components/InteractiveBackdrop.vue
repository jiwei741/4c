<template>
  <div
    ref="root"
    class="interactive-backdrop"
    :class="[`interactive-backdrop--${variant}`]"
    aria-hidden="true"
  >
    <div class="interactive-backdrop__grid"></div>
    <div class="interactive-backdrop__mesh interactive-backdrop__mesh--one"></div>
    <div class="interactive-backdrop__mesh interactive-backdrop__mesh--two"></div>
    <div class="interactive-backdrop__mesh interactive-backdrop__mesh--three"></div>
    <div class="interactive-backdrop__orbit interactive-backdrop__orbit--one"></div>
    <div class="interactive-backdrop__orbit interactive-backdrop__orbit--two"></div>
    <div class="interactive-backdrop__beam interactive-backdrop__beam--one"></div>
    <div class="interactive-backdrop__beam interactive-backdrop__beam--two"></div>
    <div class="interactive-backdrop__halo interactive-backdrop__halo--primary"></div>
    <div class="interactive-backdrop__halo interactive-backdrop__halo--secondary"></div>
    <div class="interactive-backdrop__tracker interactive-backdrop__tracker--one"></div>
    <div class="interactive-backdrop__tracker interactive-backdrop__tracker--two"></div>
    <div class="interactive-backdrop__tracker interactive-backdrop__tracker--three"></div>
    <div class="interactive-backdrop__grain"></div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, ref } from 'vue'

defineProps({
  variant: {
    type: String,
    default: 'home',
  },
})

const root = ref(null)

let animationFrame = 0
const pointer = {
  targetX: 0.52,
  targetY: 0.34,
  x: 0.52,
  y: 0.34,
}

function writePointer() {
  if (!root.value) return
  root.value.style.setProperty('--pointer-x', `${(pointer.x * 100).toFixed(2)}%`)
  root.value.style.setProperty('--pointer-y', `${(pointer.y * 100).toFixed(2)}%`)
}

function animatePointer() {
  pointer.x += (pointer.targetX - pointer.x) * 0.08
  pointer.y += (pointer.targetY - pointer.y) * 0.08
  writePointer()
  animationFrame = window.requestAnimationFrame(animatePointer)
}

function handlePointerMove(event) {
  const width = window.innerWidth || 1
  const height = window.innerHeight || 1
  pointer.targetX = Math.min(1, Math.max(0, event.clientX / width))
  pointer.targetY = Math.min(1, Math.max(0, event.clientY / height))
}

function handlePointerLeave() {
  pointer.targetX = 0.52
  pointer.targetY = 0.34
}

onMounted(() => {
  writePointer()
  window.addEventListener('pointermove', handlePointerMove, { passive: true })
  window.addEventListener('pointerleave', handlePointerLeave, { passive: true })
  animationFrame = window.requestAnimationFrame(animatePointer)
})

onUnmounted(() => {
  window.removeEventListener('pointermove', handlePointerMove)
  window.removeEventListener('pointerleave', handlePointerLeave)
  if (animationFrame) {
    window.cancelAnimationFrame(animationFrame)
  }
})
</script>

<style scoped>
.interactive-backdrop {
  --pointer-x: 52%;
  --pointer-y: 34%;
  position: fixed;
  inset: 0;
  overflow: clip;
  pointer-events: none;
  z-index: 0;
}

.interactive-backdrop__grid,
.interactive-backdrop__mesh,
.interactive-backdrop__halo,
.interactive-backdrop__tracker,
.interactive-backdrop__grain,
.interactive-backdrop__orbit,
.interactive-backdrop__beam {
  position: absolute;
  inset: 0;
}

.interactive-backdrop__grid {
  background:
    linear-gradient(rgba(255, 255, 255, 0.018) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.018) 1px, transparent 1px);
  background-size: 52px 52px;
  mask-image: linear-gradient(180deg, rgba(0, 0, 0, 0.78), rgba(0, 0, 0, 0.12));
  opacity: 0.58;
}

.interactive-backdrop__mesh {
  filter: blur(92px);
  opacity: 0.64;
  transform-origin: center;
}

.interactive-backdrop__mesh--one {
  inset: -8% auto auto -10%;
  width: 42vw;
  height: 42vw;
  background: radial-gradient(circle, rgba(42, 164, 214, 0.42), transparent 66%);
  animation: driftOne 16s ease-in-out infinite alternate;
}

.interactive-backdrop__mesh--two {
  inset: 14% -10% auto auto;
  width: 36vw;
  height: 36vw;
  background: radial-gradient(circle, rgba(79, 191, 127, 0.34), transparent 64%);
  animation: driftTwo 18s ease-in-out infinite alternate;
}

.interactive-backdrop__mesh--three {
  inset: auto auto -16% 22%;
  width: 34vw;
  height: 34vw;
  background: radial-gradient(circle, rgba(228, 178, 91, 0.18), transparent 62%);
  animation: driftThree 20s ease-in-out infinite alternate;
}

.interactive-backdrop__orbit {
  inset: auto;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.06);
  filter: blur(0.2px);
}

.interactive-backdrop__orbit--one {
  width: 520px;
  height: 520px;
  left: -110px;
  top: 14vh;
  transform: rotate(18deg);
  animation: spinSlow 28s linear infinite;
}

.interactive-backdrop__orbit--two {
  width: 680px;
  height: 680px;
  right: -180px;
  top: -60px;
  transform: rotate(-12deg);
  opacity: 0.58;
  animation: spinSlowReverse 34s linear infinite;
}

.interactive-backdrop__beam {
  inset: auto;
  border-radius: 999px;
  filter: blur(10px);
  opacity: 0.55;
}

.interactive-backdrop__beam--one {
  width: 28vw;
  height: 2px;
  left: 14vw;
  top: calc(var(--pointer-y) - 14vh);
  background: linear-gradient(90deg, transparent, rgba(31, 143, 188, 0.42), transparent);
}

.interactive-backdrop__beam--two {
  width: 24vw;
  height: 2px;
  right: 10vw;
  top: calc(var(--pointer-y) + 10vh);
  background: linear-gradient(90deg, transparent, rgba(79, 191, 127, 0.38), transparent);
}

.interactive-backdrop__halo {
  inset: auto;
  width: 420px;
  height: 420px;
  border-radius: 50%;
  filter: blur(42px);
  opacity: 0.5;
  transform: translate3d(calc(var(--pointer-x) - 210px), calc(var(--pointer-y) - 210px), 0);
}

.interactive-backdrop__halo--primary {
  background: radial-gradient(circle, rgba(79, 191, 127, 0.22), rgba(79, 191, 127, 0));
}

.interactive-backdrop__halo--secondary {
  width: 240px;
  height: 240px;
  transform: translate3d(calc(var(--pointer-x) - 120px), calc(var(--pointer-y) - 120px), 0);
  background: radial-gradient(circle, rgba(31, 143, 188, 0.26), rgba(31, 143, 188, 0));
  filter: blur(24px);
  opacity: 0.7;
}

.interactive-backdrop__tracker {
  inset: auto;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.06);
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.08), rgba(255, 255, 255, 0.02));
  box-shadow: 0 18px 38px rgba(0, 0, 0, 0.16);
  backdrop-filter: blur(18px);
}

.interactive-backdrop__tracker--one {
  width: 132px;
  height: 132px;
  transform: translate3d(calc(var(--pointer-x) * 0.18 + 6vw), calc(var(--pointer-y) * 0.12 + 10vh), 0);
}

.interactive-backdrop__tracker--two {
  width: 88px;
  height: 88px;
  transform: translate3d(calc(var(--pointer-x) * -0.12 + 72vw), calc(var(--pointer-y) * 0.08 + 22vh), 0);
}

.interactive-backdrop__tracker--three {
  width: 96px;
  height: 96px;
  transform: translate3d(calc(var(--pointer-x) * 0.1 + 18vw), calc(var(--pointer-y) * -0.08 + 68vh), 0);
}

.interactive-backdrop__grain {
  opacity: 0.22;
  mix-blend-mode: soft-light;
  background-image:
    radial-gradient(circle at 20% 20%, rgba(255, 255, 255, 0.08) 0 1px, transparent 1px),
    radial-gradient(circle at 80% 40%, rgba(255, 255, 255, 0.08) 0 1px, transparent 1px),
    radial-gradient(circle at 40% 80%, rgba(255, 255, 255, 0.08) 0 1px, transparent 1px);
  background-size: 180px 180px, 220px 220px, 260px 260px;
}

.interactive-backdrop--evidence .interactive-backdrop__mesh--three {
  opacity: 0.38;
}

@keyframes driftOne {
  from { transform: translate3d(0, 0, 0) scale(1); }
  to { transform: translate3d(4vw, 3vh, 0) scale(1.08); }
}

@keyframes driftTwo {
  from { transform: translate3d(0, 0, 0) scale(1); }
  to { transform: translate3d(-5vw, 4vh, 0) scale(1.12); }
}

@keyframes driftThree {
  from { transform: translate3d(0, 0, 0) scale(1); }
  to { transform: translate3d(3vw, -5vh, 0) scale(1.1); }
}

@keyframes spinSlow {
  from { transform: rotate(18deg); }
  to { transform: rotate(378deg); }
}

@keyframes spinSlowReverse {
  from { transform: rotate(-12deg); }
  to { transform: rotate(-372deg); }
}
</style>
