#!/usr/bin/env python3
"""
YodaOS Sprite 卡片 —— A2UI JSONL 渲染器（客户端侧）
=====================================================
读取 generate_a2ui.py 输出的 JSONL，按 A2UI v0.8 协议解析，
将抽象组件树绑定数据后渲染为符合 YodaOS-Sprite 设计规范的 HTML 文件。

YodaOS-Sprite Catalog 映射规则（本渲染器实现的组件目录）：
  catalog: "yoda-os-sprite-v1"

  布局组件：Column / Row / Card / Spacer / Divider
  文本组件：Text（usageHint: display|title|subtitle|body|caption|button）
  交互组件：Button / ProgressIndicator / Icon / Dot / Chart / TimelineItem

用法:
  python3 render_a2ui.py --input weather.jsonl --output weather_card.html
  python3 render_a2ui.py --input fund.jsonl    --output fund_card.html
  cat express.jsonl | python3 render_a2ui.py --output express_card.html
"""

import argparse
import json
import sys
from typing import Any

# ─────────────────────────────────────────────
# YodaOS-Sprite 设计规范 Token
# ─────────────────────────────────────────────
TOKENS = {
    "color_primary":  "#40FF5E",
    "color_bg_card":  "#1C1C1C",
    "color_bg_dark":  "#000000",
    "color_dim":      "rgba(64,255,94,0.55)",
    "color_divider":  "rgba(64,255,94,0.25)",
    "color_positive": "#40FF5E",
    "color_negative": "#FF4040",
    "border_radius":  12,
    "border_width":   2,
    "font_family":    "'HarmonyOS Sans SC','PingFang SC','Microsoft YaHei',sans-serif",
    # usageHint → CSS
    "usage_hints": {
        "display":  "font-size:52px;line-height:60px;font-weight:600",
        "title":    "font-size:24px;line-height:30px;font-weight:500",
        "subtitle": "font-size:20px;line-height:26px;font-weight:500",
        "h1":       "font-size:32px;line-height:40px;font-weight:600",
        "h2":       "font-size:28px;line-height:36px;font-weight:600",
        "body":     "font-size:16px;line-height:22px;font-weight:400",
        "caption":  "font-size:13px;line-height:18px;font-weight:400",
        "button":   "font-size:15px;line-height:20px;font-weight:500",
    },
    # icon name → inline SVG
    "icons": {
        "location": '<svg width="{s}" height="{s}" viewBox="0 0 16 16" fill="none"><path d="M8 1C5.24 1 3 3.24 3 6c0 3.75 5 9 5 9s5-5.25 5-9c0-2.76-2.24-5-5-5zm0 6.75A1.75 1.75 0 116 6a1.75 1.75 0 012 1.75z" fill="#40FF5E"/></svg>',
        "refresh":  '<svg width="{s}" height="{s}" viewBox="0 0 16 16" fill="none"><path d="M13.65 2.35A8 8 0 104 14.83" stroke="#40FF5E" stroke-width="1.5" stroke-linecap="round"/><path d="M4 11v4H0" stroke="#40FF5E" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>',
        "package":  '<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none"><path d="M3 7l9-4 9 4v10l-9 4-9-4V7z" stroke="#40FF5E" stroke-width="1.5" stroke-linejoin="round"/><path d="M12 3v18M3 7l9 4 9-4" stroke="#40FF5E" stroke-width="1.5" stroke-linejoin="round"/></svg>',
        "local_shipping": '<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none"><path d="M3 13h14V5H3v8z" stroke="#40FF5E" stroke-width="1.5" stroke-linejoin="round"/><path d="M17 8h3l2 4v4h-5V8z" stroke="#40FF5E" stroke-width="1.5" stroke-linejoin="round"/><circle cx="6.5" cy="17.5" r="1.5" stroke="#40FF5E" stroke-width="1.5"/><circle cx="19.5" cy="17.5" r="1.5" stroke="#40FF5E" stroke-width="1.5"/></svg>',
        "music_note": '<svg width="{s}" height="{s}" viewBox="0 0 32 32" fill="none"><path d="M12 25V8l16-3v17" stroke="#40FF5E" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/><circle cx="9" cy="25" r="3" stroke="#40FF5E" stroke-width="1.5"/><circle cx="25" cy="22" r="3" stroke="#40FF5E" stroke-width="1.5"/></svg>',
        "skip_previous": '<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none"><path d="M19 5L5 12l14 7V5z" stroke="#40FF5E" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/><line x1="5" y1="5" x2="5" y2="19" stroke="#40FF5E" stroke-width="1.5" stroke-linecap="round"/></svg>',
        "skip_next": '<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none"><path d="M5 5l14 7-14 7V5z" stroke="#40FF5E" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/><line x1="19" y1="5" x2="19" y2="19" stroke="#40FF5E" stroke-width="1.5" stroke-linecap="round"/></svg>',
        "play_arrow": '<svg width="{s}" height="{s}" viewBox="0 0 28 28" fill="none"><circle cx="14" cy="14" r="13" stroke="#40FF5E" stroke-width="1.5"/><path d="M11 9l10 5-10 5V9z" fill="#40FF5E"/></svg>',
        "pause": '<svg width="{s}" height="{s}" viewBox="0 0 28 28" fill="none"><circle cx="14" cy="14" r="13" stroke="#40FF5E" stroke-width="1.5"/><rect x="9" y="9" width="4" height="10" rx="1" fill="#40FF5E"/><rect x="15" y="9" width="4" height="10" rx="1" fill="#40FF5E"/></svg>',
        # 天气图标
        "sunny": '<svg width="{s}" height="{s}" viewBox="0 0 40 40" fill="none"><circle cx="20" cy="20" r="7" stroke="#40FF5E" stroke-width="2"/><line x1="20" y1="2" x2="20" y2="7" stroke="#40FF5E" stroke-width="2" stroke-linecap="round"/><line x1="20" y1="33" x2="20" y2="38" stroke="#40FF5E" stroke-width="2" stroke-linecap="round"/><line x1="2" y1="20" x2="7" y2="20" stroke="#40FF5E" stroke-width="2" stroke-linecap="round"/><line x1="33" y1="20" x2="38" y2="20" stroke="#40FF5E" stroke-width="2" stroke-linecap="round"/><line x1="6.34" y1="6.34" x2="9.87" y2="9.87" stroke="#40FF5E" stroke-width="2" stroke-linecap="round"/><line x1="30.13" y1="30.13" x2="33.66" y2="33.66" stroke="#40FF5E" stroke-width="2" stroke-linecap="round"/><line x1="33.66" y1="6.34" x2="30.13" y2="9.87" stroke="#40FF5E" stroke-width="2" stroke-linecap="round"/><line x1="9.87" y1="30.13" x2="6.34" y2="33.66" stroke="#40FF5E" stroke-width="2" stroke-linecap="round"/></svg>',
        "cloudy": '<svg width="{s}" height="{s}" viewBox="0 0 40 40" fill="none"><path d="M28 28H12a8 8 0 010-16 7.9 7.9 0 013.27.7A9 9 0 0128 20a8 8 0 010 8z" stroke="#40FF5E" stroke-width="2" stroke-linejoin="round"/></svg>',
        "cloudy_drizzle": '<svg width="{s}" height="{s}" viewBox="0 0 40 40" fill="none"><path d="M26 22H12a7 7 0 010-14 6.9 6.9 0 012.87.62A8 8 0 0126 14a7 7 0 010 8z" stroke="#40FF5E" stroke-width="2" stroke-linejoin="round"/><circle cx="14" cy="30" r="1.5" fill="#40FF5E"/><circle cx="20" cy="34" r="1.5" fill="#40FF5E"/><circle cx="26" cy="30" r="1.5" fill="#40FF5E"/></svg>',
        "snow": '<svg width="{s}" height="{s}" viewBox="0 0 40 40" fill="none"><line x1="20" y1="4" x2="20" y2="36" stroke="#40FF5E" stroke-width="2" stroke-linecap="round"/><line x1="4" y1="20" x2="36" y2="20" stroke="#40FF5E" stroke-width="2" stroke-linecap="round"/><line x1="8.69" y1="8.69" x2="31.31" y2="31.31" stroke="#40FF5E" stroke-width="2" stroke-linecap="round"/><line x1="31.31" y1="8.69" x2="8.69" y2="31.31" stroke="#40FF5E" stroke-width="2" stroke-linecap="round"/><circle cx="20" cy="20" r="2" fill="#40FF5E"/></svg>',
        "default": '<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" stroke="#40FF5E" stroke-width="1.5"/></svg>',
    }
}


