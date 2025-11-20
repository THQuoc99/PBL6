import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:flutter_app/constants/sizes.dart';
import 'package:flutter_app/screens/home/components/section_heading.dart';
import 'package:flutter_app/shop/controllers/address_controller.dart';
import 'package:flutter_app/features/personalization/screens/address/address.dart';

class BillingAddressSection extends StatelessWidget{
  const BillingAddressSection({super.key});

  @override
  Widget build(BuildContext context) {
    final addressController = Get.put(AddressController()); 

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        SectionHeading(
            title: 'Shipping Address', 
            buttonTitle: 'Change', 
            onButtonPressed: () => Get.to(() => const UserAddressScreen())
        ),
        
        const SizedBox(height: AppSizes.spaceBtwItems / 2),
        
        // Hiển thị địa chỉ đang chọn
        Obx(() {
           final selectedAddr = addressController.selectedAddress.value;
           if (selectedAddr == null) {
             return const Text('Chưa chọn địa chỉ giao hàng', style: TextStyle(color: Colors.red));
           }
           
           return Column(
             crossAxisAlignment: CrossAxisAlignment.start,
             children: [
                Text(selectedAddr.name, style: Theme.of(context).textTheme.bodyLarge),
                const SizedBox(height: AppSizes.spaceBtwItems/2),
                Row(
                  children: [
                    const Icon(Icons.phone, size: 16, color: Colors.grey),
                    const SizedBox(width: AppSizes.spaceBtwItems),
                    Text(selectedAddr.phoneNumber, style: Theme.of(context).textTheme.bodyMedium)
                  ],
                ),
                const SizedBox(height: AppSizes.spaceBtwItems/2),
                Row(
                  children: [
                    const Icon(Icons.location_history, size: 16, color: Colors.grey),
                    const SizedBox(width: AppSizes.spaceBtwItems),
                    Expanded(
                        child: Text(selectedAddr.fullAddress, 
                            style: Theme.of(context).textTheme.bodyMedium, 
                            maxLines: 2, overflow: TextOverflow.ellipsis
                        )
                    )
                  ],
                ),
             ],
           );
        })
      ],
    );
  }
}