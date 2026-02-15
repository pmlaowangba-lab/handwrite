from __future__ import annotations

import math
import re
from dataclasses import dataclass

import httpx

from app.core.config import get_settings
from app.schemas.ai import ContentTemplate, NotePolishRequest
from app.services.render_service import PAPER_SIZES

settings = get_settings()
MODEL_ALIASES = {
    "codex-5.3": "gpt-5.3-codex",
    "codex-5.2": "gpt-5.2-codex",
    "codex-5.1": "gpt-5.1-codex",
}

SYSTEM_PROMPT = """你是"中文手写笔记润色助手"。
你的输出会被渲染到 A4 纸张上，必须满足：
1) 全中文，专业、简洁、高密度，避免口语化。
2) 严禁输出任何 Emoji。
3) 使用 Markdown 层级结构：
   - # 主标题（H0）
   - ## 一级章节（H1）
   - ### 二级小节（H2）
4) 每个 H1 至少包含 2-3 个 H2，每个 H2 下至少包含 2-3 条正文要点。
5) 对关键术语补充：定义、适用场景、常见误区或计算思路。
6) 输出直接可用，不要解释你如何完成任务。
"""

# 4套文案结构模板的 System Prompt
TEMPLATE_SYSTEM_PROMPTS = {
    ContentTemplate.CONCEPT: """你是专业的概念讲解笔记助手。
输出必须用于"单页手写稿排版"，目标是在 A4 竖版一页内尽量写满（填充率≥90%，但不能溢出到下一页）。

硬规则：
1) 严禁使用任何 Emoji。
2) 禁止输出任何思考过程/解释/自述（禁止出现：<think>、让我、我将、我需要、下面、开始构建、分析任务等）。
3) 只输出最终内容本体，不要 Markdown 代码块。
4) 结构必须严格按以下 6 个区块依次输出，每个区块之间空一行：
【顶部】
【左侧纵向流程链】
【上半三列框架】
【中部方法清单】
【右侧对照项】
【底部总结盒】
5) 符号：允许使用全角符号、编号①②③④、箭头→、顿号、括号；不要项目符号"-"。
6) 长度：控制在 900~1200 个中文字符。

区块细则：
- 顶部：主标题+副标题（同一行，用"｜"分隔）
- 左侧纵向流程链：5个方框节点，写成"[A]→[B]→[C]→[D]→[E]"
- 上半三列框架：分成"列1/列2/列3"，每列=问题(<=10字)；关键词4个（用顿号）；收敛句以"因此："开头
- 中部方法清单：①②③④，每条20~35字，问句优先
- 右侧对照项：至少6条"X→Y"，每条<=16字
- 底部总结盒：4条短句（每条<=18字）

输出要求：
- 使用简洁、高密度的专业语言，避免口语化
- 每个概念至少扩展 2-3 个支撑点，关键名词必须补充定义
- 保持严肃、专业的学术风格""",

    ContentTemplate.PRACTICAL: """你是专业的干货流程撰写助手。
输出必须用于"单页手写稿排版"，目标是在 A4 竖版一页内尽量写满（填充率≥90%，但不能溢出到下一页）。

硬规则：
1) 严禁使用任何 Emoji。
2) 禁止输出任何思考过程/解释/自述（禁止出现：<think>、让我、我将、我需要、下面、开始构建、分析任务等）。
3) 只输出最终内容本体，不要 Markdown 代码块。
4) 结构必须严格按以下 5 个区块依次输出，每个区块之间空一行：
【顶部】
【左侧问题区】
【右上流程链】
【中间框架图】
【底部要点区】
5) 符号：允许使用全角符号、编号①②③④、箭头→、方框□、顿号、括号；不要项目符号"-"。
6) 长度：控制在 900~1200 个中文字符。

区块细则：
- 顶部：主标题+副标题（同一行，用"｜"分隔）
- 左侧问题区：3-5 个核心问题，每个问题 ≤12 字，问句形式
- 右上流程链：①②③④⑤ 关键步骤，每步 ≤15 字，动词开头
- 中间框架图：方法框架，可包含表格、流程图、分支结构，展示具体操作方法
- 底部要点区：3-5 条总结要点，每条 ≤20 字

输出要求：
- 强调"怎么做"，而非"是什么"
- 步骤清晰，可直接执行
- 方法具体，避免空泛概念
- 使用简洁、高密度的专业语言""",

    ContentTemplate.FULL_PROCESS: """你是专业的完整流程设计助手。
输出必须用于"单页手写稿排版"，目标是在 A4 竖版一页内尽量写满（填充率≥90%，但不能溢出到下一页）。

硬规则：
1) 严禁使用任何 Emoji。
2) 禁止输出任何思考过程/解释/自述（禁止出现：<think>、让我、我将、我需要、下面、开始构建、分析任务等）。
3) 只输出最终内容本体，不要 Markdown 代码块。
4) 结构必须严格按以下 5 个区块依次输出，每个区块之间空一行：
【顶部】
【左侧流程链】
【中间主体区】
【右侧补充区】
【底部总结区】
5) 符号：允许使用全角符号、编号①②③④、箭头→、方框□、顿号、括号；不要项目符号"-"。
6) 长度：控制在 900~1200 个中文字符。

区块细则：
- 顶部：主标题+副标题（同一行，用"｜"分隔）
- 左侧流程链：3-5个业务阶段，纵向排列，用方框和箭头连接（如：[阶段A]→[阶段B]→[阶段C]）
- 中间主体区：
  - 角色定义（2-3个关键角色，每个角色的目标）
  - 每个阶段的详细内容（目标、方法、注意事项）
  - 可包含表格、流程图、分支结构
- 右侧补充区：关键要点、注意事项、补充说明（3-5条，每条 ≤18 字）
- 底部总结区：3-5条核心要点，每条 ≤20 字

输出要求：
- 强调完整的业务流程（前中后）
- 多角色视角，展示不同角色的目标和行为
- 每个阶段都有具体的操作方法
- 内容系统化，可直接用于业务设计
- 使用简洁、高密度的专业语言""",

    ContentTemplate.DECISION: """你是专业的决策分析笔记助手。
输出必须用于"单页手写稿排版"，目标是在 A4 竖版一页内尽量写满（填充率≥90%，但不能溢出到下一页）。

硬规则：
1) 严禁使用任何 Emoji。
2) 禁止输出任何思考过程/解释/自述（禁止出现：<think>、让我、我将、我需要、下面、开始构建、分析任务等）。
3) 只输出最终内容本体，不要 Markdown 代码块。
4) 结构必须严格按以下 5 个区块依次输出，每个区块之间空一行：
【顶部】
【核心矛盾区】
【多维对比区】
【决策路径区】
【底部结论区】
5) 符号：允许使用全角符号、编号①②③④、箭头→、方框□、顿号、括号；不要项目符号"-"。
6) 长度：控制在 900~1200 个中文字符。

区块细则：
- 顶部：主标题+副标题（同一行，用"｜"分隔）
- 核心矛盾区：明确决策的核心冲突点，2-3 个关键矛盾，每个矛盾用"A vs B"格式
- 多维对比区：至少 4 个维度的对比分析，每个维度包含：维度名称、选项A评估、选项B评估、权重建议
- 决策路径区：3-4 条决策路径，每条包含：适用条件（<=15字）、推荐选择、核心理由（<=25字）
- 底部结论区：3-4 条决策原则，每条 ≤20 字

输出要求：
- 强调"如何选"，而非"是什么"
- 提供可量化的判断标准
- 避免模棱两可，给出明确倾向
- 使用简洁、高密度的专业语言""",
}


