<template>
  <ForceGraphPage
    title="资金归集关系"
    :colors="colors"
    :names="names"
    :menu-items="menuItems"
    :info-items="infoItems"
    :data-loader="loadData"
    show-arrow
    link-label-key="date"
    :link-width="d => d.width"
  />
</template>

<script setup>
import ForceGraphPage from '../components/ForceGraphPage.vue'

const names = ['start', 'mid', 'end', 'pos', 'neg']
const colors = ['#4e88af', '#6ca46c', '#ca635f', '#4e88af', '#ded295']

const menuItems = [
  { label: 'moneyCollection', type: 'link', data: '/data/moneyCollection_json/moneyCollection.json' },
  {
    label: 'All',
    type: 'select',
    options: Array.from({ length: 5 }, (_, i) => ({
      label: `all_${i}`,
      data: `/data/moneyCollection_json/all_${i}.json`
    }))
  },
]

const infoItems = [
  { color: '#4e88af', text: 'moneyCollection：具有赛题中定义的资金归集行为的子图。资金归集判别规则：1、贷款发放金额*0.9<=对外转账金额<=贷款发放金额 2、转账日期在贷款发放后5日内' },
  { color: '#ded295', text: 'all：不具有资金归集行为但存在贷款和转账交易的所有子图' },
  { color: '#4e88af', text: 'start/mid/end：具有资金归集行为的子图的根节点、中间节点、叶子节点' },
  { color: '#ded295', text: 'pos：净资金流入为正的节点 | neg：净资金流入为负的节点' },
]

async function loadData(url) {
  const res = await fetch(url)
  return res.json()
}
</script>
