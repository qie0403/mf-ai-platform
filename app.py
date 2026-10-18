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
    page_title="多功能AI工具平台",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

def render_page_header():
    """渲染页面头部标题和介绍"""
    st.title("🤖 多功能AI工具平台")
    st.caption("一站式AI生产力工具，集成智能对话、文档总结、文案生成、多模态图片解析四大核心能力")
    st.divider()

def main():
    # 渲染页面头部
    render_page_header()

    # 侧边栏模块导航
    with st.sidebar:
        st.title("功能导航")
        st.divider()
        # 模块选择
        selected_module = st.radio(
            "请选择功能模块",
            options=["智能对话", "文档总结", "文案生成", "多模态图片解析"],
            index=0
        )
        st.divider()
        st.caption("v1.0 | AI应用开发工程师项目实战")

    # 根据选择渲染对应模块界面
    if selected_module == "智能对话":
        render_chat_interface()
    elif selected_module == "文档总结":
        render_document_summary_interface()
    elif selected_module == "文案生成":
        render_copywriting_gen_interface()
    elif selected_module == "多模态图片解析":
        render_multimodal_parser_interface()

# 程序入口
if __name__ == "__main__":
    main()