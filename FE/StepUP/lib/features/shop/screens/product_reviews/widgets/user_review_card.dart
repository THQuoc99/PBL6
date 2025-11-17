import 'package:flutter/material.dart';
import 'package:flutter_app/common/widgets/ratings/rating_indicator.dart';
import 'package:flutter_app/constants/colors.dart';
import 'package:flutter_app/constants/image_string.dart';
import 'package:flutter_app/constants/sizes.dart';
import 'package:flutter_app/widgets/containers/rounded_container.dart';
import 'package:readmore/readmore.dart';
import 'package:flutter_app/utils/helpers/helper_function.dart';


class UserReviewCard extends StatelessWidget {
  const UserReviewCard({
    super.key,
  });

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
                  backgroundImage: AssetImage(AppImages.sabrina),
                ),
                const SizedBox(width: AppSizes.spaceBtwItems,),
                Text('Nguyen Viet', style: Theme.of(context).textTheme.titleLarge,),
              ],
            ),
            IconButton(onPressed: (){}, icon: const Icon(Icons.more_vert))
          ],
        ),
        const SizedBox(height: AppSizes.spaceBtwItems,),
        // Review content
        Row(
          children: [
            const CusRatingBarIndicator(rating: 4),
            const SizedBox(width: AppSizes.spaceBtwItems,),
            Text('10/10/2023', style: Theme.of(context).textTheme.bodyMedium,),
          ],
        ),
        const SizedBox(height: AppSizes.spaceBtwItems,),
        ReadMoreText(
          'This product is really amazing! I have been using it for a few weeks now and it has exceeded my expectations. The quality is top-notch and the performance is outstanding. I would highly recommend this to anyone looking for a reliable and efficient product. The design is sleek and modern, making it a great addition to my collection. Overall, I am extremely satisfied with my purchase and will definitely be buying more in the future.',
          trimLines: 3,
          colorClickableText: Theme.of(context).colorScheme.primary,
          trimMode: TrimMode.Line,
          trimCollapsedText: ' Read more',
          trimExpandedText: ' Show less',
          style: Theme.of(context).textTheme.bodyMedium,
        ),
        const SizedBox(height: AppSizes.spaceBtwItems,),

        // Company's answer
        RoundedContainer(
          bgcolor: dark ? AppColors.darkGray : AppColors.grey,
          child: Padding(
            padding: const EdgeInsets.all(AppSizes.defaultSpace),
            child: Column(
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text('Nike Company', style: Theme.of(context).textTheme.titleMedium),
                    Text('11/10/2023', style: Theme.of(context).textTheme.bodyMedium,),
                  ],
                ),
                const SizedBox(height: AppSizes.spaceBtwItems,),
                const ReadMoreText(
                  'Thank you for your positive feedback! We are thrilled to hear that our product has met your expectations and that you are satisfied with its quality and performance. Your recommendation means a lot to us, and we look forward to serving you again in the future.',
                  trimLines: 2,
                  colorClickableText: Colors.blue,
                  trimMode: TrimMode.Line,
                  trimCollapsedText: ' Read more',
                  trimExpandedText: ' Show less',
                )
              ],
            ),
          ),
        ),
        const SizedBox(height: AppSizes.spaceBtwSections,),

      ],
    );
  }
}