<script setup>
import { onMounted, onUnmounted, ref, watch } from 'vue'
import * as Cesium from 'cesium'
import HeatMapLayer from './HeatMapLayer.vue'
import { generateMockCarbonData } from '../mock/carbonData.js'
import { getBackendCarbonData } from '../api/backendDataLoader.js'

const props = defineProps({
  date: String,
  scenarioResult: Object // 情景推演结果，用于显示对比视图
})

// 数据源配置
// true = 使用后端API, false = 使用Mock数据
const USE_BACKEND_API = false  // 等后端服务启动后再改为 true
// 后端API使用日期格式 (2023-06-01)，前端时间轴使用季度格式 (2023-Q2)
// 需要转换
const USE_QUARTER_FORMAT = true

const cesiumContainer = ref(null)
let viewer = null
const viewerReady = ref(null)
const gridData = ref([])
const layerVisible = ref(true)  // 控制热力图层显示/隐藏

// 绘制相关状态
let isDrawingMode = false
let drawHandler = null
let drawingEntity = null
let startPosition = null
let tempRectangle = null

const TIANDITU_TOKEN = 'f7c661500b1d6f3873b1538c67d81ad8'

// 时间戳映射：将季度格式转换为后端API需要的日期格式
function quarterToDate(quarterStr) {
  // '2020-Q2' -> '2020-06-01'
  const [year, quarter] = quarterStr.split('-Q')
  const months = { 'Q1': '-01-01', 'Q2': '-04-01', 'Q3': '-07-01', 'Q4': '-10-01' }
  return `${year}${months[quarter]}`
}

// 反向转换：日期格式转季度格式
function dateToQuarter(dateStr) {
  // '2020-06-01' -> '2020-Q2'
  const year = dateStr.substring(0, 4)
  const month = parseInt(dateStr.substring(5, 7))
  let quarter = 'Q1'
  if (month >= 4 && month <= 6) quarter = 'Q2'
  else if (month >= 7 && month <= 9) quarter = 'Q3'
  else if (month >= 10) quarter = 'Q4'
  return `${year}-${quarter}`
}

// 获取用于API调用的日期格式
function getApiDate(dateStr) {
  if (USE_QUARTER_FORMAT) {
    // 前端使用季度格式，需要转换为日期格式给后端
    return quarterToDate(dateStr)
  }
  // 已经是日期格式，直接使用
  return dateStr
}

watch(() => props.date, async (newDate) => {
  console.log('日期变化:', newDate)

  if (USE_BACKEND_API) {
    try {
      const apiDate = getApiDate(newDate)
      console.log('请求API日期:', apiDate)
      const data = await getBackendCarbonData(apiDate)
      console.log('收到数据:', data.grid.length, '个网格')
      if (data.grid.length > 0) {
        console.log('第一个网格点:', data.grid[0])
      }
      gridData.value = data.grid
    } catch (error) {
      console.error('从后端加载失败，使用Mock数据:', error)
      const mockData = generateMockCarbonData(newDate)
      gridData.value = mockData.grid
    }
  } else {
    const mockData = generateMockCarbonData(newDate)
    gridData.value = mockData.grid
  }
})

// 进入绘制模式
function enterDrawingMode() {
  isDrawingMode = true
  // 禁用相机控制，防止拖动时地图跟着动
  viewer.scene.screenSpaceCameraController.enableInputs = false
  viewer.canvas.style.cursor = 'crosshair'
  showDrawingHint()
}

// 退出绘制模式
function exitDrawingMode() {
  isDrawingMode = false
  // 重新启用相机控制
  viewer.scene.screenSpaceCameraController.enableInputs = true
  viewer.canvas.style.cursor = 'default'
  clearDrawing()
  removeDrawingHint()
}

// 显示绘制提示
let hintEntity = null
function showDrawingHint() {
  hintEntity = viewer.entities.add({
    position: Cesium.Cartesian3.fromDegrees(118.8, 32.0),
    label: {
      text: '🖊️ 拖动鼠标绘制新增工业区',
      font: '16px sans-serif',
      fillColor: Cesium.Color.WHITE,
      outlineColor: Cesium.Color.BLACK,
      outlineWidth: 2,
      style: Cesium.LabelStyle.FILL_AND_OUTLINE,
      pixelOffset: new Cesium.Cartesian2(0, -50),
      showBackground: true,
      backgroundColor: new Cesium.Color(0.2, 0.2, 0.2, 0.8)
    }
  })
}

function removeDrawingHint() {
  if (hintEntity) {
    viewer.entities.remove(hintEntity)
    hintEntity = null
  }
}

// 清除绘制内容
function clearDrawing() {
  if (drawingEntity) {
    viewer.entities.remove(drawingEntity)
    drawingEntity = null
  }
  if (drawHandler) {
    drawHandler.destroy()
    drawHandler = null
  }
  startPosition = null
  tempRectangle = null
}

