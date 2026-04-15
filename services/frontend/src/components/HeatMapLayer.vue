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
    return Cesium.Color.fromCssColorString('rgba(239, 125, 87, 0.56)')
  }

  const safeMax = Math.max(Math.abs(Number(maxValue)) || 0, 1e-6)
  const ratio = Math.min(1, Math.max(0, Math.abs(Number(value)) / safeMax))

  if (ratio >= 0.85) return Cesium.Color.fromCssColorString('rgba(88, 217, 160, 0.72)')
  if (ratio >= 0.65) return Cesium.Color.fromCssColorString('rgba(204, 209, 102, 0.66)')
  if (ratio >= 0.4) return Cesium.Color.fromCssColorString('rgba(228, 178, 91, 0.60)')
  return Cesium.Color.fromCssColorString('rgba(239, 125, 87, 0.52)')
}

function clearEntities() {
  if (!props.viewer) return
  entities.forEach((entity) => props.viewer.entities.remove(entity))
  entities = []
  props.viewer.scene.requestRender()
}

function buildPointData(point) {
  return {
    nodeId: point.nodeId,
    lat: Number(point.lat),
    lon: Number(point.lon),
    gpp: Number(point.gpp),
    riskLevel: point.riskLevel || null,
    riskScore: point.riskScore ?? null,
    comparisonGap: point.comparisonGap ?? null,
    landcoverLabel: point.landcoverLabel || null,
    scenarioDelta: point.scenarioDelta ?? null,
  }
}

function buildCellBounds(point) {
  const lon = Number(point.lon)
  const lat = Number(point.lat)
  const fallbackPadding = 0.018

  return {
    west: Number.isFinite(Number(point.minLon)) ? Number(point.minLon) : lon - fallbackPadding,
    east: Number.isFinite(Number(point.maxLon)) ? Number(point.maxLon) : lon + fallbackPadding,
    south: Number.isFinite(Number(point.minLat)) ? Number(point.minLat) : lat - fallbackPadding,
    north: Number.isFinite(Number(point.maxLat)) ? Number(point.maxLat) : lat + fallbackPadding,
  }
}

function renderHeatmap(gridData) {
  if (!props.viewer || !Array.isArray(gridData) || gridData.length === 0) {
    clearEntities()
    return
  }

  clearEntities()

  const maxValue = Math.max(...gridData.map((item) => Math.abs(Number(item.gpp) || 0)), 1e-6)

  gridData.forEach((point) => {
    const pointData = buildPointData(point)
    const bounds = buildCellBounds(point)

    const rectangleEntity = props.viewer.entities.add({
      rectangle: {
        coordinates: Cesium.Rectangle.fromDegrees(
          bounds.west,
          bounds.south,
          bounds.east,
          bounds.north,
        ),
        material: colorByScore(point.gpp, maxValue),
        outline: true,
        outlineColor: Cesium.Color.fromCssColorString('rgba(255,255,255,0.28)'),
        outlineWidth: 1.6,
        height: 0,
      },      
      properties: {
        pointData,
      },
      show: props.visible,
    })
    entities.push(rectangleEntity)

  })
  props.viewer.scene.requestRender()
}

watch(
  () => props.viewer,
  () => {
    if (props.viewer) {
      renderHeatmap(props.gridData)
    }
  },
)

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
    props.viewer?.scene.requestRender()
  },
)

onMounted(() => {
  renderHeatmap(props.gridData)
})
</script>

<template>
  <div />
</template>
