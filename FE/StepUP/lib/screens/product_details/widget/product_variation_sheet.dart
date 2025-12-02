import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:flutter_app/constants/sizes.dart';
import 'package:flutter_app/constants/colors.dart';
import 'package:flutter_app/shop/models/product_model.dart';
import 'package:flutter_app/shop/controllers/cart_controller.dart';
import 'package:flutter_app/shop/controllers/product_variation_controller.dart';
import 'package:flutter_app/widgets/containers/rounded_container.dart';
import 'package:flutter_app/screens/product_details/widget/choice_chip.dart'; 
import 'package:flutter_app/features/shop/screens/cart/cart.dart';
import 'package:iconsax_flutter/iconsax_flutter.dart';

enum SheetMode { addToCart, buyNow }

class ProductVariationSheet extends StatelessWidget {
  final ProductModel product;
  final SheetMode mode;

  const ProductVariationSheet({
    super.key,
    required this.product,
    required this.mode,
  });

  @override
  Widget build(BuildContext context) {
    // Sử dụng tag để tránh xung đột controller nếu mở nhiều sheet
    final controller = Get.put(VariationController(), tag: product.id.toString());
    
    // Reset controller khi sheet được dựng xong
    WidgetsBinding.instance.addPostFrameCallback((_) => controller.reset());

    final uniqueAttributes = controller.getUniqueAttributes(product);

    String imageUrl = product.image ?? "";
    if (imageUrl.startsWith("/media")) {
      imageUrl = "http://10.0.2.2:8000$imageUrl";
    }

    return Padding(
      padding: const EdgeInsets.all(AppSizes.defaultSpace),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // --- 1. HEADER ---
          Row(
            children: [
              RoundedContainer(
                height: 80, width: 80,
                padding: const EdgeInsets.all(AppSizes.sm),
                bgcolor: AppColors.light,
                child: Image.network(
                  imageUrl, fit: BoxFit.cover,
                  errorBuilder: (_, __, ___) => const Icon(Icons.image),
                ),
              ),
              const SizedBox(width: AppSizes.spaceBtwItems),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(product.name, maxLines: 2, overflow: TextOverflow.ellipsis, style: Theme.of(context).textTheme.titleMedium),
                    const SizedBox(height: 8),
                    Obx(() {
                      final variant = controller.selectedVariant.value;
                      final priceToShow = variant != null ? variant.price : product.price;
                      final stockText = controller.variationStockStatus.value;

                      return Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('\$${priceToShow.toStringAsFixed(0)}', 
                              style: Theme.of(context).textTheme.headlineSmall!.copyWith(color: AppColors.primary, fontWeight: FontWeight.bold)),
                          if (uniqueAttributes.isNotEmpty && stockText.isNotEmpty)
                            Text(stockText, style: Theme.of(context).textTheme.labelMedium),
                        ],
                      );
                    }),
                  ],
                ),
              )
            ],
          ),
          const SizedBox(height: AppSizes.spaceBtwSections),

          // --- 2. DANH SÁCH THUỘC TÍNH ---
          if (uniqueAttributes.isNotEmpty)
            ...uniqueAttributes.entries.map((entry) {
              final attributeName = entry.key;
              final attributeValues = entry.value.toList();

              return Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(attributeName, style: Theme.of(context).textTheme.titleMedium),
                  const SizedBox(height: AppSizes.spaceBtwItems / 2),
                  Obx(() => Wrap(
                    spacing: 8,
                    children: attributeValues.map((value) {
                      final isSelected = controller.selectedAttributes[attributeName] == value;
                      return MyChoiceChip(
                        text: value,
                        selected: isSelected,
                        onSelected: (selected) => controller.onAttributeSelected(product, attributeName, value),
                      );
                    }).toList(),
                  )),
                  const SizedBox(height: AppSizes.spaceBtwItems),
                ],
              );
            }).toList()
          else 
             const Padding(
               padding: EdgeInsets.symmetric(vertical: 10),
               child: Text("Sản phẩm tiêu chuẩn (Không có tùy chọn)."),
             ),

          const SizedBox(height: AppSizes.spaceBtwSections),

          // --- 3. NÚT ACTION ---
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: () {
                final cartController = Get.put(CartController());
                
                // --- LOGIC KIỂM TRA ---
                if (uniqueAttributes.isNotEmpty) {
                  final variant = controller.selectedVariant.value;
                  
                  // Check 1: Đã chọn đủ thuộc tính chưa?
                  if (controller.selectedAttributes.length < uniqueAttributes.keys.length) {
                      _showSnackbar('Chưa chọn đủ thông tin', 'Vui lòng chọn đầy đủ Màu sắc/Kích thước', isError: true);
                      return;
                  }
                  
                  // Check 2: Biến thể có tồn tại không?
                  if (variant == null) {
                      _showSnackbar('Lỗi', 'Phiên bản này không tồn tại', isError: true);
                      return;
                  }

                  // Check 3: Kiểm tra tồn kho
                  if (variant.stock <= 0) {
                      _showSnackbar('Hết hàng', 'Sản phẩm này đã hết hàng trong kho', isError: true);
                      return; 
                  }

                  // Nếu ok -> Thêm vào giỏ
                  cartController.addToCart(variant.id, 1);
                } else {
                  // Sản phẩm không biến thể
                  _showSnackbar('Thông báo', 'Sản phẩm này không có biến thể');
                  return;
                }

                // --- XỬ LÝ SAU KHI THÊM THÀNH CÔNG ---
                Get.back(); // Đóng sheet

                if (mode == SheetMode.buyNow) {
                  Get.to(() => const CartScreen());
                } else {
                  _showSnackbar('Thành công', 'Đã thêm vào giỏ hàng', isSuccess: true);
                }
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: AppColors.primary,
                padding: const EdgeInsets.all(AppSizes.md),
              ),
              child: Text(
                mode == SheetMode.buyNow ? 'Buy now' : 'Add to cart',
                style: const TextStyle(color: Colors.white),
              ),
            ),
          )
        ],
      ),
    );
  }

  // Hàm wrapper để hiện Snackbar an toàn
  void _showSnackbar(String title, String message, {bool isError = false, bool isSuccess = false}) {
    Get.snackbar(
      title,
      message,
      snackPosition: SnackPosition.TOP, // Hiện ở trên cùng để tránh bị che
      backgroundColor: isError 
          ? Colors.red.withOpacity(0.9) 
          : (isSuccess ? Colors.green.withOpacity(0.9) : Colors.grey.withOpacity(0.9)),
      colorText: Colors.white,
      margin: const EdgeInsets.all(10),
      borderRadius: 10,
      duration: const Duration(seconds: 2),
      icon: Icon(
        isError ? Iconsax.warning_2 : (isSuccess ? Iconsax.tick_circle : Iconsax.info_circle),
        color: Colors.white,
      ),
      // Quan trọng: Đảm bảo nó nằm trên các UI khác
      isDismissible: true,
      dismissDirection: DismissDirection.horizontal,
      forwardAnimationCurve: Curves.easeOutBack,
    );
  }
}