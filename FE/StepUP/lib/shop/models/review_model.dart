class ReviewModel {
  final int reviewId;
  final String userName;
  final String? userAvatar;
  final int rating;
  final String comment;
  final String createdAt;
  final int helpfulCount;

  // images: list of image URLs returned by backend
  final List<String> images;

  // optional company reply fields
  final String? companyReply;
  final String? companyReplyDate;
  final String? companyName;

  ReviewModel({
    required this.reviewId,
    required this.userName,
    this.userAvatar,
    required this.rating,
    required this.comment,
    required this.createdAt,
    required this.helpfulCount,
    this.images = const [],
    this.companyReply,
    this.companyReplyDate,
    this.companyName,
  });

  factory ReviewModel.fromJson(Map<String, dynamic> json) {
    final imgs = <String>[];
    if (json['images'] is List) {
      for (final it in json['images']) {
        try {
          final url = it['image'];
          if (url != null) imgs.add(url.toString());
        } catch (_) {}
      }
    }

    return ReviewModel(
      reviewId: json['review_id'] ?? 0,
      userName: json['user_name'] ?? 'Ẩn danh',
      userAvatar: json['user_avatar'],
      rating: (json['rating'] ?? 0) is int ? json['rating'] : (json['rating'] ?? 0).toInt(),
      comment: json['comment'] ?? '',
      createdAt: json['created_at'] ?? '',
      helpfulCount: json['helpful_count'] ?? 0,
      images: imgs,
      companyReply: json['company_reply'],
      companyReplyDate: json['company_reply_date'],
      companyName: json['company_name'],
    );
  }
}