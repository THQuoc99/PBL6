import 'package:flutter/material.dart';
import 'package:flutter_app/constants/sizes.dart';
import 'package:flutter_app/constants/colors.dart';
import 'package:flutter_app/shop/models/product_model.dart'; 
import 'package:flutter_app/features/shop/screens/product_reviews/product_review.dart';
import 'package:flutter_app/screens/home/components/section_heading.dart';
import 'package:flutter_app/screens/product_details/widget/product_attribute.dart';
import 'package:flutter_app/screens/product_details/widget/product_meta_data.dart';
import 'package:flutter_app/screens/product_details/widget/product_variation_sheet.dart';
import 'package:get/get.dart';
import 'package:iconsax_flutter/iconsax_flutter.dart';
import 'package:readmore/readmore.dart';
import 'widget/product_slider.dart';

class ProductDetail extends StatelessWidget {
  final ProductModel product;

  const ProductDetail({
    super.key,
    required this.product,
  });

  @override
  Widget build(BuildContext context) {
    // Tính số đã bán (giả lập)
    final soldCount = (product.id * 87) % 1000 + 100;

    return Scaffold(
      body: SingleChildScrollView(
        child: Column(
          children: [
            ProductSlider(product: product),

            // Detail
            Padding(
              padding: const EdgeInsets.all(AppSizes.defaultSpace),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Product Name
                  Text(
                    product.name,
                    style: Theme.of(context).textTheme.headlineSmall,
                  ),
                  const SizedBox(height: 8),

                  // Rating & Sold
                  RatingAndSold(soldCount: soldCount),
                  const SizedBox(height: AppSizes.spaceBtwItems),

                  // Price Section
                  ProductMetaData(product: product),
                  const SizedBox(height: AppSizes.spaceBtwSections),

                  // Attributes (Chỉ hiển thị, không chọn)
                  ProductAttribute(product: product),
                  const SizedBox(height: AppSizes.spaceBtwSections),

                  // Description
                  const Divider(),
                  const SizedBox(height: AppSizes.spaceBtwItems),
                  const SectionHeading(
                    title: 'Mô tả sản phẩm',
                    showActionButton: false,
                  ),
                  const SizedBox(height: AppSizes.spaceBtwItems / 2),
                  ReadMoreText(
                    product.description.isNotEmpty 
                        ? product.description 
                        : 'Chưa có mô tả cho sản phẩm này.',
                    trimLines: 3,
                    trimMode: TrimMode.Line,
                    trimCollapsedText: ' Xem thêm',
                    trimExpandedText: ' Thu gọn',
                    moreStyle: const TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                      color: Colors.blue,
                    ),
                    lessStyle: const TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
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
                        title: 'Đánh giá sản phẩm',
                        showActionButton: false,
                      ),
                      IconButton(
                        onPressed: () => Get.to(() => ProductReviewScreen(productId: product.id)),
                        icon: const Icon(Iconsax.arrow_right_3, size: 18),
                      ),
                    ],
                  ),
                  const SizedBox(height: 100), // Space for bottom bar
                ],
              ),
            )
          ],
        ),
      ),

      // Bottom Action Bar
      bottomNavigationBar: _buildBottomBar(context),
    );
  }

  Widget _buildBottomBar(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.2),
            blurRadius: 10,
            offset: const Offset(0, -2),
          ),
        ],
      ),
      child: SafeArea(
        child: Row(
          children: [
            // Add to cart button
            Expanded(
              child: OutlinedButton(
                onPressed: () => _showVariationSheet(context, SheetMode.addToCart),
                style: OutlinedButton.styleFrom(
                  side: BorderSide(color: AppColors.primary),
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(8),
                  ),
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(Iconsax.shopping_cart, color: AppColors.primary, size: 20),
                    const SizedBox(width: 8),
                    Text(
                      'Thêm vào giỏ',
                      style: TextStyle(color: AppColors.primary, fontSize: 16, fontWeight: FontWeight.w600),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(width: 12),
            // Buy now button
            Expanded(
              child: ElevatedButton(
                onPressed: () => _showVariationSheet(context, SheetMode.buyNow),
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppColors.primary,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(8),
                  ),
                ),
                child: const Text(
                  'Mua ngay',
                  style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.w600),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _showVariationSheet(BuildContext context, SheetMode mode) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => Container(
        decoration: const BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
        ),
        child: ProductVariationSheet(
          product: product,
          mode: mode,
        ),
      ),
    );
  }
}

class RatingAndSold extends StatelessWidget {
  final int soldCount;
  
  const RatingAndSold({super.key, required this.soldCount});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
          decoration: BoxDecoration(
            color: const Color.fromARGB(255, 223, 220, 220),
            borderRadius: BorderRadius.circular(4),
          ),
          child: Row(
            children: [
              Text(
                '4.8',
                style: TextStyle(
                  color: const Color.fromARGB(255, 0, 0, 0),
                  fontWeight: FontWeight.w600,
                  fontSize: 13,
                ),
              ),
              const SizedBox(width: 4),
              Icon(Iconsax.star, color: const Color.fromARGB(255, 215, 230, 17), size: 14),
            ],
          ),
        ),
        const SizedBox(width: 12),
        Text(
          '$soldCount Đánh giá',
          style: TextStyle(color: Colors.grey.shade600, fontSize: 13),
        ),
        const SizedBox(width: 12),
        Text(
          '${soldCount * 3} Đã bán',
          style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w500),
        ),
      ],
    );
  }
}
