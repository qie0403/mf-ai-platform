"""
多模态图片解析模块
支持图片上传、base64编码，调用多模态大模型，实现图片内容识别、OCR、细节问答、内容分析
"""
import streamlit as st
import base64
from io import BytesIO
from PIL import Image
from .llm_client import llm_client

def image_to_base64(image_file: BytesIO) -> str:
    """将图片文件转换为base64编码，适配多模态大模型输入要求"""
    try:
        image = Image.open(image_file)
        # 转换为RGB模式，兼容PNG透明通道等所有格式
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")
        # 保存到字节流并编码
        buffer = BytesIO()
        image.save(buffer, format="JPEG")
        base64_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return base64_str
    except Exception as e:
        st.error(f"图片处理失败：{str(e)}")
        return ""

def render_multimodal_parser_interface():
    """渲染多模态图片解析模块的界面，处理图片上传和解析逻辑"""
    st.header("🖼️ 多模态图片解析")
    st.divider()

    # 1. 图片上传区域
    st.subheader("上传图片")
    uploaded_image = st.file_uploader(
        "支持格式：JPG、PNG、JPEG",
        type=["jpg", "png", "jpeg"],
        help="请上传需要解析的图片，单个文件大小建议不超过20MB"
    )

    # 2. 图片预览
    if uploaded_image is not None:
        st.subheader("图片预览")
        st.image(uploaded_image, use_container_width=True)

    # 3. 解析功能选择与提问
    st.subheader("解析设置")
    parse_mode = st.radio(
        "解析模式",
        options=["图片整体描述", "OCR文字提取", "图片内容问答", "细节深度分析"],
        index=0,
        horizontal=True
    )

    # 解析模式默认提问
    default_queries = {
        "图片整体描述": "请详细描述这张图片的内容，包括场景、主体、环境、色彩、氛围等所有信息",
        "OCR文字提取": "请精准提取这张图片中的所有文字内容，按原文的格式和顺序输出，不要遗漏任何文字",
        "图片内容问答": "",
        "细节深度分析": "请深度分析这张图片的所有细节，包括隐藏的信息、物体的细节、场景的逻辑、可能的背景等"
    }

    user_query = st.text_area(
        "你的提问/解析要求",
        value=default_queries[parse_mode],
        height=100,
        placeholder="请输入你针对这张图片的提问或解析要求，越详细越精准",
        disabled=parse_mode not in ["图片内容问答"]
    )

    # 4. 模型参数
    temperature = st.slider(
        "模型温度",
        min_value=0.0,
        max_value=0.7,
        value=0.3,
        step=0.1,
        help="图片解析建议使用较低温度，保证识别精准度"
    )

    # 5. 解析按钮
    parse_btn = st.button(
        "开始解析图片",
        type="primary",
        use_container_width=True,
        disabled=not (uploaded_image and user_query)
    )

    # 6. 处理图片解析逻辑
    if parse_btn and uploaded_image and user_query:
        # 转换图片为base64
        with st.spinner("正在处理图片..."):
            image_bytes = BytesIO(uploaded_image.getvalue())
            image_base64 = image_to_base64(image_bytes)

        if not image_base64:
            st.error("图片处理失败，无法进行解析")
            return

        # 调用多模态大模型
        with st.spinner("正在解析图片内容，请稍候..."):
            parse_result = llm_client.multimodal_completion(
                image_base64=image_base64,
                user_query=user_query,
                temperature=temperature
            )

        # 展示解析结果
        if parse_result:
            st.subheader("🔍 图片解析结果")
            st.divider()
            st.markdown(parse_result)

            st.download_button(
                label="下载解析结果",
                data=parse_result,
                file_name=f"{uploaded_image.name.split('.')[0]}_解析结果.txt",
                mime="text/plain",
                use_container_width=True
            )
        else:
            st.error("图片解析失败，请检查多模态模型配置、API密钥或网络连接")