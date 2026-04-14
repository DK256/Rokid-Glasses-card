#!/usr/bin/env python3
"""
YodaOS Sprite 卡片 —— A2UI JSONL 生成器（Agent 侧）
=====================================================
遵循 Google A2UI v0.8 协议（https://a2ui.org/specification/v0.8-a2ui/）

工作原理：
  1. Agent 调用本脚本，输出符合 A2UI 协议的 JSONL 字符串
  2. 客户端（渲染器）解析 JSONL，绑定数据，渲染成实际 UI

协议消息顺序：
  surfaceUpdate（组件树）→ dataModelUpdate（数据）→ beginRendering（触发渲染）

用法:
  python3 generate_a2ui.py --type weather --output weather.jsonl
  python3 generate_a2ui.py --type fund    --data '{"buy_price":"1194.36",...}' --output fund.jsonl
  python3 generate_a2ui.py --type express --output express.jsonl
  python3 generate_a2ui.py --type music   --output music.jsonl
  python3 generate_a2ui.py --type notify  --output notify.jsonl
  python3 generate_a2ui.py --type custom  --output custom.jsonl

支持卡片类型:
  weather  - 天气卡片
  fund     - 基金/股票卡片
  music    - 音乐播放卡片
  notify   - 通知消息卡片
  express  - 快递物流卡片
  custom   - 自定义数据卡片
"""

import argparse
import json
import sys
from datetime import datetime


# ─────────────────────────────────────────────
# A2UI 协议消息构建工具函数
# ─────────────────────────────────────────────

def lit(s: str) -> dict:
    """字面量字符串绑定值"""
    return {"literalString": str(s)}

def lit_num(n) -> dict:
    """字面量数字绑定值"""
    return {"literalNumber": n}

def lit_bool(b: bool) -> dict:
    """字面量布尔绑定值"""
    return {"literalBoolean": b}

def path_bind(p: str, default: str = None) -> dict:
    """数据路径绑定，可附带默认字面量"""
    v = {"path": p}
    if default is not None:
        v["literalString"] = default
    return v

def component(cid: str, ctype: str, props: dict) -> dict:
    """构建组件对象"""
    return {"id": cid, "component": {ctype: props}}

def surface_update(surface_id: str, components: list) -> dict:
    """surfaceUpdate 消息"""
    return {"surfaceUpdate": {"surfaceId": surface_id, "components": components}}

def data_model_update(surface_id: str, contents: list, path: str = None) -> dict:
    """dataModelUpdate 消息"""
    msg = {"surfaceId": surface_id, "contents": contents}
    if path:
        msg["path"] = path
    return {"dataModelUpdate": msg}

def begin_rendering(surface_id: str, root_id: str) -> dict:
    """beginRendering 消息"""
    return {"beginRendering": {
        "surfaceId": surface_id,
        "root": root_id,
        "catalog": "yoda-os-sprite-v1"
    }}

def kv(key: str, value) -> dict:
    """构建 dataModelUpdate contents 中的 key-value 条目"""
    if isinstance(value, str):
        return {"key": key, "valueString": value}
    elif isinstance(value, bool):
        return {"key": key, "valueBoolean": value}
    elif isinstance(value, (int, float)):
        return {"key": key, "valueNumber": value}
    elif isinstance(value, list):
        return {"key": key, "valueArray": value}
    elif isinstance(value, dict):
        return {"key": key, "valueMap": [kv(k, v) for k, v in value.items()]}
    return {"key": key, "valueString": str(value)}

def kv_map(key: str, items: list) -> dict:
    """嵌套 map 类型"""
    return {"key": key, "valueMap": items}

def kv_arr(key: str, items: list) -> dict:
    """数组类型"""
    return {"key": key, "valueArray": items}

def to_jsonl(messages: list) -> str:
    """将消息列表序列化为 JSONL 字符串"""
    return "\n".join(json.dumps(m, ensure_ascii=False) for m in messages)


