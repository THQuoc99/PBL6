# chatbot/views.py

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
from django.db.models import Q
import requests
import json
import re
from decimal import Decimal

# --- IMPORT DRF ---
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny 
from rest_framework_simplejwt.authentication import JWTAuthentication 

# --- IMPORT MODELS ---
# Đảm bảo bạn đã có các model này khớp với datanew.sql
from products.models import Product, ProductVariant
from cart.models import Cart, CartItem
from orders.models import Order

# ==============================================================================
# 1. CƠ SỞ TRI THỨC (FAQ)
# ==============================================================================
SHOP_KNOWLEDGE_BASE = {
    "chinh_sach": """
    Chính sách Shoex:
    - Đổi trả: Trong 7 ngày (giày chưa qua sử dụng, còn nguyên tem).
    - Bảo hành: Keo chỉ 6 tháng.
    - Vận chuyển: Freeship đơn > 1.5 triệu. HCM/HN (1-2 ngày), Tỉnh (3-4 ngày).
    """,
    "lien_he": """
    Liên hệ Shoex:
    - Hotline: 1900 1234
    - Địa chỉ: 123 Đường ABC, Quận 1, TP.HCM.
    - Giờ làm việc: 8:00 - 22:00.
    """
}

# ==============================================================================
# 2. PHÂN LOẠI Ý ĐỊNH (INTENT CLASSIFIER)
# ==============================================================================
def classify_intent(user_question):
    # Sử dụng model nhỏ/nhanh để tiết kiệm chi phí
    prompt = f"""
    Phân loại câu: "{user_question}" vào 1 trong 4 nhóm:
    1. `search_product`: Tìm giày, hỏi giá, màu, size, tư vấn mua.
    2. `general_faq`: Hỏi địa chỉ, chính sách, ship, đổi trả.
    3. `user_specific`: Hỏi về "giỏ hàng", "đơn hàng của tôi", "tình trạng đơn".
    4. `chitchat`: Chào hỏi, cảm ơn, tạm biệt.
    
    Chỉ trả về đúng tên nhóm (ví dụ: search_product).
    """
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "google/gemini-2.0-flash-001", # Hoặc model bạn cấu hình
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1
            },
            timeout=5
        )
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content'].strip().lower()
        return "search_product"
    except:
        return "search_product" 

# ==============================================================================
# 3. BỘ TRÍCH XUẤT THÔNG MINH (ENTITY EXTRACTOR)
# ==============================================================================
def extract_entities(message):
    msg = message.lower()
    entities = {
        'brand': None, 
        'category': None, 
        'min_price': None, 
        'max_price': None,
        'color': None,
        'size': None,
        'sort': None
    }
    
    # 1. Brand
    brands = {
        "nike": "Nike", "adidas": "Adidas", "puma": "Puma", "jordan": "Jordan", 
        "vans": "Vans", "converse": "Converse", "new balance": "New Balance", 
        "mlb": "MLB", "asics": "Asics"
    }
    for k, v in brands.items():
        if k in msg: entities['brand'] = v; break
            
    # 2. Category
    cats = {"chạy": "Chạy bộ", "bóng rổ": "Bóng rổ", "sneaker": "Sneaker", "boot": "Boots", "lười": "Giày lười"}
    for k, v in cats.items():
        if k in msg: entities['category'] = v; break

    # 3. Color
    colors = {"đỏ": "Đỏ", "đen": "Đen", "trắng": "Trắng", "xanh": "Xanh", "vàng": "Vàng", "xám": "Xám", "hồng": "Hồng"}
    for k, v in colors.items():
        if k in msg: entities['color'] = v; break

    # 4. Size
    size_match = re.search(r"(?:size|cỡ)\s*(\d{2})", msg)
    if size_match:
        entities['size'] = size_match.group(1)
    else:
        loose_size = re.search(r"\b(3[5-9]|4[0-8])\b", msg)
        if loose_size and "triệu" not in msg and "k" not in msg:
            entities['size'] = loose_size.group(1)

    # 5. Price
    def parse_money(val_str, unit_str):
        val = float(val_str.replace(',', '.'))
        if not unit_str: return Decimal(val * 1000000) if val < 100 else Decimal(val * 1000)
        if unit_str in ['k', 'ngàn']: return Decimal(val * 1000)
        return Decimal(val * 1000000)

    range_match = re.search(r"(\d+[\.,]?\d*)\s*(?:-|đến|tới)\s*(\d+[\.,]?\d*)\s*(tr|triệu|củ|k)?", msg)
    single_match = re.search(r"(dưới|trên|tầm|khoảng)\s*(\d+[\.,]?\d*)\s*(tr|triệu|củ|k)", msg)

    try:
        if range_match:
            min_v, max_v, unit = range_match.groups()
            entities['min_price'] = parse_money(min_v, unit)
            entities['max_price'] = parse_money(max_v, unit)
        elif single_match:
            mod, val, unit = single_match.groups()
            price = parse_money(val, unit)
            if mod == "dưới": entities['max_price'] = price
            elif mod == "trên": entities['min_price'] = price
            else:
                entities['min_price'] = price * Decimal(0.9)
                entities['max_price'] = price * Decimal(1.1)
    except: pass

    # 6. Sorting
    if "rẻ" in msg: entities['sort'] = "price_asc"
    elif "đắt" in msg or "xịn" in msg: entities['sort'] = "price_desc"
    elif "mới" in msg: entities['sort'] = "newest"

    return entities

