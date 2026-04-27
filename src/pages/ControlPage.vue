<template>
  <ForceGraphPage
    title="控制关系"
    :colors="colors"
    :names="names"
    :menu-items="menuItems"
    :info-items="infoItems"
    :data-loader="loadData"
    link-label-key="rate"
    show-link-label
    show-arrow
  />
</template>

<script setup>
import ForceGraphPage from '../components/ForceGraphPage.vue'

const names = ['control', 'cross', 'root', 'normal']
const colors = ['#ca635f', '#6ca46c', '#4e88af', '#ded295']

const menuItems = [
  { label: 'Control', type: 'link', data: '/data/control_json/control.json' },
  { label: 'Cross', type: 'link', data: '/data/control_json/cross.json' },
  {
    label: 'Multi',
    type: 'select',
    options: [
      'multi_0', 'multi_1', 'multi_2', 'multi_3'
    ].map(v => ({ label: v, data: `/data/control_json/${v}.json` }))
  },
  {
    label: 'Double',
    type: 'select',
    options: Array.from({ length: 21 }, (_, i) => ({
      label: `double_${i}`,
      data: `/data/control_json/double_${i}.json`
    }))
  },
]

const infoItems = [
  { color: '#ca635f', text: 'control：不明确控制关系。所有含有"control"关系的子图，"control"关系在原始数据表中的控股比例为1314%，是一种不明确投资比例的控制关系，可能为职业任职投资关系' },
  { color: '#6ca46c', text: 'cross：交叉持股。所有含有交叉持股关系的子图，因为所有交叉持股的持股比例都为100%，在该页面中的所有子图不存在代表实际控制人的root节点' },
  { color: '#4e88af', text: 'multi：超过两个节点以上的控股关系。每一个子图通过相应算法识别出了一个实际控制人，在页面中表示为蓝色的root节点' },
  { color: '#ded295', text: 'double：双节点的控股关系。每一个子图通过相应算法识别出了一个实际控制人' },
]

async function loadData(url) {
  const res = await fetch(url)
  return res.json()
}
</script>