# ─────────────────────────────────────────────
# 天气卡片
# ─────────────────────────────────────────────
def build_weather(data: dict) -> list:
    sid = "weather_card"
    city = data.get("city", "北京")
    temp = data.get("temp", "1")
    weather_icon = data.get("weather_icon", "sunny")
    high = data.get("high", "-3")
    low = data.get("low", "-10")
    hourly = data.get("hourly", [
        {"time": "现在",  "icon": "sunny",          "temp": "1°"},
        {"time": "20:00", "icon": "cloudy_drizzle", "temp": "1°"},
        {"time": "21:00", "icon": "snow",           "temp": "-1°"},
    ])

    # ── 1. surfaceUpdate：定义组件树结构 ──
    hourly_ids = [f"hourly_{i}" for i in range(len(hourly))]
    components = [
        # 根容器
        component("root", "Column", {
            "children": {"explicitList": ["card_header", "status_row", "hourly_row"]},
            "spacing": {"literalNumber": 10}
        }),
        # 顶部行：城市名 + 高低温
        component("card_header", "Row", {
            "children": {"explicitList": ["city_icon", "city_name", "spacer_hl", "high_low_block"]},
            "alignment": {"literalString": "center"}
        }),
        component("city_icon", "Icon", {"name": lit("location"), "size": lit_num(16)}),
        component("city_name",  "Text", {"text": path_bind("/city", city), "usageHint": lit("body")}),
        component("spacer_hl",  "Spacer", {"flex": lit_num(1)}),
        component("high_low_block", "Column", {
            "children": {"explicitList": ["hl_label_row", "hl_value_row"]},
            "alignment": {"literalString": "end"}
        }),
        component("hl_label_row", "Row", {
            "children": {"explicitList": ["lbl_high", "lbl_low"]},
            "spacing": {"literalNumber": 24}
        }),
        component("lbl_high", "Text", {"text": lit("最高"), "usageHint": lit("caption")}),
        component("lbl_low",  "Text", {"text": lit("最低"), "usageHint": lit("caption")}),
        component("hl_value_row", "Row", {
            "children": {"explicitList": ["val_high", "val_low"]},
            "spacing": {"literalNumber": 16}
        }),
        component("val_high", "Text", {"text": path_bind("/high", high), "usageHint": lit("title")}),
        component("val_low",  "Text", {"text": path_bind("/low",  low),  "usageHint": lit("title")}),
        # 主状态行：图标 + 温度
        component("status_row", "Row", {
            "children": {"explicitList": ["weather_icon_comp", "temp_text"]},
            "alignment": {"literalString": "center"},
            "spacing": {"literalNumber": 10}
        }),
        component("weather_icon_comp", "Icon", {
            "name":  path_bind("/weather_icon", weather_icon),
            "size":  lit_num(48)
        }),
        component("temp_text", "Text", {
            "text":      path_bind("/temp_display", f"{temp}°"),
            "usageHint": lit("display")
        }),
        # 逐小时预报行
        component("hourly_row", "Row", {
            "children": {"explicitList": hourly_ids},
            "spacing":  {"literalNumber": 0}
        }),
    ]
    for i, hid in enumerate(hourly_ids):
        components.append(
            component(hid, "Column", {
                "children": {"explicitList": [f"h_time_{i}", f"h_icon_{i}", f"h_temp_{i}"]},
                "alignment": {"literalString": "center"},
                "spacing":   {"literalNumber": 4}
            })
        )
        components.append(component(f"h_time_{i}", "Text", {
            "text": path_bind(f"/hourly/{i}/time", hourly[i]["time"]),
            "usageHint": lit("caption")
        }))
        components.append(component(f"h_icon_{i}", "Icon", {
            "name": path_bind(f"/hourly/{i}/icon", hourly[i].get("icon","sunny")),
            "size": lit_num(24)
        }))
        components.append(component(f"h_temp_{i}", "Text", {
            "text": path_bind(f"/hourly/{i}/temp", hourly[i]["temp"]),
            "usageHint": lit("caption")
        }))

    # ── 2. dataModelUpdate：填充数据 ──
    hourly_data = [
        kv_map(str(i), [kv("time", h["time"]), kv("icon", h.get("icon","sunny")), kv("temp", h["temp"])])
        for i, h in enumerate(hourly)
    ]
    data_contents = [
        kv("city",         city),
        kv("temp_display", f"{temp}°"),
        kv("weather_icon", weather_icon),
        kv("high",         f"{high}°"),
        kv("low",          f"{low}°"),
        kv_arr("hourly",   hourly_data),
    ]

    return [
        surface_update(sid, components),
        data_model_update(sid, data_contents),
        begin_rendering(sid, "root"),
    ]


