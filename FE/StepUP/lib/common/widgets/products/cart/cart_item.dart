import 'package:flutter/material.dart';
import 'package:flutter_app/constants/colors.dart';
import 'package:flutter_app/constants/image_string.dart'; // Giữ để fallback ảnh
import 'package:flutter_app/widgets/image/rounded_image.dart';
import 'package:flutter_app/widgets/products/brands/brand_titles.dart';
import 'package:flutter_app/widgets/texts/product_title_text.dart';
import 'package:flutter_app/utils/helpers/helper_function.dart';
import 'package:flutter_app/constants/sizes.dart';
import 'package:flutter_app/shop/models/cart_item_model.dart';

class CartItem extends StatelessWidget {
  // ✅ Nhận dữ liệu từ bên ngoài
  final CartItemModel cartItem;

  const CartItem({
    super.key,
    required this.cartItem,
  });

  @override
  Widget build(BuildContext context) {
    final dark = HelperFunction.isDarkMode(context);

    // 1. Xử lý ảnh (Network vs Asset)
    String imageUrl = cartItem.image ?? "";
    if (imageUrl.startsWith("/media")) {
      imageUrl = "http://10.0.2.2:8000$imageUrl";
    }
    final isNetworkImage = imageUrl.startsWith("http");

    return Row(
      children: [
        // --- Image ---
        RoundedImage(
          imageUrl: imageUrl.isNotEmpty ? imageUrl : AppImages.sabrina,
          isNetworkImage: isNetworkImage,
          width: 60,
          height: 60,
          padding: const EdgeInsets.all(AppSizes.sm),
          bgcolor: dark ? AppColors.darkerGrey : AppColors.light,
        ),
        const SizedBox(width: AppSizes.spaceBtwItems),
    
        // --- Info ---
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              // Brand
              BrandTitlesVerify(title: cartItem.brand.isNotEmpty ? cartItem.brand : 'Shoex'),
              
              // Product Name
              Flexible(
                child: ProductTitleText(title: cartItem.productName, maxLines: 1),
              ),
              
              // ✅ Attributes (Size, Color...)
              // Duyệt qua Map attributes để hiển thị
              if (cartItem.attributes.isNotEmpty)
                Text.rich(
                  TextSpan(
                    children: cartItem.attributes.entries.map((entry) {
                      return TextSpan(
                        children: [
                          TextSpan(
                            text: '${entry.key}: ', 
                            style: Theme.of(context).textTheme.bodySmall
                          ),
                          TextSpan(
                            text: '${entry.value}  ', // Thêm khoảng trắng
                            style: Theme.of(context).textTheme.bodyLarge
                          ),
                        ]
                      );
                    }).toList(),
                  ),
                )
            ],
          ),
        )
      ],
    );
  }
}