EMOJI_PATTERN = re.compile(
    "["
    "\U0001F300-\U0001F6FF"
    "\U0001F700-\U0001F77F"
    "\U0001F780-\U0001F7FF"
    "\U0001F800-\U0001F8FF"
    "\U0001F900-\U0001F9FF"
    "\U0001FA00-\U0001FAFF"
    "\U00002700-\U000027BF"
    "\U0001F1E6-\U0001F1FF"
    "]+",
    flags=re.UNICODE,
)


class AiServiceError(RuntimeError):
    pass


class AiConfigurationError(AiServiceError):
    pass


@dataclass
class PolishResult:
    polished_text: str
    model: str
    estimated_fill_ratio: float
    target_fill_min: float
    target_fill_max: float
    expanded_rounds: int
    character_count: int
    layout_mode: str = "a4_note"


def _normalized_model_name() -> str:
    model = settings.ai_model.strip()
    return MODEL_ALIASES.get(model, model)


def _candidate_api_roots() -> list[str]:
    base_url = settings.ai_base_url.rstrip("/")
    if not base_url:
        return ["https://api.openai.com"]

    roots = [base_url]
    if base_url.endswith("/api"):
        roots.append(base_url[: -len("/api")])

    unique_roots: list[str] = []
    for item in roots:
        if item and item not in unique_roots:
            unique_roots.append(item)
    return unique_roots


