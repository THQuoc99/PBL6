import 'package:flutter/material.dart';
import 'package:flutter_app/constants/sizes.dart';

class BillingAmountSection extends StatelessWidget {
  const BillingAmountSection({
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text('subtotal', style: Theme.of(context).textTheme.bodyMedium),
            Text('\$2500', style: Theme.of(context).textTheme.labelLarge),
          ],
        ),
        SizedBox(height: AppSizes.spaceBtwItems /2,),

        // shipping
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text('Shipping Fee', style: Theme.of(context).textTheme.bodyMedium),
            Text('\$25', style: Theme.of(context).textTheme.labelLarge),
          ],
        ),
        SizedBox(height: AppSizes.spaceBtwItems /2,),

        // Total
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text('Total', style: Theme.of(context).textTheme.bodyMedium?.copyWith(fontWeight: FontWeight.bold)),
            Text('\$2525', style: Theme.of(context).textTheme.labelLarge?.copyWith(fontWeight: FontWeight.bold)),
          ],
        ),
        
      ],
    );
  }
}