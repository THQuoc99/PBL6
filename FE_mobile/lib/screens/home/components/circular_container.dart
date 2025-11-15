import 'package:flutter/material.dart';

class CircularContainer extends StatelessWidget {
  final double height;
  final double width;
  final double radius;
  final Color color;
  final Widget? child;
  final double padding;
  final EdgeInsets? margin;
  const CircularContainer({
    super.key,
    this.child,
    this.height = 400,
    this.width = 400,
    this.radius = 400,
    this.color = Colors.white,
    this.padding = 0,
    this.margin,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: width,
      height: height,
      padding: EdgeInsets.all(padding),
      margin: margin,
      decoration: BoxDecoration(
        color: color,
        borderRadius: BorderRadius.circular(radius),                      
      ),
      child: child,
    );
  }
}