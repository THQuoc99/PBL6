import 'package:flutter/material.dart';
import 'package:flutter_app/constants/colors.dart';
import 'package:flutter_app/constants/sizes.dart';
import 'package:flutter_app/shop/models/product_model.dart'; 
import 'package:flutter_app/screens/product_details/product_detail.dart'; 
import 'package:flutter_app/widgets/containers/rounded_container.dart';
import 'package:flutter_app/widgets/image/rounded_image.dart';
import 'package:flutter_app/widgets/icons/circular_icon.dart';
import 'package:flutter_app/utils/helpers/helper_function.dart';
import 'package:flutter_app/widgets/products/brands/brand_titles.dart';
import 'package:flutter_app/widgets/texts/product_price_text.dart';
import 'package:flutter_app/widgets/texts/product_title_text.dart';
import 'package:get/get.dart';
import 'package:iconsax_flutter/iconsax_flutter.dart';
import 'package:flutter_app/shop/controllers/wishlist_controller.dart';

class ProductCardHorizontal extends StatelessWidget {
  final ProductModel product; // ✅ THÊM THAM SỐ NÀY

  const ProductCardHorizontal({
    super.key,
    required this.product, // ✅ BẮT BUỘC TRUYỀN VÀO
  });

  @override
  Widget build(BuildContext context) {
    final dark = HelperFunction.isDarkMode(context);
    final wishlistController = Get.put(WishlistController());

    // Xử lý URL ảnh - Luôn dùng product ID để tạo URL chuẩn
    String imageUrl = "http://10.0.2.2:8000/media/products/${product.id}/${product.id}_0.jpg";
    final bool isNetworkImage = true;

    return GestureDetector(
      onTap: () => Get.to(() => ProductDetail(product: product)), // ✅ CHUYỂN TRANG CHI TIẾT
      child: Container(
        width: 310,
        padding: const EdgeInsets.all(1),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(AppSizes.productImageRadius),
          color: dark ? AppColors.darkGray : AppColors.softGrey,
        ),
        child: Row(
          children: [
            // --- 1. THUMBNAIL ---
            RoundedContainer(
              height: 120,
              padding: const EdgeInsets.all(AppSizes.sm),
              bgcolor: dark ? AppColors.dark : AppColors.white,
              child: Stack(
                children: [
                  // Thumbnail image
                  SizedBox(
                    height: 120,
                    width: 120,
                    child: RoundedImage(
                      imageUrl: imageUrl, 
                      isNetworkImage: isNetworkImage,
                      applyImageRadius: true
                    ),
                  ),

                  // Sale Tag (Ẩn nếu không giảm giá)
                  Positioned(
                    top: 0,
                    child: RoundedContainer(
                      radius: AppSizes.sm,
                      bgcolor: AppColors.secondary,
                      padding: const EdgeInsets.symmetric(horizontal: AppSizes.sm, vertical: AppSizes.xs),
                      child: Text('25%', style: Theme.of(context).textTheme.labelLarge!.apply(color: AppColors.black)),
                    ),
                  ),

                  // Favorite Icon
                  Positioned(
                    top: 0,
                    right: 0,
                    child: Obx(() {
                      final isFavorite = wishlistController.isFavorite(product.id);
                      return CircularIcon(
                        icon: Iconsax.heart,
                        color: isFavorite ? Colors.red : Colors.grey,
                        onpress: () => wishlistController.toggleFavorite(product),
                      );
                    }),
                  )
                ],
              ),
            ),

            // --- 2. DETAILS ---
            Expanded(
              child: Padding(
                padding: const EdgeInsets.fromLTRB(AppSizes.sm, AppSizes.sm, 0, AppSizes.sm),
                child: SizedBox(
                  height: 120,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // Title & Brand
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          ProductTitleText(title: product.name, smallSize: true), // ✅ TÊN SẢN PHẨM
                          const SizedBox(height: AppSizes.spaceBtwItems / 2),
                          BrandTitlesVerify(title: product.storeName.isNotEmpty ? product.storeName : 'Store'), // ✅ TÊN SHOP
                        ],
                      ),
                  
                      const Spacer(),
                  
                      // Price & Add to cart
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          // ✅ GIÁ
                          ProductPriceText(price: product.price.toStringAsFixed(0)),
                  
                          // Add to cart Button
                          Container(
                            decoration: const BoxDecoration(
                              color: AppColors.dark,
                              borderRadius: BorderRadius.only(
                                topLeft: Radius.circular(AppSizes.cardRadiusMd),
                                bottomRight: Radius.circular(AppSizes.productImageRadius),
                              ),
                            ),
                            child: const Padding(
                              padding: EdgeInsets.all(AppSizes.sm), 
                              child: Icon(Iconsax.add, color: AppColors.white, size: AppSizes.iconSm), 
                            ),
                          )
                        ],
                      )
                    ],
                  ),
                ),
              ),
            )
          ],
        ),
      ),
    );
  }
}