# ==============================================================================
# 4. TRUY VẤN SẢN PHẨM (ADVANCED SEARCH) - ĐÃ FIX CHO DB MỚI
# ==============================================================================
def advanced_shoe_search(criteria):
    # Lọc biến thể còn hàng và đang hoạt động
    variants = ProductVariant.objects.filter(is_active=True, stock__gt=0).select_related('product', 'product__category')

    # 1. Giá
    if criteria['min_price']: variants = variants.filter(price__gte=criteria['min_price'])
    if criteria['max_price']: variants = variants.filter(price__lte=criteria['max_price'])

    # 2. Màu/Size (Tìm trong cột JSONB option_combinations)
    # Vì datanew.sql dùng JSONB, ta dùng icontains để tìm text trong chuỗi JSON
    if criteria['color']:
        variants = variants.filter(option_combinations__icontains=criteria['color'])
    if criteria['size']:
        # Tìm chính xác số size trong JSON
        variants = variants.filter(option_combinations__icontains=f'"{criteria["size"]}"')

    # 3. Thông tin sản phẩm cha
    if criteria['brand']:
        variants = variants.filter(product__brand__icontains=criteria['brand'])
    if criteria['category']:
        variants = variants.filter(product__category__name__icontains=criteria['category'])

    # 4. Sắp xếp
    if criteria['sort'] == 'price_asc': variants = variants.order_by('price')
    elif criteria['sort'] == 'price_desc': variants = variants.order_by('-price')
    else: variants = variants.order_by('-created_at')

    # 5. Distinct Product (Chỉ lấy sản phẩm đại diện)
    seen_products = set()
    final_products = []
    
    for v in variants:
        if v.product_id not in seen_products:
            # Gán giá hiển thị
            v.product.display_price = v.price 
            final_products.append(v.product)
            seen_products.add(v.product_id)
        
        if len(final_products) >= 5: break

    return final_products

# ==============================================================================
# 5. TRUY XUẤT THÔNG TIN USER - ĐÃ FIX CHO DB MỚI
# ==============================================================================
def get_user_specific_context(user, user_question):
    msg = user_question.lower()
    
    # --- XỬ LÝ GIỎ HÀNG ---
    if "giỏ" in msg:
        try:
            cart = Cart.objects.get(user=user)
            items = cart.items.select_related('variant', 'variant__product').all()
            
            if not items: return "Giỏ hàng của bạn đang trống."
            
            details = []
            for i in items:
                # FIX: Lấy thông tin từ JSONB thay vì property ảo
                variant_info = i.variant.option_combinations # Trả về dict/json
                # Format chuỗi biến thể (Ví dụ: Màu: Đỏ, Size: 40)
                if isinstance(variant_info, dict):
                    variant_str = ", ".join([f"{k}: {v}" for k, v in variant_info.items()])
                else:
                    variant_str = str(variant_info)
                    
                details.append(f"- {i.variant.product.name} ({variant_str}) x{i.quantity}")
                
            return f"Giỏ hàng ({cart.total_items} món):\n" + "\n".join(details) + f"\nTổng: {cart.total_amount:,.0f} đ"
        except Cart.DoesNotExist:
            return "Giỏ hàng trống."
        except Exception as e:
            return "Không thể lấy thông tin giỏ hàng lúc này."
    
    # --- XỬ LÝ ĐƠN HÀNG ---
    if "đơn" in msg:
        # Bảng orders_order có buyer_id khớp với user
        orders = Order.objects.filter(buyer=user).order_by('-created_at')[:3]
        if not orders: return "Bạn chưa có đơn hàng nào."
        
        details = [f"- Đơn #{o.order_id} ({o.get_status_display()}): {o.total_amount:,.0f} đ" for o in orders]
        return "Đơn hàng gần đây:\n" + "\n".join(details)
    
    return "Không tìm thấy thông tin cá nhân liên quan."

