import 'package:flutter/material.dart';
import 'package:flutter_app/common/widgets/ratings/rating_indicator.dart';
import 'package:flutter_app/constants/colors.dart';
import 'package:flutter_app/constants/image_string.dart';
import 'package:flutter_app/constants/sizes.dart';
import 'package:flutter_app/widgets/containers/rounded_container.dart';
import 'package:readmore/readmore.dart';
import 'package:flutter_app/utils/helpers/helper_function.dart';
import 'package:flutter_app/shop/models/review_model.dart';

class UserReviewCard extends StatelessWidget {
  final ReviewModel review;
  const UserReviewCard({super.key, required this.review});

  @override
  Widget build(BuildContext context) {
    final dark = HelperFunction.isDarkMode(context);
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
            IconButton(onPressed: () {}, icon: const Icon(Icons.more_vert))
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