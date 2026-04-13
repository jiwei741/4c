<script setup>
import { onMounted, watch } from 'vue'
import * as Cesium from 'cesium'

const props = defineProps({
  viewer: Object,
  gridData: {
    type: Array,
    default: () => [],
  },
  visible: {
    type: Boolean,
    default: true,
  },
})

let entities = []

function colorByScore(value, maxValue) {
  if (!Number.isFinite(Number(value))) {
    return Cesium.Color.fromCssColorString('rgba(239, 125, 87, 0.4)')
  }

  const safeMax = Math.max(Number(maxValue) || 0, 1e-6)
  const ratio = Math.min(1, Math.max(0, Number(value) / safeMax))

  if (ratio >= 0.85) return Cesium.Color.fromCssColorString('rgba(118, 219, 155, 0.56)')
  if (ratio >= 0.65) return Cesium.Color.fromCssColorString('rgba(204, 209, 102, 0.5)')
  if (ratio >= 0.4) return Cesium.Color.fromCssColorString('rgba(228, 178, 91, 0.46)')
  return Cesium.Color.fromCssColorString('rgba(239, 125, 87, 0.42)')
}

function clearEntities() {
  if (!props.viewer) return
  entities.forEach((entity) => props.viewer.entities.remove(entity))
  entities = []
}

function renderHeatmap(gridData) {
  if (!props.viewer || !Array.isArray(gridData) || gridData.length === 0) return

  clearEntities()

  const maxValue = Math.max(...gridData.map((item) => Number(item.gpp) || 0))

  gridData.forEach((point) => {
    const entity = props.viewer.entities.add({
      position: Cesium.Cartesian3.fromDegrees(Number(point.lon), Number(point.lat)),
      ellipse: {
        semiMinorAxis: 900,
        semiMajorAxis: 900,
        material: colorByScore(point.gpp, maxValue),
        outline: false,
        height: 0,
      },
      properties: {
        pointData: {
          nodeId: point.nodeId,
          lat: Number(point.lat),
          lon: Number(point.lon),
          gpp: Number(point.gpp),
          riskLevel: point.riskLevel || null,
          riskScore: point.riskScore ?? null,
          comparisonGap: point.comparisonGap ?? null,
        },
      },
      show: props.visible,
    })
    entities.push(entity)
  })

}

watch(
  () => props.gridData,
  (newData) => {
    renderHeatmap(newData)
  },
  { deep: true },
)

watch(
  () => props.visible,
  (value) => {
    entities.forEach((entity) => {
      entity.show = value
    })
  },
)

onMounted(() => {
  renderHeatmap(props.gridData)
})
</script>

<template>
  <div />
</template>
