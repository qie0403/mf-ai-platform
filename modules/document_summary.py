"""
文档总结模块
支持PDF、DOCX、TXT格式文件上传，实现文档内容读取、核心信息提炼、多维度总结
"""
import streamlit as st
from PyPDF2 import PdfReader
from docx import Document
from io import BytesIO
from .llm_client import llm_client

# 优化后的文档总结系统Prompt，保证提炼精准
DOC_SUMMARY_SYSTEM_PROMPT = """
你是一名专业的文档分析师，具备超强的内容提炼和总结能力，严格遵守以下规则：
1. 精准理解文档的核心主题、核心观点、关键数据和重要结论
2. 总结内容必须完全基于文档原文，不添加任何外部信息和主观臆断
3. 根据用户选择的总结模式，输出对应格式的内容，结构清晰，逻辑严谨
4. 语言简洁精炼，避免冗余，同时不遗漏文档的核心信息
5. 若文档内容存在逻辑混乱或信息不全，如实告知用户，不编造内容
"""

def read_pdf_file(file_bytes: BytesIO) -> str:
    """读取PDF文件内容，提取文本"""
    try:
        reader = PdfReader(file_bytes)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
    except Exception as e:
        st.error(f"PDF文件读取失败：{str(e)}")
        return ""

def read_docx_file(file_bytes: BytesIO) -> str:
    """读取Word(DOCX)文件内容，提取文本"""
    try:
        doc = Document(file_bytes)
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text
    except Exception as e:
        st.error(f"Word文件读取失败：{str(e)}")
        return ""

def read_txt_file(file_bytes: BytesIO) -> str:
    """读取TXT文本文件内容，兼容多编码格式"""
    try:
        text = file_bytes.read().decode("utf-8")
        return text
    except UnicodeDecodeError:
        try:
            text = file_bytes.read().decode("gbk")
            return text
        except Exception as e:
            st.error(f"TXT文件读取失败，不支持的编码格式：{str(e)}")
            return ""
    except Exception as e:
        st.error(f"TXT文件读取失败：{str(e)}")
        return ""

def render_document_summary_interface():
    """渲染文档总结模块的界面，处理文件上传和总结逻辑"""
    st.header("📄 文档总结")
    st.divider()

    # 1. 文件上传区域
    st.subheader("上传文档")
    uploaded_file = st.file_uploader(
        "支持格式：PDF、DOCX、TXT",
        type=["pdf", "docx", "txt"],
        help="请上传需要总结的文档文件，单个文件大小建议不超过50MB"
    )

    # 2. 总结参数配置
    st.subheader("总结设置")
    col1, col2 = st.columns(2)
    with col1:
        summary_mode = st.selectbox(
            "总结模式",
            options=["精简总结", "详细总结", "大纲式总结", "核心要点提取"],
            index=0
        )
    with col2:
        temperature = st.slider(
            "模型温度",
            min_value=0.0,
            max_value=0.8,
            value=0.3,
            step=0.1,
            help="文档总结建议使用较低温度，保证内容精准"
        )

    # 自定义补充要求
    custom_requirement = st.text_area(
        "自定义补充要求（选填）",
        placeholder="例如：重点总结文档中的数据部分、突出风险点、按章节总结等",
        height=80
    )

    # 3. 文档内容读取与展示
    document_text = ""
    if uploaded_file is not None:
        file_ext = uploaded_file.name.split(".")[-1].lower()
        file_bytes = BytesIO(uploaded_file.getvalue())

        with st.spinner("正在读取文档内容..."):
            if file_ext == "pdf":
                document_text = read_pdf_file(file_bytes)
            elif file_ext == "docx":
                document_text = read_docx_file(file_bytes)
            elif file_ext == "txt":
                document_text = read_txt_file(file_bytes)

        # 展示文档读取结果
        if document_text:
            st.success(f"文档读取成功！共提取到{len(document_text)}个字符")
            with st.expander("查看文档原文", expanded=False):
                st.text_area("文档内容", document_text, height=300, disabled=True)
        else:
            st.warning("文档内容为空或读取失败，请检查文件是否损坏")

    # 4. 生成总结按钮
    generate_btn = st.button(
        "生成文档总结",
        type="primary",
        use_container_width=True,
        disabled=not document_text
    )

    # 5. 处理总结生成逻辑
    if generate_btn and document_text:
        user_prompt = f"""
        请对以下文档内容进行{summary_mode}，严格遵守系统提示词的规则。
        补充要求：{custom_requirement if custom_requirement else '无'}
        文档内容如下：
        ------------------------
        {document_text}
        ------------------------
        """

        messages = [
            {"role": "system", "content": DOC_SUMMARY_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ]

        with st.spinner("正在生成文档总结，请稍候..."):
            summary_result = llm_client.chat_completion(
                messages=messages,
                temperature=temperature
            )

        # 展示总结结果
        if summary_result:
            st.subheader("📋 文档总结结果")
            st.divider()
            st.markdown(summary_result)

            st.download_button(
                label="下载总结结果",
                data=summary_result,
                file_name=f"{uploaded_file.name.split('.')[0]}_总结结果.txt",
                mime="text/plain",
                use_container_width=True
            )
        else:
            st.error("总结生成失败，请检查API配置或网络连接")