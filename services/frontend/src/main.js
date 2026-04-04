import './assets/main.css'
// 导入 Cesium CSS（vite-plugin-cesium 会自动处理）
import 'cesium/Build/Cesium/Widgets/widgets.css'

import { createApp } from 'vue'
import App from './App.vue'

createApp(App).mount('#app')
