class AddressStore {
  final int addressId;
  final String province;
  final String ward;
  final String? hamlet;
  final String detail;
  final bool isDefault;

  AddressStore({
    required this.addressId,
    required this.province,
    required this.ward,
    this.hamlet,
    required this.detail,
    required this.isDefault,
  });

  factory AddressStore.fromJson(Map<String, dynamic> json) {
    return AddressStore(
      addressId: json['address_id'] ?? 0,
      province: json['province'] ?? '',
      ward: json['ward'] ?? '',
      hamlet: json['hamlet'],
      detail: json['detail'] ?? '',
      isDefault: json['is_default'] ?? false,
    );
  }

  String get fullAddress {
    List<String> parts = [detail, hamlet ?? '', ward, province];
    return parts.where((p) => p.isNotEmpty).join(', ');
  }
}

class StoreImage {
  final String image;
  final String? title;

  StoreImage({required this.image, this.title});

  factory StoreImage.fromJson(Map<String, dynamic> json) {
    return StoreImage(
      image: json['image'] ?? '',
      title: json['title'],
    );
  }
}

class Store {
  final String storeId;
  final String name;
  final String slug;
  final String description;
  
  final String? avatar;
  final String? coverImage;
  
  final double rating;
  final int followersCount;
  final int productsCount;
  final bool isVerified;
  
  final List<AddressStore> addresses;
  final List<StoreImage> images;
  final bool isFollowing; // Trạng thái user hiện tại có follow không

  Store({
    required this.storeId,
    required this.name,
    required this.slug,
    required this.description,
    this.avatar,
    this.coverImage,
    this.rating = 0.0,
    this.followersCount = 0,
    this.productsCount = 0,
    this.isVerified = false,
    this.addresses = const [],
    this.images = const [],
    this.isFollowing = false,
  });

  factory Store.fromJson(Map<String, dynamic> json) {
    // Parse Address List
    List<AddressStore> addrList = [];
    if (json['addresses'] != null) {
      addrList = (json['addresses'] as List).map((e) => AddressStore.fromJson(e)).toList();
    }

    // Parse Image List
    List<StoreImage> imgList = [];
    if (json['images'] != null) {
      imgList = (json['images'] as List).map((e) => StoreImage.fromJson(e)).toList();
    }

    return Store(
      storeId: json['store_id'] ?? '',
      name: json['name'] ?? 'Unknown Store',
      slug: json['slug'] ?? '',
      description: json['description'] ?? '',
      
      // Backend trả về full URL hoặc path
      avatar: json['avatar'], 
      coverImage: json['cover_image'],
      
      rating: double.tryParse(json['rating']?.toString() ?? '0') ?? 0.0,
      followersCount: json['followers_count'] ?? 0,
      productsCount: json['products_count'] ?? 0,
      isVerified: json['is_verified'] ?? false,
      
      addresses: addrList,
      images: imgList,
      isFollowing: json['is_following'] ?? false,
    );
  }
}