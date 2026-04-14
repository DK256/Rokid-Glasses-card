#!/usr/bin/env python3
"""
YodaOS Sprite - 480×380px 基础模板生成器

符合以下规范：
1. 显示区域：480×380px（整个眼镜视野）
2. 最小字号：16px（caption和button）
3. 字体：HarmonyOS Sans SC
4. 主色：#40FF5E，背景色：#000000
5. 圆角：12px，描边：2px
6. A2UI v0.8 协议 + yoda-os-sprite-v1 catalog
"""

import json
import sys
from datetime import datetime

# A2UI 协议构建工具函数
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

def to_jsonl(messages: list) -> str:
    """将消息列表序列化为 JSONL 字符串"""
    return "\n".join(json.dumps(m, ensure_ascii=False) for m in messages)


def build_480x380_base_template(card_type: str, data: dict) -> str:
    """
    构建480×380px基础模板
    
    核心设计原则：
    1. 整个显示区域限制在480×380px内
    2. 将状态切换导航集成在显示区域内
    3. 使用标准组件和颜色系统
    4. 严格遵循A2UI协议
    """
    surface_id = f"{card_type}_card"
    
    # 获取卡片标题和状态数据
    title = data.get("title", "场景卡片")
    subtitle = data.get("subtitle", "")
    states = data.get("states", ["状态1", "状态2", "状态3"])
    current_state = data.get("current_state", 0)
    
    # ── 1. surfaceUpdate：定义组件树结构（480×380px）──
    components = [
        # 根容器 - 480×380px显示区域
        component("root", "Column", {
            "children": {"explicitList": ["header_section", "state_selector", "content_area"]},
            "spacing": {"literalNumber": 16},
            "width": lit_num(480),  # 固定宽度480px
            "height": lit_num(380), # 固定高度380px
            "padding": {"literalString": "16px"}  # 内部padding
        }),
        
        # 标题区域
        component("header_section", "Column", {
            "children": {"explicitList": ["title_text", "subtitle_text"]},
            "spacing": {"literalNumber": 4}
        }),
        component("title_text", "Text", {
            "text": path_bind("/title", title),
            "usageHint": lit("title")
        }),
        component("subtitle_text", "Text", {
            "text": path_bind("/subtitle", subtitle),
            "usageHint": lit("subtitle")
        }),
        
        # 状态选择器（集成导航）- 水平排列
        component("state_selector", "Row", {
            "children": {"explicitList": [f"state_btn_{i}" for i in range(len(states))]},
            "spacing": {"literalNumber": 8},
            "alignment": {"literalString": "center"}
        }),
    ]
    
    # 添加状态按钮
    for i, state_name in enumerate(states):
        btn_id = f"state_btn_{i}"
        components.append(component(btn_id, "Button", {
            "text": path_bind(f"/states/{i}/name", state_name),
            "onClick": {"literalString": f"select_state_{i}"},
            "style": path_bind(f"/states/{i}/style", "normal"),
            "usageHint": lit("button")
        }))
    
    # 内容区域 - 自适应高度
    components.append(component("content_area", "Container", {
        "child": "content_inner",
        "flex": lit_num(1)  # 自适应填充剩余空间
    }))
    
    components.append(component("content_inner", "Column", {
        "children": {"explicitList": ["state_content"]},
        "spacing": {"literalNumber": 12}
    }))
    
    components.append(component("state_content", "Card", {
        "child": "state_specific_content",
        "padding": {"literalString": "20px"},
        "borderRadius": lit_num(12),
        "borderWidth": lit_num(2),
        "borderColor": path_bind("/border_color", "#40FF5E")
    }))
    
    components.append(component("state_specific_content", "Column", {
        "children": {"explicitList": ["state_title", "state_main_content"]},
        "spacing": {"literalNumber": 16}
    }))
    
    components.append(component("state_title", "Text", {
        "text": path_bind("/current_state_name", states[current_state]),
        "usageHint": lit("title"),
        "color": path_bind("/title_color", "#40FF5E")
    }))
    
    components.append(component("state_main_content", "Column", {
        "children": {"explicitList": ["dynamic_content_1", "dynamic_content_2", "dynamic_content_3"]},
        "spacing": {"literalNumber": 12}
    }))
    
    # 动态内容占位符
    for i in range(1, 4):
        components.append(component(f"dynamic_content_{i}", "Text", {
            "text": path_bind(f"/dynamic_content_{i}", f"内容 {i}"),
            "usageHint": lit("body")
        }))
    
    # ── 2. dataModelUpdate：数据绑定 ──
    data_contents = [
        kv("title", title),
        kv("subtitle", subtitle),
        kv("border_color", "#40FF5E"),
        kv("title_color", "#40FF5E"),
        kv("current_state", current_state),
        kv("current_state_name", states[current_state])
    ]
    
    # 添加状态数据
    for i, state_name in enumerate(states):
        data_contents.append(kv(f"states/{i}/name", state_name))
        data_contents.append(kv(f"states/{i}/style", "normal" if i == current_state else "outline"))
    
    # 添加动态内容数据
    for i in range(1, 4):
        data_contents.append(kv(f"dynamic_content_{i}", f"动态内容 {i}"))
    
    # ── 构建完整的A2UI消息序列 ──
    messages = [
        surface_update(surface_id, components),
        data_model_update(surface_id, data_contents),
        begin_rendering(surface_id, "root")
    ]
    
    return to_jsonl(messages)


