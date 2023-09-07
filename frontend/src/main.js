import { createApp } from 'vue'
import {createRouter, createWebHistory} from 'vue-router'
import './style.css'
import App from './App.vue'

/* import the fontawesome core */
import { library } from '@fortawesome/fontawesome-svg-core'
/* import font awesome icon component */
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
/* import specific icons */
import { faExpand } from '@fortawesome/free-solid-svg-icons'

/* add icons to the library */
library.add(faExpand)

import {routes} from './views'

const router = createRouter({
    history: createWebHistory(),
    routes: routes
})

createApp(App)
    .use(router)
    .component("font-awesome-icon", FontAwesomeIcon)
    .mount('#app')
