from typing import Any, Dict, List

from .ai_gateway import ai_gateway
from .prompts import CORE_RULES


AI_NOTICE = "AI 初稿，需由專利工程師確認。"


def _clip(text: str, limit: int = 24000) -> str:
    return (text or "")[:limit]


def _summary_seed(text: str, limit: int = 700) -> str:
    compact = " ".join((text or "").split())
    return compact[:limit] if compact else "原始揭露內容尚未提供。"


def _case_context(case: Any) -> Dict[str, Any]:
    return {
        "case_title": getattr(case, "case_title", ""),
        "client_name": getattr(case, "client_name", ""),
        "inventors": getattr(case, "inventors", []),
        "technical_field": getattr(case, "technical_field", ""),
        "source_text": _clip(getattr(case, "transcript_or_disclosure_text", "")),
        "engineering_definition": getattr(case, "engineering_definition", {}),
        "disclosure_completion": getattr(case, "disclosure_completion", {}),
        "progressive_elaboration_disclosure": getattr(case, "progressive_elaboration_disclosure", {}),
        "embodiment_expansion": getattr(case, "embodiment_expansion", {}),
    }


def generate_engineering_definition(input_text: str) -> Dict[str, Any]:
    seed = _summary_seed(input_text)
    fallback = {
        "notice": AI_NOTICE,
        "original_invention_intent": f"依原始揭露內容整理：{seed}",
        "technical_problem": "需由 AI 或專利工程師進一步收斂：原揭露中涉及的輸入資料、處理流程、輸出結果與技術效果之間的工程問題。",
        "original_solution": f"依原始揭露可見的解決手段包含：{seed}",
        "engineering_boundary": "僅在原始揭露所描述的問題、資料來源、流程、模組、用途與限制內進行補足；不新增全新發明。",
        "project_scope": "產出可供專利工程師撰寫專利說明書的完整揭露書初稿；不生成 Claim，不生成完整專利說明書。",
        "unclear_points": [
            "請確認核心技術問題是否已收斂為具體工程問題。",
            "請確認哪些元件屬必要技術元素，哪些只是產品附加功能。",
            "請確認技術效果是否可由原揭露內容或合理推論支持。",
        ],
    }
    prompt = f"""
請執行 generateEngineeringDefinition(input_text)。

{CORE_RULES}

請以精簡、明確、工程化方式重述原始揭露，並只輸出 JSON：
{{
  "original_invention_intent": "",
  "technical_problem": "",
  "original_solution": "",
  "engineering_boundary": "",
  "project_scope": "",
  "unclear_points": []
}}

原始揭露內容：
{_clip(input_text)}
"""
    return ai_gateway.json_task(prompt, fallback)


