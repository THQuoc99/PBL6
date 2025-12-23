import re
from decimal import Decimal

# Định nghĩa dữ liệu tĩnh (Constants)
BRANDS = {
    "nike": "Nike", "adidas": "Adidas", "puma": "Puma", "jordan": "Jordan",
    "vans": "Vans", "converse": "Converse", "new balance": "New Balance",
    "mlb": "MLB", "asics": "Asics", "biti": "Biti's", "bitis": "Biti's",
    "gosto": "Gosto", "skechers": "Skechers", "fila": "Fila"
}

CATEGORIES = {
    "thể thao": "Thể thao",
    "chạy bộ": "Chạy bộ", "giày chạy": "Chạy bộ", "running": "Chạy bộ",
    "bóng rổ": "Bóng rổ", "basket": "Bóng rổ",
    "sneaker": "Sneaker", "bata": "Sneaker",
    "boot": "Boots", "bốt": "Boots",
    "lười": "Giày lười", "slip on": "Giày lười", "slip-on": "Giày lười",
    "cao gót": "Cao gót", "guốc": "Cao gót",
    "búp bê": "Búp bê", "flat": "Búp bê",
    "sandal": "Sandal", "xăng đan": "Sandal",
    "dép": "Dép", "slide": "Dép",
    "tây": "Giày tây", "oxford": "Giày tây", "loafer": "Giày tây"
}

COLORS = {
    "đỏ": "Đỏ", "đen": "Đen", "trắng": "Trắng", "xanh dương": "Xanh dương",
    "xanh lá": "Xanh lá", "xanh": "Xanh", "vàng": "Vàng", "xám": "Xám",
    "ghi": "Xám", "hồng": "Hồng", "cam": "Cam", "tím": "Tím",
    "nâu": "Nâu", "be": "Be", "kem": "Kem"
}

def extract_entities(message):
    """
    Trích xuất thực thể từ tin nhắn người dùng.
    Input: "Tìm giày Nike chạy bộ màu đỏ tầm 1 triệu"
    Output: {'brand': 'Nike', 'category': 'Chạy bộ', 'color': 'Đỏ', 'max_price': 1000000, ...}
    """
    msg = message.lower().strip()
    entities = {
        'brand': None,
        'category': None,
        'min_price': None,
        'max_price': None,
        'color': None,
        'size': None,
        'sort': None,
        'keyword': None
    }

    # 1. Trích xuất Brand
    for k, v in BRANDS.items():
        if k in msg:
            entities['brand'] = v
            break

    # 2. Trích xuất Category (Xử lý thông minh)
    # Loại trừ các cụm từ gây nhiễu: "bán chạy" chứa từ "chạy"
    exclude_phrases = ["bán chạy", "chạy nhất", "chạy nhanh", "chạy tốt"]
    should_skip_category = any(phrase in msg for phrase in exclude_phrases)

    if not should_skip_category:
        for k, v in CATEGORIES.items():
            # Dùng regex để bắt chính xác từ (tránh bắt nhầm từ con)
            # ví dụ: tránh bắt "thể thao" trong "tập thể dục" nếu không muốn, 
            # hoặc đảm bảo biên từ. Ở đây dùng \b để bắt biên từ.
            if re.search(r'\b' + re.escape(k) + r'\b', msg):
                entities['category'] = v
                break

    # 3. Trích xuất Color
    for k, v in COLORS.items():
        if k in msg:
            entities['color'] = v
            break

    # 4. Trích xuất Size
    # Bắt: "size 40", "cỡ 40", "sz 40", "40" (nếu là số 35-48 đứng riêng)
    size_match = re.search(r"(?:size|cỡ|sz)\s*(\d{2})", msg)
    if size_match:
        entities['size'] = size_match.group(1)
    else:
        # Tìm số size lỏng (loose) nhưng tránh nhầm với giá tiền/năm
        loose_size = re.search(r"\b(3[5-9]|4[0-8])\b", msg)
        if loose_size:
            # Kiểm tra kỹ hơn: không được dính với từ khóa tiền tệ
            start, end = loose_size.span()
            context = msg[max(0, start-5):min(len(msg), end+5)]
            if not any(x in context for x in ['k', 'tr', 'ngàn', 'triệu', 'đ', '%']):
                entities['size'] = loose_size.group(1)

    # 5. Trích xuất Price (Logic phức tạp tách ra hàm riêng _extract_price)
    _extract_price(msg, entities)

    # 6. Trích xuất Sorting
    if any(x in msg for x in ["bán chạy", "phổ biến", "hot", "nhiều người mua"]):
        entities['sort'] = "best_selling"
    elif any(x in msg for x in ["rẻ", "thấp", "giá mềm"]):
        entities['sort'] = "price_asc"
    elif any(x in msg for x in ["đắt", "cao cấp", "xịn", "sang"]):
        entities['sort'] = "price_desc"
    elif any(x in msg for x in ["mới", "new"]):
        entities['sort'] = "newest"

    # 7. Trích xuất Keywords & Context (Nhu cầu sử dụng)
    keywords = []
    
    # Chất liệu / Kiểu dáng
    material_keywords = ["da", "vải", "canvas", "lưới", "cao cổ", "thấp cổ", "cổ điển", "vintage", "retro", "chunky"]
    keywords.extend([kw for kw in material_keywords if kw in msg])

    # Use cases (Nhu cầu) -> Map sang Category nếu chưa có
    if not entities['category']:
        if any(x in msg for x in ["đi làm", "công sở", "văn phòng", "tiệc", "đám cưới"]):
            keywords.extend(["lịch sự", "trang trọng"])
            # Gợi ý category phù hợp context
            if "nữ" in msg or "bà" in msg or "cô" in msg:
                entities['category'] = "Cao gót" # Ưu tiên
            elif "nam" in msg or "ông" in msg or "chú" in msg:
                entities['category'] = "Giày tây"
        
        elif any(x in msg for x in ["đi chơi", "dạo phố", "du lịch", "cà phê"]):
            entities['category'] = "Sneaker"
        
        elif any(x in msg for x in ["tập", "gym", "yoga", "thể dục"]):
            entities['category'] = "Thể thao"

    if keywords:
        entities['keyword'] = " ".join(keywords)

    return entities