def create_scene_card(card_type: str, scene_data: dict) -> str:
    """创建特定场景卡片"""
    
    if card_type == "cooking":
        return build_cooking_card(scene_data)
    elif card_type == "driving":
        return build_driving_card(scene_data)
    elif card_type == "fitness":
        return build_fitness_card(scene_data)
    elif card_type == "navigation":
        return build_navigation_card(scene_data)
    elif card_type == "shopping":
        return build_shopping_card(scene_data)
    elif card_type == "translation":
        return build_translation_card(scene_data)
    else:
        # 默认使用基础模板
        return build_480x380_base_template(card_type, scene_data)


def build_cooking_card(data: dict) -> str:
    """构建烹饪卡片"""
    surface_id = "cooking_card"
    
    # 烹饪卡片数据
    states = ["准备食材", "烹饪中", "计时中", "用量提醒", "完成"]
    current_state = data.get("current_state", 0)
    
    # 使用基础模板
    base_data = {
        "title": "烹饪助手",
        "subtitle": "智能烹饪指导",
        "states": states,
        "current_state": current_state
    }
    
    # 添加烹饪特定数据
    base_data.update({
        "dish_name": data.get("dish_name", "红烧肉"),
        "step_desc": data.get("step_desc", "准备食材并切块"),
        "timer_value": data.get("timer_value", 300),  # 5分钟
        "ingredient_name": data.get("ingredient_name", "酱油"),
        "ingredient_amount": data.get("ingredient_amount", "20ml")
    })
    
    jsonl = build_480x380_base_template("cooking", base_data)
    
    # 转换为基础HTML渲染
    return convert_a2ui_to_html(jsonl, surface_id)


def build_driving_card(data: dict) -> str:
    """构建驾驶卡片"""
    surface_id = "driving_card"
    
    # 驾驶卡片数据
    states = ["正常行驶", "超速警告", "疲劳提醒", "路况提醒", "已停车"]
    current_state = data.get("current_state", 0)
    
    base_data = {
        "title": "驾驶辅助",
        "subtitle": "智能安全提醒",
        "states": states,
        "current_state": current_state
    }
    
    # 添加驾驶特定数据
    base_data.update({
        "speed": data.get("speed", 60),
        "speed_limit": data.get("speed_limit", 80),
        "warning_message": data.get("warning_message", "请保持安全车速"),
        "border_color": "#FF4040" if current_state == 1 else "#40FF5E"
    })
    
    jsonl = build_480x380_base_template("driving", base_data)
    return convert_a2ui_to_html(jsonl, surface_id)


