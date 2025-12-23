import 'package:flutter/material.dart';
import 'package:flutter_app/constants/colors.dart';
import 'package:flutter_app/constants/device_utility.dart';

class RatingProgressIndicator extends StatelessWidget {
  final double value;
  final String text;

  const RatingProgressIndicator({
    super.key,
    required this.value,
    required this.text,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Expanded(flex: 1, child: Text(text, style: Theme.of(context).textTheme.bodyMedium)),
        const SizedBox(width: 8),
        Expanded(
          flex: 11,
          child: ClipRRect(
            borderRadius: BorderRadius.circular(7),
            child: LinearProgressIndicator(
              value: value.clamp(0.0, 1.0),
              minHeight: 11,
              backgroundColor: Colors.grey.shade300,
              valueColor: const AlwaysStoppedAnimation(AppColors.primary),
            ),
          ),
        )
      ],
    );
  }
}