# YodaOS Sprite 场景卡片库

> Rokid Glasses · 音视分离体验设计系统
>
> 协议：A2UI v0.8 | 设计规范：YodaOS Sprite v1 | 画布：480 × 400px

## 项目概述

本项目是 **YodaOS Sprite** 的场景卡片库实现，基于 Google **A2UI v0.8** 协议构建。核心目标是为 Rokid Glasses提供一套统一、高可用的 UI 卡片生成方案，使 AI Agent 能够通过声明式 JSONL 流描述 UI，由客户端渲染器映射为符合设计规范的 HTML 卡片。

### 核心特性

- **A2UI 协议**：遵循 Google A2UI v0.8，Agent 输出 JSONL 流，客户端解析渲染
- **6 种卡片类型**：天气、基金/股票、音乐、通知、快递、自定义数据
- **YodaOS 设计规范**：深色背景 + 荧光绿主色（#40FF5E），HarmonyOS Sans SC 字体
- **35+ 场景卡片**：涵盖副屏辅助、主屏辅助、主动填充、日常高频、趣味休闲等场景

## 目录结构

```
yoda-os-card/
├── SKILL.md                    # CodeBuddy Skill 配置文档
├── README.md                   # 本文档
├── scripts/                    # 核心脚本
│   ├── generate_a2ui.py        # A2UI JSONL 生成器（Agent 侧）
│   └── render_a2ui.py          # HTML 渲染器（客户端侧）
├── references/                 # 设计规范
│   └── design-spec.md          # 完整设计规范 + A2UI 协议说明
└── assets/                     # 场景卡片资源
    ├── index.html              # 场景卡片库索引页
    └── scenes/                 # 35 个场景卡片 HTML
```

## 设计规范速查

| 规范项 | 值 |
|--------|-----|
| 主色 | `#40FF5E`（荧光绿，不可改） |
| 背景色 | `#000000`（页面）/ `#1C1C1C`（卡片） |
| 字体 | HarmonyOS Sans SC |
| 圆角 | 12px |
| 描边 | 2px solid #40FF5E |
| 卡片分辨率 | 480 × 400px |
| 最小字号 | caption 13px / button 15px |
| **禁忌** | 禁用渐变、禁用大面积高亮色 |
| 图标 | 线性 SVG |

### 字号系统

| usageHint | 字号 | 行高 |
|-----------|------|------|
| display | 52px | 60px |
| title / h2 | 24px | 30px |
| subtitle | 20px | 26px |
| body | 16px | 22px |
| caption | 13px | 18px |
| button | 15px | 20px |

## 快速开始

### 环境要求

- Python 3.8+

### 安装

```bash
# 无需安装，直接使用
cd /Users/iotarray/Desktop/yoda-os-card
```

### 预览场景卡片

直接在浏览器打开 `assets/index.html`，点击任意卡片进入查看：

```bash
open assets/index.html
```

### 生成 A2UI JSONL

```bash
# 生成天气卡片
python3 scripts/generate_a2ui.py --type weather --output weather.jsonl

# 生成带自定义数据的天气卡片
python3 scripts/generate_a2ui.py \
  --type weather \
  --data '{"city":"上海","temp":"12","weather_icon":"sunny","high":"15","low":"8"}' \
  --output weather.jsonl

# 输出到 stdout（管道给渲染器）
python3 scripts/generate_a2ui.py --type express
```

### 渲染为 HTML

```bash
# 从文件读取
python3 scripts/render_a2ui.py --input weather.jsonl --output weather_card.html

# 从 stdin 读取
cat weather.jsonl | python3 scripts/render_a2ui.py --output weather_card.html
```

### 一键生成（推荐）

```bash
# 生成 + 渲染一步完成
TYPE=weather && \
python3 scripts/generate_a2ui.py --type $TYPE | \
python3 scripts/render_a2ui.py --output /tmp/${TYPE}_card.html

# 查看生成的卡片
open /tmp/weather_card.html
```

## 支持的卡片类型

| 类型 | 中文名 | 典型场景 |
|------|--------|----------|
| `weather` | 天气卡片 | 当前天气 + 逐小时预报 + 出行建议 |
| `fund` | 基金/股票卡片 | 实时行情 + 涨跌幅 + 迷你走势图 |
| `music` | 音乐播放卡片 | 播放控制 + 进度条 + 歌词 |
| `notify` | 通知卡片 | 消息提醒 + 快捷回复 |
| `express` | 快递物流卡片 | 全流程追踪 + 时间线 |
| `custom` | 自定义数据卡片 | 通用数据展示 |