// 设置绘制事件监听
function setupDrawingHandler() {
  drawHandler = new Cesium.ScreenSpaceEventHandler(viewer.scene.canvas)

  // 鼠标按下 - 开始绘制
  drawHandler.setInputAction((movement) => {
    if (!isDrawingMode) return

    // 使用 pickEllipsoid 获取地球表面的位置（更可靠）
    const cartesian = viewer.camera.pickEllipsoid(movement.position, viewer.scene.globe.ellipsoid)
    if (!cartesian) return

    const cartographic = Cesium.Cartographic.fromCartesian(cartesian)
    startPosition = {
      lon: Cesium.Math.toDegrees(cartographic.longitude),
      lat: Cesium.Math.toDegrees(cartographic.latitude)
    }

    console.log('开始绘制:', startPosition)
  }, Cesium.ScreenSpaceEventType.LEFT_DOWN)

  // 鼠标移动 - 更新矩形
  drawHandler.setInputAction((movement) => {
    if (!isDrawingMode || !startPosition) return

    const cartesian = viewer.camera.pickEllipsoid(movement.endPosition, viewer.scene.globe.ellipsoid)
    if (!cartesian) return

    const cartographic = Cesium.Cartographic.fromCartesian(cartesian)
    const currentPosition = {
      lon: Cesium.Math.toDegrees(cartographic.longitude),
      lat: Cesium.Math.toDegrees(cartographic.latitude)
    }

    // 计算矩形边界
    const west = Math.min(startPosition.lon, currentPosition.lon)
    const east = Math.max(startPosition.lon, currentPosition.lon)
    const south = Math.min(startPosition.lat, currentPosition.lat)
    const north = Math.max(startPosition.lat, currentPosition.lat)

    tempRectangle = { west, south, east, north }

    // 更新或创建绘制实体
    if (drawingEntity) {
      drawingEntity.rectangle.coordinates = new Cesium.Rectangle(
        Cesium.Math.toRadians(west),
        Cesium.Math.toRadians(south),
        Cesium.Math.toRadians(east),
        Cesium.Math.toRadians(north)
      )
    } else {
      drawingEntity = viewer.entities.add({
        rectangle: {
          coordinates: new Cesium.Rectangle(
            Cesium.Math.toRadians(west),
            Cesium.Math.toRadians(south),
            Cesium.Math.toRadians(east),
            Cesium.Math.toRadians(north)
          ),
          material: Cesium.Color.YELLOW.withAlpha(0.3),
          outline: true,
          outlineColor: Cesium.Color.YELLOW,
          outlineWidth: 2,
          height: 0,
          classificationType: Cesium.ClassificationType.TERRAIN
        }
      })
    }
  }, Cesium.ScreenSpaceEventType.MOUSE_MOVE)

  // 鼠标释放 - 完成绘制
  drawHandler.setInputAction(() => {
    if (!isDrawingMode || !startPosition || !tempRectangle) return

    // 计算区域信息
    const { west, south, east, north } = tempRectangle

    // 计算中心点
    const centerLon = (west + east) / 2
    const centerLat = (south + north) / 2

    // 估算面积（简化计算，使用纬度修正）
    const latDiff = north - south
    const lonDiff = east - west
    const avgLat = (north + south) / 2
    // 每度纬度约111km，每度经度约111km * cos(纬度)
    const latKm = latDiff * 111
    const lonKm = lonDiff * 111 * Math.cos(avgLat * Math.PI / 180)
    const areaKm2 = Math.abs(latKm * lonKm)

    console.log('完成绘制:', { center: { lat: centerLat, lon: centerLon }, areaKm2 })

    // 触发区域选择事件
    window.dispatchEvent(new CustomEvent('area-selected', {
      detail: {
        center: { lat: centerLat, lon: centerLon },
        bounds: tempRectangle,
        areaKm2: Math.round(areaKm2 * 10) / 10
      }
    }))

    // 完成绘制，保留矩形让用户看到
    startPosition = null
  }, Cesium.ScreenSpaceEventType.LEFT_UP)
}

// 点击事件处理器 - 显示热力点详情
let clickHandler = null
function setupClickHandler() {
  clickHandler = new Cesium.ScreenSpaceEventHandler(viewer.scene.canvas)
  clickHandler.setInputAction((movement) => {
    if (isDrawingMode) return

    const cartesian = viewer.camera.pickEllipsoid(movement.position, viewer.scene.globe.ellipsoid)
    if (!cartesian) return

    const cartographic = Cesium.Cartographic.fromCartesian(cartesian)
    const clickLon = Cesium.Math.toDegrees(cartographic.longitude)
    const clickLat = Cesium.Math.toDegrees(cartographic.latitude)

    // 找最近的热力点
    let nearestPoint = null
    let minDist = Infinity
    for (const p of gridData.value) {
      const dist = Math.sqrt(Math.pow(p.lon - clickLon, 2) + Math.pow(p.lat - clickLat, 2))
      if (dist < 0.05 && dist < minDist) {
        minDist = dist
        nearestPoint = p
      }
    }

    if (nearestPoint) {
      window.dispatchEvent(new CustomEvent('point-selected', {
        detail: { lat: nearestPoint.lat, lon: nearestPoint.lon, gpp: nearestPoint.gpp }
      }))
    }
  }, Cesium.ScreenSpaceEventType.LEFT_CLICK)
}


