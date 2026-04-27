<template>
  <svg ref="svgEl" class="force-svg"></svg>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted, nextTick } from 'vue'
import * as d3 from 'd3'

const props = defineProps({
  data: Object,
  colors: Array,
  viewMode: { type: String, default: 'circles' },
  showArrow: { type: Boolean, default: false },
  linkLabelKey: { type: String, default: '' },
  showLinkLabel: { type: Boolean, default: false },
  linkWidth: { type: Function, default: null },
})

const svgEl = ref(null)
const hoverType = ref('')
const hoverId = ref('')

let simulation = null
let svg = null
let graphData = null
let linkElements = null
let nodeElements = null
let textElements = null
let edgesTextElements = null
let dragging = false

onMounted(() => {
  setupSvg()
})

onUnmounted(() => {
  if (simulation) simulation.stop()
})

watch(() => props.data, (newData) => {
  if (newData) render(newData)
})

watch(() => props.viewMode, (mode) => {
  if (!svg) return
  if (mode === 'circles') {
    svg.selectAll('.nodes circle').style('display', null)
    svg.selectAll('.texts text').style('display', 'none')
  } else {
    svg.selectAll('.nodes circle').style('display', 'none')
    svg.selectAll('.texts text').style('display', null)
  }
})

function setupSvg() {
  if (!svgEl.value) return
  svg = d3.select(svgEl.value)

  const zoom = d3.zoom()
    .scaleExtent([0.1, 8])
    .on('zoom', (event) => {
      svg.select('g.main-group').attr('transform', event.transform)
    })

  svg.call(zoom)

  // Create main group
  const mainGroup = svg.append('g').attr('class', 'main-group')

  // Create marker arrow
  if (props.showArrow) {
    mainGroup.append('defs')
      .append('marker')
      .attr('id', 'arrowhead')
      .attr('markerUnits', 'userSpaceOnUse')
      .attr('viewBox', '0 -5 10 10')
      .attr('refX', 26)
      .attr('refY', 0)
      .attr('markerWidth', 5)
      .attr('markerHeight', 6)
      .attr('orient', 'auto')
      .attr('stroke-width', 2)
      .append('path')
      .attr('d', 'M0,-5L10,0L0,5')
      .attr('fill', '#4e88af')
  }

  // Create layers
  mainGroup.append('g').attr('class', 'links')
  mainGroup.append('g').attr('class', 'edges-texts')
  mainGroup.append('g').attr('class', 'nodes')
  mainGroup.append('g').attr('class', 'texts')

  // Setup simulation
  simulation = d3.forceSimulation()
    .force('link', d3.forceLink().id(d => d.id).distance(60))
    .force('charge', d3.forceManyBody().strength(-200))
    .force('center', d3.forceCenter(
      svgEl.value.clientWidth / 2,
      svgEl.value.clientHeight / 2
    ))
    .on('tick', ticked)

  // If data already loaded
  if (props.data) render(props.data)
}

function ticked() {
  if (linkElements) {
    linkElements
      .attr('x1', d => d.source.x)
      .attr('y1', d => d.source.y)
      .attr('x2', d => d.target.x)
      .attr('y2', d => d.target.y)
      .attr('marker-end', props.showArrow ? 'url(#arrowhead)' : null)
  }
  if (edgesTextElements) {
    edgesTextElements
      .attr('x', d => (d.source.x + d.target.x) / 2)
      .attr('y', d => (d.source.y + d.target.y) / 2)
  }
  if (nodeElements) {
    nodeElements
      .attr('cx', d => d.x)
      .attr('cy', d => d.y)
  }
  if (textElements) {
    textElements.attr('transform', d => `translate(${d.x},${d.y + (d.size || 5) / 2})`)
  }
}

function render(data) {
  if (!svg) return
  graphData = data

  const mainGroup = svg.select('g.main-group')
  const w = svgEl.value.clientWidth
  const h = svgEl.value.clientHeight

  // Clear old
  mainGroup.select('.links').selectAll('*').remove()
  mainGroup.select('.edges-texts').selectAll('*').remove()
  mainGroup.select('.nodes').selectAll('*').remove()
  mainGroup.select('.texts').selectAll('*').remove()

  simulation.stop()

  const nodes = data.nodes.map(d => ({ ...d }))
  const links = data.links.map(d => ({ ...d }))

  // Links
  linkElements = mainGroup.select('.links')
    .selectAll('line')
    .data(links)
    .enter()
    .append('line')
    .attr('stroke', '#fff')
    .attr('stroke-opacity', 0.5)
    .attr('stroke-width', d => {
      if (props.linkWidth) return props.linkWidth(d)
      return 1
    })

  // Link labels
  if (props.showLinkLabel && props.linkLabelKey) {
    edgesTextElements = mainGroup.select('.edges-texts')
      .selectAll('text')
      .data(links)
      .enter()
      .append('text')
      .text(d => d[props.linkLabelKey] ?? '')
      .attr('font-size', 5)
      .attr('fill', '#f2f2f2')
      .attr('opacity', 0.5)
      .attr('text-anchor', 'middle')
  } else {
    edgesTextElements = mainGroup.select('.edges-texts')
      .selectAll('text')
      .data([])
  }

  // Nodes (circles)
  const radiusFn = d => {
    const size = d.size ?? 5
    return Math.max(size / 4 + 2, 3)
  }

  nodeElements = mainGroup.select('.nodes')
    .selectAll('circle')
    .data(nodes)
    .enter()
    .append('circle')
    .attr('r', radiusFn)
    .attr('fill', d => (props.colors && props.colors[d.group]) ? props.colors[d.group] : '#fff')
    .attr('stroke', '#fff')
    .attr('stroke-width', 0.3)
    .attr('data-id', d => d.id)
    .attr('data-gid', d => d.Gid)
    .attr('data-ctx', d => d.ctx || d.class || '')
    .call(dragBehavior())
    .on('mouseenter', handleMouseEnter)
    .on('mouseleave', handleMouseLeave)

  // Text labels
  textElements = mainGroup.select('.texts')
    .selectAll('text')
    .data(nodes)
    .enter()
    .append('text')
    .attr('font-size', d => Math.max(radiusFn(d), 4))
    .attr('fill', d => (props.colors && props.colors[d.group]) ? props.colors[d.group] : '#fff')
    .text(d => d.id)
    .attr('text-anchor', 'middle')
    .attr('data-id', d => d.id)
    .attr('data-gid', d => d.Gid)
    .attr('data-ctx', d => d.ctx || d.class || '')
    .style('display', props.viewMode === 'texts' ? null : 'none')
    .call(dragBehavior())
    .on('mouseenter', handleMouseEnterText)
    .on('mouseleave', handleMouseLeave)

  // Simulation
  simulation.nodes(nodes)
  simulation.force('link').links(links)
  simulation.alpha(1).restart()
}

