---
name: yoda-os-card
description: "This skill should be used when the user wants to generate UI cards for YodaOS Sprite (Rokid AR glasses). It strictly follows the official YodaOS-Sprite design specification and the Google A2UI v0.8 protocol: the Agent outputs A2UI JSONL (surfaceUpdate + dataModelUpdate + beginRendering), and the renderer parses JSONL and renders HTML. Primary color #40FF5E on dark background, HarmonyOS Sans SC font, 12px border-radius, linear icons, no gradients. Supported card types: weather, fund/stock, music, notification, express, and custom. Trigger when user mentions Yoda, YodaOS, Sprite, Rokid, AR卡片, 眼镜卡片, or asks to generate a card."
---

# YodaOS Sprite 卡片生成器（A2UI 协议）

严格按照官方 YodaOS-Sprite 设计规范 + Google A2UI v0.8 协议。

## 架构说明

```
┌─────────────────────────┐     JSONL 流      ┌────────────────────────────┐
│   Agent（LLM 侧）        │ ────────────────► │   Renderer（客户端侧）      │
│   generate_a2ui.py      │  surfaceUpdate    │   render_a2ui.py           │
│                         │  dataModelUpdate  │                            │
│   输出 A2UI JSONL        │  beginRendering   │   解析 JSONL → 渲染 HTML    │
└─────────────────────────┘                   └────────────────────────────┘
```

- **`scripts/generate_a2ui.py`** — Agent 侧：根据卡片类型和数据，输出 A2UI v0.8 协议 JSONL
- **`scripts/render_a2ui.py`**  — 客户端侧：解析 JSONL，绑定数据，渲染为符合 YodaOS-Sprite 规范的 HTML
- **`references/design-spec.md`** — 完整设计规范 + A2UI 协议说明 + Catalog 组件表

## 设计规范速查

详细规范见 `references/design-spec.md`。核心要点：

| 规范项 | 值 |
|---|---|
| 主色 | `#40FF5E`（绿色，不可改） |
| 背景色 | `#000000` / `#1C1C1C` 深色 |
| 字体 | HarmonyOS Sans SC |
| 圆角 | 12px |
| 描边 | 2px，使用主色 |
| 卡片分辨率 | 480×400px（宽×高） |
| 最小字号 | caption 13px / button 15px |
| 禁忌 | 禁用渐变、禁用大面积高亮色 |
| 图标 | 线性 SVG |

## 支持的卡片类型

| 类型 | 中文名 |
|---|---|
| `weather` | 天气卡片 |
| `fund` | 基金/股票卡片 |
| `music` | 音乐播放卡片 |
| `notify` | 通知卡片 |
| `express` | 快递物流卡片 |
| `custom` | 自定义数据卡片 |

## 工作流

### 步骤 1：生成 A2UI JSONL（Agent 侧）

To generate A2UI JSONL for a card, run `scripts/generate_a2ui.py`:

```bash
# 输出到文件
python3 ~/.workbuddy/skills/yoda-os-card/scripts/generate_a2ui.py \
  --type weather \
  --output /path/to/output.jsonl

# 自定义数据
python3 ~/.workbuddy/skills/yoda-os-card/scripts/generate_a2ui.py \
  --type weather \
  --data '{"city":"上海","temp":"12","weather_icon":"sunny","high":"15","low":"8"}' \
  --output /path/to/output.jsonl

# 输出到 stdout（可直接 pipe 给渲染器）
python3 ~/.workbuddy/skills/yoda-os-card/scripts/generate_a2ui.py --type express
```

### 步骤 2：渲染为 HTML（客户端侧）

To render JSONL to HTML, run `scripts/render_a2ui.py`:

```bash
# 从文件读取
python3 ~/.workbuddy/skills/yoda-os-card/scripts/render_a2ui.py \
  --input /path/to/output.jsonl \
  --output /path/to/card.html

# 一步完成（pipe）
python3 ~/.workbuddy/skills/yoda-os-card/scripts/generate_a2ui.py --type express | \
  python3 ~/.workbuddy/skills/yoda-os-card/scripts/render_a2ui.py --output /path/to/express.html
```

### 步骤 3：一键生成（generate + render 串联）

To generate and render in one step:

```bash
TYPE=weather && \
python3 ~/.workbuddy/skills/yoda-os-card/scripts/generate_a2ui.py --type $TYPE | \
python3 ~/.workbuddy/skills/yoda-os-card/scripts/render_a2ui.py --output /tmp/${TYPE}_card.html
```

## 各类型数据字段

**天气卡片 `weather`：**
```json
{
  "city": "北京",
  "temp": "1",
  "weather_icon": "sunny",
  "high": "-3",
  "low": "-10",
  "hourly": [
    {"time": "现在",  "icon": "sunny",          "temp": "1°"},
    {"time": "20:00", "icon": "cloudy_drizzle", "temp": "1°"},
    {"time": "21:00", "icon": "snow",           "temp": "-1°"}
  ]
}
```
可用天气图标：`sunny` / `cloudy` / `cloudy_drizzle` / `snow`

**基金卡片 `fund`：**
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

**音乐卡片 `music`：**
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

**通知卡片 `notify`：**
```json
{
  "app_name": "微信",
  "title": "通知标题",
  "content": "通知内容",
  "time": "刚刚",
  "btn_text": "查看"
}
```

**快递卡片 `express`：**
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

**自定义卡片 `custom`：**
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

## A2UI 协议输出示例（LLM 直接生成）

When asked to generate a card, the LLM can also directly output A2UI JSONL without running the script.
The output must follow the protocol order: `surfaceUpdate` → `dataModelUpdate` → `beginRendering`.

Example (minimal text card):
```jsonl
{"surfaceUpdate":{"surfaceId":"demo","components":[{"id":"root","component":{"Column":{"children":{"explicitList":["title","body"]},"spacing":{"literalNumber":12}}}},{"id":"title","component":{"Text":{"text":{"path":"/title","literalString":"标题"},"usageHint":{"literalString":"subtitle"}}}},{"id":"body","component":{"Text":{"text":{"path":"/content","literalString":"内容"},"usageHint":{"literalString":"body"},"colorHint":{"literalString":"dim"}}}}]}}
{"dataModelUpdate":{"surfaceId":"demo","contents":[{"key":"title","valueString":"你好 YodaOS"},{"key":"content","valueString":"这是一张演示卡片"}]}}
{"beginRendering":{"surfaceId":"demo","root":"root","catalog":"yoda-os-sprite-v1"}}
```

Then pipe to `render_a2ui.py` to get HTML.

## 扩展说明

- To add a new card type: add a `build_xxx(data)` function in `generate_a2ui.py` following the `surfaceUpdate → dataModelUpdate → beginRendering` pattern, then register in `BUILDERS`.
- To add a new catalog component: implement `_render_xxx()` method in `YodaOSRenderer` in `render_a2ui.py`.
- All design tokens are centralized in `TOKENS` dict in `render_a2ui.py`.
- The old `generate_card.py` (direct HTML generation) is deprecated in favor of the A2UI pipeline.