# ─────────────────────────────────────────────
# A2UI 协议解析器
# ─────────────────────────────────────────────
class A2UIRuntime:
    """最小化 A2UI v0.8 运行时：解析 JSONL，维护组件缓冲区和数据模型"""

    def __init__(self):
        self.surfaces: dict[str, dict] = {}   # surfaceId → {components, data, root}

    def _get_surface(self, sid: str) -> dict:
        if sid not in self.surfaces:
            self.surfaces[sid] = {"components": {}, "data": {}, "root": None}
        return self.surfaces[sid]

    def process(self, line: str):
        """处理一条 JSONL 消息"""
        msg = json.loads(line.strip())
        if "surfaceUpdate" in msg:
            su = msg["surfaceUpdate"]
            sid  = su.get("surfaceId", "default")
            surf = self._get_surface(sid)
            for comp in su.get("components", []):
                surf["components"][comp["id"]] = comp["component"]
        elif "dataModelUpdate" in msg:
            dm   = msg["dataModelUpdate"]
            sid  = dm.get("surfaceId", "default")
            surf = self._get_surface(sid)
            self._apply_data(surf["data"], dm.get("contents", []), dm.get("path"))
        elif "beginRendering" in msg:
            br   = msg["beginRendering"]
            sid  = br.get("surfaceId", "default")
            surf = self._get_surface(sid)
            surf["root"] = br["root"]
        elif "deleteSurface" in msg:
            ds = msg["deleteSurface"]
            self.surfaces.pop(ds.get("surfaceId", "default"), None)

    def _apply_data(self, store: dict, contents: list, path: str = None):
        target = store
        if path:
            for seg in path.strip("/").split("/"):
                target = target.setdefault(seg, {})
        for item in contents:
            key = item["key"]
            if "valueString"  in item: target[key] = item["valueString"]
            elif "valueNumber"  in item: target[key] = item["valueNumber"]
            elif "valueBoolean" in item: target[key] = item["valueBoolean"]
            elif "valueMap"     in item:
                target[key] = {}
                self._apply_data(target[key], item["valueMap"])
            elif "valueArray"   in item:
                arr = {}
                self._apply_data(arr, item["valueArray"])
                target[key] = arr

    def resolve_bound(self, bv: Any, data: dict) -> Any:
        """解析 BoundValue：literalXxx 或 path 绑定"""
        if isinstance(bv, dict):
            if "literalString"  in bv: return bv["literalString"]
            if "literalNumber"  in bv: return bv["literalNumber"]
            if "literalBoolean" in bv: return bv["literalBoolean"]
            if "path"           in bv:
                val = self._lookup(data, bv["path"])
                if val is None and "literalString" in bv:
                    return bv["literalString"]
                return val if val is not None else ""
        return bv

    def _lookup(self, data: dict, path: str) -> Any:
        segs = path.strip("/").split("/")
        cur  = data
        for seg in segs:
            if isinstance(cur, dict) and seg in cur:
                cur = cur[seg]
            else:
                return None
        return cur


