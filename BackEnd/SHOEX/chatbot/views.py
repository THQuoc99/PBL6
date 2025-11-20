from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
from django.db.models import Q
import requests
import json
import re
from decimal import Decimal

# --- IMPORT NÂNG CẤP ---
# Import các decorator và
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny # Cho phép cả người lạ và người đã đăng nhập
from rest_framework_simplejwt.authentication import JWTAuthentication # (Bạn có thể đổi sang TokenAuthentication nếu dùng)

# Import các model để truy vấn
from products.models import Product, ProductVariant, Category
from cart.models import Cart
from orders.models import Order


# ==============================================================================
# --- PHẦN 1: CƠ SỞ TRI THỨC CỦA SHOP (KNOWLEDGE BASE) ---
# (Thêm lại từ lần trước để bot trả lời được câu hỏi chung)
# ==============================================================================
SHOP_KNOWLEDGE_BASE = {
    "chinh_sach_doi_tra": """
    Chính sách đổi trả của Shoex:
    - Shoex hỗ trợ đổi trả trong vòng 7 ngày kể từ ngày nhận hàng.
    - Sản phẩm phải còn nguyên tem, mác, chưa qua sử dụng và đầy đủ hộp.
    """,
    "chinh_sach_giao_hang": """
    Chính sách giao hàng của Shoex:
    - Shoex giao hàng toàn quốc.
    - Miễn phí vận chuyển (freeship) cho đơn hàng từ 1.500.000 VNĐ.
    - Đơn hàng nội thành TP.HCM / Hà Nội: dự kiến 1-2 ngày.
    - Đơn hàng ngoại thành/tỉnh khác: dự kiến 3-5 ngày.
    """,
    "thong_tin_lien_he": """
    Thông tin liên hệ Shoex:
    - Địa chỉ: 123 Đường ABC, Quận 1, TP. Hồ Chí Minh
    - Hotline: 1900 1234
    - Email: support@shoex.com
    - Giờ làm việc: 9:00 - 21:00 hàng ngày.
    """
}


# ==============================================================================
# --- PHẦN 2: BỘ NÃO PHÂN LOẠI (INTENT CLASSIFIER) ---
# (Hàm mới, nâng cấp)
# ==============================================================================
def classify_intent(user_question):
    """
    Sử dụng LLM để phân loại ý định của người dùng.
    """
    prompt = f"""
Bạn là một bộ phân loại ý định. Hãy đọc câu hỏi của người dùng và phân loại nó vào 1 trong 4 danh mục sau:

1.  `search_product`: Người dùng đang tìm kiếm, hỏi về sản phẩm, giá cả, thương hiệu, hoặc loại giày. (ví dụ: "có giày nike không", "tìm giày chạy bộ", "giày này giá bao nhiêu")
2.  `general_faq`: Người dùng đang hỏi về thông tin chung của shop, chính sách, địa chỉ, giao hàng, đổi trả. (ví dụ: "shop ở đâu", "cách đổi hàng", "giao hàng mất bao lâu")
3.  `user_specific`: Người dùng hỏi về thông tin CÁ NHÂN của họ. (ví dụ: "giỏ hàng của tôi", "xem đơn hàng", "tài khoản của tôi", "đơn hàng của tôi sao rồi")
4.  `chitchat`: Người dùng đang chào hỏi, tạm biệt, cảm ơn, hoặc nói chuyện phiếm. (ví dụ: "chào shop", "cảm ơn bạn", "bạn có khỏe không")

Chỉ trả về MỘT từ duy nhất là tên của danh mục (ví dụ: `search_product`).

Câu hỏi của người dùng: "{user_question}"
Danh mục: """
    
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "google/gemini-2.0-flash-001", # Dùng model nhanh để phân loại
                "messages": [{"role": "user", "content": prompt}],
            }
        )
        response.raise_for_status()
        data = response.json()
        intent = data['choices'][0]['message']['content'].strip().replace("`", "").split('\n')[0].strip()
        
        # Đảm bảo đầu ra là một trong 4 loại
        if intent not in ["search_product", "general_faq", "user_specific", "chitchat"]:
            return "search_product" # Mặc định là tìm sản phẩm nếu không chắc
        return intent
        
    except Exception as e:
        print(f"Lỗi Classify Intent: {e}")
        return "search_product" # Mặc định nếu API lỗi

# ==============================================================================
# --- PHẦN 3: CÁC HÀM TRUY XUẤT (RETRIEVAL) ---
# ==============================================================================

# --- Hàm 3.1: Truy xuất FAQ (Hàm mới) ---
def get_faq_context(user_question):
    """
    Lấy thông tin từ Knowledge Base.
    """
    # Nối tất cả các chính sách lại thành một chuỗi context
    full_context = "\n\n".join(SHOP_KNOWLEDGE_BASE.values())
    return full_context

