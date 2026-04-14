from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any
from urllib import error, request

from .config import REPO_ROOT

DEFAULT_CHAT_ENDPOINT = "https://api.deepseek.com/v1/chat/completions"
DEFAULT_CHAT_MODEL = "deepseek-chat"

LOCAL_ENV_PATHS = (
    REPO_ROOT / ".env.secrets",
    REPO_ROOT / ".env",
    Path(r"D:\悟空行\.env.secrets"),
    Path(r"D:\悟空行\app\.env"),
)

STARTER_QUESTIONS = [
    "工作台里怎么查看历史季度？",
    "怎样发起一次情景推演？",
    "模型结果页主要看什么？",
    "我应该先进入哪一个入口？",
]

ACTION_LIBRARY = {
    "workspace": {
        "label": "进入工作台",
        "route": "/workspace",
        "hint": "查看地图、季度切换、节点详情和热力层。",
    },
    "scenario": {
        "label": "打开情景推演",
        "route": "/workspace",
        "query": {"intent": "scenario"},
        "hint": "进入工作台后直接打开情景推演面板。",
    },
    "evidence": {
        "label": "查看模型结果",
        "route": "/evidence",
        "hint": "查看当前结果表现、稳定性和使用建议。",
    },
    "guide": {
        "label": "查看使用引导",
        "route": "/guide",
        "hint": "先了解平台怎么用，再进入工作台。",
    },
    "home": {
        "label": "回到首页",
        "route": "/",
        "hint": "返回平台首页查看整体介绍与功能入口。",
    },
}


