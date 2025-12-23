from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.http import JsonResponse
from chatbot.services.intent_service import classify_intent
from chatbot.services.entity_service import extract_entities
from chatbot.services.product_service import search_products
from chatbot.services.user_context_service import get_user_context
from chatbot.services.llm_service import generate_answer
from chatbot.services.conversation_service import get_or_create_session, save_message



@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([AllowAny])
def chat(request):
    """Main chatbot endpoint with production-ready architecture"""
    message = request.data.get('message', '').strip()
    if not message:
        return JsonResponse({'response': 'Shoex xin chào!', 'products': []})

    session = get_or_create_session(request)
    intent = classify_intent(message)
    save_message(session, 'user', message, intent)

    context = None
    all_products = []

    if intent == 'search_product':
        criteria = extract_entities(message)
        products = search_products(criteria)
        context = products
        
        print(f"[DEBUG] Criteria: {criteria}")
        print(f"[DEBUG] Found {len(products)} products")

        if products:
            all_products.extend(products)
        else:
            context = []

    elif intent == 'user_specific':
        if not request.user.is_authenticated:
            return JsonResponse({'response': 'Vui lòng đăng nhập để xem thông tin cá nhân.', 'products': []})
        context = get_user_context(request.user, message)

    elif intent == 'general_faq':
        context = 'Bạn có thể xem chính sách tại website Shoex.'
    
    elif intent == 'chitchat':
        # Để context rỗng, LLM sẽ tự trả lời chitchat tự nhiên
        context = ''
    
    else:
        # Fallback cho các intent khác
        context = ''

    reply, product_list = generate_answer(context, message)
    
    # Hardcode response nếu không tìm thấy sản phẩm (tránh LLM hallucinate)
    if intent == 'search_product' and not all_products:
        reply = "Xin lỗi, mình chưa tìm thấy sản phẩm phù hợp với yêu cầu của bạn."
    
    # Format response với product links (avoid duplicates)
    product_data = []
    seen_ids = set()
    for p in all_products:
        if p.pk not in seen_ids:
            # Lấy ảnh thumbnail
            thumbnail = p.product_images.filter(is_thumbnail=True).first()
            image_url = thumbnail.image.url if thumbnail and thumbnail.image else None
            
            product_data.append({
                'id': p.pk,
                'name': p.name,
                'price': int(p.display_price),
                'image': image_url
            })
            seen_ids.add(p.pk)
    
    print(f"[DEBUG] all_products count: {len(all_products)}")
    print(f"[DEBUG] product_data count: {len(product_data)}")
    print(f"[DEBUG] Response: reply='{reply[:50]}...', products={len(product_data)}")

    save_message(session, 'bot', reply, intent)

    return JsonResponse({
        'response': reply,
        'recommendation': None,
        'products': product_data
    })


# Backward compatibility - alias for old endpoint
chat_with_gpt = chat


# ==============================================================================
# OLD CODE REMOVED - NOW USING SERVICES ARCHITECTURE
# ==============================================================================
# All functionality has been refactored into specialized service modules:
# - services/intent_service.py: Intent classification with LLM
# - services/entity_service.py: Entity extraction (brand, category, price, color, size)
# - services/product_service.py: Product search with filtering
# - services/recommendation_service.py: Product recommendations with price filtering
# - services/upsell_ai_service.py: Upsell text generation
# - services/llm_service.py: LLM response generation
# - services/user_context_service.py: User cart and order data retrieval
# - services/conversation_service.py: Session management
#
# This refactoring provides:
# ✅ Separation of concerns
# ✅ Better testability
# ✅ Code reusability
# ✅ Easier maintenance
# ✅ Production-ready architecture
# ==============================================================================
