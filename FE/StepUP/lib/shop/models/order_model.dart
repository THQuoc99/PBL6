import 'package:intl/intl.dart';
import 'address_model.dart'; 

class OrderItemModel {
  final int itemId;
  final int productId; // thêm
  final int? variantId; // thêm (có thể null)
  final String productName;
  final int quantity;
  final double priceAtOrder;
  final String? productImage;
  final Map<String, dynamic> attributes;

  OrderItemModel({
    required this.itemId,
    required this.productId,
    this.variantId,
    required this.productName,
    required this.quantity,
    required this.priceAtOrder,
    this.productImage,
    this.attributes = const {},
  });

  factory OrderItemModel.fromJson(Map<String, dynamic> json) {
    // productId: ưu tiên trường trực tiếp, nếu không có tìm trong variant->product
    int parsedProductId = json['product_id'] ?? 0;
    int? parsedVariantId;

    if ((parsedProductId == 0) && json['variant'] != null) {
      final variant = json['variant'];
      // variant may contain product or product_id fields
      if (variant is Map) {
        if (variant['product'] != null && variant['product'] is Map) {
          parsedProductId = variant['product']['product_id'] ?? variant['product']['id'] ?? parsedProductId;
        }
        parsedVariantId = variant['variant_id'] ?? variant['id'] ?? parsedVariantId;
      }
    }

    // Fallback: sometimes API returns product object at top-level
    if (parsedProductId == 0 && json['product'] != null && json['product'] is Map) {
      parsedProductId = json['product']['product_id'] ?? json['product']['id'] ?? parsedProductId;
    }

    String pName = json['product_name'] ?? '';
    if (pName.isEmpty && json['variant'] != null && json['variant']['product'] != null) {
       pName = json['variant']['product']['name'] ?? 'Sản phẩm';
    }

    // Xử lý URL ảnh sản phẩm
    String? imgUrl = json['product_image'];
    if (imgUrl != null && !imgUrl.startsWith('http')) {
        if (imgUrl.startsWith('/')) {
            imgUrl = 'http://10.0.2.2:8000$imgUrl';
        } else {
            imgUrl = 'http://10.0.2.2:8000/$imgUrl';
        }
    }

    return OrderItemModel(
      itemId: json['item_id'] ?? json['id'] ?? 0,
      productId: parsedProductId,
      variantId: parsedVariantId,
      productName: pName,
      quantity: json['quantity'] ?? 0,
      priceAtOrder: double.tryParse(json['price_at_order'].toString()) ?? 0.0,
      productImage: imgUrl,
      attributes: json['attributes'] is Map ? Map<String, dynamic>.from(json['attributes']) : {},
    );
  }
}

class SubOrderModel {
  final int subOrderId;
  final String storeName;
  final double subTotal;
  final String status;
  final String? trackingNumber;
  final List<OrderItemModel> items;

  SubOrderModel({
    required this.subOrderId,
    required this.storeName,
    required this.subTotal,
    required this.status,
    this.trackingNumber,
    required this.items,
  });

  factory SubOrderModel.fromJson(Map<String, dynamic> json) {
    List<OrderItemModel> itemsList = [];
    if (json['items'] != null && json['items'] is List) {
      itemsList = (json['items'] as List).map((i) => OrderItemModel.fromJson(i)).toList();
    }

    return SubOrderModel(
      subOrderId: json['sub_order_id'] ?? 0,
      storeName: json['store_name'] ?? 'Shop',
      subTotal: double.tryParse(json['subtotal'].toString()) ?? 0.0,
      status: json['status'] ?? 'pending',
      trackingNumber: json['tracking_number'],
      items: itemsList,
    );
  }
}

class OrderModel {
  final int id;
  final String status;
  final String paymentStatus; 
  final double totalAmount;
  final double shippingFee;
  // [NEW] Thêm trường giảm giá sàn để hiển thị đúng
  final double discountAmount; 
  final DateTime orderDate;
  final String paymentMethod;
  final AddressModel? address;
  final List<SubOrderModel> subOrders;
  final bool hasReturnRequest; 
  final String? notes; 

  OrderModel({
    required this.id,
    required this.status,
    required this.paymentStatus,
    required this.totalAmount,
    required this.orderDate,
    this.shippingFee = 0.0,
    this.discountAmount = 0.0, // Default
    this.paymentMethod = 'COD',
    this.address,
    this.subOrders = const [],
    this.hasReturnRequest = false,
    this.notes,
  });

  String get orderStatusText {
    switch (status.toLowerCase()) {
      case 'pending': return 'Chờ xác nhận';
      case 'processing': return 'Đang xử lý';
      case 'shipped': return 'Đang giao hàng';
      case 'completed': return 'Hoàn thành';
      case 'cancelled': return 'Đã hủy';
      default: return status;
    }
  }

  String get formattedOrderDate {
    try {
      return DateFormat('dd/MM/yyyy HH:mm').format(orderDate);
    } catch (e) {
      return orderDate.toString();
    }
  }

  factory OrderModel.fromJson(Map<String, dynamic> json) {
    List<SubOrderModel> subOrdersList = [];
    if (json['sub_orders'] != null && json['sub_orders'] is List) {
      subOrdersList = (json['sub_orders'] as List)
          .map((sub) => SubOrderModel.fromJson(sub))
          .toList();
    }

    return OrderModel(
      id: json['order_id'] ?? 0,
      status: json['status'] ?? 'pending',
      paymentStatus: json['payment_status'] ?? 'pending',
      totalAmount: double.tryParse(json['total_amount'].toString()) ?? 0.0,
      shippingFee: double.tryParse(json['shipping_fee']?.toString() ?? '0') ?? 0.0,
      // [NEW] Parse discountAmount
      discountAmount: double.tryParse(json['discount_amount']?.toString() ?? '0') ?? 0.0,
      orderDate: DateTime.tryParse(json['created_at'] ?? '') ?? DateTime.now(),
      paymentMethod: json['payment_method'] ?? 'COD',
      address: json['address'] != null ? AddressModel.fromJson(json['address']) : null,
      subOrders: subOrdersList,
      hasReturnRequest: json['has_return_request'] ?? false,
      notes: json['notes'],
    );
  }
}