import json
import os
import base64
from typing import Any, Dict
from urllib import parse, request

from dotenv import load_dotenv

from .prompts import SYSTEM_PROMPT

load_dotenv(override=True)


class AIGateway:
    def __init__(self) -> None:
        self.provider = os.getenv("AI_PROVIDER", "openai").strip().lower()
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
        self.openrouter_model = os.getenv("OPENROUTER_MODEL", "openrouter/free")
        self.openrouter_fallback_models = [
            item.strip()
            for item in os.getenv(
                "OPENROUTER_FALLBACK_MODELS",
                "nvidia/nemotron-nano-9b-v2:free,cohere/north-mini-code:free",
            ).split(",")
            if item.strip()
        ]
        self.openrouter_base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        self.openrouter_site_url = os.getenv("OPENROUTER_SITE_URL", "http://127.0.0.1:8010")
        self.openrouter_app_name = os.getenv("OPENROUTER_APP_NAME", "Disclosure Completion AI MVP")
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        self.gemini_base_url = os.getenv("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta")
        self.demo_mode = os.getenv("APP_DEMO_MODE", "true").lower() == "true"
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY", "")
        self.google_api_key = os.getenv("GOOGLE_API_KEY", "") or os.getenv("GEMINI_API_KEY", "")

    def json_task(self, task_prompt: str, fallback: Dict[str, Any]) -> Dict[str, Any]:
        if self.demo_mode:
            return fallback
        try:
            if self.provider == "gemini":
                return self._call_gemini_json_task(task_prompt)
            return self._call_openai_compatible_json_task(task_prompt)
        except Exception as exc:
            fallback["ai_gateway_warning"] = f"{self.provider} 呼叫失敗，已改用本機 fallback：{exc}"
            return fallback

    def text_task(self, task_prompt: str, fallback: str) -> str:
        if self.demo_mode:
            return fallback
        try:
            if self.provider == "gemini":
                return self._call_gemini_text_task(task_prompt)
            return self._call_openai_compatible_text_task(task_prompt)
        except Exception as exc:
            return f"{fallback}\n\n## AI Gateway Warning\n\n- {self.provider} 呼叫失敗，已改用本機 fallback：{exc}\n"

    def image_ocr_task(self, image_bytes: bytes, mime_type: str, filename: str = "image") -> str:
        if self.demo_mode:
            return "Demo OCR：請在正式模式使用 Gemini API 進行圖片文字辨識。"
        if self.provider != "gemini":
            raise ValueError("圖片 OCR 目前僅支援 AI_PROVIDER=gemini")
        prompt = (
            "請對此圖片進行 OCR 文字辨識，輸出繁體中文或原文文字。"
            "若圖片包含專利揭露書、技術文件、手寫或列印文字，請盡量保留段落、條列與標號。"
            "只輸出辨識出的文字，不要摘要，不要加入未出現在圖片中的內容。"
            f"\n\n檔名：{filename}"
        )
        return self._call_gemini_with_image(prompt, image_bytes, mime_type)

    def _call_openai_compatible_json_task(self, task_prompt: str) -> Dict[str, Any]:
        from openai import OpenAI

        client, models_to_try = self._openai_compatible_client()
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": task_prompt},
        ]

        errors = []
        for model in models_to_try:
            try:
                return self._request_openai_compatible_json(client, model, messages)
            except Exception as exc:
                errors.append(f"{model}: {exc}")
        raise RuntimeError("All configured models failed. " + " | ".join(errors))

    def _call_openai_compatible_text_task(self, task_prompt: str) -> str:
        client, models_to_try = self._openai_compatible_client()
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": task_prompt},
        ]
        errors = []
        for model in models_to_try:
            try:
                response = client.chat.completions.create(model=model, messages=messages, temperature=0.2)
                return response.choices[0].message.content or ""
            except Exception as exc:
                errors.append(f"{model}: {exc}")
        raise RuntimeError("All configured models failed. " + " | ".join(errors))

    def _openai_compatible_client(self) -> tuple[Any, list[str]]:
        from openai import OpenAI

        if self.provider == "openrouter":
            if not self.openrouter_api_key:
                raise ValueError("OPENROUTER_API_KEY is required when AI_PROVIDER=openrouter")
            client = OpenAI(
                api_key=self.openrouter_api_key,
                base_url=self.openrouter_base_url,
                default_headers={
                    "HTTP-Referer": self.openrouter_site_url,
                    "X-OpenRouter-Title": self.openrouter_app_name,
                },
            )
            return client, [self.openrouter_model, *self.openrouter_fallback_models]
        if self.provider == "openai":
            if not self.openai_api_key:
                raise ValueError("OPENAI_API_KEY is required when AI_PROVIDER=openai")
            return OpenAI(api_key=self.openai_api_key), [self.openai_model]
        raise ValueError("AI_PROVIDER must be 'openai', 'openrouter', or 'gemini'")

    def _request_openai_compatible_json(self, client: Any, model: str, messages: list[dict[str, str]]) -> Dict[str, Any]:
        try:
            response = client.chat.completions.create(
                model=model,
                response_format={"type": "json_object"},
                messages=messages,
                temperature=0.2,
            )
        except Exception:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    *messages,
                    {"role": "user", "content": "請只輸出合法 JSON 物件，不要 Markdown，不要程式碼區塊，不要額外說明。"},
                ],
                temperature=0.2,
            )

        content = response.choices[0].message.content or "{}"
        return json.loads(self._extract_json(content))

    def _call_gemini_json_task(self, task_prompt: str) -> Dict[str, Any]:
        content = self._call_gemini(
            f"{task_prompt}\n\n請只輸出合法 JSON 物件，不要 Markdown，不要程式碼區塊，不要額外說明。",
            response_mime_type="application/json",
        )
        return json.loads(self._extract_json(content or "{}"))

    def _call_gemini_text_task(self, task_prompt: str) -> str:
        return self._call_gemini(task_prompt, response_mime_type="text/plain")

    def _call_gemini(self, task_prompt: str, response_mime_type: str) -> str:
        if not self.google_api_key:
            raise ValueError("GOOGLE_API_KEY or GEMINI_API_KEY is required when AI_PROVIDER=gemini")

        endpoint = (
            f"{self.gemini_base_url}/models/{parse.quote(self.gemini_model, safe='')}:generateContent"
            f"?key={parse.quote(self.google_api_key)}"
        )
        payload = {
            "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
            "contents": [{"role": "user", "parts": [{"text": task_prompt}]}],
            "generationConfig": {
                "temperature": 0.2,
                "responseMimeType": response_mime_type,
            },
        }
        req = request.Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with request.urlopen(req, timeout=90) as response:
            data = json.loads(response.read().decode("utf-8"))

        parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
        return "".join(part.get("text", "") for part in parts).strip()

    def _call_gemini_with_image(self, task_prompt: str, image_bytes: bytes, mime_type: str) -> str:
        if not self.google_api_key:
            raise ValueError("GOOGLE_API_KEY or GEMINI_API_KEY is required when AI_PROVIDER=gemini")
        if not mime_type.startswith("image/"):
            raise ValueError("OCR input must be an image")

        endpoint = (
            f"{self.gemini_base_url}/models/{parse.quote(self.gemini_model, safe='')}:generateContent"
            f"?key={parse.quote(self.google_api_key)}"
        )
        payload = {
            "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {"text": task_prompt},
                        {
                            "inline_data": {
                                "mime_type": mime_type,
                                "data": base64.b64encode(image_bytes).decode("ascii"),
                            }
                        },
                    ],
                }
            ],
            "generationConfig": {
                "temperature": 0,
                "responseMimeType": "text/plain",
            },
        }
        req = request.Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with request.urlopen(req, timeout=120) as response:
            data = json.loads(response.read().decode("utf-8"))
        parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
        return "".join(part.get("text", "") for part in parts).strip()

    def _extract_json(self, content: str) -> str:
        text = content.strip()
        if text.startswith("```"):
            text = text.strip("`")
            if text.lower().startswith("json"):
                text = text[4:].strip()
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end >= start:
            return text[start : end + 1]
        return text


ai_gateway = AIGateway()
