import 'package:flutter/material.dart';


class ProductTitleText extends StatelessWidget {
  final String title;
  final bool smallSize;
  final int maxLines;
  final TextAlign? textAlign;
  const ProductTitleText({
    super.key,
    this.maxLines = 2,
    this.smallSize = false,
    this.textAlign = TextAlign.left,
    required this.title,
  });

  @override
  Widget build(BuildContext context) {
    return Text(
      title,
      style: smallSize ? Theme.of(context).textTheme.labelLarge : Theme.of(context).textTheme.titleSmall,
      overflow: TextOverflow.ellipsis,
      maxLines: maxLines,
      textAlign: textAlign,
    );
  }
}