<template>
  <div class="graph-layout">
    <div class="sidebar">
      <h2 class="page-title">{{ title }}</h2>

      <div class="mode">
        <span :class="{ active: viewMode === 'circles' }" @click="viewMode = 'circles'">Circles</span>
        <span :class="{ active: viewMode === 'texts' }" @click="viewMode = 'texts'">Texts</span>
      </div>

      <div class="search-box">
        <input
          ref="searchIdRef"
          type="text"
          placeholder="search by id"
          @focus="onFocus"
          @blur="onBlur"
          @keyup="onSearch"
        />
      </div>
      <div class="search-box">
        <input
          ref="searchTypeRef"
          type="text"
          placeholder="search by type"
          @focus="onFocus"
          @blur="onBlur"
          @keyup="onSearch"
        />
      </div>

      <div class="indicator">
        <div v-for="(name, i) in names" :key="name">
          <span :style="{ backgroundColor: colors[i] }"></span>{{ name }}
        </div>
      </div>
    </div>

    <div class="graph-area">
      <ForceGraph
        ref="graphRef"
        :data="graphData"
        :colors="colors"
        :view-mode="viewMode"
        :show-arrow="showArrow"
        :link-label-key="linkLabelKey"
        :show-link-label="showLinkLabel"
        :link-width="linkWidth"
      />
      <div class="info-panel">
        <h4 v-if="hoverType">{{ hoverType }}</h4>
        <h5 v-if="hoverId">{{ hoverId }}</h5>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import ForceGraph from './ForceGraph.vue'

const props = defineProps({
  title: String,
  colors: Array,
  names: Array,
  menuItems: Array,
  infoItems: Array,
  dataLoader: Function,
  linkLabelKey: { type: String, default: '' },
  showLinkLabel: { type: Boolean, default: false },
  showArrow: { type: Boolean, default: false },
  linkWidth: { type: Function, default: null },
})

const viewMode = ref('circles')
const graphRef = ref(null)
const currentDataUrl = ref(null)
const graphData = ref(null)

const hoverType = computed(() => graphRef.value?.hoverType ?? '')
const hoverId = computed(() => graphRef.value?.hoverId ?? '')

const searchIdRef = ref(null)
const searchTypeRef = ref(null)

function onFocus(e) {
  if (e.target.placeholder === e.target.value) {
    e.target.value = ''
  }
  e.target.style.color = '#fffffa'
}

function onBlur(e) {
  if (e.target.value === '') {
    e.target.placeholder === 'search by id' ? (e.target.placeholder = 'search by id') : (e.target.placeholder = 'search by type')
    e.target.style.color = '#999'
  }
}

function onSearch() {
  const idVal = searchIdRef.value?.value || ''
  const typeVal = searchTypeRef.value?.value || ''
  graphRef.value?.search(idVal, typeVal)
}

async function loadUrl(url) {
  currentDataUrl.value = url
  graphData.value = await props.dataLoader(url)
}

defineExpose({ loadUrl })

// Auto-load first link data
const firstLink = props.menuItems?.find(m => m.type === 'link')
if (firstLink) {
  loadUrl(firstLink.data)
}
</script>

<style scoped>
.graph-layout {
  display: flex;
  height: 100vh;
  background-color: #272b30;
}

.sidebar {
  width: 14%;
  min-width: 160px;
  padding: 20px 10px 20px 2%;
  display: flex;
  flex-direction: column;
}

.page-title {
  color: azure;
  font-size: 25px;
  margin-bottom: 30px;
  text-align: left;
  padding-left: 5px;
}

.mode {
  margin-bottom: 25px;
}

.mode span {
  display: inline-block;
  border: 1.5px solid #E6E6E6;
  color: #E6E6E6;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 15px;
  margin-right: 4px;
  cursor: pointer;
  transition: all 0.4s;
}

.mode span.active,
.mode span:hover {
  background-color: white;
  color: #333;
}

.search-box {
  margin-bottom: 8px;
}

.search-box input {
  width: 130px;
  height: 35px;
  border-radius: 5px;
  border: none;
  outline: none;
  background-color: slategrey;
  color: #f2f2f2;
  text-align: center;
  font-size: 15px;
}

.indicator {
  margin-top: 20px;
  margin-left: 5px;
  color: #f2f2f2;
  font-size: 14px;
}

.indicator span {
  display: inline-block;
  width: 30px;
  height: 15px;
  margin-right: 8px;
  margin-top: 5px;
}

.graph-area {
  position: relative;
  flex: 1;
  height: 100%;
}

.info-panel {
  position: absolute;
  top: 10px;
  right: 30px;
  text-align: left;
  pointer-events: none;
}

.info-panel h4 {
  padding: 15px 0;
  font-size: 15px;
}

.info-panel h5 {
  font-size: 15px;
}
</style>