# --- Hàm 3.2: Truy xuất thông tin User (Hàm mới) ---
def get_user_specific_context(user, user_question):
    """
    Lấy context cá nhân (giỏ hàng, đơn hàng) cho người dùng đã đăng nhập.
    """
    if "giỏ hàng" in user_question or "trong giỏ" in user_question:
        try:
            # Dựa trên schema, Cart liên kết với User qua 'user'
            cart = Cart.objects.get(user=user)
            # Dựa trên schema, CartItem liên kết với Cart qua 'cart'
            items = cart.cartitem_set.all() 
            if not items.exists():
                return "Giỏ hàng của bạn đang trống."
            
            item_list = []
            total_price = Decimal(0)
            for item in items:
                item_total = item.quantity * item.unit_price
                total_price += item_total
                item_list.append(f"- {item.quantity} x {item.variant.product.name} (Size: {item.variant.option_combinations.get('Size', 'N/A')}, Màu: {item.variant.option_combinations.get('Màu Sắc', 'N/A')}) - {item_total:,.0f} VNĐ")
            
            return (f"Giỏ hàng của bạn có {items.count()} món:\n" + 
                    "\n".join(item_list) + 
                    f"\nTổng tạm tính: {total_price:,.0f} VNĐ")

        except Cart.DoesNotExist:
            return "Giỏ hàng của bạn đang trống."
            
    elif "đơn hàng" in user_question or "order" in user_question:
        # Lấy 3 đơn hàng gần nhất
        orders = Order.objects.filter(buyer=user).order_by('-created_at')[:3]
        if not orders.exists():
            return "Bạn chưa có đơn hàng nào."
            
        order_list = []
        for order in orders:
            order_list.append(
                f"- Đơn hàng #{order.order_id} (Ngày: {order.created_at.strftime('%d/%m/%Y')}):\n"
                f"  Trạng thái: {order.get_status_display()}\n" # Dùng get_status_display() nếu có
                f"  Giao hàng: {order.get_shipment_status_display()}\n" # Dùng get_shipment_status_display() nếu có
                f"  Tổng tiền: {order.total_amount:,.0f} VNĐ"
            )
        return "Đây là các đơn hàng gần nhất của bạn:\n" + "\n\n".join(order_list)
        
    return "Không tìm thấy thông tin cá nhân bạn yêu cầu. Bạn thử hỏi về giỏ hàng hoặc đơn hàng nhé."


# --- Hàm 3.3: Trích xuất thực thể sản phẩm (Cập nhật) ---
# (Thêm lại các loại giày từ lần trước)
def extract_entities(message):
    entities = {'brand': None, 'purpose': None, 'min_price': None, 'max_price': None}
    
    brands = {
        "nike": "Nike", "adidas": "Adidas", "puma": "Puma", "converse": "Converse",
        "vans": "Vans", "jordan": "Jordan", "asics": "ASICS", "hoka": "Hoka",
        "under armour": "Under Armour", "cole haan": "Cole Haan", "ecco": "ECCO",
        "clarks": "Clarks", "g.h. bass": "G.H. Bass", "sperry": "Sperry",
        "pedro": "Pedro", "zara": "Zara", "birkenstock": "Birkenstock",
        "teva": "Teva", "crocs": "Crocs", "chaco": "Chaco", "suicoke": "Suicoke",
        "dr. martens": "Dr. Martens", "timberland": "Timberland",
        "palladium": "Palladium", "red wing": "Red Wing", "blundstone": "Blundstone",
    }
    for keyword, brand_name in brands.items():
        if keyword in message: entities['brand'] = brand_name; break
            
    purposes = {
        "đi chơi": "Giày Sneaker", "sneaker": "Giày Sneaker",
        "chạy bộ": "Giày Chạy Bộ", "chạy": "Giày Chạy Bộ",
        "bóng rổ": "Giày Bóng Rổ", "giày tây": "Giày Tây & Lười",
        "giày lười": "Giày Tây & Lười", "công sở": "Giày Tây & Lười",
        "sandal": "Giày Sandal & Dép", "dép": "Giày Sandal & Dép",
        "giày cổ cao": "Giày Cổ Cao & Bốt", "bốt": "Giày Cổ Cao & Bốt",
        "boot": "Giày Cổ Cao & Bốt",
    }
    for keyword, category_name in purposes.items():
        if keyword in message: entities['purpose'] = category_name; break

    # (Giữ nguyên phần xử lý giá tiền)
    price_match_mil = re.search(r"(\d+[\.,]?\d*)\s*(triệu|tr)", message)
    price_match_k = re.search(r"(\d+[\.,]?\d*)\s*k", message)
    price_limit = None
    try:
        if price_match_mil:
            price_value = price_match_mil.group(1).replace(',', '.'); price_limit = Decimal(price_value) * 1_000_000
        elif price_match_k:
            price_value = price_match_k.group(1).replace(',', '.'); price_limit = Decimal(price_value) * 1_000
        if price_limit is not None:
            if 'dưới' in message or 'nhỏ hơn' in message: entities['max_price'] = price_limit
            elif 'trên' in message or 'lớn hơn' in message: entities['min_price'] = price_limit
            else: entities['min_price'] = max(Decimal(0), price_limit - 500_000); entities['max_price'] = price_limit + 500_000
    except: pass 
    return entities