onMounted(async () => {
  console.log('=== CesiumViewer onMounted 开始 ===')

  // 等待 DOM 完全渲染
  await new Promise(resolve => setTimeout(resolve, 100))

  console.log('cesiumContainer.value:', cesiumContainer.value)
  if (!cesiumContainer.value) {
    console.error('❌ cesiumContainer.value 是 null!')
    return
  }

  const rect = cesiumContainer.value.getBoundingClientRect()
  console.log('container尺寸:', rect.width, 'x', rect.height)

  if (rect.width === 0 || rect.height === 0) {
    console.error('❌ 容器尺寸为 0，无法渲染!')
  }

  // 使用高德地图（国内稳定，不需要 token）
  try {
    console.log('开始创建 viewer...')

    viewer = new Cesium.Viewer(cesiumContainer.value, {
      baseLayer: false,
      baseLayerPicker: false,
      geocoder: false,
      homeButton: false,
      sceneModePicker: false,
      timeline: false,
      animation: false,
      fullscreenButton: false,
      infoBox: false,
      selectionIndicator: false,
      navigationHelpButton: false,
    })
    console.log('✓ Viewer created')

    // 高德矢量地图
    const gaodeLayer = new Cesium.UrlTemplateImageryProvider({
      url: 'https://webrd02.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}',
      minimumLevel: 3,
      maximumLevel: 18
    })
    viewer.imageryLayers.addImageryProvider(gaodeLayer)
    console.log('✓ 高德地图已添加（包含中文地名）')

    console.log('  - scene:', !!viewer.scene)
    console.log('  - canvas:', viewer.canvas)

    // 等待渲染
    viewer.scene.postRender.addEventListener(() => {
      console.log('✓ Scene rendered')
    })

  } catch (error) {
    console.error('❌ Viewer 创建失败:', error)
    return
  }

  // 监听重置视图事件
  window.addEventListener('reset-view', () => {
    if (viewer) {
      viewer.camera.flyTo({
        destination: Cesium.Cartesian3.fromDegrees(118.8, 32.0, 80000),
        duration: 1.5
      })
    }
  })

  // 监听切换图层事件
  window.addEventListener('toggle-layer', () => {
    layerVisible.value = !layerVisible.value
  })

  // 监听绘制模式事件
  window.addEventListener('enter-drawing-mode', () => {
    enterDrawingMode()
  })

  window.addEventListener('exit-drawing-mode', () => {
    exitDrawingMode()
  })

  viewerReady.value = viewer

  console.log('=== 初始化数据加载 ===')
  console.log('USE_BACKEND_API:', USE_BACKEND_API)
  console.log('props.date:', props.date)

  // 加载初始数据
  const initialDate = props.date || '2020-Q2'
  const apiDate = getApiDate(initialDate)
  console.log('初始日期:', initialDate, 'API日期:', apiDate)

  if (USE_BACKEND_API) {
    getBackendCarbonData(apiDate).then(data => {
      console.log('初始数据加载成功:', data.grid.length, '个网格')
      gridData.value = data.grid
    }).catch(err => {
      console.error('从后端加载失败，使用Mock数据:', err)
      const mockData = generateMockCarbonData(initialDate)
      gridData.value = mockData.grid
    })
  } else {
    const mockData = generateMockCarbonData(initialDate)
    gridData.value = mockData.grid
  }

  // 飞到南京
  viewer.camera.flyTo({
    destination: Cesium.Cartesian3.fromDegrees(118.8, 32.0, 80000),
  })

  // 初始化绘制处理器（但不激活）
  setupDrawingHandler()

  // 初始化点击事件处理器
  setupClickHandler()
})

onUnmounted(() => {
  // 清理点击事件处理器
  if (clickHandler) {
    clickHandler.destroy()
    clickHandler = null
  }

  if (viewer) {
    viewer.destroy()
  }
})
</script>

<template>
  <div ref="cesiumContainer" class="cesium-container" />
  <HeatMapLayer :viewer="viewerReady" :gridData="gridData" :visible="layerVisible" />
</template>

<style scoped>
.cesium-container {
  width: 100vw;
  height: 100vh;
  position: fixed;
  top: 0;
  left: 0;
  z-index: 0;
  background: #000;
}

/* 确保Cesium的canvas可见 */
.cesium-container :deep(canvas) {
  display: block !important;
  width: 100% !important;
  height: 100% !important;
}
</style>