# ─────────────────────────────────────────────
# 基金/股票卡片
# ─────────────────────────────────────────────
def build_fund(data: dict) -> list:
    sid = "fund_card"
    buy_price   = data.get("buy_price",   "1194.36")
    sell_price  = data.get("sell_price",  "1191.17")
    change_pct  = data.get("change_pct",  "+3.20%")
    update_time = data.get("update_time", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    btn_left    = data.get("btn_left",  "看看昨天")
    btn_right   = data.get("btn_right", "看看明天")
    chart_data  = data.get("chart_data", [40,42,38,45,43,47,50,48,52,55,53,58,60])
    is_up = not change_pct.startswith("-")

    components = [
        component("root", "Column", {
            "children": {"explicitList": ["top_row", "data_row", "btn_row"]},
            "spacing":  {"literalNumber": 14}
        }),
        component("top_row", "Row", {
            "children": {"explicitList": ["mini_chart", "spacer_top", "update_info"]},
            "alignment": {"literalString": "start"}
        }),
        component("mini_chart", "Chart", {
            "type":   lit("sparkline"),
            "data":   path_bind("/chart_data"),
            "width":  lit_num(120),
            "height": lit_num(50)
        }),
        component("spacer_top", "Spacer", {"flex": lit_num(1)}),
        component("update_info", "Row", {
            "children": {"explicitList": ["update_label", "refresh_icon"]},
            "alignment": {"literalString": "center"},
            "spacing":   {"literalNumber": 6}
        }),
        component("update_label", "Text", {
            "text":      path_bind("/update_time_display", f"更新时间 {update_time}"),
            "usageHint": lit("caption")
        }),
        component("refresh_icon", "Icon", {"name": lit("refresh"), "size": lit_num(14)}),
        # 数据行
        component("data_row", "Row", {
            "children": {"explicitList": ["buy_block", "sell_block", "change_block"]},
        }),
        component("buy_block", "Column", {
            "children": {"explicitList": ["buy_value", "buy_label"]},
            "spacing":  {"literalNumber": 3}
        }),
        component("buy_value", "Text", {
            "text":      path_bind("/buy_price", buy_price),
            "usageHint": lit("display")
        }),
        component("buy_label", "Text", {"text": lit("买入价"), "usageHint": lit("caption")}),
        component("sell_block", "Column", {
            "children": {"explicitList": ["sell_value", "sell_label"]},
            "spacing":  {"literalNumber": 3}
        }),
        component("sell_value", "Text", {
            "text":      path_bind("/sell_price", sell_price),
            "usageHint": lit("display")
        }),
        component("sell_label", "Text", {"text": lit("赎回价"), "usageHint": lit("caption")}),
        component("change_block", "Column", {
            "children": {"explicitList": ["change_value", "change_label"]},
            "spacing":  {"literalNumber": 3},
            "alignment": {"literalString": "end"}
        }),
        component("change_value", "Text", {
            "text":      path_bind("/change_pct", change_pct),
            "usageHint": lit("display"),
            "colorHint": lit("positive" if is_up else "negative")
        }),
        component("change_label", "Text", {"text": lit("实时涨幅"), "usageHint": lit("caption")}),
        # 按钮行
        component("btn_row", "Row", {
            "children": {"explicitList": ["btn_left_comp", "btn_right_comp"]},
            "spacing":  {"literalNumber": 14}
        }),
        component("btn_left_comp", "Button", {
            "child":  "btn_left_text",
            "action": {"name": lit("btn_left"), "context": []}
        }),
        component("btn_left_text", "Text", {
            "text": path_bind("/btn_left", btn_left), "usageHint": lit("button")
        }),
        component("btn_right_comp", "Button", {
            "child":  "btn_right_text",
            "action": {"name": lit("btn_right"), "context": []}
        }),
        component("btn_right_text", "Text", {
            "text": path_bind("/btn_right", btn_right), "usageHint": lit("button")
        }),
    ]

    chart_arr = [{"key": str(i), "valueNumber": v} for i, v in enumerate(chart_data)]
    data_contents = [
        kv("buy_price",          buy_price),
        kv("sell_price",         sell_price),
        kv("change_pct",         change_pct),
        kv("update_time_display", f"更新时间 {update_time}"),
        kv("btn_left",           btn_left),
        kv("btn_right",          btn_right),
        kv("is_up",              is_up),
        {"key": "chart_data", "valueArray": chart_arr},
    ]

    return [
        surface_update(sid, components),
        data_model_update(sid, data_contents),
        begin_rendering(sid, "root"),
    ]


# ─────────────────────────────────────────────
# 音乐卡片
# ─────────────────────────────────────────────
def build_music(data: dict) -> list:
    sid = "music_card"
    title        = data.get("title",        "Santa Tell Me")
    artist       = data.get("artist",       "Ariana Grace")
    progress     = data.get("progress",     35)
    current_time = data.get("current_time", "1:23")
    total_time   = data.get("total_time",   "3:45")
    is_playing   = data.get("is_playing",   True)

    components = [
        component("root", "Column", {
            "children": {"explicitList": ["info_row", "progress_bar", "time_row", "controls_row"]},
            "spacing":  {"literalNumber": 10}
        }),
        component("info_row", "Row", {
            "children":  {"explicitList": ["album_art", "track_info"]},
            "alignment": {"literalString": "center"},
            "spacing":   {"literalNumber": 16}
        }),
        component("album_art", "Icon", {"name": lit("music_note"), "size": lit_num(60), "bordered": lit_bool(True)}),
        component("track_info", "Column", {
            "children": {"explicitList": ["track_title", "track_artist"]},
            "spacing":  {"literalNumber": 6}
        }),
        component("track_title",  "Text", {"text": path_bind("/title",  title),  "usageHint": lit("subtitle")}),
        component("track_artist", "Text", {"text": path_bind("/artist", artist), "usageHint": lit("body"),  "colorHint": lit("dim")}),
        component("progress_bar", "ProgressIndicator", {
            "type":  lit("linear"),
            "value": path_bind("/progress_ratio", str(progress / 100))
        }),
        component("time_row", "Row", {
            "children": {"explicitList": ["time_current", "spacer_time", "time_total"]},
        }),
        component("time_current", "Text", {"text": path_bind("/current_time", current_time), "usageHint": lit("caption"), "colorHint": lit("dim")}),
        component("spacer_time",  "Spacer", {"flex": lit_num(1)}),
        component("time_total",   "Text", {"text": path_bind("/total_time",   total_time),   "usageHint": lit("caption"), "colorHint": lit("dim")}),
        component("controls_row", "Row", {
            "children":  {"explicitList": ["btn_prev", "btn_play_pause", "btn_next"]},
            "alignment": {"literalString": "center"},
            "spacing":   {"literalNumber": 28}
        }),
        component("btn_prev", "Button", {
            "child":  "icon_prev",
            "action": {"name": lit("prev_track"), "context": []}
        }),
        component("icon_prev",       "Icon", {"name": lit("skip_previous"), "size": lit_num(24)}),
        component("btn_play_pause",  "Button", {
            "child":  "icon_play_pause",
            "action": {"name": lit("toggle_play"), "context": []}
        }),
        component("icon_play_pause", "Icon", {
            "name": path_bind("/play_icon", "pause" if is_playing else "play_arrow"),
            "size": lit_num(36),
            "bordered": lit_bool(True)
        }),
        component("btn_next", "Button", {
            "child":  "icon_next",
            "action": {"name": lit("next_track"), "context": []}
        }),
        component("icon_next", "Icon", {"name": lit("skip_next"), "size": lit_num(24)}),
    ]

    data_contents = [
        kv("title",         title),
        kv("artist",        artist),
        kv("progress_ratio", progress / 100),
        kv("current_time",  current_time),
        kv("total_time",    total_time),
        kv("is_playing",    is_playing),
        kv("play_icon",     "pause" if is_playing else "play_arrow"),
    ]

    return [
        surface_update(sid, components),
        data_model_update(sid, data_contents),
        begin_rendering(sid, "root"),
    ]


# ─────────────────────────────────────────────
# 通知卡片
# ─────────────────────────────────────────────
def build_notify(data: dict) -> list:
    sid      = "notify_card"
    app_name = data.get("app_name", "微信")
    title    = data.get("title",    "新消息")
    content  = data.get("content",  "你有一条新的消息，请查看。")
    time_str = data.get("time",     "刚刚")
    btn_text = data.get("btn_text", "查看")

    components = [
        component("root", "Column", {
            "children": {"explicitList": ["header_row", "notify_title", "notify_content", "footer_row"]},
            "spacing":  {"literalNumber": 10}
        }),
        component("header_row", "Row", {
            "children":  {"explicitList": ["app_dot", "app_name_text", "spacer_h", "time_text"]},
            "alignment": {"literalString": "center"}
        }),
        component("app_dot",       "Dot",  {"size": lit_num(8)}),
        component("app_name_text", "Text", {"text": path_bind("/app_name", app_name), "usageHint": lit("body")}),
        component("spacer_h",      "Spacer", {"flex": lit_num(1)}),
        component("time_text",     "Text", {"text": path_bind("/time", time_str), "usageHint": lit("caption"), "colorHint": lit("dim")}),
        component("notify_title",   "Text", {"text": path_bind("/title",   title),   "usageHint": lit("subtitle")}),
        component("notify_content", "Text", {"text": path_bind("/content", content), "usageHint": lit("body"), "colorHint": lit("dim")}),
        component("footer_row", "Row", {
            "children":  {"explicitList": ["spacer_f", "btn_view"]},
            "alignment": {"literalString": "center"}
        }),
        component("spacer_f", "Spacer", {"flex": lit_num(1)}),
        component("btn_view", "Button", {
            "child":  "btn_view_text",
            "action": {"name": lit("view_notify"), "context": []}
        }),
        component("btn_view_text", "Text", {
            "text": path_bind("/btn_text", btn_text), "usageHint": lit("button")
        }),
    ]

    data_contents = [
        kv("app_name", app_name),
        kv("title",    title),
        kv("content",  content),
        kv("time",     time_str),
        kv("btn_text", btn_text),
    ]

    return [
        surface_update(sid, components),
        data_model_update(sid, data_contents),
        begin_rendering(sid, "root"),
    ]


# ─────────────────────────────────────────────
# 快递卡片
# ─────────────────────────────────────────────
def build_express(data: dict) -> list:
    sid           = "express_card"
    company       = data.get("company",     "顺丰速运")
    tracking_no   = data.get("tracking_no", "SF1234567890123")
    status        = data.get("status",      "派送中")
    status_sub    = data.get("status_sub",  "快递员正在配送，请保持手机畅通")
    eta           = data.get("eta",         "预计今日送达")
    progress      = data.get("progress",    75)
    steps         = data.get("steps",       ["已揽收","运输中","到达驿站","派送中","已签收"])
    current_step  = data.get("current_step", 3)
    tracks        = data.get("tracks", [
        {"desc": "快递员【李师傅 138****8888】正在派送", "time": "2026-03-27  17:42", "latest": True},
        {"desc": "快件已到达【北京朝阳营业部】",         "time": "2026-03-27  09:15"},
        {"desc": "快件离开【上海浦东转运中心】，发往北京","time": "2026-03-27  03:30"},
        {"desc": "快件已揽收，等待装车",                 "time": "2026-03-26  18:05"},
    ])
    btn_left  = data.get("btn_left",  "联系快递员")
    btn_right = data.get("btn_right", "查看详情")

    step_ids = [f"step_{i}" for i in range(len(steps))]
    track_ids = [f"track_{i}" for i in range(len(tracks))]

    components = [
        component("root", "Column", {
            "children": {"explicitList": ["header_row", "status_row", "progress_section", "divider", "timeline_col", "btn_row"]},
            "spacing":  {"literalNumber": 12}
        }),
        # 顶部：公司 + 单号
        component("header_row", "Row", {
            "children":  {"explicitList": ["company_icon", "company_name", "spacer_h", "tracking_no_text"]},
            "alignment": {"literalString": "center"}
        }),
        component("company_icon",    "Icon", {"name": lit("package"), "size": lit_num(32), "bordered": lit_bool(True)}),
        component("company_name",    "Text", {"text": path_bind("/company",     company),    "usageHint": lit("subtitle")}),
        component("spacer_h",        "Spacer", {"flex": lit_num(1)}),
        component("tracking_no_text","Text", {"text": path_bind("/tracking_no", tracking_no),"usageHint": lit("caption"), "colorHint": lit("dim")}),
        # 状态行
        component("status_row", "Row", {
            "children":  {"explicitList": ["status_icon", "status_info", "spacer_s", "eta_text"]},
            "alignment": {"literalString": "center"},
            "spacing":   {"literalNumber": 12}
        }),
        component("status_icon", "Icon", {"name": lit("local_shipping"), "size": lit_num(22)}),
        component("status_info", "Column", {
            "children": {"explicitList": ["status_badge", "status_sub_text"]},
            "spacing":  {"literalNumber": 3}
        }),
        component("status_badge",    "Text", {"text": path_bind("/status",     status),     "usageHint": lit("title")}),
        component("status_sub_text", "Text", {"text": path_bind("/status_sub", status_sub), "usageHint": lit("caption"), "colorHint": lit("dim")}),
        component("spacer_s",  "Spacer", {"flex": lit_num(1)}),
        component("eta_text",  "Text",   {"text": path_bind("/eta", eta), "usageHint": lit("caption"), "colorHint": lit("dim")}),
        # 进度条区域
        component("progress_section", "Column", {
            "children": {"explicitList": ["progress_bar", "steps_row"]},
            "spacing":  {"literalNumber": 6}
        }),
        component("progress_bar", "ProgressIndicator", {
            "type":  lit("linear"),
            "value": path_bind("/progress_ratio", str(progress / 100))
        }),
        component("steps_row", "Row", {
            "children": {"explicitList": step_ids},
        }),
        *[component(sid_, "Text", {
            "text":      path_bind(f"/steps/{i}", steps[i]),
            "usageHint": lit("caption"),
            "colorHint": lit("primary" if i <= current_step else "dim")
        }) for i, sid_ in enumerate(step_ids)],
        # 分割线
        component("divider", "Divider", {}),
        # 时间线
        component("timeline_col", "Column", {
            "children": {"explicitList": track_ids},
            "spacing":  {"literalNumber": 0}
        }),
        *[component(tid, "TimelineItem", {
            "description": path_bind(f"/tracks/{i}/desc", tracks[i]["desc"]),
            "timestamp":   path_bind(f"/tracks/{i}/time", tracks[i]["time"]),
            "isLatest":    lit_bool(tracks[i].get("latest", False))
        }) for i, tid in enumerate(track_ids)],
        # 按钮行
        component("btn_row", "Row", {
            "children": {"explicitList": ["btn_left_comp", "btn_right_comp"]},
            "spacing":  {"literalNumber": 10}
        }),
        component("btn_left_comp",  "Button", {"child": "btn_left_text",  "action": {"name": lit("contact"),  "context": []}}),
        component("btn_left_text",  "Text",   {"text": path_bind("/btn_left",  btn_left),  "usageHint": lit("button")}),
        component("btn_right_comp", "Button", {"child": "btn_right_text", "action": {"name": lit("details"),  "context": []}}),
        component("btn_right_text", "Text",   {"text": path_bind("/btn_right", btn_right), "usageHint": lit("button")}),
    ]

    steps_data  = [kv(str(i), s) for i, s in enumerate(steps)]
    tracks_data = [
        kv_map(str(i), [kv("desc", t["desc"]), kv("time", t["time"]), kv("latest", t.get("latest", False))])
        for i, t in enumerate(tracks)
    ]
    data_contents = [
        kv("company",        company),
        kv("tracking_no",    tracking_no),
        kv("status",         status),
        kv("status_sub",     status_sub),
        kv("eta",            eta),
        kv("progress_ratio", progress / 100),
        kv("current_step",   current_step),
        kv("btn_left",       btn_left),
        kv("btn_right",      btn_right),
        kv_arr("steps",      steps_data),
        kv_arr("tracks",     tracks_data),
    ]

    return [
        surface_update(sid, components),
        data_model_update(sid, data_contents),
        begin_rendering(sid, "root"),
    ]


# ─────────────────────────────────────────────
# 自定义数据卡片
# ─────────────────────────────────────────────
def build_custom(data: dict) -> list:
    sid      = "custom_card"
    title    = data.get("title",    "数据概览")
    subtitle = data.get("subtitle", "")
    items    = data.get("items", [
        {"label": "数据项1", "value": "123"},
        {"label": "数据项2", "value": "456"},
        {"label": "数据项3", "value": "789"},
    ])
    buttons  = data.get("buttons", [])
    footer   = data.get("footer",  "")

    item_ids   = [f"item_{i}" for i in range(len(items))]
    header_ids = ["card_title"] + (["card_subtitle"] if subtitle else [])
    body_ids   = ["data_grid"]
    extra_ids  = (["btn_row"] if buttons else []) + (["card_footer"] if footer else [])
    btn_ids    = [f"btn_{i}" for i in range(len(buttons))]
    btn_text_ids = [f"btn_text_{i}" for i in range(len(buttons))]

    components = [
        component("root", "Column", {
            "children": {"explicitList": header_ids + body_ids + extra_ids},
            "spacing":  {"literalNumber": 14}
        }),
        component("card_title", "Text", {"text": path_bind("/title", title), "usageHint": lit("subtitle")}),
    ]
    if subtitle:
        components.append(component("card_subtitle", "Text", {
            "text": path_bind("/subtitle", subtitle), "usageHint": lit("caption"), "colorHint": lit("dim")
        }))

    components.append(component("data_grid", "Row", {
        "children": {"explicitList": item_ids},
        "spacing":  {"literalNumber": 28}
    }))
    for i, iid in enumerate(item_ids):
        components.append(component(iid, "Column", {
            "children": {"explicitList": [f"item_val_{i}", f"item_lbl_{i}"]},
            "spacing":  {"literalNumber": 4}
        }))
        components.append(component(f"item_val_{i}", "Text", {
            "text": path_bind(f"/items/{i}/value", items[i]["value"]), "usageHint": lit("title")
        }))
        components.append(component(f"item_lbl_{i}", "Text", {
            "text": path_bind(f"/items/{i}/label", items[i]["label"]), "usageHint": lit("caption"), "colorHint": lit("dim")
        }))

    if buttons:
        components.append(component("btn_row", "Row", {
            "children": {"explicitList": btn_ids},
            "spacing":  {"literalNumber": 12}
        }))
        for i, bid in enumerate(btn_ids):
            components.append(component(bid, "Button", {
                "child":  btn_text_ids[i],
                "action": {"name": lit(f"btn_{i}"), "context": []}
            }))
            components.append(component(btn_text_ids[i], "Text", {
                "text": path_bind(f"/buttons/{i}", buttons[i]), "usageHint": lit("button")
            }))

    if footer:
        components.append(component("card_footer", "Text", {
            "text": path_bind("/footer", footer), "usageHint": lit("caption"), "colorHint": lit("dim")
        }))

    items_data   = [kv_map(str(i), [kv("label", it["label"]), kv("value", it["value"])]) for i, it in enumerate(items)]
    buttons_data = [kv(str(i), b) for i, b in enumerate(buttons)]
    data_contents = [
        kv("title",    title),
        kv("subtitle", subtitle),
        kv("footer",   footer),
        kv_arr("items",   items_data),
        kv_arr("buttons", buttons_data),
    ]

    return [
        surface_update(sid, components),
        data_model_update(sid, data_contents),
        begin_rendering(sid, "root"),
    ]


# ─────────────────────────────────────────────
# 主入口
# ─────────────────────────────────────────────
BUILDERS = {
    "weather": build_weather,
    "fund":    build_fund,
    "music":   build_music,
    "notify":  build_notify,
    "express": build_express,
    "custom":  build_custom,
}


def main():
    parser = argparse.ArgumentParser(description="YodaOS Sprite 卡片 A2UI JSONL 生成器")
    parser.add_argument("--type", choices=list(BUILDERS.keys()), default="weather",
                        help="卡片类型")
    parser.add_argument("--data", type=str, default="{}",
                        help="JSON 格式的卡片数据")
    parser.add_argument("--output", type=str, default=None,
                        help="输出 .jsonl 文件路径（不指定则打印到 stdout）")
    args = parser.parse_args()

    try:
        card_data = json.loads(args.data)
    except json.JSONDecodeError as e:
        print(f"[错误] 数据格式不合法: {e}", file=sys.stderr)
        sys.exit(1)

    messages = BUILDERS[args.type](card_data)
    output   = to_jsonl(messages)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"✅ A2UI JSONL 已生成: {args.output}  ({len(messages)} 条消息)", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
