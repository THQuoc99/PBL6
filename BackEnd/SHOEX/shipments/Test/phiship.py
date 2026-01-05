import requests
import json
from typing import Optional, List, Dict, Any

def calculate_ghtk_fee(
    weight: int,
    # Tham số địa chỉ (Có thể dùng ID hoặc các trường đầy đủ)
    pick_address_id: Optional[str] = None,
    pick_province: Optional[str] = None,
    pick_district: Optional[str] = None,
    province: Optional[str] = None,
    district: Optional[str] = None,
    
    # Các trường tùy chọn khác
    pick_address: Optional[str] = None,
    pick_ward: Optional[str] = None,
    pick_street: Optional[str] = None,
    address: Optional[str] = None,
    ward: Optional[str] = None,
    street: Optional[str] = None,
) -> Dict[str, Any]:
   
    endpoint = f"{base_url}/services/shipment/fee"
    
    # 1. Chuẩn bị Headers
    headers = {
        'Token': api_token,
        'X-Client-Source': partner_code
    }
    
    # 2. Chuẩn bị Tham số (Query Parameters)
    params = {
        'weight': weight,  # Bắt buộc
        'transport': 'road', # Không bắt buộc
        
        # Các tham số địa chỉ và thông tin khác (chỉ thêm nếu có giá trị)
        'pick_address_id': pick_address_id, # Ưu tiên nếu có
        'pick_province': pick_province, # Bắt buộc nếu không dùng pick_address_id
        'pick_district': pick_district, # Bắt buộc nếu không dùng pick_address_id
        'province': province, # Bắt buộc
        'district': district, # Bắt buộc
        
        'pick_address': pick_address, # Không bắt buộc
        'pick_ward': pick_ward, # Không bắt buộc
        'pick_street': pick_street, # Không bắt buộc
        'address': address, # Không bắt buộc
        'ward': ward, # Không bắt buộc
        'street': street, # Không bắt buộc
        # tags được xử lý khác, nếu cần có thể thêm vào đây
    }
    
    # Lọc bỏ các tham số có giá trị None
    params = {k: v for k, v in params.items() if v is not None}
    
    # 3. Thực hiện Request GET
    try:
        response = requests.get(endpoint, headers=headers, params=params)
        response.raise_for_status() # Báo lỗi nếu mã trạng thái HTTP là lỗi (4xx hoặc 5xx)
        
        # 4. Trả về kết quả JSON
        return response.json()
        
    except requests.exceptions.RequestException as e:
        return {"success": False, "message": f"Lỗi gọi API: {e}", "response_text": response.text if 'response' in locals() else None}

# --- END OF FUNCTION DEFINITION ---