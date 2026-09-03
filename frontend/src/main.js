import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './assets/role-theme.css'
import './assets/tema-sigta.css'

const app = createApp(App)

app.use(router)

app.mount('#app')
