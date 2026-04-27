<template>
  <div class="home-bg">
    <h1 class="title">"江苏银行"杯金融大数据建模挑战赛</h1>
    <h1 class="subtitle">—— 基于关联图谱的企业关系识别</h1>
    <p class="authors">作者：陈志祥 李正材</p>

    <div class="mode">
      <router-link to="/control">控制关系</router-link>
      <router-link to="/guarantee">担保关系</router-link>
      <router-link to="/money-collection">资金归集关系</router-link>
    </div>

    <div class="guide">
      <h3>操作指南</h3>
      <ol>
        <li><strong>搜索框：</strong>'search by type'：通过节点类型在子图中查找节点<br>'search by id'：通过节点id在子图中查找节点</li>
        <li>界面默认展示为圆形展示，可点击text按键切换到id展示</li>
        <li><strong>缩放功能：</strong>在图形区域通过滑动鼠标滚轮实现可视化界面缩放</li>
        <li><strong>可视化界面移动功能：</strong>左键点击并按住左键进行拖拽</li>
        <li><strong>鼠标指针交互事件：</strong>鼠标指针移动到某一节点后，右上角显示该节点的id和类型，且只保留该节点所在的子图，其他子图做半透明处理</li>
      </ol>
    </div>
  </div>
</template>

<script setup>
</script>

<style scoped>
.home-bg {
  min-height: 100vh;
  background-color: #272b30;
  text-align: center;
  padding: 60px 40px;
}

.title {
  color: #fff;
  font-size: 30px;
  margin-bottom: 10px;
}

.subtitle {
  color: #fff;
  font-size: 25px;
  margin-bottom: 20px;
}

.authors {
  color: #fff;
  font-size: 20px;
  margin-bottom: 60px;
}

.mode {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-bottom: 60px;
}

.mode a {
  display: inline-block;
  border: 1px solid #fff;
  color: #f2f2f2;
  padding: 12px 30px;
  border-radius: 4px;
  font-size: 18px;
  transition: all 0.3s;
  cursor: pointer;
}

.mode a:hover,
.mode a.router-link-active {
  background-color: white;
  color: #333;
}

.guide {
  position: absolute;
  left: 30px;
  top: 180px;
  text-align: left;
  max-width: 300px;
}

.guide h3 {
  color: #afaaaa;
  font-size: 16px;
  margin-bottom: 10px;
}

.guide ol {
  list-style: decimal;
  padding-left: 20px;
  color: #afaaaa;
  font-size: 13px;
  line-height: 1.8;
}
</style>
