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


def generate_low_quota_completion_bundle(case: Any) -> Dict[str, Any]:
    """Quota-saving mode: one AI call fills every completion section.

    This intentionally avoids the normal multi-step chain so mobile/Render users
    spend fewer Gemini/OpenRouter requests and are less likely to hit 429 limits.
    """
    source_text = getattr(case, "transcript_or_disclosure_text", "") or ""
    seed = _summary_seed(source_text, 900)
    fallback = _build_low_quota_fallback(case, seed)
    prompt = f"""
你現在執行 Disclosure Completion AI 的「省額度模式」。

最高規則：
1. 你不是在生成專利說明書，也不是在生成 Claim。
2. 你的任務是在不超出 Original Invention Intent 與 Engineering Boundary 的前提下，將原始揭露內容補足為一份可供專利工程師撰寫專利說明書使用的完整揭露書。
3. 不得創造全新發明，不得擅自改變原解決方案。
4. 可以在原問題與原解決手段邊界內合理補足技術背景、待解決問題、必要技術元素、技術流程、替代實施方式、技術效果、應用情境與進步性鋪陳。
5. 合理推論內容必須標示為「AI合理補足」。
6. 無法合理推論者必須列入「待確認事項」。
7. 不得把產品附加功能誤認為必要技術元素。
8. 所有輸出都是 AI 初稿，必須由專利工程師確認。

請只輸出 JSON，不要輸出 Markdown code fence。JSON schema 必須完全符合：
{{
  "engineering_definition": {{
    "original_invention_intent": "",
    "technical_problem": "",
    "original_solution": "",
    "engineering_boundary": "",
    "project_scope": "",
    "unclear_points": []
  }},
  "disclosure_completion": {{
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
  }},
  "progressive_elaboration_disclosure": {{
    "known_solution_limitations": [],
    "why_existing_methods_are_insufficient": [],
    "technical_improvement_logic": "",
    "necessary_combination_reasoning": "",
    "technical_effect_chain": [],
    "inventive_step_support_points": []
  }},
  "embodiment_expansion": {{
    "main_embodiment": "",
    "alternative_embodiments": [],
    "parameter_variations": [],
    "module_variations": [],
    "process_variations": [],
    "application_variations": []
  }},
  "completed_disclosure_draft": ""
}}

案件資料：
- case_title: {getattr(case, "case_title", "")}
- client_name: {getattr(case, "client_name", "")}
- inventors: {getattr(case, "inventors", [])}
- technical_field: {getattr(case, "technical_field", "")}

原始揭露內容：
{_clip(source_text)}
"""
    result = ai_gateway.json_task(prompt, fallback)
    return _normalize_low_quota_bundle(result, fallback)


def _build_low_quota_fallback(case: Any, seed: str) -> Dict[str, Any]:
    title = getattr(case, "case_title", "") or "待命名發明"
    field = getattr(case, "technical_field", "") or "待確認技術領域"
    definition = {
        "notice": AI_NOTICE,
        "original_invention_intent": f"依據目前揭露內容，發明意圖初步集中於：{seed}",
        "technical_problem": "原始揭露尚需由專利工程師確認具體工程問題，尤其是輸入資料、處理流程、輸出結果與技術效果之間的限制關係。",
        "original_solution": "依據原始揭露內容整理既有解決手段；未明確揭露之處不視為新增發明。",
        "engineering_boundary": "工程邊界限於原始揭露文字中已載明或可合理確認之技術架構、流程、模組、資料處理與輸出效果。",
        "project_scope": "本階段僅產出可撰寫揭露書初稿，不生成 Claim，不生成完整專利說明書。",
        "unclear_points": [
            "請確認核心輸入資料、處理條件與輸出結果。",
            "請確認哪些模組或流程是達成技術效果的必要技術元素。",
            "請確認產品功能與必要技術特徵之界線。",
        ],
    }
    completion = {
        "notice": AI_NOTICE,
        "invention_title_options": [title, f"{field}之揭露補全系統及方法"],
        "technical_field": field,
        "background_problem": f"目前揭露內容顯示，既有方案在特定工程場景中仍可能存在資料取得、流程判斷、結果輸出或技術效果驗證不足等問題。原始內容摘要：{seed}",
        "technical_problem": definition["technical_problem"],
        "invention_objective": "在原始揭露範圍內，補足可支撐後續專利工程撰寫的技術問題、解決手段、必要元素與技術效果。",
        "core_solution": definition["original_solution"],
        "necessary_technical_elements": [
            "輸入資料取得或接收元件",
            "資料解析、判斷或處理流程",
            "依據處理結果產生輸出、提示、控制或互動結果之元件",
            "用於限制工程邊界與技術效果的必要條件",
        ],
        "system_architecture": "AI合理補足：可先以輸入層、處理層、輸出層與人工確認層描述系統架構；實際模組名稱與關聯仍需依原始揭露確認。",
        "method_flow": [
            "接收原始揭露中指定的資料或訊號",
            "依既有揭露之規則、模型、演算法或流程進行處理",
            "產生與技術問題對應的輸出結果",
            "由專利工程師確認各步驟是否屬必要技術元素",
        ],
        "data_flow": [
            "原始資料或訊號進入系統",
            "資料經處理流程形成中間判斷或特徵",
            "中間結果轉換為輸出結果或技術效果",
        ],
        "technical_effects": [
            "AI合理補足：提升資料處理一致性、降低人工判斷落差或改善特定工程流程的可追蹤性。",
            "實際技術效果需由發明人以實驗、案例或流程比較確認。",
        ],
        "alternative_embodiments": [
            "AI合理補足：可依不同資料來源、不同處理規則、不同輸出介面或不同部署環境描述替代實施方式，但不得超出原始解決手段。",
        ],
        "application_scenarios": [
            "AI合理補足：可應用於原始揭露所屬技術領域中需要資料整理、判斷、輸出或互動提示的場景。",
        ],
        "implementation_details": [
            "請補充資料格式、觸發條件、模組間連接關係、輸出格式與例外處理。",
        ],
        "ai_reasonably_inferred_content": [
            "AI合理補足：以輸入、處理、輸出、效果四段式整理揭露內容，以利後續專利工程撰寫。",
        ],
        "items_to_confirm": definition["unclear_points"],
    }
    elaboration = {
        "notice": AI_NOTICE,
        "known_solution_limitations": ["既有方案限制需由發明人提供實際比較基準，避免只停留在產品需求描述。"],
        "why_existing_methods_are_insufficient": ["需確認既有方法在何種工程條件下無法達成預期輸出或技術效果。"],
        "technical_improvement_logic": "以原始解決手段如何克服既有限制、產生可驗證技術效果作為進步性鋪陳主線。",
        "necessary_combination_reasoning": "請確認各必要技術元素彼此配合的原因，而非單純功能堆疊。",
        "technical_effect_chain": ["輸入條件 -> 處理流程 -> 中間判斷 -> 輸出結果 -> 技術效果"],
        "inventive_step_support_points": ["補充既有方案差異、必要組合原因、不可任意替換的技術條件與效果鏈。"],
    }
    embodiment = {
        "notice": AI_NOTICE,
        "main_embodiment": "AI合理補足：主要實施例可依原始揭露之核心流程描述，包含輸入資料、處理步驟、輸出結果與專利工程師確認事項。",
        "alternative_embodiments": ["在不改變原始解決手段下，可改變資料來源、模組配置、輸出介面或部署環境。"],
        "parameter_variations": ["參數、閾值、時間窗口、資料欄位或模型設定需由發明人確認。"],
        "module_variations": ["各模組可整合或分離部署，但需確認是否影響技術效果。"],
        "process_variations": ["流程可依不同使用情境調整順序或觸發條件，但不得改變核心技術邏輯。"],
        "application_variations": ["可延伸到同一技術領域內相同工程問題的其他場景。"],
    }
    bundle = {
        "engineering_definition": definition,
        "disclosure_completion": completion,
        "progressive_elaboration_disclosure": elaboration,
        "embodiment_expansion": embodiment,
    }
    bundle["completed_disclosure_draft"] = _build_bundle_completed_draft(case, bundle)
    return bundle