def _extract_error_message(response: httpx.Response) -> str:
    content_type = response.headers.get("content-type", "")
    try:
        payload = response.json()
    except ValueError:
        text = response.text.strip()
        if "text/html" in content_type and text:
            title_match = re.search(r"<title>(.*?)</title>", text, flags=re.IGNORECASE | re.DOTALL)
            if title_match:
                title = re.sub(r"\s+", " ", title_match.group(1)).strip()
                if title:
                    return title
            if "bad gateway" in text.lower():
                return "Bad gateway"
        return (text[:220] + "...") if len(text) > 220 else (text or response.reason_phrase)
    if isinstance(payload, dict):
        error = payload.get("error")
        if isinstance(error, dict):
            message = error.get("message")
            if message:
                return str(message)
        message = payload.get("message")
        if message:
            return str(message)
    return response.text.strip() or response.reason_phrase


def _normalize_text(text: str) -> str:
    normalized = text.strip()
    if normalized.startswith("```"):
        normalized = re.sub(r"^```[\w-]*\n?", "", normalized, count=1)
        normalized = re.sub(r"\n?```$", "", normalized, count=1)
    normalized = EMOJI_PATTERN.sub("", normalized)
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)
    return normalized.strip()


def _request_openai_chat(url: str, messages: list[dict[str, str]]) -> httpx.Response:
    headers = {
        "Authorization": f"Bearer {settings.ai_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": _normalized_model_name(),
        "messages": messages,
        "temperature": 0.65,
        "max_tokens": settings.ai_max_tokens,
    }
    return httpx.post(url, headers=headers, json=payload, timeout=settings.ai_timeout_seconds)


def _request_messages_api(url: str, messages: list[dict[str, str]]) -> httpx.Response:
    headers = {
        "Authorization": f"Bearer {settings.ai_api_key}",
        "Content-Type": "application/json",
        "anthropic-version": "2023-06-01",
    }
    system_sections = [item["content"] for item in messages if item.get("role") == "system" and item.get("content")]
    non_system_sections = [item for item in messages if item.get("role") != "system" and item.get("content")]

    if non_system_sections:
        user_content = "\n\n".join(f"{item['role']}:\n{item['content']}" for item in non_system_sections)
    else:
        user_content = "请生成中文专业手写笔记内容。"

    payload: dict[str, object] = {
        "model": _normalized_model_name(),
        "max_tokens": min(4096, settings.ai_max_tokens),
        "messages": [{"role": "user", "content": user_content}],
    }
    if system_sections:
        payload["system"] = "\n\n".join(system_sections)

    return httpx.post(url, headers=headers, json=payload, timeout=settings.ai_timeout_seconds)


def _parse_openai_response(response: httpx.Response) -> str:
    try:
        data = response.json()
    except ValueError as exc:
        raise AiServiceError("AI 服务返回了无法解析的 JSON") from exc

    if not isinstance(data, dict):
        raise AiServiceError("AI 服务返回格式异常")

    choices = data.get("choices")
    if not isinstance(choices, list) or not choices:
        raise AiServiceError("AI 服务未返回可用内容")

    message = choices[0].get("message", {})
    content = message.get("content")
    if isinstance(content, list):
        content = "".join(item.get("text", "") if isinstance(item, dict) else str(item) for item in content)
    if not isinstance(content, str) or not content.strip():
        raise AiServiceError("AI 服务返回文本为空")

    return _normalize_text(content)


