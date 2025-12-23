from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db import transaction
from decimal import Decimal

from .models import ReturnRequest, ReturnItem, ReturnImage, ReturnTracking
from .serializers import (
    ReturnRequestSerializer, 
    CreateReturnRequestSerializer
)
from .permissions import IsShopOwner, IsBuyerOrShopOwner
from orders.models import Order, SubOrder, OrderItem


class ReturnRequestViewSet(viewsets.ModelViewSet):
    """
    API Quản lý yêu cầu trả hàng
    
    - GET /api/returns/ - Danh sách yêu cầu của user
    - POST /api/returns/create/ - Tạo yêu cầu mới
    - GET /api/returns/{id}/ - Chi tiết yêu cầu
    - POST /api/returns/{id}/cancel/ - Hủy yêu cầu
    - POST /api/returns/{id}/update_tracking/ - Cập nhật mã vận đơn
    """
    
    serializer_class = ReturnRequestSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        """
        Shop APIs cần IsShopOwner permission
        Các APIs khác chỉ cần IsAuthenticated
        """
        if self.action in ['shop_approve', 'shop_reject', 'shop_mark_received', 'shop_complete', 'shop_list']:
            return [IsAuthenticated(), IsShopOwner()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        """Chỉ xem yêu cầu của chính mình"""
        return ReturnRequest.objects.filter(buyer=self.request.user).select_related(
            'order', 'sub_order', 'buyer'
        ).prefetch_related('items', 'images', 'tracking_history')
    
    @action(detail=False, methods=['post'])
    def create_return(self, request):
        """
        Tạo yêu cầu trả hàng mới
        
        Body:
        {
            "order_id": 123,
            "sub_order_id": 456,  // optional
            "return_type": "refund",
            "reason": "damaged",
            "description": "Sản phẩm bị rách...",
            "items": [
                {"order_item_id": 1, "quantity": 2}
            ],
            "images": [file1, file2]  // multipart/form-data
        }
        """
        # Parse multipart form data - unwrap single-value lists (except files)
        import json
        from django.core.files.uploadedfile import UploadedFile
        
        request_data = {}
        
        for key, value in request.data.items():
            # Skip images - they should be handled separately
            if key == 'images':
                continue
                
            # If it's a list with one element (and not a file), extract it
            if isinstance(value, list) and len(value) == 1:
                request_data[key] = value[0]
            else:
                request_data[key] = value
        
        # Handle images from request.FILES
        if request.FILES:
            images = request.FILES.getlist('images')
            if images:
                request_data['images'] = images
        
        # Parse items from JSON string to list
        if 'items' in request_data and isinstance(request_data['items'], str):
            try:
                request_data['items'] = json.loads(request_data['items'])
            except json.JSONDecodeError:
                return Response({
                    'error': 'Invalid items format. Expected JSON array.'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = CreateReturnRequestSerializer(data=request_data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        try:
            # 1. Validate Order
            order = Order.objects.get(order_id=data['order_id'], buyer=request.user)
            
            if order.status != 'completed':
                return Response({
                    'error': 'Chỉ có thể trả hàng cho đơn hàng đã hoàn thành'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 2. Validate SubOrder (if provided)
            sub_order = None
            if data.get('sub_order_id'):
                sub_order = SubOrder.objects.get(
                    sub_order_id=data['sub_order_id'],
                    order=order
                )
                
                # Check 7 days policy
                if sub_order.delivered_at:
                    days_since = (timezone.now() - sub_order.delivered_at).days
                    if days_since > 7:
                        return Response({
                            'error': 'Đã quá thời gian trả hàng (7 ngày kể từ khi nhận hàng)'
                        }, status=status.HTTP_400_BAD_REQUEST)
            
            # 3. Check existing return request
            existing = ReturnRequest.objects.filter(
                order=order,
                status__in=['pending', 'approved', 'shipping_back', 'received']
            ).exists()
            
            if existing:
                return Response({
                    'error': 'Đơn hàng đã có yêu cầu trả hàng đang xử lý'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 4. Validate items
            items_data = data['items']
            order_items = []
            total_refund = Decimal(0)
            
            for item_data in items_data:
                order_item = OrderItem.objects.get(
                    item_id=item_data['order_item_id'],
                    order=order
                )
                
                # Check if product is returnable
                if not order_item.variant.product.is_returnable:
                    return Response({
                        'error': f'Sản phẩm "{order_item.variant.product.name}" không được phép trả hàng'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                if item_data['quantity'] > order_item.quantity:
                    return Response({
                        'error': f'Số lượng trả vượt quá số lượng đã mua cho sản phẩm {order_item.variant.product.name}'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                order_items.append({
                    'order_item': order_item,
                    'quantity': item_data['quantity']
                })
                
                # Calculate refund amount
                total_refund += order_item.price_at_order * item_data['quantity']
            
            # 5. Create Return Request
            with transaction.atomic():
                return_request = ReturnRequest.objects.create(
                    order=order,
                    sub_order=sub_order,
                    buyer=request.user,
                    return_type=data['return_type'],
                    reason=data['reason'],
                    description=data['description'],
                    refund_amount=total_refund,
                    status='pending'
                )
                
                # Create return items
                for item_info in order_items:
                    ReturnItem.objects.create(
                        return_request=return_request,
                        order_item=item_info['order_item'],
                        quantity=item_info['quantity']
                    )
                
                # Upload images (if any)
                images = request.FILES.getlist('images', [])
                for img in images:
                    ReturnImage.objects.create(
                        return_request=return_request,
                        image=img
                    )
                
                # Create tracking log
                ReturnTracking.objects.create(
                    return_request=return_request,
                    status='pending',
                    note='Yêu cầu trả hàng được tạo',
                    created_by=request.user
                )
            
            serializer = ReturnRequestSerializer(return_request, context={'request': request})
            return Response({
                'success': True,
                'message': 'Tạo yêu cầu trả hàng thành công',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except Order.DoesNotExist:
            return Response({'error': 'Đơn hàng không tồn tại'}, status=status.HTTP_404_NOT_FOUND)
        except SubOrder.DoesNotExist:
            return Response({'error': 'SubOrder không tồn tại'}, status=status.HTTP_404_NOT_FOUND)
        except OrderItem.DoesNotExist:
            return Response({'error': 'Sản phẩm không tồn tại trong đơn hàng'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Hủy yêu cầu trả hàng (chỉ khi status = pending)"""
        return_request = self.get_object()
        
        if return_request.status != 'pending':
            return Response({
                'error': 'Chỉ có thể hủy yêu cầu đang chờ duyệt'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return_request.status = 'cancelled'
        return_request.save()
        
        # Log
        ReturnTracking.objects.create(
            return_request=return_request,
            status='cancelled',
            note='Khách hàng hủy yêu cầu',
            created_by=request.user
        )
        
        return Response({
            'success': True,
            'message': 'Đã hủy yêu cầu trả hàng'
        })
    
    @action(detail=True, methods=['post'])
    def update_tracking(self, request, pk=None):
        """
        Cập nhật mã vận đơn trả hàng (sau khi shop approve)
        
        Body: {"tracking_code": "GHTK123456"}
        """
        return_request = self.get_object()
        
        if return_request.status != 'approved':
            return Response({
                'error': 'Yêu cầu chưa được duyệt'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        tracking_code = request.data.get('tracking_code')
        if not tracking_code:
            return Response({'error': 'Vui lòng cung cấp mã vận đơn'}, status=status.HTTP_400_BAD_REQUEST)
        
        return_request.return_tracking_code = tracking_code
        return_request.status = 'shipping_back'
        return_request.save()
        
        # Log
        ReturnTracking.objects.create(
            return_request=return_request,
            status='shipping_back',
            note=f'Khách hàng đã gửi hàng về. Mã vận đơn: {tracking_code}',
            created_by=request.user
        )
        
        return Response({
            'success': True,
            'message': 'Đã cập nhật mã vận đơn'
        })
    
    # ============== SHOP APIs ==============
    
    @action(detail=True, methods=['post'], url_path='shop/approve')
    def shop_approve(self, request, pk=None):
        """
        Shop duyệt yêu cầu trả hàng
        
        Body: {
            "response": "Đồng ý cho trả hàng..."
        }
        """
        return_request = self.get_object()
        
        if return_request.status != 'pending':
            return Response({
                'error': 'Chỉ có thể duyệt yêu cầu đang chờ duyệt'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        shop_response = request.data.get('response', '')
        
        return_request.status = 'approved'
        return_request.shop_response = shop_response
        return_request.approved_at = timezone.now()
        return_request.save()
        
        # Log
        ReturnTracking.objects.create(
            return_request=return_request,
            status='approved',
            note=f'Shop đã duyệt yêu cầu. {shop_response}',
            created_by=request.user
        )
        
        # TODO: Send notification to buyer
        
        return Response({
            'success': True,
            'message': 'Đã duyệt yêu cầu trả hàng'
        })
    
    @action(detail=True, methods=['post'], url_path='shop/reject')
    def shop_reject(self, request, pk=None):
        """
        Shop từ chối yêu cầu trả hàng
        
        Body: {
            "reason": "Sản phẩm đã qua sử dụng..."
        }
        """
        return_request = self.get_object()
        
        if return_request.status != 'pending':
            return Response({
                'error': 'Chỉ có thể từ chối yêu cầu đang chờ duyệt'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        reject_reason = request.data.get('reason', '')
        
        if not reject_reason:
            return Response({
                'error': 'Vui lòng cung cấp lý do từ chối'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return_request.status = 'rejected'
        return_request.reject_reason = reject_reason
        return_request.save()
        
        # Log
        ReturnTracking.objects.create(
            return_request=return_request,
            status='rejected',
            note=f'Shop từ chối: {reject_reason}',
            created_by=request.user
        )
        
        # TODO: Send notification to buyer
        
        return Response({
            'success': True,
            'message': 'Đã từ chối yêu cầu trả hàng'
        })
    
    @action(detail=True, methods=['post'], url_path='shop/mark-received')
    def shop_mark_received(self, request, pk=None):
        """
        Shop đánh dấu đã nhận hàng trả về
        
        Body: {
            "note": "Hàng còn nguyên vẹn...",
            "images": [file1, file2]  // optional
        }
        """
        return_request = self.get_object()
        
        if return_request.status != 'shipping_back':
            return Response({
                'error': 'Yêu cầu chưa ở trạng thái đang gửi hàng về'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        note = request.data.get('note', 'Shop đã nhận hàng trả về')
        
        return_request.status = 'received'
        return_request.save()
        
        # Upload images nếu có (ảnh hàng shop nhận được)
        images = request.FILES.getlist('images', [])
        for img in images:
            ReturnImage.objects.create(
                return_request=return_request,
                image=img
            )
        
        # Log
        ReturnTracking.objects.create(
            return_request=return_request,
            status='received',
            note=note,
            created_by=request.user
        )
        
        return Response({
            'success': True,
            'message': 'Đã xác nhận nhận hàng'
        })
    
    @action(detail=True, methods=['post'], url_path='shop/complete')
    def shop_complete(self, request, pk=None):
        """
        Hoàn thành trả hàng (đã hoàn tiền/đổi hàng)
        
        Body: {
            "refund_note": "Đã hoàn tiền vào tài khoản...",
            "refund_transaction_id": "TXN123456"  // optional
        }
        """
        return_request = self.get_object()
        
        if return_request.status != 'received':
            return Response({
                'error': 'Chưa nhận hàng trả về'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        refund_note = request.data.get('refund_note', '')
        transaction_id = request.data.get('refund_transaction_id', '')
        
        # Nếu là exchange - tạo order mới
        if return_request.return_type == 'exchange':
            from orders.models import Order, OrderItem
            from django.db import transaction as db_transaction
            
            # Lấy thông tin từ order gốc
            original_order = return_request.order
            
            with db_transaction.atomic():
                # Tạo order mới với cùng thông tin
                new_order = Order.objects.create(
                    user=original_order.user,
                    phone=original_order.phone,
                    province=original_order.province,
                    district=original_order.district,
                    ward=original_order.ward,
                    address_detail=original_order.address_detail,
                    notes=f"Đổi hàng từ đơn #{original_order.order_id}",
                    status='pending',
                    payment_status='pending',
                    total_amount=0  # Sẽ cập nhật sau
                )
                
                # Copy các items từ return request
                total = 0
                for return_item in return_request.items.all():
                    variant = return_item.order_item.variant
                    price = variant.price
                    quantity = return_item.quantity
                    
                    OrderItem.objects.create(
                        order=new_order,
                        variant=variant,
                        quantity=quantity,
                        price_at_purchase=price
                    )
                    total += price * quantity
                
                new_order.total_amount = total
                new_order.save()
                
                # Link order mới với return request
                return_request.exchange_order = new_order
                return_request.save()
                
                refund_note += f" Đã tạo đơn đổi hàng #{new_order.order_id}"
                # TODO: Gửi notification cho buyer về order mới
                # TODO: Tạo shipment cho order mới
        
        return_request.status = 'completed'
        return_request.completed_at = timezone.now()
        return_request.save()
        
        # Log
        note_text = f'Hoàn thành trả hàng. {refund_note}'
        if transaction_id:
            note_text += f' Transaction ID: {transaction_id}'
        
        ReturnTracking.objects.create(
            return_request=return_request,
            status='completed',
            note=note_text,
            created_by=request.user
        )
        
        # TODO: Auto refund via payment gateway
        # TODO: Send notification to buyer
        
        return Response({
            'success': True,
            'message': 'Đã hoàn thành yêu cầu trả hàng'
        })
    
    @action(detail=False, methods=['get'], url_path='shop/list')
    def shop_list(self, request):
        """
        Danh sách yêu cầu trả hàng cho shop (dựa vào products của shop)
        
        Query params:
        - status: pending, approved, shipping_back, received, completed
        """
        # Filter by shop owner
        # TODO: Khi có Store.owner, uncomment code dưới:
        # from products.models import Product
        # 
        # # Lấy các store mà user sở hữu
        # owned_stores = Store.objects.filter(owner=request.user)
        # 
        # # Lấy return requests có sản phẩm thuộc stores này
        # queryset = ReturnRequest.objects.filter(
        #     items__order_item__variant__product__store__in=owned_stores
        # ).distinct()
        
        # Tạm thời: Admin xem tất cả, user thường không xem được
        if not request.user.is_staff:
            return Response({
                'error': 'Chức năng này chỉ dành cho shop owner. Vui lòng liên hệ admin để được cấp quyền.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        status_filter = request.query_params.get('status')
        
        queryset = ReturnRequest.objects.all()
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        queryset = queryset.select_related(
            'order', 'sub_order', 'buyer'
        ).prefetch_related('items', 'images', 'tracking_history').order_by('-created_at')
        
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data
        })
