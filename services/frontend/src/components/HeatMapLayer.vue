<script setup>
import { onMounted, watch } from 'vue'
import * as Cesium from 'cesium'

const props = defineProps({
  viewer: Object,
  gridData: Array,
  visible: {
    type: Boolean,
    default: true
  }
})

let entities = []
let clickHandler = null

// GPP值映射颜色：深红(低) → 橙 → 黄 → 亮绿(高)
function gppToColor(gpp, maxGpp) {
  // 安全检查
  if (!gpp || !maxGpp || maxGpp <= 0) {
    // 返回默认颜色（红色）
    return Cesium.Color.fromCssColorString('hsla(0, 80%, 40%, 0.3)')
  }

  const ratio = Math.min(1, Math.max(0, gpp / maxGpp))

  // 色相从红色(0)渐变到浅绿色(90)
  const hue = ratio * 90

  // 饱和度从高到低，让高值颜色更淡雅
  const saturation = 80 - ratio * 20

  // 亮度从暗到亮
  const lightness = 40 + ratio * 20

  return Cesium.Color.fromCssColorString(
    `hsla(${hue}, ${saturation}%, ${lightness}%, 0.3)`
  )
}


function renderHeatmap(gridData) {
  if (!props.viewer || !gridData || gridData.length === 0) return

  // 清除旧图形
  entities.forEach((e) => props.viewer.entities.remove(e))
  entities = []

  const maxGpp = Math.max(...gridData.map((d) => d.gpp))

  gridData.forEach((point) => {
    const entity = props.viewer.entities.add({
      position: Cesium.Cartesian3.fromDegrees(point.lon, point.lat),
      ellipse: {
        semiMinorAxis: 1200,
        semiMajorAxis: 1200,
        material: gppToColor(point.gpp, maxGpp),
        outline: false,
        height: 0,
      },
      // 添加这一行：把数据存到属性里
      properties: {
        pointData: point
      }
    })
    entities.push(entity)
  })
  // 清除旧的点击事件
  if (clickHandler) {
    clickHandler.destroy()
  }

  // 添加新的点击事件
  clickHandler = new Cesium.ScreenSpaceEventHandler(props.viewer.scene.canvas)
  clickHandler.setInputAction((movement) => {
    const pickedObject = props.viewer.scene.pick(movement.position)
    if (pickedObject && pickedObject.id && pickedObject.id.properties) {
      const data = pickedObject.id.properties.pointData.getValue()
      if (data) {
        // 触发事件，通知详情面板
        window.dispatchEvent(new CustomEvent('point-selected', {
          detail: data
        }))
      }
    }
  }, Cesium.ScreenSpaceEventType.LEFT_CLICK)
}

watch(
  () => props.gridData,
  (newData) => renderHeatmap(newData)
)

// 监听图层显示/隐藏状态
watch(
  () => props.visible,
  (isVisible) => {
    entities.forEach(entity => {
      if (entity) {
        entity.show = isVisible
      }
    })
  }
)

onMounted(() => {
  if (props.gridData) {
    renderHeatmap(props.gridData)
  }
})
</script>

<template>
  <div />
</template>
