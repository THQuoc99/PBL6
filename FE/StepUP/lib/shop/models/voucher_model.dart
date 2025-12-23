class VoucherModel {
  final int id;
  final String code;
  final String scope; // 'store', 'platform', 'shipping'
  
  // [QUAN TRỌNG] Đổi storeId sang String để khớp với ID của Shop (UUID)
  final String? storeId; 
  final String? storeName;
  
  final String discountType; // 'percent', 'fixed'
  final double discountValue;
  final double? maxDiscount;
  final double minOrderAmount;
  
  final String startDate;
  final String endDate;
  
  final bool isFreeShipping;
  final int perUserLimit;
  final String paymentMethodRequired; // 'all', 'COD', 'VNPAY', 'PAYPAL'
  
  // UI Helpers
  final bool isSaved;   
  final bool isUsable;  
  final String? reason; 

  VoucherModel({
    required this.id,
    required this.code,
    required this.scope,
    this.storeId,
    this.storeName,
    required this.discountType,
    required this.discountValue,
    this.maxDiscount,
    this.minOrderAmount = 0.0,
    required this.startDate,
    required this.endDate,
    this.isFreeShipping = false,
    this.perUserLimit = 1,
    this.paymentMethodRequired = 'all',
    this.isSaved = false,
    this.isUsable = true,
    this.reason,
  });

  factory VoucherModel.fromJson(Map<String, dynamic> json) {
    double toDouble(dynamic val) {
      if (val == null) return 0.0;
      if (val is int) return val.toDouble();
      return double.tryParse(val.toString()) ?? 0.0;
    }

    int toInt(dynamic val) {
      if (val == null) return 0;
      if (val is int) return val;
      return int.tryParse(val.toString()) ?? 0;
    }

    return VoucherModel(
      id: toInt(json['voucher_id'] ?? json['id']),
      code: json['code']?.toString() ?? '',
      scope: json['scope']?.toString() ?? json['type']?.toString() ?? 'platform',
      
      // [FIX] Lấy store_id dưới dạng String
      storeId: json['store_id']?.toString() ?? (json['store']?.toString()),
      storeName: json['store_name']?.toString(),

      discountType: json['discount_type']?.toString() ?? 'percent',
      discountValue: toDouble(json['discount_value']),
      maxDiscount: json['max_discount'] != null ? toDouble(json['max_discount']) : null,
      minOrderAmount: toDouble(json['min_order_amount']),
      
      startDate: json['start_date']?.toString() ?? '',
      endDate: json['end_date']?.toString() ?? '',
      
      isFreeShipping: json['is_free_shipping'] == true,
      perUserLimit: toInt(json['per_user_limit']),
      paymentMethodRequired: json['payment_method_required']?.toString() ?? 'all',
      
      isSaved: json['is_saved'] == true,
      isUsable: json['is_usable'] != false,
      reason: json['reason']?.toString(),
    );
  }

  String get discountString {
    if (isFreeShipping) return "Freeship";
    if (discountType == 'fixed') {
      return "-${discountValue.toStringAsFixed(0)}đ";
    }
    return "-${discountValue.toStringAsFixed(0)}%";
  }
}