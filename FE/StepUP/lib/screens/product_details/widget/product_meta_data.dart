import 'package:flutter/material.dart';
import 'package:flutter_app/constants/colors.dart';
import 'package:flutter_app/constants/image_string.dart';
import 'package:flutter_app/constants/sizes.dart';
import 'package:flutter_app/utils/constants/enums.dart';
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
    final originalPrice = product.price * 1.2;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // --- Price & Sale Tag ---
        Row(
          children: [
            RoundedContainer(
              radius: AppSizes.sm,
              bgcolor: AppColors.secondary,
              padding: const EdgeInsets.symmetric(horizontal: AppSizes.sm, vertical: AppSizes.xs),
              child: Text(
                '20%', 
                style: Theme.of(context).textTheme.labelLarge!.apply(color: Colors.black),
              ),
            ),
            const SizedBox(width: AppSizes.spaceBtwItems),
            
            Text(
              '\$${originalPrice.toStringAsFixed(0)}', 
              style: Theme.of(context).textTheme.titleSmall!.apply(decoration: TextDecoration.lineThrough),
            ),
            const SizedBox(width: AppSizes.spaceBtwItems),
            
            ProductPriceText(
              price: product.price.toStringAsFixed(0), 
              isLarge: true,
            ),
          ],
        ),
        
        const SizedBox(height: AppSizes.spaceBtwItems / 1.5),
        
        // --- Product Title ---
        ProductTitleText(title: product.name),
        
        const SizedBox(height: AppSizes.spaceBtwItems / 1.5),
        
        // --- Stock Status ---
        Row(
          children: [
            const ProductTitleText(title: 'Status'),
            const SizedBox(width: AppSizes.spaceBtwItems),
            Text(
              product.variants.any((v) => v.stock > 0) ? 'In Stock' : 'Out of Stock', 
              style: Theme.of(context).textTheme.titleMedium
            ),
          ],
        ),
        
        const SizedBox(height: AppSizes.spaceBtwItems / 1.5),
        
        // --- Store Info ---
        InkWell(
          onTap: () {
            // ✅ SỬA LỖI: Dùng storeId thay vì storeName để API tìm được đúng shop
            // Nếu product.storeId rỗng (do dữ liệu cũ), fallback về storeName hoặc báo lỗi
            final idToUse = product.storeId.isNotEmpty ? product.storeId : product.storeName;
            
            if (idToUse.isNotEmpty) {
              Get.to(() => StoreScreen(storeId: idToUse)); 
            } else {
              Get.snackbar("Thông báo", "Sản phẩm này chưa liên kết với cửa hàng nào.");
            }
          },
          child: Row(
            children: [
              // Nên thay AppImages.nike bằng logo shop động nếu có (product.storeLogo)
              CircularImage(
                image: AppImages.nike, 
                width: 32,
                height: 32,
                overlayColor: Colors.blue,
              ),
              BrandTitlesVerify(
                title: product.storeName.isNotEmpty ? product.storeName : 'Shoex Official',
                brandTextSize: TextSizes.medium,
              ),
            ],
          ),
        ),
      ],
    );
  }
}