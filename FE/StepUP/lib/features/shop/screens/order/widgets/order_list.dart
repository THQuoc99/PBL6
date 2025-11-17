import 'package:flutter/material.dart';
import 'package:flutter_app/constants/colors.dart';
import 'package:flutter_app/constants/sizes.dart';
import 'package:flutter_app/utils/helpers/helper_function.dart';
import 'package:flutter_app/widgets/containers/rounded_container.dart';
import 'package:iconsax_flutter/iconsax_flutter.dart';

class OrderListItem extends StatelessWidget{
  const OrderListItem({
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    final dark = HelperFunction.isDarkMode(context); 
    return ListView.separated(
      shrinkWrap: true,
      itemCount: 8,
      separatorBuilder: (_, __) => const SizedBox(height: AppSizes.spaceBtwItems,),
      itemBuilder: (_, index) =>  RoundedContainer(
        showBorder: true,
        padding: const EdgeInsets.all(AppSizes.md),
        bgcolor: dark? AppColors.dark : AppColors.light,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Row(
              children: [
                // icon
                const Icon(Iconsax.airplane),
                SizedBox(width: AppSizes.spaceBtwItems / 2,),
      
                // Status & date
                Expanded(
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Processing',
                        style: Theme.of(context).textTheme.bodyLarge!.apply(color: AppColors.primary, fontWeightDelta: 1),
                      ),
                      Text('15 Nov 2025', style: Theme.of(context).textTheme.headlineSmall,),
                    ],
                  ),
                ),
                // icon
                IconButton(onPressed: () {}, icon: const Icon(Iconsax.arrow_right))
              ],
            ),
            SizedBox(height: AppSizes.spaceBtwItems,),
            Row(
              children: [
                Expanded(
                  child: Row(
                    children: [
                      // icon
                      const Icon(Iconsax.tag),
                      SizedBox(width: AppSizes.spaceBtwItems / 2,),
                  
                      // Status & date
                      Expanded(
                        child: Column(
                          mainAxisSize: MainAxisSize.min,
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text('Order',style: Theme.of(context).textTheme.labelMedium),
                            Text('A02', style: Theme.of(context).textTheme.titleMedium),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
                Expanded(
                  child: Row(
                    children: [
                      // icon
                      const Icon(Iconsax.calendar),
                      SizedBox(width: AppSizes.spaceBtwItems / 2,),
                  
                      // Status & date
                      Expanded(
                        child: Column(
                          mainAxisSize: MainAxisSize.min,
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text('Shipping Date',style: Theme.of(context).textTheme.labelMedium),
                            Text('01 Jan 2026', style: Theme.of(context).textTheme.titleMedium),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            )
          ],
        ),
      ),
    );
  }
}