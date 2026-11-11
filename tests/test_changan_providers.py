# encoding:utf-8
"""天枢 / 长安火山 / 自定义 catalog providers."""

from common import const
from models.custom_provider import (
    OPENAI_COMPAT_CATALOG_PROVIDERS,
    is_openai_compat_catalog_provider,
    resolve_catalog_compat_credentials,
)
from channel.web.core.providers import PROVIDER_MODELS, TIANSHU_API_BASE, CHANGAN_HUOSHAN_API_BASE


def test_ui_catalog_is_exactly_the_three_internal_providers():
    assert list(PROVIDER_MODELS.keys()) == ["tianshu", "changan_huoshan", "custom"]
    assert PROVIDER_MODELS["tianshu"]["api_base_default"] == TIANSHU_API_BASE
    assert TIANSHU_API_BASE == "https://ai.sda.changan.com.cn/api/v1"
    assert PROVIDER_MODELS["changan_huoshan"]["api_base_default"] == CHANGAN_HUOSHAN_API_BASE
    assert CHANGAN_HUOSHAN_API_BASE == "https://ark.cn-beijing.volces.com/api/v3"
    assert PROVIDER_MODELS["tianshu"]["models"] == []
    assert PROVIDER_MODELS["changan_huoshan"]["models"] == []
    assert PROVIDER_MODELS["custom"]["models"] == []


def test_catalog_compat_credentials_use_config_and_default_base(monkeypatch):
    assert is_openai_compat_catalog_provider(const.TIANSHU)
    assert is_openai_compat_catalog_provider(const.CHANGAN_HUOSHAN)
    assert not is_openai_compat_catalog_provider("custom")
    assert not is_openai_compat_catalog_provider("openai")
    assert set(OPENAI_COMPAT_CATALOG_PROVIDERS) == {"tianshu", "changan_huoshan"}

    monkeypatch.setattr(
        "models.custom_provider.conf",
        lambda: {"tianshu_api_key": "ts-key", "tianshu_api_base": ""},
    )
    key, base, model = resolve_catalog_compat_credentials("tianshu")
    assert key == "ts-key"
    assert base == TIANSHU_API_BASE
    assert model is None

    monkeypatch.setattr(
        "models.custom_provider.conf",
        lambda: {
            "changan_huoshan_api_key": "hs-key",
            "changan_huoshan_api_base": "https://example.local/api/v3",
        },
    )
    key, base, model = resolve_catalog_compat_credentials("changan_huoshan")
    assert key == "hs-key"
    assert base == "https://example.local/api/v3"
    assert model is None


def test_bot_factory_routes_tianshu_and_huoshan_to_chatgpt(monkeypatch):
    created = []

    class Dummy:
        def __init__(self, credential_bot_type=None):
            created.append(credential_bot_type)

    import models.chatgpt.chat_gpt_bot as chat_mod

    monkeypatch.setattr(chat_mod, "ChatGPTBot", Dummy)
    from models.bot_factory import create_bot

    assert isinstance(create_bot(const.TIANSHU), Dummy)
    assert isinstance(create_bot(const.CHANGAN_HUOSHAN, credential_bot_type="changan_huoshan"), Dummy)
    assert created == [None, "changan_huoshan"]
