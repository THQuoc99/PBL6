import 'package:flutter/material.dart';
import 'package:flutter_app/constants/colors.dart';
import 'package:flutter_app/constants/image_string.dart';
import 'package:flutter_app/constants/sizes.dart';
import 'package:flutter_app/features/shop/screens/store/store_screen.dart';
import 'package:flutter_app/widgets/containers/rounded_container.dart';
import 'package:flutter_app/widgets/image/circular_image.dart';
import 'package:flutter_app/widgets/products/brands/brand_titles.dart';
import 'package:flutter_app/widgets/texts/product_price_text.dart';
import 'package:flutter_app/widgets/texts/product_title_text.dart';
import 'package:get/get.dart';
import 'package:flutter_app/shop/models/product_model.dart';

class ProductMetaData extends StatelessWidget {
  final ProductModel product;

  const ProductMetaData({
    super.key,
    required this.product,
  });

  @override
  Widget build(BuildContext context) {
    // Tính giá gốc giả định (để hiển thị giảm giá)
    // Ví dụ: Giá gốc cao hơn 20% so với giá bán
    final originalPrice = product.price * 1.2;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Price & Sale Tag
        Row(
          children: [
            // Sale tag
            RoundedContainer(
              radius: AppSizes.sm,
              bgcolor: AppColors.secondary,
              padding: const EdgeInsets.symmetric(horizontal: AppSizes.sm, vertical: AppSizes.xs),
              child: Text(
                '20%', // Tạm thời để tĩnh hoặc tính toán dựa trên giá gốc/giá bán
                style: Theme.of(context).textTheme.labelLarge!.apply(color: Colors.black),
              ),
            ),
            const SizedBox(width: AppSizes.spaceBtwItems),
            
            // Original Price (Gạch ngang)
            Text(
              '\$${originalPrice.toStringAsFixed(0)}', 
              style: Theme.of(context).textTheme.titleSmall!.apply(decoration: TextDecoration.lineThrough),
            ),
            const SizedBox(width: AppSizes.spaceBtwItems),
            
            // ✅ Current Price (Giá thật từ API)
            ProductPriceText(
              price: product.price.toStringAsFixed(0), 
              isLarge: true,
            ),
          ],
        ),
        
        const SizedBox(height: AppSizes.spaceBtwItems / 1.5),
        
        // ✅ Title (Tên thật từ API)
        ProductTitleText(title: product.name),
        
        const SizedBox(height: AppSizes.spaceBtwItems / 1.5),
        
        // Stock Status
        Row(
          children: [
            const ProductTitleText(title: 'Status'),
            const SizedBox(width: AppSizes.spaceBtwItems),
            Text('In Stock', style: Theme.of(context).textTheme.titleMedium),
          ],
        ),
        
        const SizedBox(height: AppSizes.spaceBtwItems / 1.5),
        
        // Brand (Tạm thời để Nike hoặc lấy từ product.brand nếu có)
        InkWell(
          onTap: () => Get.to(() => const StoreScreen()),
          child: Row(
            children: [
              CircularImage(
                image: AppImages.nike, // Icon brand mặc định
                width: 32,
                height: 32,
                overlayColor: Colors.blue, // Đổi màu icon cho rõ trên nền sáng
              ),
              const BrandTitlesVerify(title: 'Shoex Official'),
            ],
          ),
        ),
      ],
    );
  }
}