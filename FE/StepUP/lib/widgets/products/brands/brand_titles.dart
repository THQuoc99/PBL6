import 'package:flutter/material.dart';
import 'package:flutter_app/constants/sizes.dart';
import 'package:flutter_app/widgets/products/brands/brand_title_text.dart';
import 'package:iconsax_flutter/iconsax_flutter.dart';

class BrandTitlesVerify extends StatelessWidget{
  final String title;
  final int maxlines;
  final Color? textColor, iconColor;
  final TextAlign? textAlign;
  //final TextSizes brandtextsize;

  const BrandTitlesVerify({
    super.key,
    //this.brandtextsize,
    this.iconColor,
    this.maxlines = 1,
    this.textAlign,
    this.textColor,
    required this.title
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Flexible(
          child: BrandTitleText(
            title: title,
            color: textColor,
            maxlines: maxlines,
            textAlign: textAlign,
          ),
          
        ),
        const SizedBox(width: AppSizes.xs ,),
        Icon(Iconsax.verify, color: iconColor,)
      ],
    );
  }
}