def _parse_messages_response(response: httpx.Response) -> str:
    try:
        data = response.json()
    except ValueError as exc:
        raise AiServiceError("AI 服务返回了无法解析的 JSON") from exc

    if not isinstance(data, dict):
        raise AiServiceError("AI 服务返回格式异常")

    content = data.get("content")
    if isinstance(content, list):
        text_parts = [item.get("text", "") for item in content if isinstance(item, dict)]
        text = "\n".join(part for part in text_parts if part)
    elif isinstance(content, str):
        text = content
    else:
        text = ""

    if not text.strip():
        raise AiServiceError("AI 服务返回文本为空")

    return _normalize_text(text)


def _request_chat_completion(messages: list[dict[str, str]]) -> str:
    if not settings.ai_api_key:
        raise AiConfigurationError("未配置 AI API Key，请先设置 HW_BACKEND_AI_API_KEY")

    request_chain: list[tuple[str, str]] = []
    for root in _candidate_api_roots():
        request_chain.append(("openai", f"{root}/v1/chat/completions"))
        request_chain.append(("messages", f"{root}/v1/messages"))

    last_error = ""
    attempted_urls: list[str] = []
    for request_type, url in request_chain:
        attempted_urls.append(url)
        try:
            response = (
                _request_openai_chat(url, messages)
                if request_type == "openai"
                else _request_messages_api(url, messages)
            )
        except httpx.HTTPError as exc:  # noqa: BLE001
            last_error = f"连接 AI 服务失败：{exc}"
            continue

        if response.status_code in {401, 403}:
            detail = _extract_error_message(response)
            raise AiConfigurationError(f"AI 鉴权失败（{response.status_code}）：{detail}")

        if response.status_code == 404:
            last_error = f"端点不存在：{url}"
            continue

        if response.status_code >= 400:
            detail = _extract_error_message(response)
            last_error = f"AI 服务返回异常（{response.status_code}）：{detail}"
            continue

        if request_type == "openai":
            return _parse_openai_response(response)
        return _parse_messages_response(response)

    if last_error:
        raise AiServiceError(f"{last_error}（已尝试：{' | '.join(attempted_urls)}）")
    raise AiServiceError("未能连接到可用的 AI 端点")


def _weighted_char_count(text: str) -> float:
    score = 0.0
    for char in text:
        if char.isspace():
            score += 0.35
        elif ord(char) < 128:
            score += 0.55
        else:
            score += 1.0
    return score


def estimate_fill_ratio(
    text: str,
    paper_type: str,
    font_size: int,
    line_height: float,
    render_scale: float,
) -> float:
    paper_width, paper_height = PAPER_SIZES.get(paper_type, PAPER_SIZES["a4-portrait"])
    canvas_width = max(720, int(paper_width * render_scale))
    canvas_height = max(1024, int(paper_height * render_scale))

    margin_x = int(canvas_width * 0.09)
    margin_top = int(canvas_height * 0.09)
    margin_bottom = int(canvas_height * 0.09)
    usable_width = max(120, canvas_width - margin_x * 2)
    usable_height = max(240, canvas_height - margin_top - margin_bottom)

    char_width = max(7.5, font_size * 0.62)
    chars_per_line = max(12.0, usable_width / char_width)
    line_step = max(12.0, font_size * line_height)

    lines = text.splitlines() or [text]
    logical_lines = 0.0
    for line in lines:
        stripped = line.strip()
        if not stripped:
            logical_lines += 0.7
            continue

        weighted_chars = _weighted_char_count(stripped)
        wraps = max(1.0, math.ceil(weighted_chars / chars_per_line))
        logical_lines += wraps

        if stripped.startswith("# "):
            logical_lines += 0.9
        elif stripped.startswith("## "):
            logical_lines += 0.6
        elif stripped.startswith("### "):
            logical_lines += 0.4

    occupied_height = logical_lines * line_step
    return max(0.0, min(1.5, occupied_height / usable_height))


