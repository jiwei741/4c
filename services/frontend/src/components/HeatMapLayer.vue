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
    return Cesium.Color.fromCssColorString('rgba(239, 125, 87, 0.38)')
  }

  const safeMax = Math.max(Math.abs(Number(maxValue)) || 0, 1e-6)
  const ratio = Math.min(1, Math.max(0, Math.abs(Number(value)) / safeMax))

  if (ratio >= 0.85) return Cesium.Color.fromCssColorString('rgba(88, 217, 160, 0.46)')
  if (ratio >= 0.65) return Cesium.Color.fromCssColorString('rgba(204, 209, 102, 0.40)')
  if (ratio >= 0.4) return Cesium.Color.fromCssColorString('rgba(228, 178, 91, 0.34)')
  return Cesium.Color.fromCssColorString('rgba(239, 125, 87, 0.28)')
}

function glowColorByScore(value, maxValue) {
  if (!Number.isFinite(Number(value))) {
    return Cesium.Color.fromCssColorString('rgba(239, 125, 87, 0.50)')
  }

  const safeMax = Math.max(Math.abs(Number(maxValue)) || 0, 1e-6)
  const ratio = Math.min(1, Math.max(0, Math.abs(Number(value)) / safeMax))

  if (ratio >= 0.85) return Cesium.Color.fromCssColorString('rgba(88, 217, 160, 0.58)')
  if (ratio >= 0.65) return Cesium.Color.fromCssColorString('rgba(204, 209, 102, 0.52)')
  if (ratio >= 0.4) return Cesium.Color.fromCssColorString('rgba(228, 178, 91, 0.48)')
  return Cesium.Color.fromCssColorString('rgba(239, 125, 87, 0.42)')
}

function labelColorByLandcover(label) {
  const mapping = {
    森林: Cesium.Color.fromCssColorString('#7ce8a8'),
    农田: Cesium.Color.fromCssColorString('#f0c16b'),
    水体: Cesium.Color.fromCssColorString('#6bc7f0'),
    城市: Cesium.Color.fromCssColorString('#ffae87'),
  }
  return mapping[label] || Cesium.Color.WHITE
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

function addLandcoverLabels(gridData) {
  const groups = new Map()

  gridData.forEach((point) => {
    const label = point.landcoverLabel
    if (!label) return

    if (!groups.has(label)) {
      groups.set(label, { sumLon: 0, sumLat: 0, count: 0 })
    }

    const group = groups.get(label)
    group.sumLon += Number(point.lon)
    group.sumLat += Number(point.lat)
    group.count += 1
  })

  ;['森林', '农田', '水体', '城市'].forEach((label) => {
    const group = groups.get(label)
    if (!group || group.count < 6) return

    const entity = props.viewer.entities.add({
      position: Cesium.Cartesian3.fromDegrees(group.sumLon / group.count, group.sumLat / group.count),
      label: {
        text: label,
        font: '600 15px "Microsoft YaHei", sans-serif',
        fillColor: labelColorByLandcover(label),
        outlineColor: Cesium.Color.fromCssColorString('#08131d'),
        outlineWidth: 3,
        style: Cesium.LabelStyle.FILL_AND_OUTLINE,
        showBackground: true,
        backgroundColor: Cesium.Color.fromCssColorString('rgba(5, 13, 22, 0.72)'),
        pixelOffset: new Cesium.Cartesian2(0, -8),
        disableDepthTestDistance: Number.POSITIVE_INFINITY,
      },
      show: props.visible,
    })
    entities.push(entity)
  })
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

    const rectangleEntity = props.viewer.entities.add({
      rectangle: {
        coordinates: Cesium.Rectangle.fromDegrees(
          Number(point.minLon ?? point.lon) - 0.002,
          Number(point.minLat ?? point.lat) - 0.002,
          Number(point.maxLon ?? point.lon) + 0.002,
          Number(point.maxLat ?? point.lat) + 0.002,
        ),
        material: colorByScore(point.gpp, maxValue),
        outline: true,
        outlineColor: Cesium.Color.fromCssColorString('rgba(255,255,255,0.08)'),
        outlineWidth: 1,
        height: 0,
      },
      properties: {
        pointData,
      },
      show: props.visible,
    })
    entities.push(rectangleEntity)

    const glowRadius = 320 + Math.min(1.3, Math.abs(Number(point.gpp) || 0) / maxValue + 0.25) * 360
    const glowEntity = props.viewer.entities.add({
      position: Cesium.Cartesian3.fromDegrees(Number(point.lon), Number(point.lat)),
      ellipse: {
        semiMinorAxis: glowRadius,
        semiMajorAxis: glowRadius,
        material: glowColorByScore(point.gpp, maxValue),
        outline: false,
        height: 0,
      },
      properties: {
        pointData,
      },
      show: props.visible,
    })
    entities.push(glowEntity)

    const markerEntity = props.viewer.entities.add({
      position: Cesium.Cartesian3.fromDegrees(Number(point.lon), Number(point.lat)),
      point: {
        pixelSize: 6,
        color: Cesium.Color.WHITE.withAlpha(0.8),
        outlineWidth: 1,
        outlineColor: Cesium.Color.fromCssColorString('#08131d').withAlpha(0.6),
        disableDepthTestDistance: Number.POSITIVE_INFINITY,
      },
      properties: {
        pointData,
      },
      show: props.visible,
    })
    entities.push(markerEntity)
  })

  addLandcoverLabels(gridData)
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
