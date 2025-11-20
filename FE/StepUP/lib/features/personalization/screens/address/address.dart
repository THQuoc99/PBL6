import 'package:flutter/material.dart';
import 'package:flutter_app/constants/colors.dart';
import 'package:flutter_app/constants/sizes.dart';
import 'package:flutter_app/features/personalization/screens/address/widgets/single_address.dart';
import 'package:flutter_app/widgets/appbar/appbar.dart';
import 'package:get/get.dart';
import 'add_new_address.dart';
import 'package:flutter_app/shop/controllers/address_controller.dart';

class UserAddressScreen extends StatelessWidget {
  const UserAddressScreen({super.key});

  @override
  Widget build(BuildContext context) {
    // Khởi tạo Controller
    final controller = Get.put(AddressController());

    return Scaffold(
      floatingActionButton: FloatingActionButton(
        backgroundColor: AppColors.primary,
        onPressed: () => Get.to(() => const AddNewAddressScreen()),
        child: const Icon(Icons.add, color: Colors.white),
      ),
      appBar: CusAppbar(
        showBackArrow: true,
        title: Text(
          'Addresses',
          style: Theme.of(context).textTheme.headlineSmall,
        ),
      ),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(AppSizes.defaultSpace),
          child: Obx(
            () {
              // 1. Loading
              if (controller.isLoading.value) {
                return const Center(child: CircularProgressIndicator());
              }
              
              // 2. Empty
              if (controller.addresses.isEmpty) {
                return Center(
                  child: Column(
                    children: [
                      const SizedBox(height: 100),
                      const Icon(Icons.location_off, size: 60, color: Colors.grey),
                      const SizedBox(height: 16),
                      const Text('Bạn chưa lưu địa chỉ nào.'),
                      const SizedBox(height: 16),
                      ElevatedButton(
                        onPressed: () => Get.to(() => const AddNewAddressScreen()),
                        child: const Text('Thêm địa chỉ mới'),
                      )
                    ],
                  ),
                );
              }

              // 3. List Addresses
              // ✅ SỬA LỖI: Trả về trực tiếp ListView.builder (nó là 1 Widget), không bọc trong Column.
              return ListView.builder(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                itemCount: controller.addresses.length,
                itemBuilder: (_, index) {
                  final address = controller.addresses[index];
                  
                  // Sử dụng Obx cục bộ để UI cập nhật mượt mà khi chọn
                  return Obx(() {
                    final isSelected = controller.selectedAddress.value?.id == address.id;
                    return SingleAddress(
                      address: address,
                      selected: isSelected,
                      onTap: () => controller.selectAddress(address),
                    );
                  });
                },
              );
            },
          ),
        ),
      ),
    );
  }
}