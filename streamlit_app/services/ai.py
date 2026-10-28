from __future__ import annotations

import json
import os

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # pragma: no cover - optional in deployment environments
    pass

from analytics.kpis import KPI_CATALOG


def mock_answer(question: str, values: dict[str, float | None]) -> dict:
    below = []
    for code, value in values.items():
        if value is None or code not in KPI_CATALOG:
            continue
        kpi = KPI_CATALOG[code]
        unfavorable = value < kpi.target if kpi.better == "higher" else value > kpi.target
        if unfavorable:
            below.append(
                f"{kpi.name} ({value:.1%} vs {kpi.target:.1%})"
                if kpi.unit == "%"
                else f"{kpi.name} ({value:.1f} vs {kpi.target:.1f})"
            )
    observation = "Below-target metrics: " + (
        ", ".join(below) if below else "none in the current snapshot"
    )
    return {
        "provider": "deterministic mock",
        "question": question,
        "observation": observation,
        "hypothesis": "Regional capacity, repeat visits, and part lead times should be investigated; this is a hypothesis, not a causal claim.",
        "recommendation": "Review the regional and delay Pareto views, then create a manager-approved DMAIC case for the largest verified contributor.",
        "evidence": [{"kpi_id": code, "value": value} for code, value in values.items()],
    }


def _build_gemini_prompt(question: str, values: dict[str, float | None]) -> str:
    metric_lines = []
    for code, value in values.items():
        if value is None or code not in KPI_CATALOG:
            continue
        spec = KPI_CATALOG[code]
        metric_lines.append(
            f"- {code} ({spec.name}): value={value}, unit={spec.unit}, target={spec.target}, direction={spec.better}"
        )
    joined = "\n".join(metric_lines)
    return (
        "You are an evidence-based field-service performance analyst. "
        "Use the provided KPI values only and never invent new data. "
        "Return valid JSON with keys: provider, question, observation, hypothesis, recommendation, evidence. "
        "Evidence is a list of objects with kpi_id and value. "
        "Keep the response concise, executive, and grounded in the KPI snapshot.\n\n"
        f"Question: {question}\n\nKPI snapshot:\n{joined}"
    )


def _extract_response_text(response: object) -> str:
    if response is None:
        raise ValueError("empty response")
    if hasattr(response, "text") and isinstance(response.text, str):
        return response.text
    if hasattr(response, "candidates"):
        try:
            parts = response.candidates[0].content.parts
            text_parts = [part.text for part in parts if hasattr(part, "text")]
            if text_parts:
                return "".join(text_parts)
        except (IndexError, AttributeError, TypeError):
            pass
    raise ValueError("response did not include text")


def _parse_json_response(raw: str) -> dict:
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`\n ")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:].strip()
    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start >= 0 and end > start:
            parsed = json.loads(cleaned[start : end + 1])
        else:
            raise
    if not isinstance(parsed, dict):
        raise ValueError("Gemini response was not a JSON object")
    return parsed


def _call_gemini_api(api_key: str, model_name: str, prompt: str) -> str:
    try:
        from google import genai

        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(model=model_name, contents=prompt)
        return _extract_response_text(response)
    except Exception:
        try:
            import google.generativeai as genai

            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            return _extract_response_text(response)
        except Exception:
            raise


def gemini_answer(question: str, values: dict[str, float | None]) -> dict:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return mock_answer(question, values)

    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    prompt = _build_gemini_prompt(question, values)

    try:
        payload = _parse_json_response(_call_gemini_api(api_key, model_name, prompt))
        return {
            "provider": "gemini",
            "question": payload.get("question", question),
            "observation": payload.get("observation", "No observation returned."),
            "hypothesis": payload.get(
                "hypothesis",
                "Regional capacity, repeat visits, and parts lead time should be reviewed in the next operating review.",
            ),
            "recommendation": payload.get(
                "recommendation",
                "Review the KPI contributors and validate the largest verified issue with the operation manager.",
            ),
            "evidence": payload.get(
                "evidence",
                [{"kpi_id": code, "value": value} for code, value in values.items()],
            ),
        }
    except Exception:
        return mock_answer(question, values)


def answer(question: str, values: dict[str, float | None]) -> dict:
    if os.getenv("GEMINI_API_KEY"):
        return gemini_answer(question, values)
    return mock_answer(question, values)