function dragBehavior() {
  return d3.drag()
    .on('start', (event, d) => {
      if (!event.active) simulation.alphaTarget(0.1).restart()
      d.fx = d.x
      d.fy = d.y
      dragging = true
    })
    .on('drag', (event, d) => {
      d.fx = event.x
      d.fy = event.y
    })
    .on('end', (event, d) => {
      if (!event.active) simulation.alphaTarget(0.0001)
      d.fx = null
      d.fy = null
      dragging = false
    })
}

function handleMouseEnter(event, d) {
  hoverType.value = `type: ${d.ctx || d.class || ''}`
  hoverId.value = `id: ${d.id}`

  if (!dragging && graphData) {
    const gid = d.Gid
    svg.selectAll('.nodes circle').attr('class', node => {
      if (node.id === d.id) return ''
      for (const l of graphData.links) {
        if ((l.source.Gid === gid && l.target.Gid === node.Gid) ||
            (l.target.Gid === gid && l.source.Gid === node.Gid)) {
          return ''
        }
      }
      return 'inactive'
    })
    svg.selectAll('.links line').attr('class', l => {
      if (l.source.Gid === gid || l.target.Gid === gid) return ''
      return 'inactive'
    })
  }
}

function handleMouseEnterText(event, d) {
  hoverType.value = `type: ${d.ctx || d.class || ''}`
  hoverId.value = `id: ${d.id}`

  if (!dragging && graphData) {
    const gid = d.Gid
    svg.selectAll('.texts text').attr('class', node => {
      if (node.id === d.id) return ''
      for (const l of graphData.links) {
        if ((l.source.Gid === gid && l.target.Gid === node.Gid) ||
            (l.target.Gid === gid && l.source.Gid === node.Gid)) {
          return ''
        }
      }
      return 'inactive'
    })
    svg.selectAll('.links line').attr('class', l => {
      if (l.source.Gid === gid || l.target.Gid === gid) return ''
      return 'inactive'
    })
  }
}

function handleMouseLeave() {
  if (!dragging) {
    svg?.selectAll('.nodes circle').attr('class', '')
    svg?.selectAll('.texts text').attr('class', '')
    svg?.selectAll('.links line').attr('class', '')
  }
}

function search(idQuery, typeQuery) {
  if (!svg || !graphData) return

  const resetAll = () => {
    svg.selectAll('.nodes circle').attr('class', '')
    svg.selectAll('.texts text').attr('class', '')
    svg.selectAll('.links line').attr('class', '')
  }

  if (!idQuery && !typeQuery) {
    resetAll()
    return
  }

  if (idQuery) {
    svg.selectAll('.nodes circle').attr('class', d => {
      return d.id.toLowerCase().includes(idQuery.toLowerCase()) ? '' : 'inactive'
    })
    svg.selectAll('.texts text').attr('class', d => {
      return d.id.toLowerCase().includes(idQuery.toLowerCase()) ? '' : 'inactive'
    })
    svg.selectAll('.links line').attr('class', 'inactive')
  }

  if (typeQuery) {
    svg.selectAll('.nodes circle').attr('class', d => {
      const c = (d.class || '').toLowerCase()
      const ctx = (d.ctx || '').toLowerCase()
      return c.includes(typeQuery.toLowerCase()) || ctx.includes(typeQuery.toLowerCase()) ? '' : 'inactive'
    })
    svg.selectAll('.texts text').attr('class', d => {
      const c = (d.class || '').toLowerCase()
      const ctx = (d.ctx || '').toLowerCase()
      return c.includes(typeQuery.toLowerCase()) || ctx.includes(typeQuery.toLowerCase()) ? '' : 'inactive'
    })
    svg.selectAll('.links line').attr('class', 'inactive')
  }
}

defineExpose({ hoverType, hoverId, search })
</script>

<style>
.force-svg {
  width: 100%;
  height: 100%;
}

.links line {
  stroke: #fff;
  stroke-opacity: 0.5;
}

.links line.inactive {
  stroke-opacity: 0.05;
}

.nodes circle {
  cursor: pointer;
}

.nodes circle.inactive {
  opacity: 0.15;
}

.texts text {
  cursor: pointer;
}

.texts text.inactive {
  opacity: 0.15;
}

.texts text:hover {
  cursor: pointer;
}
</style>