def _extract_price(msg, entities):
    """Hàm phụ trợ xử lý giá tiền (Helper function)"""
    
    def parse_money(val_str, unit_str):
        if not val_str: return None
        try:
            val = float(val_str.replace(',', '.'))
        except ValueError: return None

        # Nếu không có đơn vị, đoán dựa trên giá trị
        if not unit_str:
            if val < 100: return Decimal(val * 1_000_000) # 1.5 -> 1.5 triệu
            if val >= 1000: return Decimal(val) # 500000 -> 500k
            return Decimal(val * 1_000) # 300 -> 300k

        unit_str = unit_str.strip()
        if unit_str in ['tr', 'triệu', 'củ', 'm']:
            return Decimal(val * 1_000_000)
        if unit_str in ['k', 'ngàn', 'nghìn', 'đ', 'vnd']:
            return Decimal(val * 1_000)
        return Decimal(val)

    # Pattern: khoảng giá (1tr - 3tr, 1 đến 3 triệu)
    range_pattern = r"(\d+[\.,]?\d*)\s*(tr|triệu|củ|k|ngàn)?\s*(?:-|đến|tới)\s*(\d+[\.,]?\d*)\s*(tr|triệu|củ|k|ngàn)?"
    range_match = re.search(range_pattern, msg)

    # Pattern: so sánh (dưới 1tr, trên 500k, tầm 2 củ)
    single_pattern = r"(dưới|trên|tầm|khoảng|hơn)\s*(\d+[\.,]?\d*)\s*(tr|triệu|củ|k|ngàn)?"
    single_match = re.search(single_pattern, msg)

    try:
        if range_match:
            min_v, min_unit, max_v, max_unit = range_match.groups()
            # Nếu min_unit thiếu, lấy theo max_unit (VD: 1-3 triệu)
            if not min_unit and max_unit: min_unit = max_unit
            
            entities['min_price'] = parse_money(min_v, min_unit)
            entities['max_price'] = parse_money(max_v, max_unit)

        elif single_match:
            mod, val, unit = single_match.groups()
            price = parse_money(val, unit)
            
            if mod in ["dưới", "nhỏ hơn"]:
                entities['max_price'] = price
            elif mod in ["trên", "hơn", "lớn hơn"]:
                entities['min_price'] = price
            elif mod in ["tầm", "khoảng", "quanh"]:
                entities['min_price'] = price * Decimal('0.85') # +/- 15%
                entities['max_price'] = price * Decimal('1.15')
    except Exception:
        pass # Bỏ qua lỗi parse giá để không crash app