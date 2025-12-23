import requests
from django.conf import settings

ALLOWED_INTENTS = {
    "search_product",
    "general_faq",
    "user_specific",
    "chitchat"
}


def classify_intent(message: str) -> str:
    """Classify user message into intent categories using LLM"""
    prompt = f"""
    Phân loại câu sau vào 1 trong 4 nhóm:
    search_product | general_faq | user_specific | chitchat

    Câu: "{message}"
    Chỉ trả về đúng 1 từ.
    """

    try:
        res = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "google/gemini-2.0-flash-001",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1
            }, timeout=5
        )
        intent = res.json()['choices'][0]['message']['content'].strip()
        return intent if intent in ALLOWED_INTENTS else "search_product"
    except Exception:
        return "search_product"
