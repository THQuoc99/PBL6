import 'package:flutter/material.dart';
import 'package:flutter_app/common/widgets/ratings/rating_indicator.dart';
import 'package:flutter_app/constants/colors.dart';
import 'package:flutter_app/constants/image_string.dart';
import 'package:flutter_app/constants/sizes.dart';
import 'package:flutter_app/widgets/containers/rounded_container.dart';
import 'package:readmore/readmore.dart';
import 'package:flutter_app/utils/helpers/helper_function.dart';
import 'package:flutter_app/shop/models/review_model.dart';
import 'package:get/get.dart';
import 'package:flutter_app/shop/controllers/user_controller.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:http/http.dart' as http;

class UserReviewCard extends StatelessWidget {
  final ReviewModel review;
  final VoidCallback? onDeleted;
  const UserReviewCard({super.key, required this.review, this.onDeleted});

  Future<void> _deleteReview(BuildContext context) async {
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('token');
    if (token == null) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Vui lòng đăng nhập')));
      return;
    }

    final confirm = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Xóa đánh giá'),
        content: const Text('Bạn có chắc chắn muốn xóa đánh giá của mình?'),
        actions: [
          TextButton(onPressed: () => Navigator.of(ctx).pop(false), child: const Text('Hủy')),
          ElevatedButton(onPressed: () => Navigator.of(ctx).pop(true), child: const Text('Xóa')),
        ],
      ),
    );
    if (confirm != true) return;

    final uri = Uri.parse('http://10.0.2.2:8000/api/reviews/${review.reviewId}/');
    final resp = await http.delete(uri, headers: {'Authorization': 'Bearer $token'});
    if (resp.statusCode == 204 || resp.statusCode == 200) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Xóa đánh giá thành công')));
      }
      if (onDeleted != null) onDeleted!();
    } else {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Lỗi khi xóa: ${resp.body}')));
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final dark = HelperFunction.isDarkMode(context);
    final userCtrl = Get.find<UserController>();
    final bool isMine = userCtrl.fullName.value.isNotEmpty && userCtrl.fullName.value == review.userName;

    return Column(
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Row(
              children: [
                CircleAvatar(
                  radius: 20,
                  backgroundImage: review.userAvatar != null && review.userAvatar!.isNotEmpty
                      ? NetworkImage(review.userAvatar!) as ImageProvider
                      : AssetImage(AppImages.sabrina),
                ),
                const SizedBox(width: AppSizes.spaceBtwItems),
                Text(review.userName, style: Theme.of(context).textTheme.titleLarge),
              ],
            ),
            // Chỉ hiện menu nếu là review của mình
            if (isMine)
              PopupMenuButton<int>(
                onSelected: (v) async {
                  if (v == 1) await _deleteReview(context);
                },
                itemBuilder: (_) => [
                  const PopupMenuItem(value: 1, child: Text('Xóa đánh giá', style: TextStyle(color: Colors.red))),
                ],
                icon: const Icon(Icons.more_vert),
              )
            else
              const SizedBox(width: 40),
          ],
        ),
        const SizedBox(height: AppSizes.spaceBtwItems),
        Row(
          children: [
            CusRatingBarIndicator(rating: review.rating.toDouble()),
            const SizedBox(width: AppSizes.spaceBtwItems),
            Text(review.createdAt.split('T').first, style: Theme.of(context).textTheme.bodyMedium),
          ],
        ),
        const SizedBox(height: AppSizes.spaceBtwItems),
        ReadMoreText(
          review.comment,
          trimLines: 3,
          colorClickableText: Theme.of(context).colorScheme.primary,
          trimMode: TrimMode.Line,
          trimCollapsedText: ' Read more',
          trimExpandedText: ' Show less',
          style: Theme.of(context).textTheme.bodyMedium,
        ),
        const SizedBox(height: AppSizes.spaceBtwItems),

        // Company's answer (if present)
        if (review.companyReply != null && review.companyReply!.isNotEmpty)
          RoundedContainer(
            bgcolor: dark ? AppColors.darkGray : AppColors.grey,
            child: Padding(
              padding: const EdgeInsets.all(AppSizes.defaultSpace),
              child: Column(
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(review.companyName ?? 'Shop', style: Theme.of(context).textTheme.titleMedium),
                      Text(review.companyReplyDate ?? '', style: Theme.of(context).textTheme.bodyMedium),
                    ],
                  ),
                  const SizedBox(height: AppSizes.spaceBtwItems),
                  ReadMoreText(
                    review.companyReply!,
                    trimLines: 2,
                    colorClickableText: Colors.blue,
                    trimMode: TrimMode.Line,
                    trimCollapsedText: ' Read more',
                    trimExpandedText: ' Show less',
                  ),
                ],
              ),
            ),
          ),
        const SizedBox(height: AppSizes.spaceBtwItems),

        // Hiển thị ảnh review (nếu có)
        if (review.images.isNotEmpty)
          SizedBox(
            height: 80,
            child: ListView.separated(
              scrollDirection: Axis.horizontal,
              itemCount: review.images.length,
              separatorBuilder: (_, __) => const SizedBox(width: 8),
              itemBuilder: (context, idx) {
                final imgUrl = review.images[idx];
                return ClipRRect(
                  borderRadius: BorderRadius.circular(6),
                  child: Image.network(
                    imgUrl,
                    width: 80,
                    height: 80,
                    fit: BoxFit.cover,
                    errorBuilder: (ctx, err, st) => Container(
                      width: 80,
                      height: 80,
                      color: Colors.grey[200],
                      child: const Icon(Icons.broken_image, size: 28),
                    ),
                    loadingBuilder: (ctx, child, progress) {
                      if (progress == null) return child;
                      return SizedBox(
                        width: 80,
                        height: 80,
                        child: Center(
                          child: CircularProgressIndicator(
                            value: progress.expectedTotalBytes != null
                                ? progress.cumulativeBytesLoaded / (progress.expectedTotalBytes ?? 1)
                                : null,
                            strokeWidth: 2,
                          ),
                        ),
                      );
                    },
                  ),
                );
              },
            ),
          ),
        const SizedBox(height: AppSizes.spaceBtwSections),
      ],
    );
  }
}