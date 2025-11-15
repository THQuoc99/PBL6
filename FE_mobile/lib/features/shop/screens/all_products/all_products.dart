import 'package:flutter/material.dart';
import 'package:flutter_app/constants/sizes.dart';
import 'package:flutter_app/widgets/appbar/appbar.dart';
import 'package:flutter_app/widgets/layouts/grid_layout.dart';
import 'package:flutter_app/widgets/products/product_cards/product_card_vertical.dart';
import 'package:iconsax_flutter/iconsax_flutter.dart';

class AllProducts extends StatelessWidget{
  const AllProducts({
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: const CusAppbar(title: Text('Popular Products'), showBackArrow: true,),
      body: SingleChildScrollView(
        child: Padding(
          padding: EdgeInsets.all(AppSizes.defaultSpace),
          child: Column(
            children: [
              // Dropdown
              DropdownButtonFormField(
                decoration: InputDecoration(prefixIcon: Icon(Iconsax.sort)),
                onChanged: (value){},
                items: ['Name', 'Price', 'Sale']
                  .map((option) => DropdownMenuItem( value: option,child: Text(option)))
                  .toList(),
              ),
              const SizedBox(height: AppSizes.spaceBtwItems,),

              //Product
              GridLayout(itemCount: 8, itemBuilder: (_,index) => ProductCardVertical()),
            ],
          ),
        ),
      ),
    );
  }
}