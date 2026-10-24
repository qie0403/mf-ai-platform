"""
首页模块
工作台落地页：展示四大功能入口、快速开始引导
"""
import streamlit as st


def _feature_card(emoji: str, title: str, desc: str, features: list):
    """渲染单个功能卡片（深色主题：石板灰底 + 钢蓝描边）"""
    feature_html = "".join(f"<li>{f}</li>" for f in features)
    st.markdown(
        f"""
        <div style="
            background-color:#1F2530;
            border:1px solid #2E3A52;
            border-left:3px solid #4A90D9;
            border-radius:12px;
            padding:18px 20px;
            margin-bottom:16px;
            min-height:210px;
        ">
            <div style="font-size:26px; margin-bottom:6px;">{emoji}</div>
            <div style="font-size:18px; font-weight:700; color:#E6E9EF; margin-bottom:8px;">{title}</div>
            <div style="font-size:13px; color:#9AA7BD; line-height:1.6; margin-bottom:10px;">{desc}</div>
            <ul style="font-size:13px; color:#B8C0CC; line-height:1.8; margin:0; padding-left:18px;">
                {feature_html}
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_home_interface():
    """渲染首页工作台"""
    # 欢迎区
    st.markdown(
        """
        <div style="
            background: linear-gradient(135deg, #16213A 0%, #1F2530 100%);
            border:1px solid #2E3A52;
            border-radius:14px;
            padding:28px 32px;
            margin-bottom:26px;
        ">
            <div style="font-size:22px; font-weight:700; color:#E6E9EF; margin-bottom:10px;">
                👋 欢迎使用 MF-AI 工作台
            </div>
            <div style="font-size:14px; color:#9AA7BD; line-height:1.8;">
                一站式 AI 生产力工具，集成 <b style="color:#7FB3E8;">文案生成</b>、
                <b style="color:#7FB3E8;">智能对话</b>、
                <b style="color:#7FB3E8;">文档总结</b>、
                <b style="color:#7FB3E8;">多模态图片解析</b> 四大能力。
                从左侧边栏选择功能即可开始，所有接口兼容 OpenAI 格式。
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 四大功能卡片：2 列 × 2 行
    st.markdown("#### 🧭 功能导航")
    col1, col2 = st.columns(2)
    with col1:
        _feature_card(
            "✍️", "文案生成",
            "6 大高频场景的专属 Prompt，一键生成高质量营销/职场文案。",
            ["小红书 / 公众号 / 短视频脚本", "商务邮件 / 工作总结 / 通用文案", "支持风格、字数、多版本差异化"]
        )
        _feature_card(
            "📄", "文档总结",
            "上传文档自动提炼核心内容，支持多种总结模式。",
            ["支持 PDF / DOCX / TXT", "精简 / 详细 / 大纲 / 要点四种模式", "结果可一键下载"]
        )
    with col2:
        _feature_card(
            "💬", "智能对话",
            "流式多轮对话，历史本地持久化，结构化输出。",
            ["打字机流式输出，上下文记忆", "刷新/重启不丢失对话历史", "一键导出 Markdown 对话报告"]
        )
        _feature_card(
            "🖼️", "多模态图片解析",
            "调用多模态大模型，识别图片内容、文字与细节。",
            ["整体描述 / OCR 文字提取", "内容问答 / 细节深度分析", "支持 JPG / PNG / JPEG"]
        )

    # 快速开始
    st.markdown("#### 🚀 快速开始")
    step1, step2, step3 = st.columns(3)
    with step1:
        st.info("**第 1 步**\n\n在左侧边栏选择需要的功能模块")
    with step2:
        st.info("**第 2 步**\n\n填写需求、上传文档或图片")
    with step3:
        st.info("**第 3 步**\n\n点击生成，结果可下载或导出")

    st.divider()
    st.caption("MF-AI 工作台 v1.1 · 基于 Streamlit + OpenAI 兼容接口 · 仅供学习实战使用")