### 各类型数据字段

#### 天气卡片 `weather`

```json
{
  "city": "北京",
  "temp": "1",
  "weather_icon": "sunny",
  "high": "-3",
  "low": "-10",
  "hourly": [
    {"time": "现在", "icon": "sunny", "temp": "1°"},
    {"time": "20:00", "icon": "cloudy_drizzle", "temp": "1°"},
    {"time": "21:00", "icon": "snow", "temp": "-1°"}
  ]
}
```

可用天气图标：`sunny` / `cloudy` / `cloudy_drizzle` / `snow`

#### 基金卡片 `fund`

```json
{
  "buy_price": "1194.36",
  "sell_price": "1191.17",
  "change_pct": "+3.20%",
  "update_time": "2026-03-02 19:29:37",
  "btn_left": "看看昨天",
  "btn_right": "看看明天",
  "chart_data": [40, 42, 38, 45, 50, 53, 58, 60]
}
```

#### 音乐卡片 `music`

```json
{
  "title": "歌曲名",
  "artist": "歌手名",
  "progress": 35,
  "current_time": "1:23",
  "total_time": "3:45",
  "is_playing": true
}
```

#### 通知卡片 `notify`

```json
{
  "app_name": "微信",
  "title": "通知标题",
  "content": "通知内容",
  "time": "刚刚",
  "btn_text": "查看"
}
```

#### 快递卡片 `express`

```json
{
  "company": "顺丰速运",
  "tracking_no": "SF1234567890123",
  "status": "派送中",
  "status_sub": "快递员正在配送，请保持手机畅通",
  "eta": "预计今日送达",
  "progress": 75,
  "steps": ["已揽收","运输中","到达驿站","派送中","已签收"],
  "current_step": 3,
  "tracks": [
    {"desc": "快递员正在派送", "time": "2026-03-27 17:42", "latest": true},
    {"desc": "到达北京朝阳营业部", "time": "2026-03-27 09:15"}
  ],
  "btn_left": "联系快递员",
  "btn_right": "查看详情"
}
```

#### 自定义卡片 `custom`

```json
{
  "title": "卡片标题",
  "subtitle": "副标题（可选）",
  "items": [
    {"label": "数据项", "value": "数值"}
  ],
  "buttons": ["按钮文本"],
  "footer": "底部备注（可选）"
}
```

## 场景卡片库

场景卡片库按用户注意力分配分为三类：

### A 类 · 副屏辅助

用户主注意力在别处，卡片作为副屏提供极简信息：

| 场景 | 描述 |
|------|------|
| 🍳 烹饪辅助 | 步骤、计时、用量、火候极简呈现 |
| 🏃 健康运动 | 心率区间 + 配速 + 里程数 + 警告 |
| 🚗 驾驶辅助 | 大号速度数字 + 超速警告 + 疲劳提醒 |

### B 类 · 主屏辅助

用户正在处理信息本身，卡片提供核心辅助：

| 场景 | 描述 |
|------|------|
| 🗺️ 导航 | 路线规划 + 转弯提示 + 到达总结 |
| 🌐 实时翻译 | 待机 + 识别中 + 大字译文 + 历史回顾 |
| 💼 会议 | 等待开始 + 发言人 + AI摘要 + 决策确认 |
| 📖 学习辅助 | 生词卡 + 知识关联 + 进度 + 测验 |

### C 类 · 主动填充

用户正在等待或过渡，卡片主动填充内容：

| 场景 | 描述 |
|------|------|
| 🍔 餐饮点单 | 扫描菜单 + 推荐 + 已点 + 等待出餐 |
| 🛍️ 购物比价 | 识别 + 多平台比价 + 评价摘要 |
| 📦 快递追踪 | 已下单 + 运输中 + 派送中 + 签收 |

### 日常高频

贯穿全天的基础服务场景：

| 场景 | 描述 |
|------|------|
| 📞 通话/消息 | 来电提醒 + 通话中 + 消息列表 |
| 💳 支付 | 扫码收款 + 支付成功 + 收款通知 |
| 📅 日程提醒 | 今日概览 + 出发提醒 + 进行中 |
| 🎵 音乐播放 | 播放中 + 暂停 + 歌词模式 |
| ❤️ 健康监测 | 心率 + 血氧 + 睡眠报告 |
| 🌤️ 天气出行 | 当前天气 + 逐小时 + 穿衣建议 |
| 🏠 智能家居 | 设备总览 + 温控 + 场景模式 |
| 👤 社交识别 | 扫描识别 + 熟人信息 + 名片分享 |
| 🚇 停车/交通 | 寻找停车 + 计时 + 打车出行 |
| ✈️ 购票核验 | 电子登机牌 + 核验 + 候车 |

