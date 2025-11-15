import 'package:flutter/material.dart';
import 'package:flutter_app/widgets/containers/rounded_container.dart';
import 'package:flutter_app/constants/colors.dart';
import 'package:flutter_app/constants/sizes.dart';
import 'package:flutter_app/utils/helpers/helper_function.dart';

class CouponCode extends StatelessWidget {
  const CouponCode({
    super.key,
    
  });

  @override
  Widget build(BuildContext context) {
    final dark = HelperFunction.isDarkMode(context);
    return RoundedContainer(
      showBorder: true,
      bgcolor: dark ? AppColors.dark : AppColors.light,
      padding: const EdgeInsets.only(top: AppSizes.sm, bottom: AppSizes.sm, right: AppSizes.sm, left: AppSizes.md),
      child: Row(
        children: [
          Flexible(
            child: TextFormField(
              decoration: InputDecoration(
                hintText: 'Enter coupon code',
                border: InputBorder.none,
                focusedBorder: InputBorder.none,
                enabledBorder: InputBorder.none,
                errorBorder: InputBorder.none,
                disabledBorder: InputBorder.none,
              ),
            ),
          ),
    
          SizedBox(
            //width: 80,
            child: ElevatedButton(
              onPressed: () {
                // Thêm logic áp dụng coupon tại đây
                debugPrint('Apply coupon');
              },
              
              style: ElevatedButton.styleFrom(
                foregroundColor: dark ? AppColors.white.withAlpha(125) : AppColors.black.withAlpha(125),
                backgroundColor: Colors.grey.withAlpha(30),
                side: BorderSide(color: Colors.grey.withAlpha(25)),
              ),
              child: const Text('Apply'),
            ),
          ),
        ],
      ),
    );
  }
}