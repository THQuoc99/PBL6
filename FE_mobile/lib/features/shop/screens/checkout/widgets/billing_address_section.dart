import 'package:flutter/material.dart';
import 'package:flutter_app/constants/sizes.dart';
import 'package:flutter_app/screens/home/components/section_heading.dart';


class BillingAddressSection extends StatelessWidget{
  const BillingAddressSection({
    super.key
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        SectionHeading(title: 'Shipping Address', buttonTitle: 'Change', onButtonPressed: () {},),
        Text('Nguyen Viet', style: Theme.of(context).textTheme.bodyLarge,),
        SizedBox(height: AppSizes.spaceBtwItems/2,),
        Row(
          children: [
            const Icon(Icons.phone, size: AppSizes.md,),
            const SizedBox(width: AppSizes.spaceBtwItems,),
            Text('0828 924 648', style: Theme.of(context).textTheme.bodyMedium)
          ],
        ),
        SizedBox(height: AppSizes.spaceBtwItems/2,),
        Row(
          children: [
            const Icon(Icons.house, size: AppSizes.md,),
            const SizedBox(width: AppSizes.spaceBtwItems,),
            Expanded(child: Text('121 Pham Nhu Xuong - Hoa Khanh - Da Nang', style: Theme.of(context).textTheme.bodyMedium))
          ],
        ),
      ],
    );
  }
}