class VoucherModel {
  final int id;
  final String code;
  final String title;
  final String description;
  final String discountType; // 'percent' or 'fixed'
  final double discountValue;
  final double? maxDiscount;
  final String startDate;
  final String endDate;
  final String type;
  final bool isFreeShipping;
  final List<int>? applicableStores;
  final List<int>? appliesToProducts;
  final List<int>? appliesToCategories;
  final double? minOrderAmount;
  final int? perUserLimit;

  VoucherModel({
    required this.id,
    required this.code,
    required this.title,
    required this.description,
    required this.discountType,
    required this.discountValue,
    this.maxDiscount,
    required this.startDate,
    required this.endDate,
    required this.type,
    this.isFreeShipping = false,
    this.applicableStores,
    this.appliesToProducts,
    this.appliesToCategories,
    this.minOrderAmount,
    this.perUserLimit,
  });

  factory VoucherModel.fromJson(Map<String, dynamic> json) {
    double? parseDouble(dynamic v) {
      if (v == null) return null;
      if (v is num) return v.toDouble();
      final s = v.toString();
      return double.tryParse(s);
    }

    int? parseInt(dynamic v) {
      if (v == null) return null;
      if (v is int) return v;
      final s = v.toString();
      return int.tryParse(s);
    }

    List<int>? parseIntList(dynamic v) {
      if (v == null) return null;
      if (v is List) {
        return v.map((e) => parseInt(e) ?? 0).toList();
      }
      // if backend returns a comma-separated string
      if (v is String) {
        return v.split(',').map((e) => int.tryParse(e.trim()) ?? 0).toList();
      }
      return null;
    }

    return VoucherModel(
      id: parseInt(json['voucher_id'] ?? json['id']) ?? 0,
      code: json['code']?.toString() ?? '',
      title: json['title']?.toString() ?? json['name']?.toString() ?? json['description']?.toString() ?? '',
      description: json['description']?.toString() ?? '',
      discountType: json['discount_type']?.toString() ?? 'percent',
      discountValue: parseDouble(json['discount_value']) ?? 0.0,
      maxDiscount: parseDouble(json['max_discount']),
      startDate: json['start_date']?.toString() ?? '',
      endDate: json['end_date']?.toString() ?? '',
      type: json['type']?.toString() ?? 'platform',
      isFreeShipping: json['is_free_shipping'] == true || json['is_free_shipping']?.toString() == 'true',
      applicableStores: parseIntList(json['applicable_stores']),
      appliesToProducts: parseIntList(json['applies_to_products']),
      appliesToCategories: parseIntList(json['applies_to_categories']),
      minOrderAmount: parseDouble(json['min_order_amount']),
      perUserLimit: parseInt(json['per_user_limit']),
    );
  }
}
