import 'package:flutter/material.dart';
import 'package:flutter_app/constants/colors.dart';
import 'package:flutter_app/constants/sizes.dart';
import 'package:flutter_app/widgets/containers/rounded_container.dart';
import 'package:iconsax_flutter/iconsax_flutter.dart';
import 'package:flutter_app/shop/models/address_model.dart';
import 'package:get/get.dart';
// Import Controllers
import 'package:flutter_app/shop/controllers/address_controller.dart';
import 'package:flutter_app/shop/controllers/add_address_controller.dart';
import 'package:flutter_app/features/personalization/screens/address/add_new_address.dart';


class SingleAddress extends StatelessWidget {
  final AddressModel address;
  final bool selected;
  final VoidCallback onTap;

  const SingleAddress({
    super.key,
    required this.address,
    required this.selected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final dark = Theme.of(context).brightness == Brightness.dark;
    final controller = Get.find<AddressController>(); 

    return GestureDetector(
      onTap: onTap,
      child: RoundedContainer(
        width: double.infinity,
        padding: const EdgeInsets.all(AppSizes.md),
        showBorder: true,
        bgcolor: selected ? AppColors.primary.withOpacity(0.5) : Colors.transparent,
        borderColor: selected 
            ? Colors.transparent 
            : dark ? AppColors.darkerGrey : AppColors.grey,
        margin: const EdgeInsets.only(bottom: AppSizes.spaceBtwItems),
        child: Stack(
          children: [
            // ✅ NÚT MENU SỬA/XÓA (Góc trên phải)
            Positioned(
              right: 0,
              top: 0,
              child: PopupMenuButton<String>(
                icon: Icon(
                  Icons.more_vert, 
                  color: selected ? (dark ? AppColors.light : AppColors.dark) : Colors.grey,
                ),
                onSelected: (value) {
                  if (value == 'edit') {
                    // --- LOGIC SỬA ---
                    final addController = Get.put(AddAddressController());
                    addController.initUpdateData(address); // Nạp data cũ vào form
                    Get.to(() => const AddNewAddressScreen());
                  } else if (value == 'delete') {
                    // --- LOGIC XÓA ---
                    controller.deleteAddress(address.id);
                  }
                },
                itemBuilder: (BuildContext context) => <PopupMenuEntry<String>>[
                  const PopupMenuItem<String>(
                    value: 'edit',
                    child: Row(
                      children: [
                        Icon(Icons.edit, size: 18), 
                        SizedBox(width: 8), 
                        Text('Sửa')
                      ]
                    ),
                  ),
                  const PopupMenuItem<String>(
                    value: 'delete',
                    child: Row(
                      children: [
                        Icon(Icons.delete, size: 18, color: Colors.red), 
                        SizedBox(width: 8), 
                        Text('Xóa', style: TextStyle(color: Colors.red))
                      ]
                    ),
                  ),
                ],
              ),
            ),
            
            // Thông tin địa chỉ
            Padding(
              padding: const EdgeInsets.only(right: 30), // Tránh đè lên nút menu
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Tên
                  Text(
                    address.name,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                  const SizedBox(height: AppSizes.sm / 2),
                  
                  // Số điện thoại
                  Text(
                    address.phoneNumber, 
                    maxLines: 1, 
                    overflow: TextOverflow.ellipsis
                  ),
                  const SizedBox(height: AppSizes.sm / 2),
                  
                  // Địa chỉ chi tiết
                  Text(
                    address.fullAddress, 
                    softWrap: true,
                    style: Theme.of(context).textTheme.bodyMedium,
                  ),
                  
                  // Tick chọn (chỉ hiện khi selected)
                  if (selected) ...[
                     const SizedBox(height: 8),
                     Row(
                       children: [
                         Icon(Iconsax.tick_circle, color: dark ? AppColors.light : AppColors.dark, size: 16),
                         const SizedBox(width: 4),
                         Text("Đang chọn", style: Theme.of(context).textTheme.labelMedium),
                       ],
                     )
                  ]
                ],
              ),
            )
          ],
        ),
      ),
    );
  }
}