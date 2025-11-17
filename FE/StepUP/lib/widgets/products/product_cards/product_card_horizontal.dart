import 'package:flutter/material.dart';
import 'package:flutter_app/constants/colors.dart';
import 'package:flutter_app/constants/image_string.dart';
import 'package:flutter_app/constants/sizes.dart';
import 'package:flutter_app/widgets/containers/rounded_container.dart';
import 'package:flutter_app/widgets/image/rounded_image.dart';
import 'package:flutter_app/widgets/icons/circular_icon.dart';
import 'package:flutter_app/utils/helpers/helper_function.dart';
import 'package:flutter_app/widgets/products/brands/brand_titles.dart';
import 'package:flutter_app/widgets/texts/product_price_text.dart';
import 'package:flutter_app/widgets/texts/product_title_text.dart';
import 'package:iconsax_flutter/iconsax_flutter.dart';

class ProductCardHorizontal extends StatelessWidget {
  const ProductCardHorizontal({
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    final dark = HelperFunction.isDarkMode(context);

    return Container(
      width: 310,
      padding: const EdgeInsets.all(1),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(AppSizes.productImageRadius),
        color: dark ? AppColors.darkGray : AppColors.softGrey,
      ),
      child: Row(
        children: [
          // thumbnail
          RoundedContainer(
            height: 120,
            padding: const EdgeInsets.all(AppSizes.sm),
            bgcolor: dark ? AppColors.dark : AppColors.white,
            child: Stack(
              children: [
                // Thumbnail image
                const SizedBox(
                  height: 120,
                  width: 120,
                  child: RoundedImage(imageUrl: AppImages.football1, applyImageRadius: true),
                ),

                // Sale Tag
                Positioned(
                  top: 0,
                  child: RoundedContainer(
                    radius: AppSizes.sm,
                    bgcolor: AppColors.secondary,
                    padding: const EdgeInsets.symmetric(horizontal: AppSizes.sm, vertical: AppSizes.xs),
                    child: Text('25%', style: Theme.of(context).textTheme.labelLarge!.apply(color: AppColors.black)),
                  ),
                ),

                // Add favorite
                const Positioned(
                  top: 0,
                  right: 0,
                  child: CircularIcon(
                    icon: Iconsax.heart,
                    color: Colors.red,
                  ),
                )
              ],
            ),
          ),

          // --- 2. PHẦN CHI TIẾT SẢN PHẨM ---
          // Dùng Expanded để tự động lấp đầy không gian còn lại (310 - 120)
          Expanded(
            child: Padding(
              // Thêm padding bottom để nút Add to cart không bị sát
              padding: const EdgeInsets.fromLTRB(AppSizes.sm, AppSizes.sm, 0, AppSizes.sm),
              child: SizedBox(
                height: 120,
                child: Column(
                  // Giới hạn chiều cao Column bằng chiều cao ảnh
                   
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Title & Brand
                    const Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        ProductTitleText(title: 'Nike special product 1', smallSize: true),
                        SizedBox(height: AppSizes.spaceBtwItems / 2),
                        BrandTitlesVerify(title: 'Nike'),
                      ],
                    ),
                
                    // Thêm Spacer để đẩy giá + nút xuống dưới cùng
                    const Spacer(),
                
                    // Price & Add to cart
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        //Price
                        const ProductPriceText(price: '300'),
                
                        //add to cart
                        Container(
                          decoration: const BoxDecoration(
                            color: AppColors.dark,
                            borderRadius: BorderRadius.only(
                              topLeft: Radius.circular(AppSizes.cardRadiusMd),
                              bottomRight: Radius.circular(AppSizes.productImageRadius),
                            ),
                          ),
                          // Sửa lại kích thước nút Add
                          child: const Padding(
                            padding: EdgeInsets.all(AppSizes.sm), // Tăng kích thước
                            child: Icon(Iconsax.add, color: AppColors.white, size: AppSizes.iconSm), // Dùng size icon
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
    );
  }
}