# ─────────────────────────────────────────────
# HTML 渲染器（YodaOS-Sprite Catalog）
# ─────────────────────────────────────────────
class YodaOSRenderer:
    """将 A2UI 运行时中的组件树渲染为 HTML，应用 YodaOS-Sprite 设计规范"""

    def __init__(self, runtime: A2UIRuntime):
        self.rt = runtime

    def render_surface(self, sid: str) -> str:
        surf = self.rt.surfaces.get(sid)
        if not surf or not surf["root"]:
            return "<div>No surface</div>"
        html_body = self._render_comp(surf["root"], surf["components"], surf["data"])
        return self._wrap_page(html_body, sid)

    def _render_comp(self, cid: str, comps: dict, data: dict) -> str:
        comp = comps.get(cid)
        if not comp:
            return ""
        ctype = list(comp.keys())[0]
        props = comp[ctype]

        dispatch = {
            "Column":            self._render_column,
            "Row":               self._render_row,
            "Card":              self._render_card_comp,
            "Spacer":            self._render_spacer,
            "Divider":           self._render_divider,
            "Text":              self._render_text,
            "Button":            self._render_button,
            "Icon":              self._render_icon,
            "Dot":               self._render_dot,
            "ProgressIndicator": self._render_progress,
            "Chart":             self._render_chart,
            "TimelineItem":      self._render_timeline_item,
            "Expandable":        self._render_expandable,
        }
        fn = dispatch.get(ctype)
        if fn:
            return fn(cid, props, comps, data)
        return f"<!-- unknown component: {ctype} -->"

    def _children_html(self, props: dict, comps: dict, data: dict) -> str:
        children = props.get("children", {})
        ids = []
        if "explicitList" in children:
            ids = children["explicitList"]
        elif "template" in children:
            # 简单模板：不实现完整动态列表，直接返回占位
            ids = []
        return "".join(self._render_comp(cid, comps, data) for cid in ids)

    def _rv(self, val, data: dict):
        return self.rt.resolve_bound(val, data)

    # ── 布局 ──

    def _render_column(self, cid, props, comps, data) -> str:
        spacing = self._rv(props.get("spacing", {"literalNumber": 8}), data)
        align   = self._rv(props.get("alignment", {"literalString": "start"}), data)
        flex_align = {"center": "center", "end": "flex-end", "start": "flex-start"}.get(str(align), "flex-start")
        style = f"display:flex;flex-direction:column;gap:{spacing}px;align-items:{flex_align};"
        inner = self._children_html(props, comps, data)
        return f'<div style="{style}">{inner}</div>'

    def _render_row(self, cid, props, comps, data) -> str:
        spacing = self._rv(props.get("spacing", {"literalNumber": 8}), data)
        align   = self._rv(props.get("alignment", {"literalString": "center"}), data)
        flex_align = {"center": "center", "end": "flex-end", "start": "flex-start"}.get(str(align), "center")
        style = f"display:flex;flex-direction:row;align-items:{flex_align};gap:{spacing}px;width:100%;"
        inner = self._children_html(props, comps, data)
        return f'<div style="{style}">{inner}</div>'

    def _render_card_comp(self, cid, props, comps, data) -> str:
        child_id = props.get("child", "")
        inner = self._render_comp(child_id, comps, data) if child_id else ""
        style = (f"background:{TOKENS['color_bg_card']};"
                 f"border:{TOKENS['border_width']}px solid {TOKENS['color_primary']};"
                 f"border-radius:{TOKENS['border_radius']}px;padding:20px 24px;")
        return f'<div style="{style}">{inner}</div>'

    def _render_spacer(self, cid, props, comps, data) -> str:
        flex = self._rv(props.get("flex", {"literalNumber": 1}), data)
        return f'<div style="flex:{flex};"></div>'

    def _render_divider(self, cid, props, comps, data) -> str:
        return f'<div style="height:1px;background:{TOKENS["color_divider"]};width:100%;"></div>'

    # ── 文本 ──

    def _color_hint_css(self, hint: str) -> str:
        return {
            "primary":  f"color:{TOKENS['color_primary']};",
            "dim":      f"color:{TOKENS['color_dim']};",
            "positive": f"color:{TOKENS['color_positive']};",
            "negative": f"color:{TOKENS['color_negative']};",
        }.get(hint, f"color:{TOKENS['color_primary']};")

    def _render_text(self, cid, props, comps, data) -> str:
        text      = self._rv(props.get("text", lit("")), data)
        hint      = self._rv(props.get("usageHint", {"literalString": "body"}), data)
        color_h   = self._rv(props.get("colorHint",  {"literalString": "primary"}), data)
        type_css  = TOKENS["usage_hints"].get(str(hint), TOKENS["usage_hints"]["body"])
        color_css = self._color_hint_css(str(color_h))
        style = f"font-family:{TOKENS['font_family']};{type_css};{color_css}"
        return f'<span style="{style}">{text}</span>'

    # ── 按钮 ──

    def _render_button(self, cid, props, comps, data) -> str:
        child_id  = props.get("child", "")
        action    = props.get("action", {})
        action_nm = self._rv(action.get("name", {"literalString": ""}), data)
        inner     = self._render_comp(child_id, comps, data) if child_id else ""
        style = (f"border:{TOKENS['border_width']}px solid {TOKENS['color_primary']};"
                 f"border-radius:{TOKENS['border_radius']}px;"
                 "background:transparent;padding:10px 0;cursor:pointer;"
                 "flex:1;display:flex;align-items:center;justify-content:center;"
                 f"font-family:{TOKENS['font_family']};")
        return f'<button style="{style}" data-action="{action_nm}">{inner}</button>'

    # ── 图标 ──

    def _render_icon(self, cid, props, comps, data) -> str:
        name    = str(self._rv(props.get("name", {"literalString": "default"}), data))
        size    = int(self._rv(props.get("size", {"literalNumber": 24}), data))
        bordered = self._rv(props.get("bordered", {"literalBoolean": False}), data)
        svg_tpl = TOKENS["icons"].get(name, TOKENS["icons"]["default"])
        svg = svg_tpl.replace("{s}", str(size))
        if bordered:
            style = (f"width:{size+16}px;height:{size+16}px;"
                     f"border:1.5px solid {TOKENS['color_dim']};"
                     f"border-radius:{TOKENS['border_radius']}px;"
                     "display:flex;align-items:center;justify-content:center;flex-shrink:0;")
            return f'<div style="{style}">{svg}</div>'
        return f'<div style="flex-shrink:0;display:flex;align-items:center;">{svg}</div>'

    # ── 小圆点 ──

    def _render_dot(self, cid, props, comps, data) -> str:
        size = int(self._rv(props.get("size", {"literalNumber": 8}), data))
        style = (f"width:{size}px;height:{size}px;border-radius:50%;"
                 f"background:{TOKENS['color_primary']};flex-shrink:0;")
        return f'<div style="{style}"></div>'

    # ── 进度条 ──

    def _render_progress(self, cid, props, comps, data) -> str:
        ptype = str(self._rv(props.get("type", {"literalString": "linear"}), data))
        value = float(self._rv(props.get("value", {"literalNumber": 0}), data))
        pct   = min(max(value, 0), 1) * 100
        if ptype == "linear":
            return (f'<div style="width:100%;height:3px;background:{TOKENS["color_divider"]};border-radius:2px;">'
                    f'<div style="width:{pct:.1f}%;height:100%;background:{TOKENS["color_primary"]};border-radius:2px;"></div>'
                    f'</div>')
        # circular（简化）
        r = 18; circ = 2 * 3.14159 * r
        dash = pct / 100 * circ
        return (f'<svg width="44" height="44" viewBox="0 0 44 44">'
                f'<circle cx="22" cy="22" r="{r}" stroke="{TOKENS["color_divider"]}" stroke-width="3" fill="none"/>'
                f'<circle cx="22" cy="22" r="{r}" stroke="{TOKENS["color_primary"]}" stroke-width="3" fill="none"'
                f' stroke-dasharray="{dash:.1f} {circ:.1f}" stroke-dashoffset="{circ/4:.1f}" stroke-linecap="round"/>'
                f'</svg>')

    # ── 折线迷你图 ──

    def _render_chart(self, cid, props, comps, data) -> str:
        ctype  = str(self._rv(props.get("type",   {"literalString": "sparkline"}), data))
        width  = int(self._rv(props.get("width",  {"literalNumber": 120}), data))
        height = int(self._rv(props.get("height", {"literalNumber": 50}),  data))
        raw_data = self.rt.resolve_bound(props.get("data", {}), data)
        # raw_data 可能是 path 绑定后的 dict {0:v, 1:v, ...} 或直接 list
        if isinstance(raw_data, dict):
            vals = [float(raw_data[str(i)]) for i in range(len(raw_data)) if str(i) in raw_data]
        elif isinstance(raw_data, list):
            vals = [float(v) for v in raw_data]
        else:
            vals = [40, 45, 42, 50, 55, 58, 60]
        if len(vals) < 2:
            return ""
        n = len(vals); mn = min(vals); mx = max(vals); rng = mx - mn if mx != mn else 1
        pts = []
        for i, v in enumerate(vals):
            x = i / (n - 1) * (width - 4) + 2
            y = height - 4 - (v - mn) / rng * (height - 8)
            pts.append(f"{x:.1f},{y:.1f}")
        poly = " ".join(pts)
        fill_pts = f"2,{height-2} " + poly + f" {width-2},{height-2}"
        return (f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" fill="none">'
                f'<defs><linearGradient id="sg" x1="0" y1="0" x2="0" y2="1">'
                f'<stop offset="0%" stop-color="#40FF5E" stop-opacity="0.4"/>'
                f'<stop offset="100%" stop-color="#40FF5E" stop-opacity="0"/></linearGradient></defs>'
                f'<polygon points="{fill_pts}" fill="url(#sg)"/>'
                f'<polyline points="{poly}" stroke="#40FF5E" stroke-width="1.5" stroke-dasharray="3 2"'
                f' fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
                f'</svg>')

    # ── 时间线条目 ──

    def _render_timeline_item(self, cid, props, comps, data) -> str:
        desc      = str(self._rv(props.get("description", {"literalString": ""}), data))
        timestamp = str(self._rv(props.get("timestamp",   {"literalString": ""}), data))
        is_latest = bool(self._rv(props.get("isLatest",   {"literalBoolean": False}), data))

        dot_style = (f"width:10px;height:10px;border-radius:50%;flex-shrink:0;"
                     f"background:{TOKENS['color_primary']};box-shadow:0 0 8px rgba(64,255,94,0.5);"
                     if is_latest else
                     f"width:10px;height:10px;border-radius:50%;flex-shrink:0;"
                     f"border:1.5px solid {TOKENS['color_primary']};background:{TOKENS['color_bg_card']};")
        desc_style = (f"font-family:{TOKENS['font_family']};font-size:15px;line-height:20px;font-weight:500;"
                      f"color:{TOKENS['color_primary']};margin-bottom:3px;"
                      if is_latest else
                      f"font-family:{TOKENS['font_family']};font-size:14px;line-height:20px;"
                      f"color:{TOKENS['color_primary']};margin-bottom:3px;")
        time_style = f"font-family:{TOKENS['font_family']};font-size:12px;color:{TOKENS['color_dim']};"
        return (f'<div style="display:flex;gap:14px;padding-bottom:14px;">'
                f'  <div style="display:flex;flex-direction:column;align-items:center;flex-shrink:0;width:10px;">'
                f'    <div style="{dot_style}"></div>'
                f'    <div style="flex:1;width:1px;background:{TOKENS["color_divider"]};margin-top:2px;"></div>'
                f'  </div>'
                f'  <div style="flex:1;">'
                f'    <div style="{desc_style}">{desc}</div>'
                f'    <div style="{time_style}">{timestamp}</div>'
                f'  </div>'
                f'</div>')

    # ── 可展开面板 ──

    def _render_expandable(self, cid, props, comps, data) -> str:
        header_id  = props.get("header", "")
        content_id = props.get("content", "")
        expanded   = bool(self._rv(props.get("expanded", {"literalBoolean": False}), data))

        header_html  = self._render_comp(header_id, comps, data) if header_id else ""
        content_html = self._render_comp(content_id, comps, data) if content_id else ""

        chevron_svg = ('<svg width="14" height="14" viewBox="0 0 14 14" fill="none" '
                       'style="transition:transform 0.25s ease;">'
                       '<path d="M3 5l4 4 4-4" stroke="#40FF5E" stroke-width="1.5" '
                       'stroke-linecap="round" stroke-linejoin="round"/></svg>')

        uid = f"exp_{cid}"
        deg = "180" if expanded else "0"
        mh = "1000px" if expanded else "0px"
        op = "1" if expanded else "0"
        mt = "14px" if expanded else "0px"

        return (f'<div class="yoda-expandable" data-id="{uid}" style="width:100%;">'
                f'  <div class="yoda-expandable-header" onclick="toggleExpand(\'{uid}\')" '
                f'style="display:flex;align-items:center;width:100%;cursor:pointer;gap:10px;padding:10px 0;">'
                f'    <div style="flex:1;">{header_html}</div>'
                f'    <div class="yoda-expandable-chevron" id="chevron_{uid}" '
                f'style="transform:rotate({deg}deg);">{chevron_svg}</div>'
                f'  </div>'
                f'  <div class="yoda-expandable-content" id="content_{uid}" '
                f'style="max-height:{mh};overflow:hidden;'
                f'opacity:{op};transition:max-height 0.3s ease,opacity 0.3s ease;'
                f'margin-top:{mt};">'
                f'    {content_html}'
                f'  </div>'
                f'</div>')

    # ── 页面包装 ──

    def _wrap_page(self, body: str, sid: str) -> str:
        return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>YodaOS Sprite · {sid}</title>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{
    background: {TOKENS['color_bg_dark']};
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: {TOKENS['font_family']};
  }}
  .yoda-card {{
    background: {TOKENS['color_bg_card']};
    border: {TOKENS['border_width']}px solid {TOKENS['color_primary']};
    border-radius: {TOKENS['border_radius']}px;
    color: {TOKENS['color_primary']};
    padding: 20px 24px;
    width: 480px;
    height: 400px;
    overflow-y: auto;
  }}
