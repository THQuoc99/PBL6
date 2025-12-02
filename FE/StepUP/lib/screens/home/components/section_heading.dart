import 'package:flutter/material.dart';

class SectionHeading extends StatelessWidget {
  final Color? textcolor;
  final bool showActionButton;
  final String title, buttonTitle;
  final VoidCallback? onButtonPressed;
  final Color? textColor;
  const SectionHeading({
    super.key,
    this.textcolor,
    this.showActionButton = true,
    required this.title,
    this.buttonTitle = "See All",
    this.onButtonPressed,
    this.textColor,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          title,
          style: Theme.of(context)
              .textTheme
              .headlineSmall!
              .apply(color: textColor),
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
        ),
        if (showActionButton)
          TextButton(onPressed: onButtonPressed, child: Text(buttonTitle))
      ],
    );
  }
}
