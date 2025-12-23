import 'package:flutter/material.dart';
import 'package:flutter_app/constants/colors.dart';
import 'package:flutter_app/constants/sizes.dart';
import 'package:flutter_app/screens/home/components/curved_edges_widget.dart';
import 'package:flutter_app/widgets/appbar/appbar.dart';
import 'package:flutter_app/widgets/icons/circular_icon.dart';
import 'package:flutter_app/widgets/image/rounded_image.dart';
import 'package:iconsax_flutter/iconsax_flutter.dart';
import 'package:flutter_app/shop/models/product_model.dart';
import 'package:get/get.dart';
import 'package:flutter_app/shop/controllers/wishlist_controller.dart';

class ProductSlider extends StatefulWidget {
  final ProductModel product;

  const ProductSlider({
    super.key,
    required this.product,
  });

  @override
  State<ProductSlider> createState() => _ProductSliderState();
}

class _ProductSliderState extends State<ProductSlider> {
  int selectedImageIndex = 0; // Track selected image index

  String _getImageUrl([int index = 0]) {
    // Ảnh được lưu ở: media/products/{productId}/{productId}_{index}.jpg
    return 'http://10.0.2.2:8000/media/products/${widget.product.id}/${widget.product.id}_$index.jpg';
  }

  @override
  Widget build(BuildContext context) {
    final wishlistController = Get.put(WishlistController());
    
    final mainImage = _getImageUrl(selectedImageIndex);
    final isNetworkImage = true; // Luôn là network image từ media folder

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
                  child: Image.network(
                    mainImage,
                    fit: BoxFit.contain,
                    errorBuilder: (_, __, ___) => const Icon(
                      Icons.image_not_supported, 
                      size: 80, 
                      color: Colors.grey,
                    ),
                  ),
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
                  itemCount: 5, // 5 thumbnails: _0.jpg to _4.jpg
                  shrinkWrap: true,
                  scrollDirection: Axis.horizontal,
                  separatorBuilder: (_, __) => const SizedBox(width: AppSizes.spaceBtwItems),
                  itemBuilder: (_, index) {
                    final thumbnailUrl = _getImageUrl(index);
                    final isSelected = selectedImageIndex == index;
                    
                    return GestureDetector(
                      onTap: () {
                        setState(() {
                          selectedImageIndex = index;
                        });
                      },
                      child: RoundedImage(
                        width: 80,
                        bgcolor: Colors.white,
                        border: Border.all(
                          color: isSelected ? AppColors.primary : Colors.grey.shade300,
                          width: isSelected ? 2 : 1,
                        ),
                        padding: const EdgeInsets.all(AppSizes.sm),
                        imageUrl: thumbnailUrl,
                        isNetworkImage: isNetworkImage,
                      ),
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
                  final isFavorite = wishlistController.isFavorite(widget.product.id);
                  return CircularIcon(
                    icon: isFavorite ? Iconsax.heart : Iconsax.heart,
                    color: isFavorite ? Colors.red : Colors.grey,
                    onpress: () => wishlistController.toggleFavorite(widget.product),
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