def _estimate_target_chars(payload: NotePolishRequest) -> int:
    paper_width, paper_height = PAPER_SIZES.get(payload.paper_type.value, PAPER_SIZES["a4-portrait"])
    canvas_width = max(720, int(paper_width * payload.render_scale))
    canvas_height = max(1024, int(paper_height * payload.render_scale))

    margin_x = int(canvas_width * 0.09)
    margin_top = int(canvas_height * 0.09)
    margin_bottom = int(canvas_height * 0.09)
    usable_width = max(120, canvas_width - margin_x * 2)
    usable_height = max(240, canvas_height - margin_top - margin_bottom)

    char_width = max(7.5, payload.font_size * 0.62)
    chars_per_line = max(12.0, usable_width / char_width)
    line_step = max(12.0, payload.font_size * payload.line_height)

    target_ratio = (payload.target_fill_min + payload.target_fill_max) / 2
    target_lines = max(30.0, (usable_height * target_ratio) / line_step)
    return int(target_lines * chars_per_line * 0.78)


def _build_initial_prompt(source_text: str, target_chars: int) -> str:
    return (
        "请把下面原文润色成“可直接手写排版”的学习笔记。\n"
        "必须满足：\n"
        "- 采用 H0/H1/H2 分层结构；\n"
        "- 每个 H1 至少 2-3 个 H2；\n"
        "- 每个 H2 补充定义、方法、示例或注意事项；\n"
        "- 文字密度高，避免空泛描述；\n"
        f"- 总字数目标约 {target_chars} 字（允许 ±20%）。\n\n"
        "原文如下：\n"
        f"{source_text.strip()}"
    )


def _build_expand_prompt(current_text: str, current_ratio: float, payload: NotePolishRequest, target_chars: int) -> str:
    return (
        "请在当前稿件基础上继续扩展内容密度。\n"
        f"当前估算铺满度为 {current_ratio:.0%}，目标至少 {payload.target_fill_min:.0%}。\n"
        f"请把内容扩展到约 {target_chars} 字，补充更多二级小节、案例、反例与执行步骤。\n"
        "保留 Markdown 层级结构，不要输出 Emoji。\n\n"
        "当前稿件：\n"
        f"{current_text}"
    )


def polish_note_text(payload: NotePolishRequest) -> PolishResult:
    """根据用户输入和模板类型润色笔记文本"""

    # 根据模板选择对应的 system prompt
    system_prompt = TEMPLATE_SYSTEM_PROMPTS.get(
        payload.content_template,
        TEMPLATE_SYSTEM_PROMPTS[ContentTemplate.CONCEPT]  # 默认回退
    )

    target_chars = _estimate_target_chars(payload)
    first_pass = _request_chat_completion(
        [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": _build_initial_prompt(payload.text, target_chars)},
        ]
    )

    polished_text = _normalize_text(first_pass)
    fill_ratio = estimate_fill_ratio(
        polished_text,
        payload.paper_type.value,
        payload.font_size,
        payload.line_height,
        payload.render_scale,
    )

    expanded_rounds = 0
    while fill_ratio < payload.target_fill_min and expanded_rounds < payload.max_expand_rounds:
        expanded_rounds += 1
        target_chars = int(target_chars * 1.20)
        expanded_text = _request_chat_completion(
            [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": _build_expand_prompt(polished_text, fill_ratio, payload, target_chars),
                },
            ]
        )
        polished_text = _normalize_text(expanded_text)
        fill_ratio = estimate_fill_ratio(
            polished_text,
            payload.paper_type.value,
            payload.font_size,
            payload.line_height,
            payload.render_scale,
        )

    return PolishResult(
        polished_text=polished_text,
        model=settings.ai_model,
        estimated_fill_ratio=round(fill_ratio, 4),
        target_fill_min=payload.target_fill_min,
        target_fill_max=payload.target_fill_max,
        expanded_rounds=expanded_rounds,
        character_count=len(polished_text),
    )
