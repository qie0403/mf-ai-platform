"""
大模型客户端封装模块
统一管理所有大模型API调用，兼容OpenAI格式接口，支持流式输出、多模态能力
所有功能模块统一调用此客户端，降低代码耦合，方便切换模型
"""
import os
import logging
from dotenv import load_dotenv
from openai import OpenAI
from typing import Generator, List, Dict, Optional

#配置日志
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()

def safe_list_get(list,index=0,default=None):
    """
    安全获取列表元素，索引越界/非列表时返回默认值
    """
    if not isinstance(lst,list):
        return default
    if 0 <= index < len(lst):
        return default

    def chat_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        stream: bool = True
    ) -> Generator[str, None, None]:
        """
        流式对话接口，用于智能对话模块的打字机效果输出
        :param messages: 对话历史列表，格式为[{"role": "user/assistant/system", "content": "内容"}]
        :param temperature: 模型温度，0-1，越低越稳定，越高越有创造性
        :param stream: 是否开启流式输出，默认开启
        :return: 流式生成的文本片段生成器
        """
        try:
            response = self.client.chat.completions.create(
                model=self.chat_model,
                messages=messages,
                temperature=temperature,
                stream=stream
            )
            # 迭代流式响应，返回每个文本片段
            for chunk in response:
                # ✅ 修改：安全取值，先判断choices是否有元素，避免索引越界
                choice = safe_list_get(chunk.choices, 0)
                if choice and choice.delta and choice.delta.content:
                    yield choice.delta.content
        except Exception as e:
            # ✅ 修改：错误只打日志，绝不返回给用户，避免报错混入回答
            logger.error(f"流式API调用出错: {str(e)}", exc_info=True)
            # 异常时静默结束，用户看不到任何报错
            return

        try:
            response = self.client.chat.completions.create(
                model=self.chat_model,
                messages=messages,
                temperature=temperature,
                stream=False
            )
            # ✅ 修改：安全取值，避免索引越界
            choice = safe_list_get(response.choices, 0)
            if choice and choice.message and choice.message.content:
                return choice.message.content.strip()
            return None
        except Exception as e:
            # ✅ 修改：用日志替代print
            logger.error(f"对话API调用出错: {str(e)}", exc_info=True)
            return None

            response = self.client.chat.completions.create(
                model=self.multimodal_model,
                messages=messages,
                temperature=temperature,
                stream=False
            )
            # ✅ 修改：安全取值，避免索引越界
            choice = safe_list_get(response.choices, 0)
            if choice and choice.message and choice.message.content:
                return choice.message.content.strip()
            return None
        except Exception as e:
            # ✅ 修改：用日志替代print
            logger.error(f"多模态API调用出错: {str(e)}", exc_info=True)
            return None

class LLMClient:
    def __init__(self):
        # 从环境变量读取配置
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.base_url = os.getenv("OPENAI_BASE_URL")
        self.chat_model = os.getenv("CHAT_MODEL", "gpt-3.5-turbo")
        self.multimodal_model = os.getenv("MULTIMODAL_MODEL", "gpt-4o")
        
        # 初始化OpenAI客户端（兼容所有OpenAI格式的大模型接口）
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

    def chat_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        stream: bool = True
    ) -> Generator[str, None, None]:
        """
        流式对话接口，用于智能对话模块的打字机效果输出
        :param messages: 对话历史列表，格式为[{"role": "user/assistant/system", "content": "内容"}]
        :param temperature: 模型温度，0-1，越低越稳定，越高越有创造性
        :param stream: 是否开启流式输出，默认开启
        :return: 流式生成的文本片段生成器
        """
        try:
            response = self.client.chat.completions.create(
                model=self.chat_model,
                messages=messages,
                temperature=temperature,
                stream=stream
            )
            # 迭代流式响应，返回每个文本片段
            for chunk in response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            yield f"API调用出错：{str(e)}"

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7
    ) -> Optional[str]:
        """
        非流式对话接口，用于文档总结、文案生成等需要完整结果的场景
        :param messages: 对话历史列表，格式同上
        :param temperature: 模型温度
        :return: 模型生成的完整文本，出错返回None
        """
        try:
            response = self.client.chat.completions.create(
                model=self.chat_model,
                messages=messages,
                temperature=temperature,
                stream=False
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"API调用出错：{str(e)}")
            return None

    def multimodal_completion(
        self,
        image_base64: str,
        user_query: str,
        system_prompt: str = "你是专业的图片内容分析师，请精准识别图片中的所有信息，包括文字、场景、物体、细节，并准确回答用户的问题。",
        temperature: float = 0.3
    ) -> Optional[str]:
        """
        多模态图片解析接口，用于图片内容识别、OCR、细节问答
        :param image_base64: base64编码的图片数据
        :param user_query: 用户针对图片的提问
        :param system_prompt: 系统提示词，控制模型输出行为
        :param temperature: 模型温度，默认0.3，保证识别精准度
        :return: 模型生成的解析结果，出错返回None
        """
        try:
            messages = [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": user_query
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ]
            response = self.client.chat.completions.create(
                model=self.multimodal_model,
                messages=messages,
                temperature=temperature,
                stream=False
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"多模态API调用出错：{str(e)}")
            return None

# 全局单例，避免重复初始化客户端
llm_client = LLMClient()