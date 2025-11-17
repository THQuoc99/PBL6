import 'package:flutter/material.dart';
import 'package:flutter_app/constants/sizes.dart';
import 'package:flutter_app/features/shop/screens/product_reviews/product_review.dart';
import 'package:flutter_app/screens/home/components/section_heading.dart';
import 'package:flutter_app/screens/product_details/widget/product_attribute.dart';
import 'package:flutter_app/screens/product_details/widget/product_meta_data.dart';
import 'package:get/get.dart';
import 'package:iconsax_flutter/iconsax_flutter.dart';
import 'package:readmore/readmore.dart';
import 'widget/product_slider.dart';
import 'widget/bottom_add_to_cart.dart';

class ProductDetail extends StatelessWidget{
  const ProductDetail({
    super.key
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      bottomNavigationBar: BottomAddCart(),
      body: SingleChildScrollView(
        child: Column(
          children: [
            // Product slider
            ProductSlider(),

            // Detail
            Padding(
              padding: EdgeInsets.only(right: AppSizes.defaultSpace, left: AppSizes.defaultSpace, bottom: AppSizes.defaultSpace),
              child: Column(
                children: [
                  // Rating $ share
                  RatingandShare(),
                  // Meta data
                  ProductMetaData(),
                  // Attributes
                  ProductAttribute(),

                  // Description
                  SizedBox(height: AppSizes.spaceBtwSections,),
                  SectionHeading(title: 'Description', showActionButton: false,),
                  SizedBox(height: AppSizes.spaceBtwItems / 2,),
                  ReadMoreText(
                    'The Nike Air Max 270 is a popular sneaker known for its comfort and style. It features a large Air Max unit in the heel for cushioning and a sleek design that combines performance and fashion. The shoe is available in various colorways and is suitable for both athletic activities and casual wear.',
                    trimLines: 2,
                    trimMode: TrimMode.Line,
                    trimCollapsedText: ' Show more ',
                    trimExpandedText: ' Show less ',
                    moreStyle: const TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.bold,
                      color: Colors.blue,
                    ),
                    lessStyle: const TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.bold,
                      color: Colors.blue,
                    ),
                  ),
                  // Reviews
                  Divider(),
                  const SizedBox(height: AppSizes.spaceBtwItems,),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const SectionHeading(title: 'Reviews', showActionButton: false,),
                      IconButton(onPressed: () => Get.to(()=> const ProductReviewScreen()), icon: const Icon(Iconsax.arrow_right_3, size: 18,)),
                    ],
                  )

                ],
              ),
            )
          ],
        ),
      ),
    );
  }
}

class RatingandShare extends StatelessWidget {
  const RatingandShare({
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Row(
          children: [
            const Icon(Iconsax.star, color: Colors.amber, size: 24,),
            const SizedBox(width: AppSizes.spaceBtwItems / 2,),
            Text.rich(
              TextSpan(
                children: [
                  TextSpan(text: '5.0', style: Theme.of(context).textTheme.bodyLarge),
                  const TextSpan(text: '(404)'),
                ]
              )
            )
          ],
        ),
        IconButton(onPressed: (){}, icon: Icon(Icons.share),)
      ],
    );
  }
}

