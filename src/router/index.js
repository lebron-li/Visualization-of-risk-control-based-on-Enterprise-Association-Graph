import { createRouter, createWebHashHistory } from 'vue-router'
import HomePage from '../pages/HomePage.vue'
import ControlPage from '../pages/ControlPage.vue'
import GuaranteePage from '../pages/GuaranteePage.vue'
import MoneyCollectionPage from '../pages/MoneyCollectionPage.vue'

const routes = [
  { path: '/', name: 'home', component: HomePage },
  { path: '/control', name: 'control', component: ControlPage },
  { path: '/guarantee', name: 'guarantee', component: GuaranteePage },
  { path: '/money-collection', name: 'moneyCollection', component: MoneyCollectionPage },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

export default router
