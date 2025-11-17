import 'package:flutter/material.dart';

class BrandTitleText extends StatelessWidget{
  final Color? color;
  final String title;
  final int maxlines;
  final TextAlign? textAlign;
  const BrandTitleText({
    super.key,
    this.color,
    this.maxlines = 1,
    this.textAlign,
    required this.title
  });

  @override
  Widget build(BuildContext context) {
    return Text(
      title,
      textAlign: textAlign,
      maxLines: maxlines,
      overflow: TextOverflow.ellipsis,
    );
  }
}