def generate_disclosure_completion(input_text: str, engineering_definition: Dict[str, Any]) -> Dict[str, Any]:
    seed = _summary_seed(input_text)
    fallback = {
        "notice": AI_NOTICE,
        "invention_title_options": [
            "依原揭露內容命名之技術方案及方法",
            "資料處理與技術流程補全系統",
        ],
        "technical_field": engineering_definition.get("project_scope") or "依原始揭露所屬技術領域，由專利工程師確認。",
        "background_problem": f"依原揭露內容，現有問題可初步整理為：{seed}",
        "technical_problem": engineering_definition.get("technical_problem", ""),
        "invention_objective": "在原始發明意圖範圍內，補足可支撐專利工程的技術目的與技術改善方向。",
        "core_solution": engineering_definition.get("original_solution") or seed,
        "necessary_technical_elements": [
            "輸入資料或輸入訊號來源",
            "資料處理、分析、比對、判斷或生成流程",
            "輸出結果及其可追溯依據",
            "執行上述流程的模組、裝置或服務架構",
        ],
        "system_architecture": f"AI合理補足：可依原揭露內容「{seed}」整理為輸入層、處理層、輸出層與人工確認層。",
        "method_flow": [
            "接收原始揭露所描述的輸入資料。",
            "依原解決手段進行資料整理、關聯、判斷或推論。",
            "產生可供使用者或後續系統利用的輸出結果。",
            "由專利工程師或發明人確認不明確的技術條件。",
        ],
        "data_flow": [
            "輸入資料進入資料接收或匯入模組。",
            "中間資料依規則、模型、模組或流程轉換。",
            "輸出結果回到使用者介面、資料庫或後續處理模組。",
        ],
        "technical_effects": [
            "AI合理補足：提升資料整理完整性。",
            "AI合理補足：提高判斷依據的一致性與可追溯性。",
            "AI合理補足：降低人工彙整或人工比對負擔。",
        ],
        "alternative_embodiments": [
            "AI合理補足：可替換等效資料來源、模組配置、部署位置或處理條件，但不得改變核心解決手段。",
        ],
        "application_scenarios": [
            "AI合理補足：適用於與原揭露相同技術問題及資料處理邊界下的應用場景。",
        ],
        "implementation_details": [
            "待確認：具體資料欄位、演算法、模型、規則、閾值、模組介面或部署條件。",
        ],
        "ai_reasonably_inferred_content": [
            "AI合理補足：系統架構、流程、資料流與技術效果係依原揭露內容整理而成，需由專利工程師確認。",
        ],
        "items_to_confirm": engineering_definition.get("unclear_points", []),
    }
    prompt = f"""
請執行 generateDisclosureCompletion(input_text, engineering_definition)。

{CORE_RULES}

目的：將原始揭露內容補足為「可撰寫揭露書」，供專利工程師直接進入下一階段撰寫專利說明書。
不得生成 Claim，不得生成完整專利說明書。
合理補足內容必須明確標示「AI合理補足」。
無法合理推論者列入 items_to_confirm。

請只輸出 JSON：
{{
  "invention_title_options": [],
  "technical_field": "",
  "background_problem": "",
  "technical_problem": "",
  "invention_objective": "",
  "core_solution": "",
  "necessary_technical_elements": [],
  "system_architecture": "",
  "method_flow": [],
  "data_flow": [],
  "technical_effects": [],
  "alternative_embodiments": [],
  "application_scenarios": [],
  "implementation_details": [],
  "ai_reasonably_inferred_content": [],
  "items_to_confirm": []
}}

Engineering Definition:
{engineering_definition}

原始揭露內容：
{_clip(input_text)}
"""
    return ai_gateway.json_task(prompt, fallback)


def generate_progressive_elaboration_for_disclosure(inputs: Dict[str, Any]) -> Dict[str, Any]:
    fallback = {
        "notice": AI_NOTICE,
        "known_solution_limitations": [
            "既有方法可能存在資料分散、流程不一致、人工判斷依據不足或結果不可追溯等限制。",
        ],
        "why_existing_methods_are_insufficient": [
            "AI合理補足：若既有方法無法同時滿足原揭露的輸入條件、處理條件與輸出要求，需補足其不足原因。",
        ],
        "technical_improvement_logic": "AI合理補足：說明核心解決手段如何對應待解決技術問題，並形成可驗證的技術改善。",
        "necessary_combination_reasoning": "待確認：各必要技術元素之間是否存在不可任意拆分的配合關係。",
        "technical_effect_chain": [
            "技術手段 -> 中間處理結果 -> 可觀察技術效果。",
        ],
        "inventive_step_support_points": [
            "補足既有方法限制、技術手段差異與技術效果之間的因果關係。",
        ],
    }
    prompt = f"""
請執行 generateProgressiveElaborationForDisclosure(input)。

{CORE_RULES}

目的：針對揭露書完整性進行進步性鋪陳，不是撰寫 Claim，也不是撰寫完整專利說明書。
請只輸出 JSON：
{{
  "known_solution_limitations": [],
  "why_existing_methods_are_insufficient": [],
  "technical_improvement_logic": "",
  "necessary_combination_reasoning": "",
  "technical_effect_chain": [],
  "inventive_step_support_points": []
}}

Input:
{inputs}
"""
    return ai_gateway.json_task(prompt, fallback)


