# open source search demo for e-commerce
# Author: community edition (MIT License)

from rank_bm25 import BM25Okapi
import json

# Giả lập dữ liệu sản phẩm
products = [
    {"id": 1, "name": "Điện thoại Samsung Galaxy S24 Ultra", "category": "Điện thoại"},
    {"id": 2, "name": "iPhone 15 Pro Max", "category": "Điện thoại"},
    {"id": 3, "name": "Tai nghe Bluetooth Samsung Buds 2", "category": "Phụ kiện"},
    {"id": 4, "name": "Ốp lưng iPhone 15 chính hãng", "category": "Phụ kiện"},
    {"id": 5, "name": "Laptop Dell XPS 13", "category": "Máy tính xách tay"}
]

# Tiền xử lý dữ liệu: tách từ để huấn luyện BM25
tokenized_corpus = [p["name"].lower().split() for p in products]
bm25 = BM25Okapi(tokenized_corpus)

# Hàm tìm kiếm
def search_products(query, top_k=7):
    tokenized_query = query.lower().split()
    scores = bm25.get_scores(tokenized_query)
    
    # Sắp xếp theo điểm từ cao đến thấp
    ranked_results = sorted(
        zip(products, scores),
        key=lambda x: x[1],
        reverse=True
    )[:top_k]
    
    return [{"product": p["name"], "score": round(s, 3)} for p, s in ranked_results]

# Thử nghiệm
query = "tai có thể nghe"
results = search_products(query)
print(json.dumps(results, indent=4, ensure_ascii=False))
