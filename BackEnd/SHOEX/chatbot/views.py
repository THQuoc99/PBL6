from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
import os
import requests

# 🔑 Lấy API key từ biến môi trường hoặc dùng key mặc định
OPENROUTER_API_KEY = os.getenv(
    "OPENROUTER_API_KEY",
    "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"
)

@csrf_exempt
def chat_with_gpt(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
        user_message = data.get("message", "").strip()
        print("🧠 User message:", user_message)

        if not user_message:
            return JsonResponse({"error": "Tin nhắn trống. Vui lòng nhập nội dung."}, status=400)

        # 🧠 Gửi request đến OpenRouter API
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "Referer": "http://localhost:8000",   # ✅ đúng header bắt buộc
            "X-Title": "SHOEX Chatbot"            # ✅ tên app hiển thị trên dashboard OpenRouter
        }

        payload = {
            "model": "meta-llama/llama-3-8b-instruct",
            "messages": [
                {"role": "system", "content": "Bạn là trợ lý ảo hỗ trợ khách hàng mua giày SHOEX."},
                {"role": "user", "content": user_message}
            ]
        }

        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)

        print("🔍 OpenRouter raw status:", response.status_code)
        print("🔍 OpenRouter raw response:", response.text)

        if response.status_code != 200:
            return JsonResponse({
                "error": f"Error code: {response.status_code}",
                "details": response.json()
            }, status=response.status_code)

        result = response.json()

        # 🧩 Kiểm tra phản hồi có hợp lệ không
        if "choices" in result and len(result["choices"]) > 0:
            reply = result["choices"][0]["message"]["content"]
            return JsonResponse({"response": reply})

        # Nếu phản hồi bất thường
        return JsonResponse({
            "error": "Phản hồi không xác định từ OpenRouter",
            "raw": result
        }, status=400)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
