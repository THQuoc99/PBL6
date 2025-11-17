import 'package:flutter/material.dart';
import 'package:flutter_app/constants/colors.dart';
import 'package:flutter_app/constants/image_string.dart';
import 'package:flutter_app/constants/sizes.dart';
import 'package:flutter_app/screens/product_details/product_detail.dart';
import 'package:flutter_app/styles/shadow.dart';
import 'package:flutter_app/widgets/containers/rounded_container.dart';
import 'package:flutter_app/widgets/image/rounded_image.dart';
import 'package:flutter_app/widgets/icons/circular_icon.dart';
import 'package:flutter_app/widgets/texts/product_title_text.dart';
import 'package:flutter_app/widgets/texts/product_price_text.dart';
import 'package:get/get.dart';

class ProductCardVertical extends StatelessWidget{
  const ProductCardVertical(
    {
      super.key
    }
  );

  @override
  Widget build(BuildContext context)
  {
    return GestureDetector(
      onTap: () => Get.to(()=> const ProductDetail()),
      child: Container(
        width: 180,
        padding: const EdgeInsets.all(1),
        decoration: BoxDecoration(
          boxShadow: [ShadowStyle.verticalProductShadow],
          borderRadius: BorderRadius.circular(AppSizes.productImageRadius),
          color: Colors.white
        ),
        child: Column(
          children: [
            //Thumbnail
            RoundedContainer(
              height: 180,
              padding: const EdgeInsets.all(10),
              bgcolor: AppColors.light,
              child: Stack(
                children: [
                  // Thumb Image
                  RoundedImage(imageUrl: AppImages.fireRedBackTongue, applyImageRadius: true,),
      
                  // Sale Tag
                  Positioned(
                    top: 12,
                    child: RoundedContainer(
                      radius: AppSizes.sm,
                      bgcolor: AppColors.secondary,
                      padding: const EdgeInsets.symmetric(horizontal: AppSizes.sm, vertical: AppSizes.xs),
                      child: Text(
                        '25%',
                        style: Theme.of(context).textTheme.labelLarge!.apply(color: Colors.black),
                      ),
                    ),
                  ),
      
                  // Add favorite
                  const Positioned(
                    top: 0,
                    right: 0,
                    child: CircularIcon(icon: Icons.favorite, color: Colors.blueAccent, bgcolor: Colors.white10,)
                  )
                ],
              ),
            ),
            //Detail
            Padding(
              padding: const EdgeInsets.only(left: AppSizes.sm),
              child: Column(
                children: [
                  const ProductTitleText(title: 'Fire Red Black Tongue', smallSize: true,),
                  const SizedBox(height: 8.0),
                  Row(
                    children: [
                      Text(
                        'Nike',
                        overflow: TextOverflow.ellipsis,
                        maxLines: 1,
                        style: Theme.of(context).textTheme.labelMedium,
                      ),
                      const SizedBox(width: AppSizes.xs),
                      const Icon(Icons.verified)
                    ],
                  ),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      // Price
                      ProductPriceText(price: '160.0'),
                      // Add to cart button
                      Container(
                        decoration: const BoxDecoration(
                          color: Colors.black,
                          borderRadius: BorderRadius.only(
                            topLeft: Radius.circular(AppSizes.cardRadiusMd),
                            bottomRight: Radius.circular(AppSizes.productImageRadius),
                          )
                        ),
                        child: const SizedBox(
                          
                          child: Icon(Icons.add, color: Colors.white,)
                        ),
                      )
                    ],
                  )
           
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}





