"""
多功能AI工具平台 - 单元测试
============================

覆盖原则：只测不依赖网络的纯函数与配置解析，避免 CI 因外部 API 波动而失败。
所有涉及 st.session_state 的函数都用假的 streamlit 对象注入，保证可在无
ScriptRunContext 的 pytest 环境里运行。

运行：pytest -q
"""

import base64
import io
import json
from types import SimpleNamespace

import pytest

from modules import chat_module, document_summary, multimodal_parser, llm_client as llm_client_module


# ---------------------------------------------------------------------------
# 测试替身
# ---------------------------------------------------------------------------

class _FakeSt:
    """最小 streamlit 替身：只需 session_state / warning / error"""

    def __init__(self, chat_messages=None):
        self.session_state = SimpleNamespace(chat_messages=chat_messages or [])
        self.loud = []

    def warning(self, msg):
        self.loud.append(("warning", msg))

    def error(self, msg):
        self.loud.append(("error", msg))


@pytest.fixture
def fake_st(monkeypatch):
    fake = _FakeSt([{"role": "user", "content": "你好"}])
    monkeypatch.setattr(chat_module, "st", fake)
    monkeypatch.setattr(document_summary, "st", fake)
    return fake


# ---------------------------------------------------------------------------
# 1. clean_answer_text：报错清洗 + Markdown 修复
# ---------------------------------------------------------------------------

def test_clean_answer_text_removes_api_error_line():
    raw = "这是正常内容\nAPI调用出错：Connection error.\n结尾"
    out = chat_module.clean_answer_text(raw)
    assert "API调用出错" not in out
    assert "正常内容" in out


def test_clean_answer_text_repairs_unclosed_bold():
    out = chat_module.clean_answer_text("**结论：可以用")
    assert out.count("**") % 2 == 0


def test_clean_answer_text_collapses_blank_lines():
    out = chat_module.clean_answer_text("第一段\n\n\n\n第二段")
    assert "\n\n\n" not in out


def test_clean_answer_text_keeps_normal_text_untouched():
    raw = "结论：可以。\n- 要点一\n- 要点二"
    assert chat_module.clean_answer_text(raw) == raw


# ---------------------------------------------------------------------------
# 2. 对话历史持久化（读 / 写 / 默认值）
# ---------------------------------------------------------------------------

def test_load_chat_history_returns_default_when_no_file(tmp_path, fake_st, monkeypatch):
    monkeypatch.setattr(chat_module, "CHAT_HISTORY_FILE", str(tmp_path / "none.json"))
    history = chat_module.load_chat_history()
    assert isinstance(history, list) and history[0]["role"] == "assistant"


def test_save_then_load_roundtrip(tmp_path, fake_st, monkeypatch):
    path = tmp_path / "chat_history.json"
    monkeypatch.setattr(chat_module, "CHAT_HISTORY_FILE", str(path))

    fake_st.session_state.chat_messages = [
        {"role": "user", "content": "问了什么"},
        {"role": "assistant", "content": "答了什么"},
    ]
    chat_module.save_chat_history()

    assert path.exists()
    saved = json.loads(path.read_text(encoding="utf-8"))
    assert saved[0]["content"] == "问了什么"

    fake_st.session_state.chat_messages = []
    loaded = chat_module.load_chat_history()
    assert len(loaded) == 2 and loaded[1]["content"] == "答了什么"


def test_load_chat_history_tolerates_broken_json(tmp_path, fake_st, monkeypatch):
    path = tmp_path / "broken.json"
    path.write_text("{ this is not json", encoding="utf-8")
    monkeypatch.setattr(chat_module, "CHAT_HISTORY_FILE", str(path))
    history = chat_module.load_chat_history()
    assert history[0]["role"] == "assistant"  # 回落默认，不抛异常


# ---------------------------------------------------------------------------
# 3. 对话报告导出
# ---------------------------------------------------------------------------

def test_build_chat_markdown_contains_roles_and_titles(fake_st):
    fake_st.session_state.chat_messages = [
        {"role": "user", "content": "问题一"},
        {"role": "assistant", "content": "回答一"},
    ]
    md = chat_module.build_chat_markdown()
    assert "# 智能对话记录报告" in md
    assert "🧑 用户" in md and "🤖 助手" in md
    assert "问题一" in md and "回答一" in md


# ---------------------------------------------------------------------------
# 4. TXT 读取：UTF-8 与 GBK 都必须正确（回归：字节流只能读一次）
# ---------------------------------------------------------------------------

def test_read_txt_file_utf8():
    content = "中文内容测试\n第二行"
    out = document_summary.read_txt_file(io.BytesIO(content.encode("utf-8")))
    assert out == content


def test_read_txt_file_gbk_regression():
    """回归测试：早期实现在 UTF-8 失败后再次 read() 已耗尽的流，GBK 文本被读成空串"""
    content = "中文内容测试\n第二行"
    out = document_summary.read_txt_file(io.BytesIO(content.encode("gbk")))
    assert out == content


def test_read_txt_file_empty_bytes():
    assert document_summary.read_txt_file(io.BytesIO(b"")) == ""


# ---------------------------------------------------------------------------
# 5. 图片转 base64
# ---------------------------------------------------------------------------

def test_image_to_base64_roundtrip():
    from PIL import Image

    img = Image.new("RGB", (8, 8), (12, 34, 56))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    b64 = multimodal_parser.image_to_base64(buf)
    assert b64
    decoded = base64.b64decode(b64)
    assert len(decoded) > 0
    # 输出统一转 JPEG
    assert decoded[:2] == b"\xff\xd8"


# ---------------------------------------------------------------------------
# 6. 客户端配置解析（不发起网络请求）
# ---------------------------------------------------------------------------

def test_llm_client_reads_env(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://example.invalid/v1")
    monkeypatch.setenv("CHAT_MODEL", "test-chat")
    monkeypatch.setenv("MULTIMODAL_MODEL", "test-vl")

    client = llm_client_module.LLMClient()
    assert client.api_key == "sk-test"
    assert client.base_url == "https://example.invalid/v1"
    assert client.chat_model == "test-chat"
    assert client.multimodal_model == "test-vl"


def test_llm_client_defaults(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.delenv("CHAT_MODEL", raising=False)
    monkeypatch.delenv("MULTIMODAL_MODEL", raising=False)

    client = llm_client_module.LLMClient()
    assert client.chat_model == "gpt-3.5-turbo"
    assert client.multimodal_model == "gpt-4o"
