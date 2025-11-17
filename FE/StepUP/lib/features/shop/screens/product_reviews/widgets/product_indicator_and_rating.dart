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
            Expanded(flex: 1, child: Text(text, style: Theme.of(context).textTheme.bodyMedium,)),
            Expanded(
              flex: 11,
              child: SizedBox(
                width: AppDeviceUtility.getScreenWidth(context) * 0.8,
                child: LinearProgressIndicator(
                    value: value,
                    minHeight: 11,
                    backgroundColor: Colors.grey,
                    borderRadius: BorderRadius.circular(7),
                    valueColor: const AlwaysStoppedAnimation(AppColors.primary),
                ),
              ),
            )
        ],
    );
  }
}