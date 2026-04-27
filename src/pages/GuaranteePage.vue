<template>
  <ForceGraphPage
    title="担保关系"
    :colors="colors"
    :names="names"
    :menu-items="menuItems"
    :info-items="infoItems"
    :data-loader="loadData"
    link-label-key="amount"
    show-link-label
    show-arrow
  />
</template>

<script setup>
import ForceGraphPage from '../components/ForceGraphPage.vue'

const names = ['Chain', 'Mutual', 'Focus', 'Cross', 'Circle', 'Normal', 'doubleRisk', 'tripleRisk', 'quadraRisk']
const colors = ['#37a6ff', '#a3ade9', '#73c187', '#ffd5b5', '#8259ab', '#ffffff', '#f1761b', '#f65d5d', '#ff0000']

const menuItems = [
  { label: 'Circle', type: 'link', data: '/data/guarantee_json/circle.json' },
  { label: 'Cross', type: 'link', data: '/data/guarantee_json/cross.json' },
  { label: 'Focus', type: 'link', data: '/data/guarantee_json/focus.json' },
  { label: 'Chain', type: 'link', data: '/data/guarantee_json/multiNormal.json' },
  { label: 'Mutual', type: 'link', data: '/data/guarantee_json/mutual.json' },
  {
    label: 'Normal',
    type: 'select',
    options: Array.from({ length: 5 }, (_, i) => ({
      label: `normal_${i}`,
      data: `/data/guarantee_json/doubleNormal_${i}.json`
    }))
  },
]

const infoItems = [
  { color: '#8259ab', text: 'Circle：担保圈。所有含有担保圈的子图。形成担保圈的企业可能含有其他类型风险' },
  { color: '#ffd5b5', text: 'Cross："一保多"。一个企业为两个以上企业提供担保，过多担保带来较大风险' },
  { color: '#73c187', text: 'Focus："多保一"。企业被两个以上企业提供担保，资金缺口较大，抗风险能力弱' },
  { color: '#37a6ff', text: 'Chain：担保链。只含有担保链的子图' },
  { color: '#a3ade9', text: 'Mutual：互保。含有"互保"现象的子图' },
  { color: '#ffffff', text: 'Normal："一保一"。一个企业对另外一个企业提供担保，属于正常的担保现象' },
]

async function loadData(url) {
  const res = await fetch(url)
  return res.json()
}
</script>
