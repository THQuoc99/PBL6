import 'package:flutter/material.dart';
import 'package:flutter_app/constants/colors.dart';
import 'package:flutter_app/constants/image_string.dart';
import 'package:flutter_app/constants/sizes.dart';
import 'package:flutter_app/screens/home/components/curved_edges_widget.dart';
import 'package:flutter_app/widgets/appbar/appbar.dart';
import 'package:flutter_app/widgets/icons/circular_icon.dart';
import 'package:flutter_app/widgets/image/rounded_image.dart';
import 'package:iconsax_flutter/iconsax_flutter.dart';
import 'package:flutter_app/shop/models/product_model.dart';
import 'package:get/get.dart';
import 'package:flutter_app/shop/controllers/wishlist_controller.dart';

class ProductSlider extends StatelessWidget {
  final ProductModel product;

  const ProductSlider({
    super.key,
    required this.product,
  });

  String _getImageUrl(String? img) {
    if (img == null || img.isEmpty) return AppImages.sabrina;
    String url = img;
    if (url.startsWith('/media')) {
      return 'http://10.0.2.2:8000$url';
    }
    return url;
  }

  @override
  Widget build(BuildContext context) {
    // ✅ KHỞI TẠO CONTROLLER
    final wishlistController = Get.put(WishlistController());
    
    final mainImage = _getImageUrl(product.image);
    final isNetworkImage = mainImage.startsWith('http');

    return CurvedEdgeWidget(
      child: Container(
        color: AppColors.light,
        child: Stack(
          children: [
            // Main Large Image
            SizedBox(
              height: 400,
              child: Padding(
                padding: const EdgeInsets.all(AppSizes.productImageRadius * 2),
                child: Center(
                  child: isNetworkImage
                      ? Image.network(
                          mainImage,
                          fit: BoxFit.contain,
                          errorBuilder: (_, __, ___) => const Icon(Icons.image_not_supported, size: 80, color: Colors.grey),
                        )
                      : Image.asset(mainImage, fit: BoxFit.contain),
                ),
              ),
            ),

            // Image Slider (Thumbnails)
            Positioned(
              right: 0,
              bottom: 30,
              left: AppSizes.defaultSpace,
              child: SizedBox(
                height: 80,
                child: ListView.separated(
                  itemCount: 4,
                  shrinkWrap: true,
                  scrollDirection: Axis.horizontal,
                  separatorBuilder: (_, __) => const SizedBox(width: AppSizes.spaceBtwItems),
                  itemBuilder: (_, index) {
                    return RoundedImage(
                      width: 80,
                      bgcolor: Colors.white,
                      border: Border.all(color: AppColors.primary),
                      padding: const EdgeInsets.all(AppSizes.sm),
                      imageUrl: mainImage,
                      isNetworkImage: isNetworkImage,
                    );
                  },
                ),
              ),
            ),

            // ✅ APPBAR VỚI NÚT TIM ĐỘNG (DYNAMIC HEART ICON)
            CusAppbar(
              showBackArrow: true,
              actions: [
                // Sử dụng Obx để lắng nghe thay đổi từ WishlistController
                Obx(() {
                  final isFavorite = wishlistController.isFavorite(product.id);
                  return CircularIcon(
                    icon: isFavorite ? Iconsax.heart : Iconsax.heart,
                    color: isFavorite ? Colors.red : Colors.grey,
                    onpress: () => wishlistController.toggleFavorite(product),
                  );
                })
              ],
            )
          ],
        ),
      ),
    );
  }
}