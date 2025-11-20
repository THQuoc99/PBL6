import 'package:flutter/material.dart';
import 'package:flutter_app/constants/colors.dart';
import 'package:flutter_app/constants/sizes.dart';
import 'package:flutter_app/shop/models/product_model.dart';
import 'package:flutter_app/screens/product_details/product_detail.dart';
import 'package:flutter_app/styles/shadow.dart';
import 'package:flutter_app/widgets/containers/rounded_container.dart';
import 'package:flutter_app/widgets/icons/circular_icon.dart';
import 'package:flutter_app/widgets/texts/product_title_text.dart';
import 'package:flutter_app/widgets/texts/product_price_text.dart';
import 'package:get/get.dart';
import 'package:iconsax_flutter/iconsax_flutter.dart';
import 'package:flutter_rating_bar/flutter_rating_bar.dart';
// ✅ Import WishlistController
import 'package:flutter_app/shop/controllers/wishlist_controller.dart';

class ProductCardVertical extends StatelessWidget {
  final ProductModel product;

  const ProductCardVertical({
    super.key,
    required this.product,
  });

  @override
  Widget build(BuildContext context) {
    // ✅ Khởi tạo Controller để quản lý yêu thích
    final wishlistController = Get.put(WishlistController());

    String imageUrl = product.image ?? "";
    if (imageUrl.startsWith("/media")) {
      imageUrl = "http://10.0.2.2:8000$imageUrl";
    }
    final isNetworkImage = imageUrl.startsWith('http');
    
    final double originalPrice = product.price * 1.2;
    final String discountPercent = '20%';
    final double averageRating = 4.5; // Giả lập rating

    return GestureDetector(
      onTap: () => Get.to(() => ProductDetail(product: product)),
      child: Container(
        width: 180,
        padding: const EdgeInsets.all(1),
        decoration: BoxDecoration(
          boxShadow: [ShadowStyle.verticalProductShadow],
          borderRadius: BorderRadius.circular(AppSizes.productImageRadius),
          color: Colors.white,
        ),
        child: Column(
          children: [
            // --- Thumbnail ---
            RoundedContainer(
              height: 135, 
              padding: const EdgeInsets.all(AppSizes.sm),
              bgcolor: AppColors.light,
              child: Stack(
                children: [
                  // Ảnh sản phẩm
                  Center(
                    child: isNetworkImage 
                      ? Image.network(
                          imageUrl,
                          fit: BoxFit.contain,
                          height: 115, 
                          errorBuilder: (context, error, stackTrace) => 
                              const Icon(Icons.image_not_supported, size: 40, color: Colors.grey),
                        )
                      : const Icon(Icons.image, size: 40, color: Colors.grey), 
                  ),

                  // Sale Tag
                  Positioned(
                    top: 0, 
                    left: 0, 
                    child: RoundedContainer(
                      radius: AppSizes.sm,
                      bgcolor: AppColors.secondary.withOpacity(0.8),
                      padding: const EdgeInsets.symmetric(horizontal: AppSizes.sm, vertical: AppSizes.xs),
                      child: Text(
                        discountPercent,
                        style: Theme.of(context).textTheme.labelLarge!.apply(color: Colors.black),
                      ),
                    ),
                  ),

                  // ✅ NÚT FAVORITE ĐÃ SỬA
                  Positioned(
                    top: 0,
                    right: 0,
                    // Dùng Obx để lắng nghe trạng thái thật từ Controller
                    child: Obx(() {
                      final isFavorite = wishlistController.isFavorite(product.id);
                      return CircularIcon(
                        icon: isFavorite ? Iconsax.heart : Iconsax.heart, 
                        color: isFavorite ? Colors.red : Colors.grey,
                        onpress: () => wishlistController.toggleFavorite(product),
                      );
                    }),
                  )
                ],
              ),
            ),
            
            const SizedBox(height: AppSizes.spaceBtwItems / 2),

            // --- Detail Info ---
            Padding(
              padding: const EdgeInsets.only(left: AppSizes.sm),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  ProductTitleText(title: product.name, smallSize: true),
                  const SizedBox(height: AppSizes.spaceBtwItems / 2),
                  
                  Row(
                    children: [
                      Text(
                        'Shoex', 
                        overflow: TextOverflow.ellipsis, 
                        maxLines: 1, 
                        style: Theme.of(context).textTheme.labelMedium
                      ),
                      const SizedBox(width: AppSizes.xs),
                      const Icon(Icons.verified, color: AppColors.primary, size: AppSizes.iconXs),
                    ],
                  ),
                ],
              ),
            ),

            const Spacer(), 

            // --- Rating, Price & Add Button ---
            Padding(
              padding: const EdgeInsets.only(left: AppSizes.sm),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Rating
                  Row(
                    children: [
                      RatingBarIndicator(
                        rating: averageRating, 
                        itemBuilder: (context, index) => const Icon(
                          Iconsax.star,
                          color: Colors.amber,
                        ),
                        itemCount: 5,
                        itemSize: 12.0,
                        direction: Axis.horizontal,
                      ),
                      const SizedBox(width: 4),
                      Text('($averageRating)', style: Theme.of(context).textTheme.labelSmall),
                    ],
                  ),
                  
                  const SizedBox(height: AppSizes.spaceBtwItems / 2),
                  
                  // Giá và Nút
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            '\$${originalPrice.toStringAsFixed(0)}',
                            style: Theme.of(context).textTheme.labelMedium!.apply(decoration: TextDecoration.lineThrough, fontSizeFactor: 0.8),
                          ),
                          ProductPriceText(price: product.price.toStringAsFixed(0)),
                        ],
                      ),
                      
                      Container(
                        decoration: const BoxDecoration(
                          color: AppColors.dark,
                          borderRadius: BorderRadius.only(
                            topLeft: Radius.circular(AppSizes.cardRadiusMd),
                            bottomRight: Radius.circular(AppSizes.productImageRadius),
                          ),
                        ),
                        child: const SizedBox(
                          width: AppSizes.iconLg,
                          height: AppSizes.iconLg,
                          child: Center(child: Icon(Iconsax.add, color: Colors.white)),
                        ),
                      )
                    ],
                  ),
                ],
              ),
            )
          ],
        ),
      ),
    );
  }
}