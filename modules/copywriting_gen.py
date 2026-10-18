"""
文案生成模块
预设多场景文案模板，优化场景化Prompt，实现高质量文案一键生成
"""
import streamlit as st
from .llm_client import llm_client

# 场景化专属Prompt，深度优化每个场景的输出效果
COPYWRITING_SYSTEM_PROMPTS = {
    "小红书文案": """
    你是一名资深的小红书爆款文案策划师，严格遵守以下小红书文案规则：
    1. 标题吸睛，多用emoji，包含关键词，符合小红书用户阅读习惯
    2. 正文口语化、接地气，有真情实感，避免生硬广告
    3. 段落简短，多用换行，重点内容加粗突出
    4. 结尾添加相关的热门话题标签（hashtag）
    5. 内容符合平台规范，不违规，不夸大
    """,
    "公众号推文": """
    你是一名资深的公众号内容主编，擅长撰写高质量公众号推文，严格遵守以下规则：
    1. 标题有吸引力，能引发用户点击欲，符合公众号传播调性
    2. 文章结构清晰，有开头引入、正文论述、结尾升华，逻辑严谨
    3. 内容有深度、有价值，能给用户带来收获，避免空洞无物
    4. 语言风格适配目标受众，可正式可亲切，符合公众号的品牌定位
    5. 结尾引导用户点赞、在看、转发、关注，提升互动率
    """,
    "短视频脚本": """
    你是一名资深的短视频内容策划师，擅长撰写爆款短视频脚本，严格遵守以下规则：
    1. 开头3秒必须有钩子，抓住用户注意力，避免划走
    2. 脚本分镜头设计，包含画面内容、台词/旁白、时长、背景音乐提示
    3. 内容节奏快，信息密度高，符合短视频用户的观看习惯
    4. 结尾有引导互动（点赞、关注、评论、收藏）的设计
    5. 时长控制合理，符合平台规则，内容积极正向
    """,
    "商务邮件": """
    你是一名专业的商务文书专员，擅长撰写规范、专业的商务邮件，严格遵守以下规则：
    1. 邮件主题清晰明确，一眼就能看出邮件核心目的
    2. 格式规范，包含称呼、正文、结尾敬语、署名、联系方式
    3. 语言专业、严谨、礼貌，逻辑清晰，重点突出，避免冗余
    4. 内容准确无误，不出现歧义，符合商务沟通的礼仪和规范
    5. 根据收件人身份调整语气，做到得体合适
    """,
    "工作总结": """
    你是一名资深的职场顾问，擅长撰写高质量、高认可度的工作总结，严格遵守以下规则：
    1. 结构清晰，包含工作成果、核心亮点、问题不足、未来规划四大核心部分
    2. 工作成果量化呈现，用数据说话，避免空泛的描述
    3. 内容重点突出，贴合岗位要求，展现个人价值和能力
    4. 语言正式、严谨、积极向上，符合职场汇报的规范
    5. 问题分析客观，未来规划具体可行，不空洞
    """,
    "通用文案": """
    你是一名专业的文案策划师，擅长撰写各类通用文案，严格遵守以下规则：
    1. 精准理解用户的核心需求，文案主题明确，重点突出
    2. 语言风格适配使用场景和目标受众，得体合适
    3. 内容逻辑清晰，有吸引力，能达到用户的文案目标
    4. 避免冗余、空洞的内容，保证文案的实用性和传播性
    """
}

def render_copywriting_gen_interface():
    """渲染文案生成模块的界面，处理文案生成逻辑"""
    st.header("✍️ 文案生成")
    st.divider()

    # 1. 文案场景选择
    st.subheader("选择文案场景")
    scene = st.selectbox(
        "文案使用场景",
        options=list(COPYWRITING_SYSTEM_PROMPTS.keys()),
        index=0
    )

    # 2. 核心需求输入
    st.subheader("填写文案核心需求")
    core_theme = st.text_input(
        "文案核心主题/产品/事件",
        placeholder="例如：春日护肤新品推广、月度工作汇报、产品推广短视频等",
        help="必填项，明确文案的核心主题"
    )
    key_info = st.text_area(
        "核心信息/重点内容（必填）",
        placeholder="例如：产品核心卖点、活动时间、优惠政策、工作核心成果、视频核心内容等",
        height=120,
        help="请填写文案必须包含的核心信息，越详细生成的文案越贴合需求"
    )
    style_requirement = st.text_input(
        "风格要求（选填）",
        placeholder="例如：温柔治愈、幽默搞笑、正式严谨、年轻化、科技感等"
    )
    word_count = st.number_input(
        "字数要求",
        min_value=50,
        max_value=10000,
        value=500,
        step=50,
        help="文案的目标字数，模型会尽量贴合该要求"
    )

    # 3. 参数配置
    col1, col2 = st.columns(2)
    with col1:
        temperature = st.slider(
            "模型温度",
            min_value=0.3,
            max_value=1.0,
            value=0.8,
            step=0.1,
            help="文案生成建议使用较高温度，提升创造性"
        )
    with col2:
        generate_count = st.selectbox(
            "生成版本数量",
            options=[1, 2, 3],
            index=0,
            help="选择生成几个不同版本的文案"
        )

    # 4. 生成按钮
    generate_btn = st.button(
        "生成文案",
        type="primary",
        use_container_width=True,
        disabled=not (core_theme and key_info)
    )

    # 5. 处理文案生成逻辑
    if generate_btn and core_theme and key_info:
        system_prompt = COPYWRITING_SYSTEM_PROMPTS[scene]
        user_prompt = f"""
        请你生成{scene}，具体要求如下：
        1. 核心主题：{core_theme}
        2. 必须包含的核心信息：{key_info}
        3. 风格要求：{style_requirement if style_requirement else '无特殊要求，贴合场景即可'}
        4. 字数要求：约{word_count}字
        5. 生成版本数量：{generate_count}个，每个版本要有明显的差异化
        请严格遵守系统提示词中的规则，生成高质量、符合要求的文案。
        """

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        with st.spinner("正在生成文案，请稍候..."):
            copywriting_result = llm_client.chat_completion(
                messages=messages,
                temperature=temperature
            )

        # 展示生成结果
        if copywriting_result:
            st.subheader("📝 文案生成结果")
            st.divider()
            st.markdown(copywriting_result)

            st.download_button(
                label="下载文案结果",
                data=copywriting_result,
                file_name=f"{core_theme}_{scene}_文案.txt",
                mime="text/plain",
                use_container_width=True
            )
        else:
            st.error("文案生成失败，请检查API配置或网络连接")