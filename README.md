# 基于关联图谱的企业关系识别

> 🏆 **"随e融杯"金融大数据建模挑战赛 一等奖**

"江苏银行"杯金融大数据建模挑战赛参赛作品。通过构建企业关联关系图谱，分析企业间的控制关系、担保关系与资金归集关系，识别对公客户关联网络中的潜在风险点。

**作者**：陈志* 李正*

---

## 项目结构

```
.
├── index.html                     # 入口 HTML
├── vite.config.js                 # Vite 构建配置
├── package.json                   # 前端依赖 (Vue3 + D3.js + Vue Router)
│
├── backend/                       # Python 数据处理后端
│   ├── __init__.py                # 包声明
│   ├── main.py                    # 数据处理入口，串联三大模块
│   ├── control.py                 # 控制关系分析：读取控制人数据 → 构建有向图 → 识别根节点 → 导出 JSON
│   ├── guarantee.py               # 担保关系分析：担保网络构建 → 风险评估标记 → 风险量化 → 导出 JSON
│   └── moneyCollection.py         # 资金归集分析：交易流水解析 → 壳企业识别 → 净收入计算 → 导出 JSON
│
├── src/                           # 前端源码 (Vue3)
│   ├── main.js                    # 应用入口，挂载 Vue Router
│   ├── App.vue                    # 根组件 (router-view)
│   ├── router/
│   │   └── index.js               # 路由配置：首页 / 控制关系 / 担保关系 / 资金归集
│   ├── pages/
│   │   ├── HomePage.vue           # 首页：项目标题、作者、导航入口、操作指南
│   │   ├── ControlPage.vue        # 控制关系页面：加载控制关系图谱数据
│   │   ├── GuaranteePage.vue      # 担保关系页面：加载担保关系图谱数据
│   │   └── MoneyCollectionPage.vue # 资金归集页面：加载资金归集图谱数据
│   ├── components/
│   │   ├── ForceGraph.vue         # 核心力导向图组件（D3-force 布局）
│   │   └── ForceGraphPage.vue     # 图谱页面通用包装组件（搜索、视图切换等）
│   └── styles/
│       └── global.css             # 全局样式
│
├── public/
│   └── data/                      # 前端可视化用的 JSON 图谱数据
│       ├── control_json/          # 控制关系图谱数据（圆形 / 交叉 / 多层 / 双重子图等）
│       ├── guarantee_json/        # 担保关系图谱数据（圆形 / 交叉 / 多层等）
│       └── moneyCollection_json/  # 资金归集图谱数据（多层子图等）
│
└── dist/                          # 构建产物（同 public/data 结构）
    └── data/
```

---

## 功能模块

### 1. 控制关系分析 (Control)

识别企业间的控制人关系网络，通过构建有向图找出被同一控制人实际控制的企业群，揭示隐性关联风险。

### 2. 担保关系分析 (Guarantee)

分析企业间的担保网络，对担保链条进行风险标记和量化评估，识别互保圈、担保集中度等风险模式。

### 3. 资金归集分析 (Money Collection)

解析企业间交易流水，识别资金归集行为——通过壳企业将资金集中到实际控制方，挖掘潜在的异常资金流动。

---

## 技术栈

| 层级 | 技术 |
|------|------|
| **前端框架** | Vue 3 (Composition API + `<script setup>`) |
| **可视化** | D3.js v7（力导向图布局、缩放平移、节点交互） |
| **路由** | Vue Router 4 (Hash 模式) |
| **构建工具** | Vite 8 |
| **后端/数据处理** | Python 3（networkx + pandas + matplotlib） |

---

## 快速开始

### 前端

```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build
```

### 后端数据预处理

```bash
# 在项目根目录执行，从 CSV 生成前端所需的 JSON 图谱数据
python -m backend.main
```

> 注意：原始 CSV 数据位于 `backend/res/` 下，由于数据保密需要已做脱敏处理。使用者可根据不同风险类型的代码自定义数据。

---

## 可视化交互说明

- **搜索框**：支持按节点类型 (search by type) 或按节点 ID (search by id) 在子图中查找节点
- **视图切换**：默认圆形展示，可切换到 ID 文本展示模式
- **缩放**：鼠标滚轮缩放可视化界面
- **平移**：左键拖拽移动视图
- **节点聚焦**：鼠标悬停节点时，右上角显示节点 ID 和类型，仅高亮该节点所在子图，其余子图半透明处理
- **子图切换**：选择不同类型子图（圆形子图、交叉子图、多层子图、双重子图等）进行切换查看

