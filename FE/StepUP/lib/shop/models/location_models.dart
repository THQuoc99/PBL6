class ProvinceModel {
  final int id;
  final String name;

  ProvinceModel({required this.id, required this.name});

  factory ProvinceModel.fromJson(Map<String, dynamic> json) {
    return ProvinceModel(
      // API OpenVN trả về "code", không phải "id"
      id: json['code'] ?? 0, 
      name: json['name'] ?? '',
    );
  }

  // Bắt buộc phải có để Dropdown hoạt động đúng
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is ProvinceModel && runtimeType == other.runtimeType && id == other.id;

  @override
  int get hashCode => id.hashCode;
  
  @override
  String toString() => name;
}

class DistrictModel {
  final int id;
  final String name;
  final int provinceId;

  DistrictModel({required this.id, required this.name, required this.provinceId});

  factory DistrictModel.fromJson(Map<String, dynamic> json) {
    return DistrictModel(
      id: json['code'] ?? 0,
      name: json['name'] ?? '',
      provinceId: json['province_code'] ?? 0,
    );
  }

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is DistrictModel && runtimeType == other.runtimeType && id == other.id;

  @override
  int get hashCode => id.hashCode;
  
  @override
  String toString() => name;
}

class WardModel {
  final int id;
  final String name;
  final int districtId;

  WardModel({required this.id, required this.name, required this.districtId});

  factory WardModel.fromJson(Map<String, dynamic> json) {
    return WardModel(
      id: json['code'] ?? 0,
      name: json['name'] ?? '',
      districtId: json['district_code'] ?? 0,
    );
  }

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is WardModel && runtimeType == other.runtimeType && id == other.id;

  @override
  int get hashCode => id.hashCode;
  
  @override
  String toString() => name;
}