class ShippingMethodModel {
  final String id;
  final String name;
  final String description;
  final double fee;
  final String estimatedDays;
  final String icon;
  final bool isFreeShip;

  ShippingMethodModel({
    required this.id,
    required this.name,
    required this.description,
    required this.fee,
    required this.estimatedDays,
    required this.icon,
    this.isFreeShip = false,
  });

  factory ShippingMethodModel.fromJson(Map<String, dynamic> json) {
    return ShippingMethodModel(
      id: json['id'] ?? '',
      name: json['name'] ?? '',
      description: json['description'] ?? '',
      fee: (json['fee'] ?? 0).toDouble(),
      estimatedDays: json['estimated_days'] ?? '',
      icon: json['icon'] ?? 'truck',
      isFreeShip: json['is_freeship'] ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'description': description,
      'fee': fee,
      'estimated_days': estimatedDays,
      'icon': icon,
      'is_freeship': isFreeShip,
    };
  }
}
