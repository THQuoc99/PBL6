import 'package:flutter/material.dart';
import 'package:flutter_app/constants/sizes.dart';
import 'package:flutter_app/utils/helpers/auth_helper.dart';
import 'package:flutter_app/widgets/appbar/appbar.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;

import 'package:flutter_app/shop/controllers/review_controller.dart';
import 'package:flutter_app/shop/models/review_model.dart';
import './widgets/rating_progress_indicator.dart';
import './widgets/user_review_card.dart';
import 'package:flutter_app/features/shop/screens/product_reviews/review_form.dart';
import 'package:get/get.dart';
import 'package:flutter_app/shop/controllers/user_controller.dart';

class ProductReviewScreen extends StatefulWidget {
  final int productId;
  const ProductReviewScreen({super.key, required this.productId});

  @override
  State<ProductReviewScreen> createState() => _ProductReviewScreenState();
}

class _ProductReviewScreenState extends State<ProductReviewScreen> {
  final ReviewController _controller = ReviewController();
  late Future<List<ReviewModel>> _futureReviews;

  bool _eligible = false;
  bool _alreadyReviewed = false;

  final UserController _userCtrl = Get.find<UserController>();

  @override
  void initState() {
    super.initState();
    // Khởi tạo ngay để tránh LateInitializationError
    _futureReviews = _controller.fetchReviews(widget.productId);
    _loadReviews(); // cập nhật eligible / alreadyReviewed bất đồng bộ
  }

  Future<void> _loadReviews() async {
    try {
      // Lấy danh sách thực sự để kiểm tra user đã review chưa
      final reviews = await _controller.fetchReviews(widget.productId);

      // Update future để đảm bảo UI có dữ liệu mới (nếu muốn)
      _futureReviews = Future.value(reviews);

      final fullname = Get.find<UserController>().fullName.value;
      _alreadyReviewed = reviews.any((r) => r.userName == fullname);

      _eligible = await _checkEligible(widget.productId);
    } catch (_) {
      // Nếu lỗi, giữ future cũ (đã khởi tạo) và reset flags
      _eligible = false;
      _alreadyReviewed = false;
    }
    if (mounted) setState(() {});
  }

  Future<bool> _checkEligible(int productId) async {
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('token');
    if (token == null) return false;
    final resp = await http.get(Uri.parse('http://10.0.2.2:8000/api/reviews/eligibility/?product_id=$productId'), headers: {'Authorization':'Bearer $token'});
    if (resp.statusCode==200) {
      final data = json.decode(resp.body);
      return data['eligible'] == true;
    }
    return false;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: CusAppbar(title: const Text('Đánh giá sản phẩm'), showBackArrow: true),
      body: FutureBuilder<List<ReviewModel>>(
        future: _futureReviews,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return Center(child: Text('Lỗi: ${snapshot.error}'));
          }
          final reviews = snapshot.data ?? [];

          final total = reviews.length;
          final avg = total == 0 ? 0.0 : reviews.map((r) => r.rating).reduce((a, b) => a + b) / total;
          final Map<int, double> distribution = {1:0,2:0,3:0,4:0,5:0};
          if (total > 0) {
            for (var r in reviews) {
              distribution[r.rating] = (distribution[r.rating] ?? 0) + 1;
            }
            for (var i = 1; i <= 5; i++) {
              distribution[i] = (distribution[i] ?? 0) / total;
            }
          }

          return SingleChildScrollView(
            child: Padding(
              padding: const EdgeInsets.all(AppSizes.defaultSpace),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  OverallProductRating(
                    average: avg,
                    distribution: distribution,
                    total: total,
                  ),
                  const SizedBox(height: AppSizes.spaceBtwSections),
                  if (reviews.isEmpty)
                    const Center(child: Text('Chưa có đánh giá nào.'))
                  else
                    ListView.separated(
                      shrinkWrap: true,
                      physics: const NeverScrollableScrollPhysics(),
                      itemCount: reviews.length,
                      separatorBuilder: (_, __) => const Divider(),
                      itemBuilder: (_, i) => UserReviewCard(
                        review: reviews[i],
                        onDeleted: _loadReviews,
                      ),
                    ),
                ],
              ),
            ),
          );
        },
      ),
      floatingActionButton: (_eligible && !_alreadyReviewed)
          ? FloatingActionButton.extended(
              onPressed: () async {
                final ok = await requireLogin(context);
                if (!ok) return;
                final result = await Navigator.of(context).push<bool>(
                  MaterialPageRoute(builder: (_) => ReviewFormScreen(productId: widget.productId)),
                );
                if (result == true) _loadReviews();
              },
              icon: const Icon(Icons.rate_review),
              label: const Text('Viết đánh giá'),
            )
          : null,
    );
  }
}