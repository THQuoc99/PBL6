class AddressModel {
  final int? addressId; 
  final String name; 
  final String phoneNumber;
  final String detail; 
  
  final String province; 
  final String ward;
  final String hamlet; 
  
  final bool isDefault;

  AddressModel({
    this.addressId,
    required this.name,
    required this.phoneNumber,
    required this.detail,
    required this.province,
    required this.ward,
    this.hamlet = '',
    this.isDefault = false,
  });

  // ✅ THÊM GETTER NÀY ĐỂ FIX LỖI UI
  // Giúp UI gọi address.id được (nếu null thì trả về 0 để tránh crash)
  int get id => addressId ?? 0;

  factory AddressModel.fromJson(Map<String, dynamic> json) {
    return AddressModel(
      addressId: json['address_id'],
      name: json['name'] ?? '', 
      phoneNumber: json['phone'] ?? '', 
      detail: json['detail'] ?? '',
      province: json['province'] ?? '',
      ward: json['ward'] ?? '',
      hamlet: json['hamlet'] ?? '',
      isDefault: json['is_default'] ?? false,
    );
  }
  
  Map<String, dynamic> toJson() {
    return {
      'detail': detail,
      'province': province, 
      'ward': ward,
      'hamlet': hamlet,
      'is_default': isDefault,
      'name': name,
      'phone': phoneNumber, 
    };
  }
  
  String get fullAddress {
    List<String> parts = [detail, hamlet, ward, province];
    return parts.where((p) => p.isNotEmpty).join(', ');
  }
}