def generate_embodiment_expansion(inputs: Dict[str, Any]) -> Dict[str, Any]:
    fallback = {
        "notice": AI_NOTICE,
        "main_embodiment": "AI合理補足：依原始揭露中的核心解決手段，整理一個主要實施例，需由專利工程師確認技術細節。",
        "alternative_embodiments": [
            "AI合理補足：在不改變核心解決手段下，替換等效模組、資料來源、部署位置或處理條件。",
        ],
        "parameter_variations": [
            "待確認：是否存在閾值、權重、頻率、時間窗、相似度或資料量等參數變化。",
        ],
        "module_variations": [
            "AI合理補足：模組可整合於單一伺服器、終端裝置或雲端服務，但不得超出原揭露邊界。",
        ],
        "process_variations": [
            "AI合理補足：流程順序可依資料取得、處理或輸出條件調整，但核心邏輯不得改變。",
        ],
        "application_variations": [
            "AI合理補足：可延伸至相同技術問題下的等效應用情境。",
        ],
    }
    prompt = f"""
請執行 generateEmbodimentExpansion(input)。

{CORE_RULES}

目的：補足可支撐後續專利說明書的實施例內容，但不得生成完整專利說明書。
請只輸出 JSON：
{{
  "main_embodiment": "",
  "alternative_embodiments": [],
  "parameter_variations": [],
  "module_variations": [],
  "process_variations": [],
  "application_variations": []
}}

Input:
{inputs}
"""
    return ai_gateway.json_task(prompt, fallback)


def generate_completed_disclosure_draft(case: Any) -> str:
    context = _case_context(case)
    fallback = _build_local_completed_draft(case)
    source_text = context.get("source_text") or ""
    prompt = f"""
請根據下列資料，直接產出一份「可撰寫揭露書初稿」Markdown。

{CORE_RULES}

要求：
- 必須根據原始揭露內容進行具體整理，不可只輸出提示語。
- 內容要足以讓專利工程師進入下一階段撰寫專利說明書。
- 不生成 Claim。
- 不生成完整專利說明書。
- 若為合理推論，標示「AI合理補足」。
- 若無法合理推論，列入「待確認事項」。
- 請只輸出 Markdown，不要 JSON。

固定章節：
# 可撰寫揭露書初稿
一、發明名稱
二、技術領域
三、先前技術與現有問題
四、待解決技術問題
五、發明目的
六、核心解決手段
七、必要技術元素組成
八、系統架構
九、方法流程
十、資料流程
十一、主要實施例
十二、替代實施例
十三、應用情境
十四、技術效果
十五、進步性鋪陳重點
十六、AI合理補足內容
十七、待確認事項

案件基本資料：
- 案件名稱：{context.get("case_title", "")}
- 客戶名稱：{context.get("client_name", "")}
- 發明人：{context.get("inventors", [])}
- 技術領域：{context.get("technical_field", "")}

原始揭露內容（最重要，必須優先依據此內容，不可視為空白）：
{source_text}

Engineering Definition：
{context.get("engineering_definition", {})}

Disclosure Completion：
{context.get("disclosure_completion", {})}

Progressive Elaboration：
{context.get("progressive_elaboration_disclosure", {})}

Embodiment Expansion：
{context.get("embodiment_expansion", {})}
"""
    return ai_gateway.text_task(prompt, fallback)


