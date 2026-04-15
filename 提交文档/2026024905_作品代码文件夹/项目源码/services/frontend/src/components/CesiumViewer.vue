<script setup>
import { nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import * as Cesium from 'cesium'

import HeatMapLayer from './HeatMapLayer.vue'
import { getPredictionAnalytics } from '../api/platform.js'
import { generateMockCarbonData } from '../mock/carbonData.js'

const props = defineProps({
  horizon: {
    type: String,
    default: '',
  },
  scenarioResult: {
    type: Object,
    default: null,
  },
})

const cesiumContainer = ref(null)
const viewerReady = ref(null)
const gridData = ref([])
const layerVisible = ref(true)
const baselineGridData = ref([])

let viewer = null
let drawHandler = null
let clickHandler = null
let resetViewListener = null
let toggleLayerListener = null
let enterDrawingModeListener = null
let exitDrawingModeListener = null
let isDrawingMode = false
let drawingEntity = null
let drawingOutlineEntity = null
let hintEntity = null
let startPosition = null
let tempRectangle = null

const defaultHorizon = '2025-Q1'
const gaodeBaseMapUrl = 'https://webrd02.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}'

function addBaseImageryLayer() {
  if (!viewer) return

  viewer.imageryLayers.removeAll()

  try {
    viewer.imageryLayers.addImageryProvider(
      new Cesium.UrlTemplateImageryProvider({
        url: gaodeBaseMapUrl,
        minimumLevel: 3,
        maximumLevel: 18,
      }),
    )
  } catch (error) {
    console.warn('Amap base layer unavailable, falling back to OpenStreetMap:', error)
    viewer.imageryLayers.addImageryProvider(
      new Cesium.OpenStreetMapImageryProvider({ url: 'https://tile.openstreetmap.org/' }),
    )
  }
}

async function loadPredictionLayer(horizon) {
  const targetHorizon = horizon || props.horizon || defaultHorizon

  try {
    const payload = await getPredictionAnalytics({ horizon: targetHorizon })
    const items = Array.isArray(payload.items) ? payload.items : []

    if (items.length === 0) {
      throw new Error('Prediction layer returned no items.')
    }

    baselineGridData.value = items.map((item) => ({
      nodeId: item.node_id,
      lat: Number(item.latitude),
      lon: Number(item.longitude),
      minLat: Number(item.min_lat),
      maxLat: Number(item.max_lat),
      minLon: Number(item.min_lon),
      maxLon: Number(item.max_lon),
      gpp: Number(item.value),
      riskLevel: item.risk_level || null,
      riskScore: item.risk_score ?? null,
      comparisonGap: item.comparison_gap ?? null,
      landcoverLabel: item.dominant_landcover || null,
      landcoverRatios: item.landcover_ratios || {},
      vegetationAreaRatio: item.vegetation_area_ratio ?? null,
      ndviMean: item.ndvi_mean ?? null,
    }))
    applyActiveLayer()
  } catch (error) {
    console.error('Failed to load real prediction layer, using mock data:', error)
    baselineGridData.value = generateMockCarbonData(targetHorizon).grid
    applyActiveLayer()
  }
}

function buildScenarioGrid() {
  const result = props.scenarioResult
  if (!result?.scenarioData?.grid?.length) {
    return null
  }

  const targetHorizon = result.forecastHorizon || result.scenarioData.date
  const currentHorizon = props.horizon || defaultHorizon
  if (targetHorizon && currentHorizon && targetHorizon !== currentHorizon) {
    return null
  }

  const changedNodeIds = new Set((result.backendSummary?.changed_nodes || []).map((item) => String(item)))
  const baselineMap = new Map(baselineGridData.value.map((item) => [String(item.nodeId), item]))

  return result.scenarioData.grid.map((point) => {
    const baseline = baselineMap.get(String(point.nodeId))
    return {
      nodeId: String(point.nodeId),
      lat: Number(point.lat),
      lon: Number(point.lon),
      minLat: Number(point.minLat ?? baseline?.minLat),
      maxLat: Number(point.maxLat ?? baseline?.maxLat),
      minLon: Number(point.minLon ?? baseline?.minLon),
      maxLon: Number(point.maxLon ?? baseline?.maxLon),
      gpp: Number(point.gpp),
      riskLevel: baseline?.riskLevel || null,
      riskScore: baseline?.riskScore ?? null,
      comparisonGap: baseline?.comparisonGap ?? null,
      landcoverLabel: baseline?.landcoverLabel || null,
      landcoverRatios: baseline?.landcoverRatios || {},
      vegetationAreaRatio: baseline?.vegetationAreaRatio ?? null,
      ndviMean: baseline?.ndviMean ?? null,
      scenarioDelta: Number(point.gpp) - Number(baseline?.gpp || 0),
      isScenarioChanged: changedNodeIds.has(String(point.nodeId)),
    }
  })
}

function applyActiveLayer() {
  const scenarioGrid = buildScenarioGrid()
  gridData.value = scenarioGrid || baselineGridData.value
}

function showDrawingHint() {
  if (!viewer) return
  removeDrawingHint()
  hintEntity = viewer.entities.add({
    position: Cesium.Cartesian3.fromDegrees(118.8, 32.02),
    label: {
      text: '拖拽鼠标框选需要进行情景干预的区域',
      font: '15px sans-serif',
      fillColor: Cesium.Color.WHITE,
      outlineColor: Cesium.Color.BLACK,
      outlineWidth: 2,
      style: Cesium.LabelStyle.FILL_AND_OUTLINE,
      pixelOffset: new Cesium.Cartesian2(0, -52),
      showBackground: true,
      backgroundColor: new Cesium.Color(0.05, 0.1, 0.16, 0.9),
    },
  })
}

function removeDrawingHint() {
  if (viewer && hintEntity) {
    viewer.entities.remove(hintEntity)
  }
  hintEntity = null
  viewer?.scene.requestRender()
}

function toRectangleCoordinates(rectangle) {
  return Cesium.Rectangle.fromDegrees(rectangle.west, rectangle.south, rectangle.east, rectangle.north)
}

function toRectangleOutline(rectangle) {
  return Cesium.Cartesian3.fromDegreesArray([
    rectangle.west,
    rectangle.south,
    rectangle.east,
    rectangle.south,
    rectangle.east,
    rectangle.north,
    rectangle.west,
    rectangle.north,
    rectangle.west,
    rectangle.south,
  ])
}

function ensureDrawingOverlay() {
  if (!viewer || drawingEntity) return

  drawingEntity = viewer.entities.add({
    rectangle: {
      coordinates: new Cesium.CallbackProperty(() => {
        if (!tempRectangle) return undefined
        return toRectangleCoordinates(tempRectangle)
      }, false),
      material: Cesium.Color.fromCssColorString('#58d9a0').withAlpha(0.16),
      classificationType: Cesium.ClassificationType.BOTH,
      outline: false,
    },
  })

  drawingOutlineEntity = viewer.entities.add({
    polyline: {
      positions: new Cesium.CallbackProperty(() => {
        if (!tempRectangle) return []
        return toRectangleOutline(tempRectangle)
      }, false),
      width: 4,
      clampToGround: true,
      material: Cesium.Color.fromCssColorString('#6fe6b4'),
      depthFailMaterial: Cesium.Color.fromCssColorString('#f0c16b'),
    },
  })
}

function clearDrawingOverlay() {
  if (viewer && drawingEntity) {
    viewer.entities.remove(drawingEntity)
  }
  if (viewer && drawingOutlineEntity) {
    viewer.entities.remove(drawingOutlineEntity)
  }
  drawingEntity = null
  drawingOutlineEntity = null
  startPosition = null
  tempRectangle = null
  viewer?.scene.requestRender()
}

function enterDrawingMode() {
  console.log('[CesiumViewer] enterDrawingMode called, viewer:', !!viewer)
  if (!viewer) return
  setupDrawingHandler()
  clearDrawingOverlay()
  isDrawingMode = true
  viewer.scene.screenSpaceCameraController.enableInputs = false
  viewer.canvas.style.cursor = 'crosshair'
  showDrawingHint()
  viewer.scene.requestRender()
  console.log('[CesiumViewer] Drawing mode activated, isDrawingMode:', isDrawingMode)
}

function exitDrawingMode() {
  if (!viewer) return
  isDrawingMode = false
  viewer.scene.screenSpaceCameraController.enableInputs = true
  viewer.canvas.style.cursor = 'default'
  clearDrawingOverlay()
  removeDrawingHint()
  viewer.scene.requestRender()
}

function setupDrawingHandler() {
  if (!viewer) return

  // 清理旧的处理器
  if (drawHandler) {
    drawHandler.destroy()
    drawHandler = null
  }

  drawHandler = new Cesium.ScreenSpaceEventHandler(viewer.scene.canvas)

  drawHandler.setInputAction((movement) => {
    if (!isDrawingMode) return

    const cartesian = viewer.camera.pickEllipsoid(movement.position, viewer.scene.globe.ellipsoid)
    if (!cartesian) return

    const cartographic = Cesium.Cartographic.fromCartesian(cartesian)
    startPosition = {
      lon: Cesium.Math.toDegrees(cartographic.longitude),
      lat: Cesium.Math.toDegrees(cartographic.latitude),
    }
    tempRectangle = {
      west: startPosition.lon,
      south: startPosition.lat,
      east: startPosition.lon,
      north: startPosition.lat,
    }
    ensureDrawingOverlay()
    viewer.scene.requestRender()
  }, Cesium.ScreenSpaceEventType.LEFT_DOWN)

  drawHandler.setInputAction((movement) => {
    if (!isDrawingMode || !startPosition) return

    const cartesian = viewer.camera.pickEllipsoid(movement.endPosition, viewer.scene.globe.ellipsoid)
    if (!cartesian) return

    const cartographic = Cesium.Cartographic.fromCartesian(cartesian)
    const current = {
      lon: Cesium.Math.toDegrees(cartographic.longitude),
      lat: Cesium.Math.toDegrees(cartographic.latitude),
    }

    const west = Math.min(startPosition.lon, current.lon)
    const east = Math.max(startPosition.lon, current.lon)
    const south = Math.min(startPosition.lat, current.lat)
    const north = Math.max(startPosition.lat, current.lat)

    tempRectangle = { west, south, east, north }
    ensureDrawingOverlay()
    viewer.scene.requestRender()
  }, Cesium.ScreenSpaceEventType.MOUSE_MOVE)

  drawHandler.setInputAction(() => {
    console.log('[CesiumViewer] LEFT_UP, isDrawingMode:', isDrawingMode, 'startPosition:', !!startPosition, 'tempRectangle:', !!tempRectangle)
    if (!isDrawingMode || !startPosition || !tempRectangle) return

    const { west, south, east, north } = tempRectangle
    const centerLon = (west + east) / 2
    const centerLat = (south + north) / 2
    const latDiff = north - south
    const lonDiff = east - west
    const avgLat = (north + south) / 2
    const latKm = latDiff * 111
    const lonKm = lonDiff * 111 * Math.cos((avgLat * Math.PI) / 180)
    const areaKm2 = Math.abs(latKm * lonKm)

    const eventData = {
      center: { lat: centerLat, lon: centerLon },
      bounds: tempRectangle,
      areaKm2: Math.round(areaKm2 * 10) / 10,
    }
    console.log('[CesiumViewer] Dispatching area-selected event:', eventData)

    window.dispatchEvent(
      new CustomEvent('area-selected', {
        detail: eventData,
      }),
    )

    startPosition = null
    viewer.scene.requestRender()
  }, Cesium.ScreenSpaceEventType.LEFT_UP)
}

function setupClickHandler() {
  if (!viewer) return

  if (clickHandler) {
    clickHandler.destroy()
    clickHandler = null
  }

  clickHandler = new Cesium.ScreenSpaceEventHandler(viewer.scene.canvas)
  clickHandler.setInputAction((movement) => {
    if (isDrawingMode) return

    const picked = viewer.scene.pick(movement.position)
    if (!picked?.id?.properties?.pointData) return

    const data = picked.id.properties.pointData.getValue()
    window.dispatchEvent(
      new CustomEvent('point-selected', {
        detail: {
          ...data,
          screenX: movement.position.x,
          screenY: movement.position.y,
        },
      }),
    )
  }, Cesium.ScreenSpaceEventType.LEFT_CLICK)
}

function bindWindowEvents() {
  resetViewListener = () => {
    viewer?.camera.flyTo({
      destination: Cesium.Cartesian3.fromDegrees(118.8, 32.0, 80000),
      duration: 1.3,
    })
  }
  window.addEventListener('reset-view', resetViewListener)

  toggleLayerListener = () => {
    layerVisible.value = !layerVisible.value
  }
  window.addEventListener('toggle-layer', toggleLayerListener)

  enterDrawingModeListener = () => {
    enterDrawingMode()
  }
  window.addEventListener('enter-drawing-mode', enterDrawingModeListener)

  exitDrawingModeListener = () => {
    exitDrawingMode()
  }
  window.addEventListener('exit-drawing-mode', exitDrawingModeListener)
}

watch(
  () => props.horizon,
  (nextHorizon) => {
    loadPredictionLayer(nextHorizon)
  },
)

watch(
  () => props.scenarioResult,
  () => {
    applyActiveLayer()
  },
  { deep: true },
)

onMounted(async () => {
  await nextTick()

  if (!cesiumContainer.value) {
    return
  }

  viewer = new Cesium.Viewer(cesiumContainer.value, {
    animation: false,
    baseLayer: false,
    baseLayerPicker: false,
    fullscreenButton: false,
    geocoder: false,
    homeButton: false,
    infoBox: false,
    sceneModePicker: false,
    selectionIndicator: false,
    timeline: false,
    navigationHelpButton: false,
    orderIndependentTranslucency: false,
    requestRenderMode: true,
  })

  addBaseImageryLayer()
  setupDrawingHandler()
  setupClickHandler()
  bindWindowEvents()

  viewerReady.value = viewer

  viewer.camera.flyTo({
    destination: Cesium.Cartesian3.fromDegrees(118.8, 32.0, 80000),
    duration: 0,
  })

  await loadPredictionLayer(props.horizon)
  viewer.scene.requestRender()
})

onUnmounted(() => {
  if (resetViewListener) window.removeEventListener('reset-view', resetViewListener)
  if (toggleLayerListener) window.removeEventListener('toggle-layer', toggleLayerListener)
  if (enterDrawingModeListener) window.removeEventListener('enter-drawing-mode', enterDrawingModeListener)
  if (exitDrawingModeListener) window.removeEventListener('exit-drawing-mode', exitDrawingModeListener)

  if (clickHandler) clickHandler.destroy()
  if (drawHandler) drawHandler.destroy()
  if (viewer) viewer.destroy()

  clickHandler = null
  drawHandler = null
  viewer = null
})
</script>

<template>
  <div ref="cesiumContainer" class="cesium-container"></div>
  <HeatMapLayer :viewer="viewerReady" :gridData="gridData" :visible="layerVisible" />
</template>

<style scoped>
.cesium-container {
  width: 100%;
  height: 100%;
}
</style>