# ==============================================================================
# 6. GENERATOR (LLM RESPONSE)
# ==============================================================================
def get_llm_response(context_data, user_question, search_criteria=None):
    
    if isinstance(context_data, list): # List Product objects
        if context_data:
            product_list = []
            for p in context_data:
                price = getattr(p, 'display_price', p.base_price)
                # Link deep link hoặc web link
                link = f"myapp://product/{p.product_id}" # Hoặc /products/{p.slug} nếu là web
                product_list.append(
                    f"- **{p.name}**\n"
                    f"  Giá: {price:,.0f} đ\n"
                    f"  Link: [Xem ngay]({link})"
                )
            formatted_context = "\n\n".join(product_list)
        else:
            formatted_context = "Không tìm thấy sản phẩm nào phù hợp."
    else:
        formatted_context = str(context_data)

    prompt = f"""
    Bạn là AI tư vấn bán hàng của Shoex.
    
    [DỮ LIỆU HỆ THỐNG]
    {formatted_context}
    ----------------
    [KHÁCH HÀNG]: "{user_question}"
    
    [YÊU CẦU]:
    1. Trả lời ngắn gọn, thân thiện bằng tiếng Việt.
    2. Nếu có sản phẩm, liệt kê tên, giá và giữ nguyên link markdown [Xem ngay](...).
    3. Nếu khách hỏi về đơn hàng/giỏ hàng, dùng dữ liệu hệ thống để trả lời chính xác.
    4. Nếu không tìm thấy sản phẩm, hãy gợi ý khách tìm từ khóa khác.
    """
    
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {settings.OPENROUTER_API_KEY}"},
            json={
                "model": "google/gemini-2.0-flash-001",
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=10
        )
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content'].strip()
        return "Hệ thống AI đang bận, vui lòng thử lại sau."
    except Exception as e:
        return f"Xin lỗi, mình đang gặp chút trục trặc: {str(e)}"

# ==============================================================================
# 7. VIEW CHÍNH
# ==============================================================================
@csrf_exempt
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([AllowAny]) # Cho phép cả khách vãng lai chat (intent search/faq)
def chat_with_gpt(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
        message = data.get("message", "").strip()
        if not message: return JsonResponse({"response": "Shoex chào bạn! Bạn cần tìm giày gì hôm nay?"})

        # 1. Phân loại ý định
        intent = classify_intent(message)
        context = None
        criteria = None

        # 2. Xử lý theo ý định
        if intent == "user_specific":
            if request.user.is_authenticated:
                context = get_user_specific_context(request.user, message)
            else:
                return JsonResponse({"response": "Bạn vui lòng đăng nhập để xem thông tin đơn hàng và giỏ hàng nhé!"})
        
        elif intent == "search_product":
            criteria = extract_entities(message)
            context = advanced_shoe_search(criteria)
        
        elif intent == "general_faq":
            context = "\n".join(SHOP_KNOWLEDGE_BASE.values())

        # 3. Gọi LLM sinh câu trả lời
        llm_reply = get_llm_response(context, message, criteria)
        
        return JsonResponse({"response": llm_reply})

    except Exception as e:
        print(f"Chatbot Error: {e}")
        return JsonResponse({"error": "Lỗi xử lý yêu cầu"}, status=500)