def _read_dotenv(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values

    for raw_line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and value:
            values[key] = value
    return values


def _resolve_llm_settings() -> dict[str, str]:
    values: dict[str, str] = {}
    for path in LOCAL_ENV_PATHS:
        if path.exists():
            values.update(_read_dotenv(path))

    values.update({key: value for key, value in os.environ.items() if value})

    api_key = (
        values.get("LLM_CHAT_API_KEY")
        or values.get("LLM_API_KEY")
        or values.get("DEEPSEEK_API_KEY")
        or ""
    )
    model = values.get("LLM_CHAT_MODEL") or DEFAULT_CHAT_MODEL
    endpoint = values.get("LLM_CHAT_ENDPOINT") or DEFAULT_CHAT_ENDPOINT
    return {"api_key": api_key, "model": model, "endpoint": endpoint}


def _sanitize_history(history: list[dict[str, Any]] | None) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    for entry in (history or [])[-6:]:
        role = str(entry.get("role") or "").strip()
        content = str(entry.get("content") or "").strip()
        if role not in {"user", "assistant"} or not content:
            continue
        items.append({"role": role, "content": content[:800]})
    return items


def _platform_prompt() -> str:
    return (
        "你是“天穹智算”平台首页里的平台问答助手。"
        "你只能回答和本平台功能、页面入口、季度范围、情景推演、模型结果查看方式相关的问题。"
        "回答必须使用简洁、专业、面向普通使用者的中文，不要提后端、接口、仓库、代码、combo、seed、参数扫描、内部实验路径。"
        "如果用户问去哪一个入口、先看什么、怎么开始，就直接告诉他推荐页面和原因，不要反问用户。"
        "优先给出可执行步骤，不要寒暄，不要自我介绍。"
        "平台当前可用页面只有：首页（总览）、工作台（地图、历史季度、预测季度、情景推演）、模型结果（结果表现、稳定性、使用建议）。"
        "平台当前历史季度范围是 2020-Q1 至 2024-Q4，预测季度范围是 2025-Q1 至 2025-Q2。"
        "情景推演的基本路径是：进入工作台，点击顶部“启动情景推演”，框选区域，运行推演，然后查看推演前后对比。"
        "如果问题超出平台使用范围，请礼貌说明你主要负责平台功能解答和入口引导。"
    )


def _call_llm(message: str, history: list[dict[str, str]]) -> str:
    settings = _resolve_llm_settings()
    if not settings["api_key"]:
        raise RuntimeError("missing_llm_key")

    payload = {
        "model": settings["model"],
        "temperature": 0.2,
        "messages": [
            {"role": "system", "content": _platform_prompt()},
            *history,
            {"role": "user", "content": message},
        ],
    }

    req = request.Request(
        settings["endpoint"],
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {settings['api_key']}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with request.urlopen(req, timeout=40) as response:
        data = json.loads(response.read().decode("utf-8"))
    return str(data.get("choices", [{}])[0].get("message", {}).get("content", "")).strip()


def _build_actions(message: str, answer: str) -> list[dict[str, Any]]:
    haystack = f"{message}\n{answer}".lower()
    keys: list[str] = []

    if any(token in haystack for token in ["怎么用", "使用方法", "使用引导", "新手", "教程", "引导"]):
        keys.extend(["guide", "workspace"])
    if any(token in haystack for token in ["去哪", "入口", "怎么开始", "先看", "先进入", "从哪里开始"]):
        keys.extend(["workspace", "evidence"])
    if any(token in haystack for token in ["情景", "推演", "框选", "干预", "对比"]):
        keys.extend(["scenario", "workspace"])
    if any(token in haystack for token in ["模型", "误差", "稳定", "结果", "准确"]):
        keys.append("evidence")
    if any(token in haystack for token in ["季度", "历史", "预测", "地图", "节点", "热力", "工作台"]):
        keys.append("workspace")
    if any(token in haystack for token in ["首页", "总览", "介绍"]):
        keys.append("home")

    if not keys:
        keys = ["workspace", "evidence"]

    deduped: list[str] = []
    for key in keys:
        if key not in deduped:
            deduped.append(key)
    return [ACTION_LIBRARY[key] for key in deduped[:3]]


def _fallback_answer(message: str) -> str:
    text = message.strip()
    if not text:
        return "我可以解答平台功能、入口和基本使用问题，也可以直接带你跳转到工作台、情景推演或模型结果页。"
    if any(token in text for token in ["情景", "推演", "框选", "干预"]):
        return "如果你想做区域干预对比，建议先进入工作台，再点击顶部的“启动情景推演”，在地图上拖拽框选区域并运行推演。完成后可以查看推演前后地图差异和受影响节点。"
    if any(token in text for token in ["模型", "误差", "稳定", "结果"]):
        return "如果你想了解当前结果表现，建议查看“模型结果”页。那里会用更直观的方式展示当前模型的整体误差、稳定性和适用场景。"
    if any(token in text for token in ["历史", "季度", "预测", "地图", "节点", "热力"]):
        return "如果你想查看历史季度、预测季度或节点详情，建议进入工作台。工作台可以统一切换 2020-Q1 至 2025-Q2 的季度结果，并在地图上查看区域分布与节点信息。"
    if any(token in text for token in ["去哪", "入口", "怎么开始", "先看什么"]):
        return "如果你是第一次使用，建议先进入工作台看地图和季度变化；如果你更关注结果表现，可以直接查看模型结果页。"
    return "我主要负责平台功能解答和入口引导。你可以直接问我如何查看历史季度、如何发起情景推演，或该进入哪一个页面。"


def answer_faq(payload: dict[str, Any]) -> dict[str, Any]:
    message = str(payload.get("message") or "").strip()
    history = _sanitize_history(payload.get("history"))

    if not message:
        welcome = _fallback_answer("")
        return {
            "message": welcome,
            "suggested_actions": [ACTION_LIBRARY["workspace"], ACTION_LIBRARY["scenario"], ACTION_LIBRARY["evidence"]],
            "starter_questions": STARTER_QUESTIONS,
            "mode": "fallback",
        }

    reply = ""
    mode = "fallback"
    try:
        reply = _call_llm(message, history)
        if reply:
            mode = "llm"
    except (RuntimeError, error.URLError, TimeoutError, ValueError):
        reply = ""

    if not reply:
        reply = _fallback_answer(message)

    return {
        "message": reply,
        "suggested_actions": _build_actions(message, reply),
        "starter_questions": STARTER_QUESTIONS,
        "mode": mode,
    }
