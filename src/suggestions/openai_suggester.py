import os
from typing import Dict
from openai import OpenAI

SYSTEM_PROMPT = (
    "You are an expert resume coach. Provide concise, actionable, bullet-point suggestions "
    "to improve keyword alignment and ATS-friendliness. Avoid generic advice; be specific."
)


def _client():
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        return None
    return OpenAI(api_key=api_key)


def generate_improvement_suggestions(
    kw_result: Dict, ats_result: Dict, resume_text: str, jd_text: str
) -> str:
    client = _client()
    if client is None:
        return (
            "Set OPENAI_API_KEY to enable AI suggestions. Meanwhile, consider: "
            "1) Add missing keywords: " + ", ".join(kw_result.get("missing_keywords", [])) + "; "
            "2) Address ATS issues: " + "; ".join(ats_result.get("issues", []))
        )

    user_prompt = (
        "Resume summary (truncated):\n" + resume_text[:4000] + "\n\n"
        "Job description (truncated):\n" + (jd_text[:4000] if jd_text else "[Not provided]") + "\n\n"
        f"Keyword match score: {kw_result.get('match_score', 0)}%\n"
        "Missing keywords: " + ", ".join(kw_result.get("missing_keywords", [])) + "\n"
        "ATS issues: " + "; ".join(ats_result.get("issues", [])) + "\n\n"
        "Provide 8-12 bullet points with concrete edits (phrases to add, section tweaks)."
    )

    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
        )
        return resp.choices[0].message.content or ""
    except Exception as e:
        return (
            f"Could not fetch AI suggestions right now ({e}). "
            "Try again later. In the meantime, focus on adding the top missing keywords and fixing noted ATS issues."
        )
