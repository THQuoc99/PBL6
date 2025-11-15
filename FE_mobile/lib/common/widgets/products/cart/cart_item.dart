import 'package:flutter/material.dart';
import 'package:flutter_app/constants/colors.dart';
import 'package:flutter_app/constants/image_string.dart';
import 'package:flutter_app/widgets/image/rounded_image.dart';
import 'package:flutter_app/widgets/products/brands/brand_titles.dart';
import 'package:flutter_app/widgets/texts/product_title_text.dart';
import 'package:flutter_app/utils/helpers/helper_function.dart';
import 'package:flutter_app/constants/sizes.dart';

class CartItem extends StatelessWidget {
  const CartItem({
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        RoundedImage(
          imageUrl: AppImages.sabrinaRed,
          width: 60,
          height: 60,
          padding: const EdgeInsets.all(AppSizes.sm),
          bgcolor: HelperFunction.isDarkMode(context) ? AppColors.darkGray : AppColors.light,
        ),
        const SizedBox(width: AppSizes.spaceBtwItems,),
    
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            const BrandTitlesVerify(title: 'Nike'),
            const Flexible(child: ProductTitleText(title: 'SABRINA RED', maxLines: 1,)),
            // Atributes
            Text.rich(
              TextSpan(
                children: [
                  TextSpan(text: 'Color:', style: Theme.of(context).textTheme.bodySmall),
                  TextSpan(text: ' Red ', style: Theme.of(context).textTheme.bodyLarge),
                  TextSpan(text: 'Size:', style: Theme.of(context).textTheme.bodySmall),
                  TextSpan(text: ' 39 ', style: Theme.of(context).textTheme.bodyLarge),
                ]
              )
            )
          ],
        )
      ],
    );
  }
}