def _normalize_low_quota_bundle(result: Dict[str, Any], fallback: Dict[str, Any]) -> Dict[str, Any]:
    normalized = {}
    for key in [
        "engineering_definition",
        "disclosure_completion",
        "progressive_elaboration_disclosure",
        "embodiment_expansion",
    ]:
        value = result.get(key)
        normalized[key] = value if isinstance(value, dict) else fallback[key]
    draft = result.get("completed_disclosure_draft")
    normalized["completed_disclosure_draft"] = draft if isinstance(draft, str) and draft.strip() else fallback["completed_disclosure_draft"]
    if result.get("ai_gateway_warning"):
        warning = result["ai_gateway_warning"]
        for section in normalized.values():
            if isinstance(section, dict):
                section["ai_gateway_warning"] = warning
        normalized["completed_disclosure_draft"] = f"{normalized['completed_disclosure_draft']}\n\n## AI Gateway Warning\n\n- {warning}\n"
    return normalized


def _build_bundle_completed_draft(case: Any, bundle: Dict[str, Any]) -> str:
    definition = bundle["engineering_definition"]
    completion = bundle["disclosure_completion"]
    elaboration = bundle["progressive_elaboration_disclosure"]
    embodiment = bundle["embodiment_expansion"]
    source = _summary_seed(getattr(case, "transcript_or_disclosure_text", ""), 1200)
    questions = _dedupe(
        _as_list(definition.get("unclear_points"))
        + _as_list(completion.get("items_to_confirm"))
        + _as_list(completion.get("implementation_details"))
    )
    return f"""# 可撰寫揭露書初稿

> AI 初稿，需由專利工程師確認。
> 本文件不是 Claim，也不是完整專利說明書；目的在於將原始揭露內容補足為可供專利工程師撰寫專利說明書使用的完整揭露書。

一、發明名稱
{_markdown_list(completion.get("invention_title_options"))}

二、技術領域
{completion.get("technical_field", "")}

三、先前技術與現有問題
{completion.get("background_problem", "")}

四、待解決技術問題
{completion.get("technical_problem") or definition.get("technical_problem", "")}

五、發明目的
{completion.get("invention_objective", "")}

六、核心解決手段
{completion.get("core_solution") or definition.get("original_solution", "")}

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
- 既有方案限制：{_markdown_list(elaboration.get("known_solution_limitations"))}
- 既有方法不足：{_markdown_list(elaboration.get("why_existing_methods_are_insufficient"))}
- 技術改良邏輯：{elaboration.get("technical_improvement_logic", "")}
- 必要組合理由：{elaboration.get("necessary_combination_reasoning", "")}
- 技術效果鏈：{_markdown_list(elaboration.get("technical_effect_chain"))}
- 進步性支撐點：{_markdown_list(elaboration.get("inventive_step_support_points"))}

十六、AI合理補足內容
{_markdown_list(completion.get("ai_reasonably_inferred_content"))}

十七、待確認事項
{_markdown_list(questions)}

十八、原始揭露摘要
{source}
"""


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
