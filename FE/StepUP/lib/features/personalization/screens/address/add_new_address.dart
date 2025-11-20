import 'package:flutter/material.dart';
import 'package:flutter_app/constants/sizes.dart';
import 'package:flutter_app/widgets/appbar/appbar.dart';
import 'package:iconsax_flutter/iconsax_flutter.dart';
import 'package:get/get.dart';
import 'package:flutter_app/shop/controllers/add_address_controller.dart';

class AddNewAddressScreen extends StatelessWidget {
  const AddNewAddressScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final controller = Get.put(AddAddressController());

    return Scaffold(
      appBar: CusAppbar(
        title: Obx(() => Text(controller.isEditMode.value ? 'Sửa Địa Chỉ' : 'Thêm Địa Chỉ Mới')),
        showBackArrow: true,
      ),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(AppSizes.defaultSpace),
          child: Form(
            child: Column(
              children: [
                TextFormField(
                  controller: controller.nameController,
                  decoration: const InputDecoration(
                    prefixIcon: Icon(Iconsax.user), 
                    labelText: 'Tên người nhận'
                  ),
                ),
                const SizedBox(height: AppSizes.spaceBtwInputFields),

                // ✅ 2. SỐ ĐIỆN THOẠI
                TextFormField(
                  controller: controller.phoneController,
                  keyboardType: TextInputType.phone,
                  decoration: const InputDecoration(
                    prefixIcon: Icon(Iconsax.mobile), 
                    labelText: 'Số điện thoại'
                  ),
                ),
                const SizedBox(height: AppSizes.spaceBtwInputFields),

                // --- 3. TỈNH / THÀNH PHỐ ---
                Obx(() => DropdownButtonFormField<int>(
                  decoration: const InputDecoration(
                    prefixIcon: Icon(Iconsax.building), 
                    labelText: 'Tỉnh / Thành phố'
                  ),
                  value: controller.selectedProvince.value,
                  items: controller.provinces.map((province) {
                    return DropdownMenuItem(
                      value: province.id,
                      child: Text(province.name, overflow: TextOverflow.ellipsis),
                    );
                  }).toList(),
                  onChanged: (val) {
                    controller.selectedProvince.value = val;
                    if (val != null) controller.fetchWards(val);
                  },
                )),
                const SizedBox(height: AppSizes.spaceBtwInputFields),

                // --- 4. PHƯỜNG / XÃ ---
                Obx(() => DropdownButtonFormField<int>(
                  decoration: const InputDecoration(
                    prefixIcon: Icon(Iconsax.activity), 
                    labelText: 'Phường / Xã'
                  ),
                  value: controller.selectedWard.value,
                  onChanged: controller.wards.isEmpty ? null : (val) {
                    controller.selectedWard.value = val;
                    if (val != null) controller.fetchHamlets(val);
                  },
                  items: controller.wards.map((ward) {
                    return DropdownMenuItem(
                      value: ward.id,
                      child: Text(ward.name, overflow: TextOverflow.ellipsis),
                    );
                  }).toList(),
                )),
                const SizedBox(height: AppSizes.spaceBtwInputFields),

                // --- 5. THÔN / XÓM (Tùy chọn) ---
                Obx(() => DropdownButtonFormField<int>(
                  decoration: const InputDecoration(
                    prefixIcon: Icon(Iconsax.home), 
                    labelText: 'Thôn / Xóm (Tùy chọn)'
                  ),
                  value: controller.selectedHamlet.value,
                  onChanged: controller.hamlets.isEmpty ? null : (val) {
                    controller.selectedHamlet.value = val;
                  },
                  items: controller.hamlets.map((hamlet) {
                    return DropdownMenuItem(
                      value: hamlet.id,
                      child: Text(hamlet.name, overflow: TextOverflow.ellipsis),
                    );
                  }).toList(),
                )),
                const SizedBox(height: AppSizes.spaceBtwInputFields),

                // --- 6. ĐỊA CHỈ CHI TIẾT ---
                TextFormField(
                  controller: controller.detailController,
                  decoration: const InputDecoration(
                    prefixIcon: Icon(Iconsax.textalign_left), 
                    labelText: 'Số nhà, tên đường...'
                  ),
                  maxLines: 2,
                ),
                const SizedBox(height: AppSizes.defaultSpace),

                // --- NÚT SAVE ---
                SizedBox(
                  width: double.infinity,
                  child: Obx(() => ElevatedButton(
                    onPressed: controller.isLoading.value ? null : () => controller.saveAddress(),
                    child: controller.isLoading.value 
                        ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2)) 
                        : Obx(() => Text(controller.isEditMode.value ? 'Cập nhật' : 'Lưu địa chỉ')),
                  )),
                )
              ],
            ),
          ),
        ),
      )
    );
  }
}