import 'package:flutter/material.dart';
import 'package:flutter_app/constants/sizes.dart';

class RoundedImage extends StatelessWidget {
  final double? width,height;
  final String imageUrl;
  final bool applyImageRadius;
  final BoxBorder? border;
  final Color bgcolor;
  final BoxFit? fit;
  final EdgeInsetsGeometry? padding;
  final bool isNetworkImage;
  final VoidCallback? onpress;
  final double radius;

  const RoundedImage({
    super.key,
    this.applyImageRadius = false,
    this.bgcolor = Colors.transparent,
    this.border,
    this.fit = BoxFit.contain,
    this.height,
    this.width,
    required this.imageUrl,
    this.isNetworkImage = false,
    this.onpress,
    this.padding,
    this.radius = AppSizes.md
  });



  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onpress,
      child: Container(
        width: width,
        height: height,
        padding: padding,
        decoration: BoxDecoration(color: bgcolor,border: border,borderRadius: BorderRadius.circular(radius)),
        child: ClipRRect(
          borderRadius: applyImageRadius ? BorderRadius.circular(radius) : BorderRadius.zero,
          child: Image(fit: fit ,image: isNetworkImage ? NetworkImage(imageUrl) : AssetImage(imageUrl) as ImageProvider),
          ),
      ),
    );
  }
}