def build_fitness_card(data: dict) -> str:
    """构建健康运动卡片"""
    surface_id = "fitness_card"
    
    states = ["准备", "运动中", "心率警告", "里程碑", "冷却", "总结"]
    current_state = data.get("current_state", 0)
    
    base_data = {
        "title": "健康运动",
        "subtitle": "实时运动监测",
        "states": states,
        "current_state": current_state
    }
    
    base_data.update({
        "heart_rate": data.get("heart_rate", 120),
        "heart_rate_zone": data.get("heart_rate_zone", "有氧区间"),
        "progress": data.get("progress", 65),
        "calories": data.get("calories", 245)
    })
    
    jsonl = build_480x380_base_template("fitness", base_data)
    return convert_a2ui_to_html(jsonl, surface_id)


def build_navigation_card(data: dict) -> str:
    """构建导航卡片"""
    surface_id = "navigation_card"
    
    states = ["路线规划", "行进中", "转弯提醒", "重新规划", "到达"]
    current_state = data.get("current_state", 1)
    
    base_data = {
        "title": "导航",
        "subtitle": "AR智能导航",
        "states": states,
        "current_state": current_state
    }
    
    base_data.update({
        "next_action": data.get("next_action", "直行"),
        "distance": data.get("distance", "500米"),
        "time": data.get("time", "3分钟"),
        "street_name": data.get("street_name", "人民路")
    })
    
    jsonl = build_480x380_base_template("navigation", base_data)
    return convert_a2ui_to_html(jsonl, surface_id)


def build_shopping_card(data: dict) -> str:
    """构建购物比价卡片"""
    surface_id = "shopping_card"
    
    states = ["待机扫描", "商品识别", "价格比对", "评价摘要", "加购确认", "收藏追价"]
    current_state = data.get("current_state", 1)
    
    base_data = {
        "title": "智能购物",
        "subtitle": "AR比价助手",
        "states": states,
        "current_state": current_state
    }
    
    base_data.update({
        "product_name": data.get("product_name", "智能手机"),
        "price_lowest": data.get("price_lowest", "¥3,299"),
        "price_save": data.get("price_save", "节省 ¥200"),
        "rating": data.get("rating", 4.5)
    })
    
    jsonl = build_480x380_base_template("shopping", base_data)
    return convert_a2ui_to_html(jsonl, surface_id)


def build_translation_card(data: dict) -> str:
    """构建实时翻译卡片"""
    surface_id = "translation_card"
    
    states = ["待机", "识别中", "译文显示", "语言切换", "历史回顾"]
    current_state = data.get("current_state", 2)
    
    base_data = {
        "title": "实时翻译",
        "subtitle": "AR翻译助手",
        "states": states,
        "current_state": current_state
    }
    
    base_data.update({
        "source_text": data.get("source_text", "Hello, how are you?"),
        "translated_text": data.get("translated_text", "你好，你怎么样？"),
        "confidence": data.get("confidence", 92),
        "source_lang": data.get("source_lang", "英语"),
        "target_lang": data.get("target_lang", "中文")
    })
    
    jsonl = build_480x380_base_template("translation", base_data)
    return convert_a2ui_to_html(jsonl, surface_id)


