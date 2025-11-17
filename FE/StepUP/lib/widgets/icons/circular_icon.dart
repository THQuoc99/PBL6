import 'package:flutter/material.dart';
import 'package:flutter_app/constants/colors.dart';
import 'package:flutter_app/constants/sizes.dart';
import 'package:flutter_app/utils/helpers/helper_function.dart';

class CircularIcon extends StatelessWidget {
  final double? width,height,size;
  final IconData icon;
  final Color? color;
  final Color? bgcolor;
  final VoidCallback? onpress;
  const CircularIcon({
    super.key,
    this.bgcolor,
    this.color,
    this.height,
    required this.icon,
    this.onpress,
    this.size = AppSizes.lg,
    this.width,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: width,
      height: height,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(100),
        color: bgcolor != null 
          ? bgcolor!
          : HelperFunction.isDarkMode(context)
            ? AppColors.black.withAlpha(200)
            : AppColors.white.withAlpha(200),
      ),
      child: IconButton(onPressed: onpress, icon: Icon(icon, color: color, size: size,)),
    );
  }
}