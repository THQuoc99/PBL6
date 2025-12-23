import os
import re
import requests
from django.conf import settings


def generate_answer(context, question):
    """Generate LLM answer for question. Returns (text_response, product_list) tuple."""
    prompt_path = os.path.join(settings.BASE_DIR, 'SHOEX/chatbot/prompts/sales_prompt.txt')
    try:
        with open(prompt_path, 'r', encoding='utf-8') as f:
            SALES_PROMPT = f.read()
    except FileNotFoundError:
        SALES_PROMPT = """Bạn là nhân viên bán hàng chuyên nghiệp tại cửa hàng giày SHOEX.

QUAN TRỌNG: Trả lời CỰC NGẮN GỌN (1-2 câu), app sẽ hiển thị danh sách sản phẩm bên dưới.

Hãy trả lời câu hỏi của khách hàng dựa trên thông tin có sẵn. Nếu có danh sách sản phẩm, hãy giới thiệu ngắn gọn."""

    # Convert context to string safely
    if context is None:
        context_str = ""
    elif isinstance(context, list):
        if context:
            # Hiển thị tên sản phẩm để LLM biết chính xác có gì
            product_names = [p.name for p in context[:3]]  # Chỉ show 3 sản phẩm đầu
            context_str = f"Tìm thấy {len(context)} sản phẩm: {', '.join(product_names)}"
            if len(context) > 3:
                context_str += "..."
        else:
            context_str = "Không tìm thấy sản phẩm phù hợp"
    else:
        context_str = str(context)

    messages = [
        {"role": "system", "content": SALES_PROMPT},
        {"role": "user", "content": f"{context_str}\n\nCâu hỏi: {question}"}
    ]
    
    print(f"[DEBUG LLM] Context: {context_str}")
    print(f"[DEBUG LLM] Question: {question}")

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "google/gemini-2.0-flash-001",
                "messages": messages
            },
            timeout=10
        )
        response.raise_for_status()
        answer = response.json()['choices'][0]['message']['content']
        
        # Extract product IDs from context string
        product_list = []
        if isinstance(context_str, str):
            id_pattern = r'\(ID:\s*(\d+)\)'
            for match in re.finditer(id_pattern, context_str):
                product_list.append(int(match.group(1)))
        
        return answer, product_list
    except Exception as e:
        print(f"LLM Error: {e}")
        return "Xin lỗi, tôi không thể xử lý yêu cầu của bạn lúc này.", []
