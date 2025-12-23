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
import 'package:flutter_app/shop/controllers/wishlist_controller.dart';

class ProductCardVertical extends StatelessWidget {
  final ProductModel product;

  const ProductCardVertical({
    super.key,
    required this.product,
  });

  @override
  Widget build(BuildContext context) {
    final wishlistController = Get.put(WishlistController());

    // Xử lý URL ảnh
    // Ảnh được lưu ở: media/products/{productId}/{productId}_0.jpg
    String imageUrl = "http://10.0.2.2:8000/media/products/${product.id}/${product.id}_0.jpg";
    final isNetworkImage = true;
    
    // Giả lập dữ liệu hiển thị (vì backend chưa trả về discount/rating cụ thể cho từng sp)
    final double originalPrice = product.price * 1.1; // Giả sử giá gốc cao hơn 10%
    final double averageRating = product.rating > 0 ? product.rating : 5.0; 

    return GestureDetector(
      // Điều hướng sang trang chi tiết
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

                  // Sale Tag (Có thể ẩn nếu không có logic sale)
                  Positioned(
                    top: 0, 
                    left: 0, 
                    child: RoundedContainer(
                      radius: AppSizes.sm,
                      bgcolor: AppColors.secondary.withOpacity(0.8),
                      padding: const EdgeInsets.symmetric(horizontal: AppSizes.sm, vertical: AppSizes.xs),
                      child: Text(
                        'Sale', // Hoặc logic tính %: '${((originalPrice - product.price)/originalPrice * 100).round()}%',
                        style: Theme.of(context).textTheme.labelLarge!.apply(color: Colors.black),
                      ),
                    ),
                  ),

                  // Nút Yêu thích
                  Positioned(
                    top: 0,
                    right: 0,
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
                  
                  // ✅ HIỂN THỊ TÊN SHOP CHÍNH XÁC
                  Row(
                    children: [
                      Text(
                        product.storeName.isNotEmpty ? product.storeName : "Shoex Store", 
                        overflow: TextOverflow.ellipsis, 
                        maxLines: 1, 
                        style: Theme.of(context).textTheme.labelMedium!.apply(color: Colors.grey),
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
                      Text('(${product.reviewCount})', style: Theme.of(context).textTheme.labelSmall),
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
                          // Giá gốc (Gạch ngang)
                          Text(
                            '\$${originalPrice.toStringAsFixed(0)}',
                            style: Theme.of(context).textTheme.labelMedium!.apply(decoration: TextDecoration.lineThrough, fontSizeFactor: 0.8),
                          ),
                          // Giá bán thực tế
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