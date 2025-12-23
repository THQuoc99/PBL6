import 'package:intl/intl.dart';

/// Model cho Return Item - sản phẩm được trả
class ReturnItemModel {
  final int? returnItemId;
  final int orderItemId;
  final String productName;
  final int quantity;
  final double priceAtOrder;
  final String? productImage;
  final Map<String, dynamic> attributes;

  ReturnItemModel({
    this.returnItemId,
    required this.orderItemId,
    required this.productName,
    required this.quantity,
    required this.priceAtOrder,
    this.productImage,
    this.attributes = const {},
  });

  factory ReturnItemModel.fromJson(Map<String, dynamic> json) {
    return ReturnItemModel(
      returnItemId: json['return_item_id'],
      orderItemId: json['order_item'] ?? json['order_item_id'] ?? 0,
      productName: json['product_name'] ?? 'Sản phẩm',
      quantity: json['quantity'] ?? 0,
      priceAtOrder: double.tryParse(json['price_at_order']?.toString() ?? '0') ?? 0.0,
      productImage: json['product_image'],
      attributes: json['attributes'] is Map 
          ? Map<String, dynamic>.from(json['attributes']) 
          : {},
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'order_item_id': orderItemId,
      'quantity': quantity,
    };
  }
}

/// Model cho Return Image - ảnh chứng minh
class ReturnImageModel {
  final int? imageId;
  final String imageUrl;
  final DateTime? uploadedAt;

  ReturnImageModel({
    this.imageId,
    required this.imageUrl,
    this.uploadedAt,
  });

  factory ReturnImageModel.fromJson(Map<String, dynamic> json) {
    return ReturnImageModel(
      imageId: json['image_id'],
      imageUrl: json['image'] ?? '',
      uploadedAt: json['uploaded_at'] != null 
          ? DateTime.parse(json['uploaded_at']) 
          : null,
    );
  }
}

/// Model cho Return Tracking - lịch sử xử lý
class ReturnTrackingModel {
  final int trackingId;
  final String status;
  final String? note;
  final DateTime createdAt;
  final String? createdBy;

  ReturnTrackingModel({
    required this.trackingId,
    required this.status,
    this.note,
    required this.createdAt,
    this.createdBy,
  });

  factory ReturnTrackingModel.fromJson(Map<String, dynamic> json) {
    return ReturnTrackingModel(
      trackingId: json['tracking_id'] ?? 0,
      status: json['status'] ?? '',
      note: json['note'],
      createdAt: DateTime.parse(json['created_at']),
      createdBy: json['created_by']?.toString(),
    );
  }

  String get statusDisplay {
    const statusMap = {
      'pending': 'Chờ duyệt',
      'approved': 'Đã duyệt',
      'rejected': 'Từ chối',
      'shipping_back': 'Đang gửi về',
      'received': 'Đã nhận hàng',
      'completed': 'Hoàn thành',
      'cancelled': 'Đã hủy',
    };
    return statusMap[status] ?? status;
  }
}

/// Model chính cho Return Request
class ReturnRequestModel {
  final int returnId;
  final int orderId;
  final int? subOrderId;
  final String returnType; // refund | exchange
  final String reason;
  final String description;
  final double refundAmount;
  final String status;
  final String? trackingCode;
  final String? shopResponse;
  final DateTime createdAt;
  final DateTime? completedAt;
  final List<ReturnItemModel> items;
  final List<ReturnImageModel> images;
  final List<ReturnTrackingModel> trackingHistory;

  ReturnRequestModel({
    required this.returnId,
    required this.orderId,
    this.subOrderId,
    required this.returnType,
    required this.reason,
    required this.description,
    required this.refundAmount,
    required this.status,
    this.trackingCode,
    this.shopResponse,
    required this.createdAt,
    this.completedAt,
    this.items = const [],
    this.images = const [],
    this.trackingHistory = const [],
  });

  factory ReturnRequestModel.fromJson(Map<String, dynamic> json) {
    return ReturnRequestModel(
      returnId: json['return_id'] ?? 0,
      orderId: json['order'] ?? json['order_id'] ?? 0,
      subOrderId: json['sub_order'],
      returnType: json['return_type'] ?? 'refund',
      reason: json['reason'] ?? '',
      description: json['description'] ?? '',
      refundAmount: double.tryParse(json['refund_amount']?.toString() ?? '0') ?? 0.0,
      status: json['status'] ?? 'pending',
      trackingCode: json['tracking_code'],
      shopResponse: json['shop_response'],
      createdAt: DateTime.parse(json['created_at']),
      completedAt: json['completed_at'] != null 
          ? DateTime.parse(json['completed_at']) 
          : null,
      items: (json['items'] as List?)
          ?.map((item) => ReturnItemModel.fromJson(item))
          .toList() ?? [],
      images: (json['images'] as List?)
          ?.map((img) => ReturnImageModel.fromJson(img))
          .toList() ?? [],
      trackingHistory: (json['tracking_history'] as List?)
          ?.map((track) => ReturnTrackingModel.fromJson(track))
          .toList() ?? [],
    );
  }

  String get statusDisplay {
    const statusMap = {
      'pending': 'Chờ duyệt',
      'approved': 'Đã duyệt - Chờ gửi hàng',
      'rejected': 'Từ chối',
      'shipping_back': 'Đang gửi hàng về',
      'received': 'Shop đã nhận hàng',
      'completed': 'Hoàn thành',
      'cancelled': 'Đã hủy',
    };
    return statusMap[status] ?? status;
  }

  String get reasonDisplay {
    const reasonMap = {
      'wrong_item': 'Giao sai sản phẩm',
      'damaged': 'Hàng bị hỏng/lỗi',
      'not_as_described': 'Không đúng mô tả',
      'size_issue': 'Không vừa size',
      'changed_mind': 'Đổi ý không muốn mua',
      'quality_issue': 'Chất lượng kém',
      'other': 'Lý do khác',
    };
    return reasonMap[reason] ?? reason;
  }

  String get returnTypeDisplay {
    return returnType == 'refund' ? 'Trả hàng hoàn tiền' : 'Đổi hàng';
  }

  String get formattedCreatedAt {
    return DateFormat('dd/MM/yyyy HH:mm').format(createdAt);
  }

  String? get formattedCompletedAt {
    return completedAt != null 
        ? DateFormat('dd/MM/yyyy HH:mm').format(completedAt!) 
        : null;
  }

  bool get canCancel => status == 'pending';
  bool get canUpdateTracking => status == 'approved';
  bool get isCompleted => status == 'completed';
  bool get isRejected => status == 'rejected';
  bool get isCancelled => status == 'cancelled';
}
