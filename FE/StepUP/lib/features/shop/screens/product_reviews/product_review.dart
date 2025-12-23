import 'package:flutter/material.dart';
import 'package:flutter_app/constants/sizes.dart';
import 'package:flutter_app/widgets/appbar/appbar.dart';

import 'package:flutter_app/shop/controllers/review_controller.dart';
import 'package:flutter_app/shop/models/review_model.dart';
import './widgets/rating_progress_indicator.dart';
import './widgets/user_review_card.dart';
import 'package:flutter_app/features/shop/screens/product_reviews/review_form.dart';

class ProductReviewScreen extends StatefulWidget {
  final int productId;
  const ProductReviewScreen({super.key, required this.productId});

  @override
  State<ProductReviewScreen> createState() => _ProductReviewScreenState();
}

class _ProductReviewScreenState extends State<ProductReviewScreen> {
  final ReviewController _controller = ReviewController();
  late Future<List<ReviewModel>> _futureReviews;

  @override
  void initState() {
    super.initState();
    _loadReviews();
  }

  void _loadReviews() {
    _futureReviews = _controller.fetchReviews(widget.productId);
    setState(() {});
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
                      itemBuilder: (_, i) => UserReviewCard(review: reviews[i]),
                    ),
                ],
              ),
            ),
          );
        },
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () async {
          final result = await Navigator.of(context).push<bool>(
            MaterialPageRoute(builder: (_) => ReviewFormScreen(productId: widget.productId)),
          );
          if (result == true) {
            _loadReviews(); // refresh immediately
            ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Đã gửi đánh giá')));
          }
        },
        icon: const Icon(Icons.rate_review),
        label: const Text('Viết đánh giá'),
      ),
    );
  }
}