</style>
</head>
<body>
  <div class="yoda-card">
    {body}
  </div>
  <script>
  function toggleExpand(id) {{
    var content = document.getElementById('content_' + id);
    var chevron = document.getElementById('chevron_' + id);
    if (!content || !chevron) return;
    var isOpen = content.style.maxHeight !== '0px';
    if (isOpen) {{
      content.style.maxHeight = '0px';
      content.style.opacity = '0';
      content.style.marginTop = '0px';
      chevron.style.transform = 'rotate(0deg)';
    }} else {{
      content.style.maxHeight = '1000px';
      content.style.opacity = '1';
      content.style.marginTop = '14px';
      chevron.style.transform = 'rotate(180deg)';
    }}
  }}
  </script>
</body>
</html>"""


# ─────────────────────────────────────────────
# 辅助：字面量绑定（renderer 内部用）
# ─────────────────────────────────────────────
def lit(s): return {"literalString": str(s)}


# ─────────────────────────────────────────────
# 主入口
# ─────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="YodaOS Sprite A2UI JSONL → HTML 渲染器")
    parser.add_argument("--input",  type=str, default=None, help="输入 .jsonl 文件路径（不指定则从 stdin 读）")
    parser.add_argument("--output", type=str, default=None, help="输出 .html 文件路径（不指定则打印到 stdout）")
    args = parser.parse_args()

    # 读取 JSONL
    if args.input:
        with open(args.input, encoding="utf-8") as f:
            lines = [l for l in f if l.strip()]
    else:
        lines = [l for l in sys.stdin if l.strip()]

    # 运行 A2UI 运行时
    rt = A2UIRuntime()
    for line in lines:
        try:
            rt.process(line)
        except Exception as e:
            print(f"[warn] 跳过无效行: {e}", file=sys.stderr)

    # 渲染所有 surface
    renderer = YodaOSRenderer(rt)
    pages = []
    for sid, surf in rt.surfaces.items():
        if surf.get("root"):
            pages.append(renderer.render_surface(sid))

    if not pages:
        print("[错误] 未找到可渲染的 surface，请确认 JSONL 中有 beginRendering 消息", file=sys.stderr)
        sys.exit(1)

    result = pages[0]  # 输出第一个 surface

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(result)
        print(f"✅ HTML 已渲染: {args.output}", file=sys.stderr)
    else:
        print(result)


if __name__ == "__main__":
    main()
