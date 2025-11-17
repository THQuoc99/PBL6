import 'package:flutter/material.dart';
import 'package:flutter_app/constants/sizes.dart';

class CircularImage extends StatelessWidget{
  final BoxFit? fit;
  final String image;
  final bool isNetworkImage;
  final Color? overlayColor;
  final Color? bgcolor;
  final double width, height, padding;
  const CircularImage({
    super.key,
    this.width = 56,
    this.height = 56,
    required this.image,
    this.fit = BoxFit.cover,
    this.padding = AppSizes.sm,
    this.isNetworkImage = false,
    this.bgcolor,
    this.overlayColor,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: width,
      height: height,
      padding: EdgeInsets.all(padding),
      decoration: BoxDecoration(
        color: bgcolor,
        borderRadius: BorderRadius.circular(100)
      ),
      child: Center(
        child: Image(
          fit: fit,
          image: isNetworkImage ? NetworkImage(image) : AssetImage(image) as ImageProvider,
          color: overlayColor,
          

        ),
      ),
    );
  }
}