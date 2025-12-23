"""
GHTK (Giao Hàng Tiết Kiệm) API Integration Service
Documentation: https://docs.giaohangtietkiem.vn/

Các tính năng:
1. Tính phí vận chuyển
2. Tạo đơn hàng
3. Hủy đơn hàng  
4. Tra cứu trạng thái
5. In tem vận đơn
"""

import requests
import json
from decimal import Decimal
from typing import Dict, Optional, List
from datetime import datetime
from django.conf import settings

class GHTKService:
    """Service tích hợp GHTK API"""
    
    # Base URLs
    BASE_URL_PROD = "https://services.giaohangtietkiem.vn/services"
    BASE_URL_DEV = "https://services.ghtklab.com/services"  # Sandbox
    
    def __init__(self, token: str = None, is_production: bool = False):
        """
        Khởi tạo GHTK Service
        
        Args:
            token: GHTK API Token (Lấy từ https://khachhang.giaohangtietkiem.vn/web/apiKey)
            is_production: True = Production, False = Sandbox
        """
        self.token = token or getattr(settings, 'GHTK_API_TOKEN', 'YOUR_GHTK_TOKEN_HERE')
        self.base_url = self.BASE_URL_PROD if is_production else self.BASE_URL_DEV
        self.headers = {
            'Token': self.token,
            'Content-Type': 'application/json'
        }
    
    def calculate_fee(self, 
                     pick_province: str,
                     pick_district: str, 
                     province: str,
                     district: str,
                     weight: int,
                     value: Decimal,
                     deliver_option: str = 'none') -> Optional[Dict]:
        """
        Tính phí vận chuyển
        
        Args:
            pick_province: Tỉnh lấy hàng (ví dụ: "Hà Nội")
            pick_district: Quận/huyện lấy hàng (ví dụ: "Quận Ba Đình")
            province: Tỉnh giao hàng
            district: Quận/huyện giao hàng
            weight: Trọng lượng (gram)
            value: Giá trị đơn hàng (VNĐ)
            deliver_option: 'none' (tiêu chuẩn) hoặc 'xteam' (nhanh)
        
        Returns:
            {
                'success': True/False,
                'fee': {
                    'name': 'Giao hàng tiết kiệm',
                    'fee': 22000,
                    'insurance_fee': 1200,
                    'estimated_pick_time': '2024-01-15 14:00',
                    'estimated_deliver_time': '2024-01-18 18:00'
                },
                'message': '...'
            }
        """
        url = f"{self.base_url}/shipment/fee"
        
        # Chuẩn hóa địa chỉ: Bỏ ALL tiền tố
        import re
        
        # Patterns to remove (case-insensitive)
        province_patterns = [
            r'^Tỉnh\s+', r'^Thành phố\s+', r'^TP\.\s*', r'^TP\s+'
        ]
        district_patterns = [
            r'^Quận\s+', r'^Huyện\s+', r'^Thị xã\s+', r'^Thành phố\s+',
            r'^Xã\s+', r'^Phường\s+', r'^Thị trấn\s+', r'^Khu phố\s+'
        ]
        
        province_clean = province
        for pattern in province_patterns:
            province_clean = re.sub(pattern, '', province_clean, flags=re.IGNORECASE).strip()
        
        pick_province_clean = pick_province
        for pattern in province_patterns:
            pick_province_clean = re.sub(pattern, '', pick_province_clean, flags=re.IGNORECASE).strip()
        
        district_clean = district
        for pattern in district_patterns:
            district_clean = re.sub(pattern, '', district_clean, flags=re.IGNORECASE).strip()
        
        pick_district_clean = pick_district
        for pattern in district_patterns:
            pick_district_clean = re.sub(pattern, '', pick_district_clean, flags=re.IGNORECASE).strip()
        
        print(f"Address cleaning:")
        print(f"  Province: '{province}' -> '{province_clean}'")
        print(f"  District: '{district}' -> '{district_clean}'")
        print(f"  Pick Province: '{pick_province}' -> '{pick_province_clean}'")
        print(f"  Pick District: '{pick_district}' -> '{pick_district_clean}'")
        
        params = {
            'pick_province': pick_province_clean,
            'pick_district': pick_district_clean,
            'province': province_clean,
            'district': district_clean,
            'weight': weight,
            'value': int(value),
            'deliver_option': deliver_option,
        }
        
        # Retry logic: 3 attempts with increasing timeout
        max_retries = 3
        timeouts = [15, 20, 30]  # Tăng timeout dần
        
        for attempt in range(max_retries):
            try:
                print(f"GHTK API attempt {attempt + 1}/{max_retries} with timeout={timeouts[attempt]}s")
                print(f"Request URL: {url}")
                print(f"Request params: {params}")
                print(f"Request headers: {self.headers}")
                
                response = requests.get(
                    url, 
                    params=params, 
                    headers=self.headers, 
                    timeout=timeouts[attempt]
                )
                
                print(f"Response status: {response.status_code}")
                print(f"Response content-type: {response.headers.get('content-type')}")
                print(f"Response body (first 500 chars): {response.text[:500]}")
                
                data = response.json()
                
                if response.status_code == 200 and data.get('success'):
                    print(f"GHTK API success on attempt {attempt + 1}")
                    return {
                        'success': True,
                        'fee': data['fee'],
                        'message': 'Tính phí thành công'
                    }
                else:
                    print(f"GHTK API error response: {data}")
                    return {
                        'success': False,
                        'message': data.get('message', 'Không thể tính phí vận chuyển')
                    }
                    
            except requests.Timeout as e:
                print(f"GHTK API timeout on attempt {attempt + 1}: {str(e)}")
                if attempt == max_retries - 1:  # Last attempt
                    return {
                        'success': False,
                        'message': f'GHTK API timeout sau {max_retries} lần thử. Vui lòng thử lại sau.'
                    }
                # Retry on next iteration
                continue
                
            except requests.RequestException as e:
                print(f"GHTK API connection error: {str(e)}")
                return {
                    'success': False,
                    'message': f'Lỗi kết nối GHTK: {str(e)}'
                }
    
    def create_order(self, order_data: Dict) -> Optional[Dict]:
        """
        Tạo đơn hàng vận chuyển
        
        Args:
            order_data: {
                'id': 'ORDER_123',  # Mã đơn hàng của bạn
                'pick_name': 'Tên shop',
                'pick_address': 'Địa chỉ lấy hàng',
                'pick_province': 'Tỉnh lấy',
                'pick_district': 'Quận lấy',
                'pick_ward': 'Phường lấy',
                'pick_tel': '0123456789',
                'name': 'Tên người nhận',
                'address': 'Địa chỉ nhận',
                'province': 'Tỉnh nhận',
                'district': 'Quận nhận', 
                'ward': 'Phường nhận',
                'hamlet': 'Thôn/Ấp',
                'tel': '0987654321',
                'note': 'Ghi chú',
                'value': 500000,  # Giá trị đơn hàng
                'pick_money': 500000,  # Tiền thu hộ (COD)
                'is_freeship': 0 hoặc 1,
                'weight': 1000,  # Gram
                'products': [
                    {
                        'name': 'Tên sản phẩm',
                        'weight': 500,
                        'quantity': 2,
                        'price': 100000
                    }
                ]
            }
        
        Returns:
            {
                'success': True/False,
                'order': {
                    'partner_id': 'ORDER_123',
                    'label': 'S12345678',  # Mã vận đơn GHTK
                    'fee': 22000,
                    'estimated_pick_time': '...',
                    'estimated_deliver_time': '...'
                },
                'message': '...'
            }
        """
        url = f"{self.base_url}/shipment/order"
        
        # Chuẩn hóa dữ liệu
        payload = {
            'products': order_data.get('products', []),
            'order': {
                'id': str(order_data['id']),
                'pick_name': order_data['pick_name'],
                'pick_address': order_data['pick_address'],
                'pick_province': order_data['pick_province'],
                'pick_district': order_data['pick_district'],
                'pick_ward': order_data.get('pick_ward', ''),
                'pick_tel': order_data['pick_tel'],
                'tel': order_data['tel'],
                'name': order_data['name'],
                'address': order_data['address'],
                'province': order_data['province'],
                'district': order_data['district'],
                'ward': order_data.get('ward', ''),
                'hamlet': order_data.get('hamlet', 'Khác'),
                'is_freeship': order_data.get('is_freeship', 0),
                'pick_money': int(order_data.get('pick_money', 0)),
                'note': order_data.get('note', ''),
                'value': int(order_data.get('value', 0)),
                'transport': order_data.get('transport', 'road'),  # road hoặc fly
                'deliver_option': order_data.get('deliver_option', 'none'),  # none hoặc xteam
                'pick_option': order_data.get('pick_option', 'cod'),  # cod hoặc post
            }
        }
        
        try:
            response = requests.post(url, json=payload, headers=self.headers, timeout=15)
            data = response.json()
            
            if response.status_code == 200 and data.get('success'):
                return {
                    'success': True,
                    'order': data['order'],
                    'message': 'Tạo đơn hàng thành công'
                }
            else:
                return {
                    'success': False,
                    'message': data.get('message', 'Không thể tạo đơn hàng')
                }
                
        except requests.RequestException as e:
            return {
                'success': False,
                'message': f'Lỗi kết nối GHTK: {str(e)}'
            }
    
    def cancel_order(self, label: str) -> Dict:
        """
        Hủy đơn hàng
        
        Args:
            label: Mã vận đơn GHTK (ví dụ: S12345678)
        
        Returns:
            {'success': True/False, 'message': '...'}
        """
        url = f"{self.base_url}/shipment/cancel/{label}"
        
        try:
            response = requests.post(url, headers=self.headers, timeout=10)
            data = response.json()
            
            if response.status_code == 200 and data.get('success'):
                return {
                    'success': True,
                    'message': 'Hủy đơn hàng thành công'
                }
            else:
                return {
                    'success': False,
                    'message': data.get('message', 'Không thể hủy đơn hàng')
                }
                
        except requests.RequestException as e:
            return {
                'success': False,
                'message': f'Lỗi kết nối GHTK: {str(e)}'
            }
    
    def get_order_status(self, label: str) -> Optional[Dict]:
        """
        Tra cứu trạng thái đơn hàng
        
        Args:
            label: Mã vận đơn GHTK
        
        Returns:
            {
                'success': True/False,
                'order': {
                    'label': 'S12345678',
                    'partner_id': 'ORDER_123',
                    'status': 2,  # -1: Hủy, 1: Chờ lấy, 2: Đã lấy, 3: Delay, 5: Đang giao, 6: Đã giao, ...
                    'status_text': 'Đã tiếp nhận',
                    'created': '2024-01-15 10:00:00',
                    'modified': '2024-01-15 14:30:00',
                    'pick_date': '2024-01-15',
                    'deliver_date': '2024-01-18',
                    'customer_fullname': 'Nguyễn Văn A',
                    'customer_tel': '0987654321',
                    'address': 'Địa chỉ giao hàng',
                    'storage_day': 0,
                    'ship_money': 22000,
                    'insurance': 1200
                },
                'message': '...'
            }
        """
        url = f"{self.base_url}/shipment/v2/{label}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            data = response.json()
            
            if response.status_code == 200 and data.get('success'):
                return {
                    'success': True,
                    'order': data['order'],
                    'message': 'Lấy thông tin thành công'
                }
            else:
                return {
                    'success': False,
                    'message': data.get('message', 'Không tìm thấy đơn hàng')
                }
                
        except requests.RequestException as e:
            return {
                'success': False,
                'message': f'Lỗi kết nối GHTK: {str(e)}'
            }
    
    def get_label_url(self, label: str) -> str:
        """
        Lấy URL in tem vận đơn (PDF)
        
        Args:
            label: Mã vận đơn GHTK
        
        Returns:
            URL của file PDF tem vận đơn
        """
        return f"{self.base_url}/label/{label}"
    
    def convert_ghtk_status_to_internal(self, ghtk_status: int) -> str:
        """
        Chuyển đổi status code của GHTK sang status nội bộ
        
        GHTK Status:
        -1: Hủy đơn hàng
        1: Chưa tiếp nhận
        2: Đã tiếp nhận
        3: Đã lấy hàng/Đã nhập kho
        4: Đã điều phối giao hàng/Đang giao hàng
        5: Đã giao hàng/Chưa đối soát
        6: Đã đối soát
        7: Không lấy được hàng
        8: Hoãn lấy hàng
        9: Không giao được hàng
        10: Delay giao hàng
        11: Đã đối soát công nợ trả hàng
        12: Đã điều phối lấy hàng/Đang lấy hàng
        13: Đơn hàng bồi hoàn
        20: Đang trả hàng (COD cầm hàng đi trả)
        21: Đã trả hàng (COD đã trả xong hàng)
        123: Shipper báo đã lấy hàng
        """
        status_map = {
            -1: 'cancelled',
            1: 'pending',
            2: 'pending',
            3: 'picked',
            4: 'shipped',
            5: 'delivered',
            6: 'delivered',
            7: 'failed',
            8: 'pending',
            9: 'failed',
            10: 'shipped',
            11: 'delivered',
            12: 'picked',
            13: 'failed',
            20: 'shipped',
            21: 'delivered',
            123: 'picked'
        }
        return status_map.get(ghtk_status, 'pending')


# Hàm tiện ích
def get_ghtk_service(is_production: bool = True) -> GHTKService:
    """
    Factory function để tạo GHTK service instance
    
    Usage:
        ghtk = get_ghtk_service()
        result = ghtk.calculate_fee(...)
    
    Note: Mặc định dùng production API (is_production=True)
    """
    return GHTKService(is_production=is_production)