def _build_local_completed_draft(case: Any) -> str:
    context = _case_context(case)
    source = _summary_seed(context["source_text"], 1200)
    definition = context["engineering_definition"]
    completion = context["disclosure_completion"]
    elaboration = context["progressive_elaboration_disclosure"]
    embodiment = context["embodiment_expansion"]
    warnings = _collect_warnings(definition, completion, elaboration, embodiment)
    questions = _dedupe(
        _as_list(definition.get("unclear_points"))
        + _as_list(completion.get("items_to_confirm"))
        + _as_list(completion.get("implementation_details"))
    )

    warning_block = ""
    if warnings:
        warning_block = "\n\n## AI Gateway Warning\n\n" + "\n".join(f"- {item}" for item in warnings)

    return f"""# 可撰寫揭露書初稿

> {AI_NOTICE}
> 本文件不是 Claim，也不是完整專利說明書。其目的在於將原始揭露內容補足為可供專利工程師撰寫專利說明書使用的完整揭露書。
{warning_block}

一、發明名稱

{_markdown_list(completion.get("invention_title_options"))}

二、技術領域

{completion.get("technical_field") or getattr(case, "technical_field", "")}

三、先前技術與現有問題

{completion.get("background_problem") or f"依原始揭露內容整理，現有問題涉及：{source}"}

四、待解決技術問題

{completion.get("technical_problem") or definition.get("technical_problem", "")}

五、發明目的

{completion.get("invention_objective", "")}

六、核心解決手段

{completion.get("core_solution") or definition.get("original_solution") or source}

七、必要技術元素組成

{_markdown_list(completion.get("necessary_technical_elements"))}

八、系統架構

{completion.get("system_architecture", "")}

九、方法流程

{_markdown_list(completion.get("method_flow"))}

十、資料流程

{_markdown_list(completion.get("data_flow"))}

十一、主要實施例

{embodiment.get("main_embodiment", "")}

十二、替代實施例

{_markdown_list(completion.get("alternative_embodiments"))}
{_markdown_list(embodiment.get("alternative_embodiments"))}

十三、應用情境

{_markdown_list(completion.get("application_scenarios"))}
{_markdown_list(embodiment.get("application_variations"))}

十四、技術效果

{_markdown_list(completion.get("technical_effects"))}

十五、進步性鋪陳重點

- 既有方案限制：
{_markdown_list(elaboration.get("known_solution_limitations"))}
- 既有方法不足原因：
{_markdown_list(elaboration.get("why_existing_methods_are_insufficient"))}
- 技術改善邏輯：{elaboration.get("technical_improvement_logic", "")}
- 必要組合理由：{elaboration.get("necessary_combination_reasoning", "")}
- 技術效果鏈：
{_markdown_list(elaboration.get("technical_effect_chain"))}
- 進步性支撐點：
{_markdown_list(elaboration.get("inventive_step_support_points"))}

十六、AI合理補足內容

{_markdown_list(completion.get("ai_reasonably_inferred_content"))}

十七、待確認事項

{_markdown_list(questions)}

十八、原始揭露摘要

{source}
"""


def _collect_warnings(*sections: Dict[str, Any]) -> List[str]:
    warnings = []
    for section in sections:
        warning = section.get("ai_gateway_warning") if isinstance(section, dict) else None
        if warning:
            warnings.append(str(warning))
    return _dedupe(warnings)


def _markdown_list(value: Any) -> str:
    values = _as_list(value)
    if not values:
        return "- 尚待補充。"
    return "\n".join(f"- {_clean_line(item)}" for item in values if _clean_line(item))


def _as_list(value: Any) -> List[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, dict):
        return [f"{key}: {item}" for key, item in value.items()]
    if isinstance(value, str):
        stripped = value.strip()
        return [stripped] if stripped else []
    return [value]


def _clean_line(value: Any) -> str:
    text = str(value).strip()
    text = text.replace("\\n", " ").replace("\r", " ").replace("\n", " ")
    while "  " in text:
        text = text.replace("  ", " ")
    return text.strip(" -\t")


def _dedupe(values: List[Any]) -> List[str]:
    seen = set()
    result = []
    for item in values:
        text = _clean_line(item)
        if text and text not in seen:
            seen.add(text)
            result.append(text)
    return result
