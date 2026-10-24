"""
多功能AI工具平台 主程序入口
基于Streamlit开发，整合智能对话、文档总结、文案生成、多模态图片解析四大核心模块
作者：AI应用开发工程师学习项目
版本：v1.0
"""
import streamlit as st
from modules.chat_module import render_chat_interface
from modules.document_summary import render_document_summary_interface
from modules.copywriting_gen import render_copywriting_gen_interface
from modules.multimodal_parser import render_multimodal_parser_interface

# 页面全局配置，必须放在代码最顶部
st.set_page_config(
    page_title="MF-AI 工作台",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---- v1.1 自定义主题：由 .streamlit/config.toml 定义深蓝黑 ----
# 侧边栏用近黑、主标题蓝渐变、主按钮钢蓝
CUSTOM_CSS = """
<style>
    /* 侧边栏：近黑，比主背景更深 */
    [data-testid="stSidebar"] {
        background-color: #0C0F14 !important;
    }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] div {
        color: #B8C0CC !important;
    }
    /* 主标题：钢蓝渐变（只套在 .title-gradient span 上，避免影响 emoji 颜色） */
    h1 .title-gradient {
        background: linear-gradient(90deg, #7FB3E8, #4A90D9);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    /* 主按钮：钢蓝 + 柔光阴影，hover 时亮一档，不与背景混淆 */
    .stButton > button[kind="primary"],
    .stDownloadButton > button[kind="primary"] {
        background-color: #4A90D9;
        border-radius: 10px;
        border: none;
        color: #FFFFFF;
        box-shadow: 0 4px 14px rgba(74, 144, 217, 0.35);
        transition: background-color 0.2s ease, transform 0.1s ease;
    }
    .stButton > button[kind="primary"]:hover,
    .stDownloadButton > button[kind="primary"]:hover {
        background-color: #6BB3F0 !important;
        color: #FFFFFF !important;
        border: none !important;
    }
    .stButton > button[kind="primary"]:active,
    .stDownloadButton > button[kind="primary"]:active {
        background-color: #3A7BC0 !important;
        color: #FFFFFF !important;
    }
    .stButton > button[kind="primary"]:focus:not(:active),
    .stDownloadButton > button[kind="primary"]:focus:not(:active) {
        background-color: #4A90D9 !important;
        color: #FFFFFF !important;
        outline: none !important;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

def render_page_header():
    """渲染页面头部标题和介绍（emoji 不参与渐变，保留原生彩色）"""
    st.markdown(
        '<h1>🚀 <span class="title-gradient">MF-AI 工作台</span></h1>',
        unsafe_allow_html=True
    )
    st.caption("一站式AI生产力工具 · 文案生成 / 智能对话 / 文档总结 / 多模态图片解析")
    st.divider()

def main():
    # 渲染页面头部
    render_page_header()

    # 侧边栏模块导航（v1.1：按使用频率重排，高频模块置顶，减少用户点击成本）
    with st.sidebar:
        st.title("功能导航")
        st.divider()
        # 模块选择：文案生成 > 智能对话 > 文档总结 > 多模态图片解析
        selected_module = st.radio(
            "请选择功能模块",
            options=["文案生成", "智能对话", "文档总结", "多模态图片解析"],
            index=0
        )
        st.divider()
        st.caption("v1.1 | MF-AI 工作台 · 迭代版")

    # 根据选择渲染对应模块界面
    if selected_module == "文案生成":
        render_copywriting_gen_interface()
    elif selected_module == "智能对话":
        render_chat_interface()
    elif selected_module == "文档总结":
        render_document_summary_interface()
    elif selected_module == "多模态图片解析":
        render_multimodal_parser_interface()

# 程序入口
if __name__ == "__main__":
    main()