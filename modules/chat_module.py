"""
智能对话模块
实现多轮对话、上下文记忆、流式输出功能
✅ 终极持久化：刷新/重启/切换页面/关闭浏览器 对话历史永不丢失
✅ 仅点击清空按钮才会删除记录
"""
import streamlit as st
import json
import os
import re  #新增
from datetime import datetime
from .llm_client import llm_client


# 配置：对话历史本地存储文件路径（自动创建，自动加载）
CHAT_HISTORY_FILE = "chat_history.json"
# v1.1 优化后的系统Prompt：强制"结论先行 + 分点论述 + 一句话总结"结构化输出，
# 解决之前回答冗长、重点不突出的问题
CHAT_SYSTEM_PROMPT = """
你是一个专业、友好、高效的AI智能助手，具备以下能力：
1. 精准理解用户的问题，给出清晰、准确、有逻辑的回答
2. 支持多轮对话，严格结合上下文信息，不偏离对话主题
3. 回答内容专业严谨，同时通俗易懂，避免冗余和无关信息
4. 当用户的问题超出你的知识范围时，诚实告知，不编造虚假信息

【输出格式硬性要求】
- 第一句必须直接给出结论或核心答案，不要绕弯子
- 中间用「分点列表」展开理由、步骤或关键信息，每条不超过2行
- 涉及代码/命令时，用 ```代码块``` 包裹，可直接复制运行
- 结尾用一句话做总结或给出下一步建议
- 整体回答控制在 300 字以内，超长问题再适当展开
"""

# --------------------------
# 核心：本地文件持久化函数
# --------------------------
def save_chat_history():
    """将对话历史保存到本地JSON文件"""
    try:
        with open(CHAT_HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(st.session_state.chat_messages, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.warning(f"保存历史失败：{str(e)}")

def load_chat_history():
    """从本地文件加载对话历史（无文件则初始化）"""
    if os.path.exists(CHAT_HISTORY_FILE):
        try:
            with open(CHAT_HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    # 默认初始对话
    return [{"role": "assistant", "content": "你好！我是你的智能AI助手，有什么可以帮你的吗？"}]

def clean_answer_text(text):
    """最终兜底：清洗系统报错、修复Markdown格式"""
    # 1. 移除所有系统报错行
    error_patterns = [
        r"API调用出错[:：].*?$",
        r"list index out of range",
        r"IndexError[:：].*?$",
        r"Error[:：].*?$",
    ]
    for pattern in error_patterns:
        text = re.sub(pattern, "", text, flags=re.MULTILINE)
    
    # 2. 修复未闭合的加粗标记 **
    if text.count("**") % 2 != 0:
        text += "**"
    
    # 3. 去除报错留下的多余空行
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def init_chat_session():
    """初始化会话：优先加载本地历史，永久不丢失"""
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = load_chat_history()

def build_chat_markdown() -> str:
    """v1.1 新增：把当前对话历史渲染成一份带时间戳的 Markdown 对话报告"""
    lines = [
        "# 智能对话记录报告",
        f"\n> 导出时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"> 共 {len(st.session_state.chat_messages)} 轮对话\n",
    ]
    for i, msg in enumerate(st.session_state.chat_messages, 1):
        role_label = "🧑 用户" if msg["role"] == "user" else "🤖 助手"
        lines.append(f"### {i}. {role_label}")
        lines.append(msg["content"].strip())
        lines.append("")
    return "\n".join(lines)

# --------------------------
# 界面渲染主逻辑
# --------------------------
def render_chat_interface():
    st.header("💬 智能对话")
    st.divider()

    # 初始化持久化对话历史
    init_chat_session()

    # 侧边栏设置
    with st.sidebar:
        st.subheader("对话参数设置")
        # v1.1：默认温度从 0.7 调到 0.5，降低输出随机性，提升回答稳定性
        temperature = st.slider(
            "模型温度", 0.0, 1.0, 0.5, 0.1, help="0=最严谨稳定，1=最有创造性；默认0.5兼顾稳定与表达力"
        )
        
        # 唯一清空逻辑：点击按钮 → 清空内存+清空本地文件
        if st.button("清空对话历史", type="primary", use_container_width=True):
            st.session_state.chat_messages = [
                {"role": "assistant", "content": "你好！我是你的智能AI助手，有什么可以帮你的吗？"}
            ]
            save_chat_history()  # 同步清空本地文件
            st.rerun()

        # v1.1 新增：一键导出对话记录为 Markdown 报告（含时间戳、轮次编号）
        st.download_button(
            label="导出对话报告 (.md)",
            data=build_chat_markdown(),
            file_name=f"chat_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            mime="text/markdown",
            use_container_width=True,
            disabled=len(st.session_state.chat_messages) <= 1,
            help="把当前所有对话导出为带轮次编号的 Markdown 报告，方便复盘/存档"
        )

    # 渲染所有对话（从持久化存储读取）
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # 用户输入处理
    if user_input := st.chat_input("请输入你想咨询的问题..."):
        # 1. 添加用户消息
        st.session_state.chat_messages.append({"role": "user", "content": user_input})
        save_chat_history()  # 实时保存
        with st.chat_message("user"):
            st.markdown(user_input)

        # 2. 构建请求消息
        full_messages = [{"role": "system", "content": CHAT_SYSTEM_PROMPT}] + st.session_state.chat_messages

                # 3. 流式输出回复
        with st.chat_message("assistant"):
            container = st.empty()
            full_response = ""
            for chunk in llm_client.chat_stream(messages=full_messages, temperature=temperature):
                full_response += chunk
                container.markdown(full_response + "▌")
            
            #新增：流式输出完成后，清洗报错文本、修复格式
            full_response = clean_answer_text(full_response)
            container.markdown(full_response)


        # 4. 添加助手消息并保存
        st.session_state.chat_messages.append({"role": "assistant", "content": full_response})
        save_chat_history()  # 实时持久化