# --- Hàm 3.4: Truy xuất Sản phẩm (Giữ nguyên) ---
def advanced_shoe_search(brand=None, purpose=None, min_price=None, max_price=None):
    variants_qs = ProductVariant.objects.filter(is_active=True, stock__gt=0)
    if min_price is not None: variants_qs = variants_qs.filter(price__gte=min_price)
    if max_price is not None: variants_qs = variants_qs.filter(price__lte=max_price)
    product_filters = Q()
    if brand: product_filters &= Q(product__brand__iexact=brand)
    if purpose: product_filters &= Q(product__category__name__iexact=purpose)
    variants_qs = variants_qs.filter(product_filters)
    final_product_ids = variants_qs.values_list('product_id', flat=True).distinct()[:3]
    return Product.objects.filter(product_id__in=final_product_ids)


# ==============================================================================
# --- PHẦN 4: BỘ NÃO TẠO SINH (GENERATOR) ---
# (Thay thế toàn bộ hàm này)
# ==============================================================================
def get_llm_response(context_data, user_question):
    """
    Hàm này xây dựng "Prompt Ràng buộc" (Grounding Prompt) và gọi API OpenRouter.
    Nó đã được nâng cấp để xử lý context là Product, Text (FAQ, User), hoặc None.
    """
    
    # 1. Định dạng Context (Nâng cấp)
    formatted_context = "Không có thông tin nào được cung cấp."
    
    # --- SỬA LỖI LOGIC BỊA LINK NẰM Ở ĐÂY ---
    
    if context_data == "USER_NOT_AUTHENTICATED":
        formatted_context = "USER_NOT_AUTHENTICATED"
    elif isinstance(context_data, str): # Nếu là FAQ hoặc thông tin User (dạng text)
        formatted_context = context_data
    elif hasattr(context_data, 'exists') and context_data.exists(): # Nếu là QuerySet Product
        product_list = []
        for p in context_data:
            # SỬA LỖI: Chúng ta tạo sẵn link Markdown CHÍNH XÁC tại đây.
            # Bot sẽ không cần phải "suy nghĩ" hay "bịa" link nữa.
            product_list.append(
                f"- Tên: **{p.name}**\n" # In đậm tên sản phẩm
                f"  Giá: {p.base_price:,.0f} VNĐ\n"
                f"  Mô tả: {p.description}\n"
                f"  Link: [Xem chi tiết](/products/{p.slug}/)" # Đây là link tương đối chính xác
            )
        formatted_context = "\n\n".join(product_list) # Tách các sản phẩm bằng 2 dấu xuống dòng
    elif hasattr(context_data, 'exists') and not context_data.exists(): # Nếu là QuerySet rỗng
        formatted_context = "Không tìm thấy sản phẩm nào phù hợp."
    
    # --- KẾT THÚC SỬA LỖI ---


    # 2. Xây dựng Prompt Ràng Buộc 
    prompt_template = f"""
Bạn là trợ lý ảo AI của shop giày Shoex.
Nhiệm vụ của bạn là trả lời câu hỏi của khách hàng.
Bạn PHẢI tuân thủ các quy tắc sau:

1.  Chỉ được trả lời dựa TRÊN VÀ CHỈ TRÊN [Thông tin được cung cấp] dưới đây.
2.  NGHIÊM CẤM sử dụng kiến thức bên ngoài, bịa đặt thông tin.

3.  --- QUY TẮC ĐẶC BIỆT ---
    - Nếu [Thông tin được cung cấp] là "USER_NOT_AUTHENTICATED":
      Hãy lịch sự thông báo cho người dùng rằng họ CẦN PHẢI ĐĂNG NHẬP để sử dụng tính năng này (ví dụ: "Dạ, bạn vui lòng đăng nhập để mình kiểm tra giỏ hàng/đơn hàng nhé!").
    
    - Nếu [Thông tin được cung cấp] là "Không tìm thấy sản phẩm nào phù hợp.":
      Hãy lịch sự thông báo cho khách là bạn không tìm thấy sản phẩm nào khớp với yêu cầu (ví dụ: "Dạ, em kiểm tra rồi nhưng tiếc là không tìm thấy mẫu nào...").

    - Nếu [Thông tin được cung cấp] là "Không có thông tin nào được cung cấp." VÀ người dùng đang `chào hỏi`, `cảm ơn` hoặc `tạm biệt`:
      Hãy lịch sự đáp lại (ví dụ: "Shoex chào bạn!", "Dạ không có gì ạ!").

    - Nếu [Thông tin được cung cấp] là "Không có thông tin nào được cung cấp." VÀ người dùng hỏi câu khác (không phải 3 ý trên):
      Hãy lịch sự thông báo rằng bạn không có thông tin (ví dụ: "Dạ, em chưa có thông tin về vấn đề này ạ.").

4.  --- SỬA LỖI QUY TẮC 4 ---
    Khi trình bày thông tin (sản phẩm, giỏ hàng, FAQ), hãy **trình bày lại gần như y hệt** nội dung trong [Thông tin được cung cấp].
    **TUYỆT ĐỐI KHÔNG** được thay đổi nội dung của "Link:".
    (Ví dụ: Nếu context là "Link: [Xem chi tiết](/products/abc/)", bạn PHẢI chép y hệt lại "Link: [Xem chi tiết](/products/abc/)").
    
5.  Luôn trả lời bằng Tiếng Việt, thân thiện, chuyên nghiệp.

---
[Thông tin được cung cấp]
{formatted_context}
---
[Câu hỏi của khách]
{user_question}
---

Hãy viết câu trả lời cho khách hàng:
"""

    # 3. Gọi API OpenRouter (Giữ nguyên)
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "google/gemini-2.0-flash-001", 
                "messages": [
                    {"role": "user", "content": prompt_template}
                ]
            }
        )
        
        response.raise_for_status() 
        data = response.json()
        return data['choices'][0]['message']['content'].strip()

    except requests.exceptions.JSONDecodeError as json_err:
        print(f"LỖI JSONDecodeError: {response.text}")
        return "Xin lỗi, hệ thống AI đang gặp sự cố (lỗi parse). Vui lòng thử lại sau."
    except requests.exceptions.HTTPError as http_err:
        print(f"LỖI HTTPError: {http_err.response.text}")
        return "Xin lỗi, hệ thống AI đang gặp lỗi (HTTP). Vui lòng thử lại sau."
    except Exception as e:
        print(f"LỖI KHÁC XẢY RA: {e}")
        return "Xin lỗi, hệ thống AI đang gặp lỗi. Vui lòng thử lại sau."

