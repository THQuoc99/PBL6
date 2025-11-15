

import 'package:flutter/material.dart';
import 'package:flutter_app/constants/sizes.dart';

class RoundedContainer extends StatelessWidget{
  final double? width;
  final double? height;
  final double radius;
  final Widget? child;
  final bool showBorder;
  final Color borderColor;
  final Color bgcolor;
  final EdgeInsetsGeometry? padding;
  final EdgeInsetsGeometry? margin;

  const RoundedContainer(
    {
      super.key,
      this.bgcolor = Colors.white10,
      this.borderColor = Colors.blueAccent,
      this.child,
      this.height,
      this.margin,
      this.padding,
      this.radius = AppSizes.cardRadiusLg,
      this.showBorder = false,
      this.width
    }
  );

  @override
  Widget build(BuildContext context) {
    return Container(
      width: width,
      height: height,
      padding: padding,
      margin: margin,
      decoration: BoxDecoration(
        color: bgcolor,
        borderRadius: BorderRadius.circular(radius),
        border: showBorder ? Border.all(color: borderColor) : null,
      ),
      child: child,
    );
  }
}