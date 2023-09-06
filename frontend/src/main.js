import { createApp } from 'vue'
import {createRouter, createWebHistory} from 'vue-router'
import './style.css'
import App from './App.vue'

import {routes} from './views'

const router = createRouter({
    history: createWebHistory(),
    routes: routes
})

createApp(App)
    .use(router)
    .mount('#app')
