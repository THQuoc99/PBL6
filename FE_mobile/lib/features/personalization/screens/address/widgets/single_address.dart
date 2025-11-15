import 'package:flutter/material.dart';
import 'package:flutter_app/constants/colors.dart';
import 'package:flutter_app/constants/sizes.dart';
import 'package:flutter_app/utils/helpers/helper_function.dart';
import 'package:flutter_app/widgets/containers/rounded_container.dart';
import 'package:iconsax_flutter/iconsax_flutter.dart';

class SingleAddress extends StatelessWidget {
  final bool isSelected;

  const SingleAddress({
    super.key,
    required this.isSelected,
  });

  @override
  Widget build(BuildContext context) {
    final dark = HelperFunction.isDarkMode(context);
    return RoundedContainer(
      width: double.infinity,
      showBorder: true,
      padding: const EdgeInsets.all(AppSizes.md),
      bgcolor: isSelected ? AppColors.primary.withAlpha(125) : Colors.transparent,
      borderColor: isSelected
      ? Colors.transparent
      : dark
          ? AppColors.darkGray
          : AppColors.grey,
      margin: const EdgeInsets.only(bottom: AppSizes.spaceBtwItems),
      child: Stack(
        children: [
          Positioned(
            right: 5,
            top: 0,
            child: Icon(
              isSelected ? Iconsax.tick_circle : null,
              color: isSelected
                ? dark
                  ? AppColors.light
                  : AppColors.dark
                : null,
            ),
          ),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Nguyen Viet',
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: Theme.of(context).textTheme.titleLarge,
              ),
              const SizedBox(height: AppSizes.sm / 2 ,),
              Text('0828 924 648', maxLines: 1, overflow: TextOverflow.ellipsis,),
              const SizedBox(height: AppSizes.sm / 2 ,),
              Text('121 Pham Nhu Xuong - Hoa Khanh - Lien Chieu - Da Nang', softWrap: true,),
            ],
          )
        ],
      ),
    );
  }
}