import 'package:flutter/material.dart';
import 'package:flutter_app/constants/sizes.dart';
import 'package:flutter_app/shop/models/product_model.dart'; 
import 'package:flutter_app/features/shop/screens/product_reviews/product_review.dart';
import 'package:flutter_app/screens/home/components/section_heading.dart';
import 'package:flutter_app/screens/product_details/widget/product_attribute.dart';
import 'package:flutter_app/screens/product_details/widget/product_meta_data.dart';
import 'package:get/get.dart';
import 'package:iconsax_flutter/iconsax_flutter.dart';
import 'package:readmore/readmore.dart';
import 'widget/product_slider.dart';
import 'widget/bottom_add_to_cart.dart';

class ProductDetail extends StatelessWidget {
  final ProductModel product;

  const ProductDetail({
    super.key,
    required this.product,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      bottomNavigationBar: BottomAddCart(product: product),
      body: SingleChildScrollView(
        child: Column(
          children: [

            ProductSlider(product: product),

            // Detail
            Padding(
              padding: const EdgeInsets.only(
                  right: AppSizes.defaultSpace,
                  left: AppSizes.defaultSpace,
                  bottom: AppSizes.defaultSpace),
              child: Column(
                children: [
                  // Rating & Share
                  const RatingandShare(),

                  ProductMetaData(product: product),

                  // Attributes (Màu sắc, Size...)
                  // (Lưu ý: Cần cập nhật file ProductAttribute để nhận biến 'product')
                  ProductAttribute(product: product),

                  // Description
                  const SizedBox(height: AppSizes.spaceBtwSections),
                  const SectionHeading(
                    title: 'Description',
                    showActionButton: false,
                  ),
                  const SizedBox(height: AppSizes.spaceBtwItems / 2),
                  
                  // ✅ Hiển thị mô tả thật từ Backend
                  ReadMoreText(
                    product.description.isNotEmpty 
                        ? product.description 
                        : 'No description available for this product.',
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
                  const Divider(),
                  const SizedBox(height: AppSizes.spaceBtwItems),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const SectionHeading(
                        title: 'Reviews',
                        showActionButton: false,
                      ),
                      IconButton(
                          onPressed: () =>
                              Get.to(() => const ProductReviewScreen()),
                          icon: const Icon(
                            Iconsax.arrow_right_3,
                            size: 18,
                          )),
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
            const Icon(
              Iconsax.star,
              color: Colors.amber,
              size: 24,
            ),
            const SizedBox(
              width: AppSizes.spaceBtwItems / 2,
            ),
            Text.rich(
              TextSpan(
                children: [
                  TextSpan(
                      text: '5.0',
                      style: Theme.of(context).textTheme.bodyLarge),
                  const TextSpan(text: '(404)'),
                ],
              ),
            )
          ],
        ),
        IconButton(
          onPressed: () {},
          icon: const Icon(Icons.share),
        )
      ],
    );
  }
}