# ==============================================================================
# --- PHẦN 5: VIEW CHÍNH (ĐÂY LÀ BỘ ĐỊNH TUYẾN - ROUTER) ---
# (Nâng cấp)
# ==============================================================================
@csrf_exempt # Vẫn giữ csrf_exempt nếu bạn chưa dùng DRF cho mọi thứ
@api_view(['POST']) # Sử dụng decorator của DRF
@authentication_classes([JWTAuthentication]) # Chỉ định cách xác thực
@permission_classes([AllowAny]) # Cho phép [AllowAny] (mọi người) gọi
def chat_with_gpt(request):
    
    # Dòng request.user này là mấu chốt:
    # - Nếu Flutter gửi token HỢP LỆ -> request.user là <User object>
    # - Nếu Flutter KHÔNG GỬI token -> request.user là <AnonymousUser>
    
    try:
        data = json.loads(request.body.decode("utf-8"))
        message = data.get("message", "").strip().lower()
        data = json.loads(request.body.decode("utf-8"))
        message = data.get("message", "").strip().lower()

        if not message:
            return JsonResponse({"response": "Bạn vui lòng cho mình biết bạn muốn tìm gì nhé."})

        # --- BƯỚC 1: PHÂN LOẠI Ý ĐỊNH ---
        intent = classify_intent(message)
        
        context = None
        
        # --- BƯỚC 2: TRUY XUẤT THÔNG TIN (Retrieval) ---
        if intent == "user_specific":
            if request.user.is_authenticated:
                # NẾU ĐÃ ĐĂNG NHẬP
                context = get_user_specific_context(request.user, message)
            else:
                # NẾU CHƯA ĐĂNG NHẬP
                context = "USER_NOT_AUTHENTICATED"
        
        elif intent == "search_product":
            entities = extract_entities(message)
            context = advanced_shoe_search(
                entities['brand'], 
                entities['purpose'], 
                entities['min_price'], 
                entities['max_price']
            )
        
        elif intent == "general_faq":
            context = get_faq_context(message)
        
        elif intent == "chitchat":
            context = None # Không cần context
        
        # --- BƯỚC 3: TẠO SINH CÂU TRẢ LỜI (Generation) ---
        llm_answer = get_llm_response(context, message)
        
        return JsonResponse({"response": llm_answer})

    except Exception as e:
        print(f"Lỗi hệ thống: {str(e)}")
        return JsonResponse({"error": f"Lỗi hệ thống: {str(e)}"}, status=500)