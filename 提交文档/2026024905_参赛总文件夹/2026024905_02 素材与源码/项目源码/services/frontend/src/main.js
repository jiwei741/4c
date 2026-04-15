import './assets/main.css'
import 'cesium/Build/Cesium/Widgets/widgets.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router/index.js'

createApp(App).use(router).mount('#app')
