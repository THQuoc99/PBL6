import 'package:flutter/material.dart';
import 'package:flutter_app/constants/colors.dart';
import 'package:flutter_app/constants/image_string.dart';
import 'package:flutter_app/constants/sizes.dart';
import 'package:flutter_app/screens/home/components/section_heading.dart';
import 'package:flutter_app/utils/helpers/helper_function.dart';
import 'package:flutter_app/widgets/containers/rounded_container.dart';

class BillingPaymentSection extends StatelessWidget {
  const BillingPaymentSection({
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    final dark = HelperFunction.isDarkMode(context);
    return Column(
      children: [
        SectionHeading(title: 'Payment Method', buttonTitle: 'Change',),
        const SizedBox(height: AppSizes.spaceBtwItems / 2),
        Row(
          children: [
            RoundedContainer(
              width: 60,
              height: 35,
              bgcolor: dark ? AppColors.light : AppColors.white,
              padding: const EdgeInsets.all(AppSizes.sm),
              child: const Image(
                image: AssetImage(AppImages.vnpay),
                fit: BoxFit.contain,
              ),
            ),
            const SizedBox(width: AppSizes.spaceBtwItems / 2),
            Text('VnPay', style: Theme.of(context).textTheme.bodyLarge,),

          ],
        )
      ],
    );
  }
}