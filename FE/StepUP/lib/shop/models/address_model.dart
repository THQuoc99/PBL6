class AddressModel {
  final int id;
  final String name; // Tên người nhận (thường lấy từ User hoặc nhập riêng)
  final String phoneNumber;
  final String street; // detail trong database
  final String ward;
  final String district; // hoặc hamlet/quan/huyen tùy db
  final String city; // province
  final bool isDefault;

  AddressModel({
    required this.id,
    required this.name,
    required this.phoneNumber,
    required this.street,
    required this.ward,
    required this.district,
    required this.city,
    this.isDefault = false,
  });

  // Factory để parse JSON từ Backend
  factory AddressModel.fromJson(Map<String, dynamic> json) {
    return AddressModel(
      id: json['address_id'] ?? json['id'] ?? 0,
      // Nếu API không trả về name/phone riêng cho địa chỉ, dùng fallback hoặc lấy từ user profile
      name: json['name'] ?? 'User', 
      phoneNumber: json['phone'] ?? '',
      street: json['detail'] ?? '',
      // Giả định backend trả về tên (string), nếu trả về ID thì cần map thêm
      ward: json['ward_name'] ?? json['ward']?.toString() ?? '', 
      district: json['district_name'] ?? json['district']?.toString() ?? '',
      city: json['province_name'] ?? json['province']?.toString() ?? '',
      isDefault: json['is_default'] ?? false,
    );
  }
  
  // Getter để hiển thị full địa chỉ
  String get fullAddress => '$street, $ward, $district, $city';
}