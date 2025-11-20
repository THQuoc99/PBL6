class ProvinceModel {
  final int id;
  final String name;
  ProvinceModel({required this.id, required this.name});
  factory ProvinceModel.fromJson(Map<String, dynamic> json) => 
      ProvinceModel(id: json['province_id'], name: json['name']);
}

class DistrictModel {
  final int id;
  final String name;
  DistrictModel({required this.id, required this.name});
  factory DistrictModel.fromJson(Map<String, dynamic> json) => 
      DistrictModel(id: json['district_id'], name: json['name']);
}

class WardModel {
  final int id;
  final String name;
  WardModel({required this.id, required this.name});
  factory WardModel.fromJson(Map<String, dynamic> json) => 
      WardModel(id: json['ward_id'], name: json['name']);
}

class HamletModel {
  final int id;
  final String name;
  HamletModel({required this.id, required this.name});
  factory HamletModel.fromJson(Map<String, dynamic> json) => 
      HamletModel(id: json['hamlet_id'], name: json['name']);
}