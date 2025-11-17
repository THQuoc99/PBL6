import 'package:flutter/material.dart';
import 'package:flutter_app/constants/colors.dart';
import 'package:flutter_app/constants/image_string.dart';
import 'package:flutter_app/constants/sizes.dart';
import 'package:flutter_app/features/shop/screens/store/store_screen.dart';
import 'package:flutter_app/widgets/containers/rounded_container.dart';
import 'package:flutter_app/widgets/image/circular_image.dart';
import 'package:flutter_app/widgets/products/brands/brand_titles.dart';
import 'package:flutter_app/widgets/texts/product_price_text.dart';
import 'package:flutter_app/widgets/texts/product_title_text.dart';
import 'package:get/get.dart';


class ProductMetaData extends StatelessWidget{
  const ProductMetaData({
    super.key
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Price
        Row(
          children: [
            // Sale tag
            RoundedContainer(
              radius: AppSizes.sm,
              bgcolor: AppColors.secondary,
              padding: const EdgeInsets.symmetric(horizontal: AppSizes.sm, vertical: AppSizes.xs),
              child: Text('90%', style: Theme.of(context).textTheme.labelLarge!.apply(color: Colors.black),),
            ),
            SizedBox(width: AppSizes.spaceBtwItems,),
            // Price
            Text('\$10000', style: Theme.of(context).textTheme.titleSmall!.apply(decoration: TextDecoration.lineThrough),),
            SizedBox(width: AppSizes.spaceBtwItems,),
            ProductPriceText(price: '100', isLarge: true,),
          ],
        ),
        SizedBox(width: AppSizes.spaceBtwItems / 1.5 ),
        // Title
        ProductTitleText(title: 'Sabrina 3 Blueprint'),
        SizedBox(width: AppSizes.spaceBtwItems / 1.5 ),
        // Stock
        Row(
          children: [
            ProductTitleText(title: 'Status'),
            SizedBox(width: AppSizes.spaceBtwItems),
            Text('In Stock', style: Theme.of(context).textTheme.titleMedium),
          ],
        ),
        
        SizedBox(width: AppSizes.spaceBtwItems / 1.5 ),
        // Brand
        InkWell(
          onTap: () => Get.to(() => const StoreScreen()),
          child: Row(
            children: [
              CircularImage(
                image: AppImages.nike,
                width: 32,
                height: 32,
                overlayColor: Colors.white,
              ),
              BrandTitlesVerify(title: 'Nike')
            ],
          ),
        ),
        
      ],
    );
  }
}