### 趣味休闲

| 场景 | 描述 |
|------|------|
| 🀄 麻将辅助 | 牌面识别 + 出牌建议 + 听牌模式 |
| 🃏 扑克辅助 | 手牌展示 + 胜率分析 + 出牌建议 |

## A2UI 协议说明

### 三种核心消息

```
surfaceUpdate  → dataModelUpdate  → beginRendering
  (定义组件树)     (填充数据)          (触发渲染)
```

**1. surfaceUpdate** — 定义组件树结构

```json
{"surfaceUpdate":{"surfaceId":"my_card","components":[
  {"id":"root","component":{"Column":{"children":{"explicitList":["title","body"]},"spacing":{"literalNumber":12}}}},
  {"id":"title","component":{"Text":{"text":{"path":"/title","literalString":"默认标题"},"usageHint":{"literalString":"subtitle"}}}}
]}}
```

**2. dataModelUpdate** — 填充数据（与结构解耦）

```json
{"dataModelUpdate":{"surfaceId":"my_card","contents":[
  {"key":"title","valueString":"实际标题"}
]}}
```

**3. beginRendering** — 触发渲染

```json
{"beginRendering":{"surfaceId":"my_card","root":"root","catalog":"yoda-os-sprite-v1"}}
```

### BoundValue 数据绑定

```json
{ "literalString": "静态文本" }      // 字面量
{ "literalNumber": 42 }              // 数字字面量
{ "path": "/data/field" }           // 路径绑定
{ "path": "/data/field", "literalString": "默认值" }  // 路径 + 默认值
```

### Catalog 组件目录

catalog id: `yoda-os-sprite-v1`

#### 布局组件

| 组件 | 主要属性 |
|------|----------|
| Column | children, spacing, alignment |
| Row | children, spacing, alignment |
| Card | child |
| Spacer | flex |
| Divider | — |

#### 内容组件

| 组件 | 主要属性 |
|------|----------|
| Text | text(BV), usageHint(BV), colorHint(BV) |
| Icon | name(BV), size(BV), bordered(BV) |
| Dot | size(BV) |
| ProgressIndicator | type(BV), value(BV: 0~1) |
| Chart | type(BV), data(BV), width(BV), height(BV) |
| TimelineItem | description(BV), timestamp(BV), isLatest(BV) |

#### 交互组件

| 组件 | 主要属性 |
|------|----------|
| Button | child, action{name(BV), context} |
| Expandable | header, content, expanded(BV) |

## 扩展指南

### 添加新卡片类型

1. 在 `generate_a2ui.py` 中添加 `build_xxx(data)` 函数，遵循 `surfaceUpdate → dataModelUpdate → beginRendering` 模式
2. 在 `BUILDERS` 字典中注册新类型
3. 在 `render_a2ui.py` 的 `YodaOSRenderer` 中添加对应的 `_render_xxx()` 方法

### 添加新场景卡片

1. 在 `assets/scenes/` 目录创建新的 HTML 文件
2. 参考现有卡片结构和设计规范
3. 在 `assets/index.html` 中添加入口卡片

### 设计规范集中管理

所有设计 Token 集中在 `render_a2ui.py` 的 `TOKENS` 字典中：

```python
TOKENS = {
    "color_primary":  "#40FF5E",
    "color_bg_card":  "#1C1C1C",
    "color_bg_dark":  "#000000",
    "color_dim":      "rgba(64,255,94,0.55)",
    "border_radius":  12,
    "border_width":   2,
    "font_family":    "'HarmonyOS Sans SC',...",
    "usage_hints": {...},   # 字号系统
    "icons": {...},         # SVG 图标库
}
```

## 技术栈

- **协议**：Google A2UI v0.8
- **生成器**：Python 3.8+ / JSONL
- **渲染器**：Python 3.8+ / HTML + CSS + SVG
- **前端**：纯 HTML + CSS + Vanilla JS（无框架依赖）

## 相关资源

- [A2UI v0.8 官方规范](https://a2ui.org/specification/v0.8-a2ui/)
- [YodaOS Sprite 设计系统](references/design-spec.md)

## 许可证

本项目仅供 Rokid YodaOS Sprite 生态使用。
