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

    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.grey.shade50,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // --- Price Section ---
          Row(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text(
                '₫${product.price.toStringAsFixed(0)}',
                style: const TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                  color: Colors.red,
                ),
              ),
              const SizedBox(width: 12),
              Text(
                '₫${originalPrice.toStringAsFixed(0)}',
                style: TextStyle(
                  fontSize: 14,
                  decoration: TextDecoration.lineThrough,
                  color: Colors.grey.shade600,
                ),
              ),
              const SizedBox(width: 8),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                decoration: BoxDecoration(
                  color: Colors.red,
                  borderRadius: BorderRadius.circular(2),
                ),
                child: const Text(
                  '-20%',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
            ],
          ),
          
          const SizedBox(height: 12),
          
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
          const SizedBox(height: 12),
        ],
      ),
    );
  }
}