def convert_a2ui_to_html(jsonl_content: str, surface_id: str) -> str:
    """
    将A2UI JSONL转换为HTML文件
    模拟渲染器的行为，生成可直接显示的HTML
    """
    html_template = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YodaOS Sprite - {surface_id.replace('_', ' ').title()}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'HarmonyOS Sans SC', -apple-system, BlinkMacSystemFont, sans-serif;
            background: #000000;
            color: #FFFFFF;
            padding: 0;
            margin: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            min-height: 100vh;
        }}
        
        /* 480×380px显示区域 */
        .viewport-container {{
            width: 480px;
            height: 380px;
            background: #1C1C1C;
            border-radius: 12px;
            border: 2px solid #40FF5E;
            overflow: hidden;
            margin: 0;
            padding: 16px;
            position: relative;
        }}
        
        .header {{
            margin-bottom: 16px;
        }}
        
        .title {{
            font-size: 24px;
            font-weight: 600;
            color: #FFFFFF;
            margin-bottom: 4px;
        }}
        
        .subtitle {{
            font-size: 16px;
            color: #AAAAAA;
            font-weight: 400;
        }}
        
        .state-selector {{
            display: flex;
            gap: 8px;
            margin-bottom: 16px;
            justify-content: center;
        }}
        
        .state-btn {{
            padding: 8px 16px;
            border: 2px solid #40FF5E;
            background: transparent;
            color: #40FF5E;
            border-radius: 6px;
            font-size: 16px;
            cursor: pointer;
            transition: all 0.2s;
        }}
        
        .state-btn.active {{
            background: #40FF5E;
            color: #000000;
        }}
        
        .state-btn:hover {{
            opacity: 0.8;
        }}
        
        .content-area {{
            flex: 1;
            overflow-y: auto;
        }}
        
        .card {{
            background: #2A2A2A;
            border-radius: 12px;
            padding: 20px;
            border: 2px solid #40FF5E;
        }}
        
        .state-title {{
            font-size: 20px;
            color: #40FF5E;
            margin-bottom: 16px;
            font-weight: 600;
        }}
        
        .state-content {{
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}
        
        .dynamic-content {{
            font-size: 16px;
            color: #FFFFFF;
            line-height: 1.5;
        }}
        
        .debug-info {{
            margin-top: 20px;
            color: #888888;
            font-size: 14px;
            text-align: center;
        }}
        
        /* 确保整个页面不超过480×380px */
        #app {{
            width: 480px;
            height: 380px;
            position: relative;
        }}
    </style>
</head>
<body>
    <div id="app">
        <div class="viewport-container">
            <div class="header">
                <div class="title" id="title">场景卡片</div>
                <div class="subtitle" id="subtitle"></div>
            </div>
            
            <div class="state-selector" id="state-selector">
                <!-- 状态按钮通过JS动态生成 -->
            </div>
            
            <div class="content-area">
                <div class="card">
                    <div class="state-title" id="state-title">当前状态</div>
                    <div class="state-content" id="state-content">
                        <div class="dynamic-content" id="dynamic-content-1">内容 1</div>
                        <div class="dynamic-content" id="dynamic-content-2">内容 2</div>
                        <div class="dynamic-content" id="dynamic-content-3">内容 3</div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="debug-info">
            显示区域：480×380px | A2UI协议v0.8 | {surface_id}
        </div>
    </div>

    <script>
        // 模拟A2UI JSONL数据
        const a2uiData = {json.dumps({"messages": jsonl_content.split("\\n")})};
        
        // 初始化数据
        let currentState = 0;
        const states = ["状态1", "状态2", "状态3", "状态4", "状态5"];
        const title = "{surface_id.replace('_', ' ').title()}";
        
        // 更新UI
        function updateUI() {{
            document.getElementById('title').textContent = title;
            document.getElementById('state-title').textContent = states[currentState];
            
            // 更新状态按钮
            const selector = document.getElementById('state-selector');
            selector.innerHTML = '';
            
            states.forEach((state, index) => {{
                const button = document.createElement('button');
                button.className = `state-btn ${{index === currentState ? 'active' : ''}}`;
                button.textContent = state;
                button.onclick = () => {{
                    currentState = index;
                    updateUI();
                }};
                selector.appendChild(button);
            }});
            
            // 更新动态内容
            for (let i = 1; i <= 3; i++) {{
                document.getElementById(`dynamic-content-${{i}}`).textContent = 
                    `状态 ${{currentState + 1}} - 内容 ${{i}}`;
            }}
        }}
        
        // 页面加载时初始化
        document.addEventListener('DOMContentLoaded', updateUI);
    </script>
</body>
</html>'''
    
    return html_template


if __name__ == "__main__":
    # 测试生成基础模板
    test_data = {
        "title": "测试卡片",
        "subtitle": "480×380px演示",
        "states": ["状态A", "状态B", "状态C", "状态D"],
        "current_state": 0
    }
    
    jsonl = build_480x380_base_template("test", test_data)
    print(jsonl)
    print("\n" + "="*80 + "\n")
    
    # 生成HTML文件
    html = convert_a2ui_to_html(jsonl, "test_card")
    print(html)