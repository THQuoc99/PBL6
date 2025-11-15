import 'package:flutter/material.dart';
import 'package:flutter_app/widgets/icons/circular_icon.dart';
import 'package:flutter_app/utils/helpers/helper_function.dart';
import 'package:flutter_app/constants/colors.dart';
import 'package:iconsax_flutter/iconsax_flutter.dart';
import 'package:flutter_app/constants/sizes.dart';


class ProductQuantityAddMinus extends StatelessWidget {
  const ProductQuantityAddMinus({
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        CircularIcon(
          icon: Iconsax.minus,
          width: 32,
          height: 32,
          size: AppSizes.md,
          color: HelperFunction.isDarkMode(context) ? AppColors.white : AppColors.black,
          bgcolor: HelperFunction.isDarkMode(context) ? AppColors.darkGray : AppColors.light,
        ),
        SizedBox(width: AppSizes.spaceBtwItems,),
        Text('1', style: Theme.of(context).textTheme.bodySmall,),
        SizedBox(width: AppSizes.spaceBtwItems,),
        CircularIcon(
          icon: Iconsax.add,
          width: 32,
          height: 32,
          size: AppSizes.md,
          color: AppColors.white,
          bgcolor: AppColors.primary,
        ),
      ],
    );
  }
}