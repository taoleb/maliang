"""Vendor catalogue for the model and settings views.

Mostly data: the provider ids, their config keys, the base-URL placeholders
shown in the form, and the recommended model list. It sat as a class attribute
on ``ConfigHandler``, but three places read it -- that handler serves it,
``ModelsHandler`` builds its capability cards from it, and ``WebChannel``
resolves provider labels through it -- so two of them had to reach across into
a handler to get at it.

The few functions at the bottom read a provider's configured values. They are
here for the same reason, and because they were the last thing tying the two
handlers to each other.
"""

from collections import OrderedDict


# Prefill these real endpoints so internal users can leave the default as-is.
TIANSHU_API_BASE = "https://ai.sda.changan.com.cn/api/v1"
CHANGAN_HUOSHAN_API_BASE = "https://ark.cn-beijing.volces.com/api/v3"
_PLACEHOLDER_V1 = "https://...../v1"

# User-facing chat model catalog. Only these three options appear in the
# desktop/web provider pickers. Other vendor bot implementations remain
# in the codebase for compatibility, but they are not offered in the UI.
PROVIDER_MODELS = OrderedDict([
    ("tianshu", {
        "label": {"zh": "天枢模型", "en": "Tianshu"},
        "api_key_field": "tianshu_api_key",
        "api_base_key": "tianshu_api_base",
        "api_base_default": TIANSHU_API_BASE,
        "api_base_placeholder": TIANSHU_API_BASE,
        "models": [],
    }),
    ("changan_huoshan", {
        "label": {"zh": "长安火山", "en": "Changan Ark"},
        "api_key_field": "changan_huoshan_api_key",
        "api_base_key": "changan_huoshan_api_base",
        "api_base_default": CHANGAN_HUOSHAN_API_BASE,
        "api_base_placeholder": CHANGAN_HUOSHAN_API_BASE,
        "models": [],
    }),
    ("custom", {
        "label": {"zh": "自定义", "en": "Custom"},
        "api_key_field": "custom_api_key",
        "api_base_key": "custom_api_base",
        "api_base_default": "",
        "api_base_placeholder": _PLACEHOLDER_V1,
        "models": [],
    }),
])


# Three helpers that read a provider's config values. They were static methods
# split across ConfigHandler and ModelsHandler, and each handler needed one
# from the other, which is a cycle the moment the two live in separate
# modules. They are about the catalogue above, so they belong here.

def is_real_key(value: str) -> bool:
    """False for an unset key and for the placeholders the form ships with."""
    return bool(value) and value not in ("", "YOUR API KEY", "YOUR_API_KEY")


def mask_key(value: str) -> str:
    """Mask the middle part of an API key for display."""
    if not value or len(value) <= 8:
        return value
    return value[:4] + "*" * (len(value) - 8) + value[-4:]


def legacy_custom_in_use(local_config: dict) -> bool:
    """True when the flat single-provider custom config is still relevant:
    either it is the active bot_type, or its key/base fields are filled.
    In that case the legacy "custom" card must stay visible even when
    multi ``custom_providers`` entries exist."""
    if (local_config.get("bot_type") or "") == "custom":
        return True
    return (is_real_key(local_config.get("custom_api_key") or "")
            or bool(local_config.get("custom_api_base")))
