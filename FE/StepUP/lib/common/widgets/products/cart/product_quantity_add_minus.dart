import 'package:flutter/material.dart';
import 'package:iconsax_flutter/iconsax_flutter.dart';
import 'package:flutter_app/constants/colors.dart';
import 'package:flutter_app/constants/sizes.dart';
import 'package:flutter_app/utils/helpers/helper_function.dart';
import 'package:flutter_app/widgets/icons/circular_icon.dart';

class ProductQuantityAddMinus extends StatelessWidget {
  const ProductQuantityAddMinus({
    super.key,
    required this.quantity, // ✅ Nhận số lượng hiện tại
    this.add,               // ✅ Hàm tăng
    this.remove,            // ✅ Hàm giảm
  });

  final int quantity;
  final VoidCallback? add, remove;

  @override
  Widget build(BuildContext context) {
    final dark = HelperFunction.isDarkMode(context);

    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        // --- Nút Trừ ---
        CircularIcon(
          icon: Iconsax.minus,
          width: 32,
          height: 32,
          size: AppSizes.md,
          color: dark ? AppColors.white : AppColors.black,
          bgcolor: dark ? AppColors.darkerGrey : AppColors.light,
          onpress: remove, // Gọi hàm giảm
        ),
        const SizedBox(width: AppSizes.spaceBtwItems),

        // --- Số lượng ---
        Text(
          quantity.toString(), 
          style: Theme.of(context).textTheme.titleSmall,
        ),
        const SizedBox(width: AppSizes.spaceBtwItems),

        // --- Nút Cộng ---
        CircularIcon(
          icon: Iconsax.add,
          width: 32,
          height: 32,
          size: AppSizes.md,
          color: AppColors.white,
          bgcolor: AppColors.primary,
          onpress: add, 
        ),
      ],
    );
  }
}