# YodaOS Sprite 设计规范 + A2UI 协议说明

## 一、YodaOS-Sprite 设计规范（Rokid Inc.）

### 字体
- 统一使用：**HarmonyOS Sans SC**（Regular 400 / Medium 500 / Bold 600）

### 字号与行高
| 语义 usageHint | 字号 | 行高 |
|---|---|---|
| display | 52px | 60px |
| title (h2) | 24px | 30px |
| subtitle | 20px | 26px |
| body | 16px | 22px |
| caption | 13px | 18px |
| button | 15px | 20px |

### 颜色
| 变量 | 值 | 用途 |
|---|---|---|
| color_primary | `#40FF5E` | 文字、图标、描边（**唯一亮色**） |
| color_bg_card | `#1C1C1C` | 卡片背景 |
| color_bg_dark | `#000000` | 页面背景 |
| color_dim | `rgba(64,255,94,0.55)` | 辅助文字 |
| color_positive | `#40FF5E` | 涨（正向） |
| color_negative | `#FF4040` | 跌（负向） |

### 禁忌
- **禁用渐变**（fill 区域除外，折线图可用渐变填充）
- **禁用大面积高亮色**
- 图标统一用**线性 SVG**

### 描边 & 圆角
- 卡片外框：`border: 2px solid #40FF5E; border-radius: 12px`
- 按钮：`border: 2px solid #40FF5E; border-radius: 12px`
- 细描边：`border: 1.5px solid rgba(64,255,94,0.4)`

### 画布
- 标准宽度：480px，最佳显示区域：480×400px

---

## 二、A2UI v0.8 协议（Google）

> 官方规范：https://a2ui.org/specification/v0.8-a2ui/

### 核心思想
A2UI（Agent to UI）是 Google 发布的声明式生成式 UI 协议，使 AI Agent 能够以 JSONL 流的形式描述 UI，由客户端（渲染器）将其映射到具体平台组件后渲染。

### 三种核心消息（JSONL，每行一条）

**1. surfaceUpdate** — 定义/更新组件树（结构）
```json
{
  "surfaceUpdate": {
    "surfaceId": "my_card",
    "components": [
      {
        "id": "root",
        "component": {
          "Column": {
            "children": { "explicitList": ["title", "body"] },
            "spacing": { "literalNumber": 12 }
          }
        }
      },
      {
        "id": "title",
        "component": {
          "Text": {
            "text": { "path": "/title", "literalString": "默认标题" },
            "usageHint": { "literalString": "subtitle" }
          }
        }
      }
    ]
  }
}
```

**2. dataModelUpdate** — 填充数据（与结构解耦）
```json
{
  "dataModelUpdate": {
    "surfaceId": "my_card",
    "contents": [
      { "key": "title",  "valueString": "实际标题" },
      { "key": "count",  "valueNumber": 42 },
      { "key": "active", "valueBoolean": true },
      { "key": "nested", "valueMap": [
          { "key": "field", "valueString": "value" }
        ]
      },
      { "key": "list", "valueArray": [
          { "key": "0", "valueString": "item0" }
        ]
      }
    ]
  }
}
```

**3. beginRendering** — 触发渲染
```json
{
  "beginRendering": {
    "surfaceId": "my_card",
    "root": "root",
    "catalog": "yoda-os-sprite-v1"
  }
}
```

### BoundValue 数据绑定
```json
{ "literalString": "静态文本" }      // 字面量
{ "literalNumber": 42 }              // 数字字面量
{ "literalBoolean": true }           // 布尔字面量
{ "path": "/data/field" }            // 路径绑定（读 dataModel）
{ "path": "/data/field", "literalString": "默认值" }  // 路径 + 默认值
```

### JSONL 消息顺序
```
surfaceUpdate → dataModelUpdate → beginRendering
```

---

## 三、YodaOS-Sprite Catalog（本 Skill 实现的组件目录）

catalog id: `yoda-os-sprite-v1`

### 布局组件
| 组件 | 主要属性 |
|---|---|
| Column | children, spacing, alignment |
| Row | children, spacing, alignment |
| Card | child |
| Spacer | flex |
| Divider | — |

### 内容组件
| 组件 | 主要属性 |
|---|---|
| Text | text(BV), usageHint(BV), colorHint(BV) |
| Icon | name(BV), size(BV), bordered(BV) |
| Dot | size(BV) |
| ProgressIndicator | type(BV: linear/circular), value(BV: 0~1) |
| Chart | type(BV: sparkline), data(BV), width(BV), height(BV) |
| TimelineItem | description(BV), timestamp(BV), isLatest(BV) |

### 交互组件
| 组件 | 主要属性 |
|---|---|
| Button | child(组件ID), action{name(BV), context} |

### colorHint 取值
| 值 | 颜色 |
|---|---|
| primary | #40FF5E |
| dim | rgba(64,255,94,0.55) |
| positive | #40FF5E |
| negative | #FF4040 |

### usageHint 取值
`display` / `title` / `subtitle` / `body` / `caption` / `button` / `h1` / `h2`
