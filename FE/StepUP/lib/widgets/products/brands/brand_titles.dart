import 'package:flutter/material.dart';
import 'package:flutter_app/constants/colors.dart';
import 'package:flutter_app/constants/sizes.dart';
import 'package:flutter_app/utils/constants/enums.dart';
import 'package:flutter_app/widgets/products/brands/brand_title_text.dart';
import 'package:iconsax_flutter/iconsax_flutter.dart';

class BrandTitlesVerify extends StatelessWidget {
  const BrandTitlesVerify({
    super.key,
    required this.title,
    this.maxLines = 1,
    this.textColor,
    this.iconColor = AppColors.primary,
    this.textAlign = TextAlign.center,
    this.brandTextSize = TextSizes.small, 
  });

  final String title;
  final int maxLines;
  final Color? textColor, iconColor;
  final TextAlign? textAlign;
  final TextSizes brandTextSize;

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Flexible(
          child: BrandTitleText(
            title: title,
            color: textColor,
            maxLines: maxLines,
            textAlign: textAlign,
            brandTextSize: brandTextSize, // Truyền tiếp vào text widget
          ),
        ),
        const SizedBox(width: AppSizes.xs),
        Icon(Iconsax.verify, color: iconColor, size: AppSizes.iconXs),
      ],
    );
  }
}