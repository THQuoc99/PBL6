import 'package:flutter/material.dart';
import 'package:flutter_app/constants/sizes.dart';
import 'package:flutter_app/shop/models/location_models.dart';
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
                  decoration: const InputDecoration(prefixIcon: Icon(Iconsax.user), labelText: 'Tên người nhận'),
                ),
                const SizedBox(height: AppSizes.spaceBtwInputFields),

                TextFormField(
                  controller: controller.phoneController,
                  keyboardType: TextInputType.phone,
                  decoration: const InputDecoration(prefixIcon: Icon(Iconsax.mobile), labelText: 'Số điện thoại'),
                ),
                const SizedBox(height: AppSizes.spaceBtwInputFields),

                // --- 3. TỈNH / THÀNH PHỐ ---
                // Lưu ý: Value là OBJECT ProvinceModel, không phải int ID
                Obx(() => DropdownButtonFormField<ProvinceModel>(
                  decoration: const InputDecoration(prefixIcon: Icon(Iconsax.building), labelText: 'Tỉnh / Thành phố'),
                  value: controller.selectedProvince.value,
                  // Cần so sánh object (override == hoặc dùng library) hoặc đơn giản là object reference
                  // Nếu API trả về list mới mỗi lần, value cũ có thể không khớp. 
                  // Tốt nhất là so sánh ID trong logic onChanged nếu gặp lỗi.
                  items: controller.provinces.map((province) {
                    return DropdownMenuItem(
                      value: province,
                      child: Text(province.name, overflow: TextOverflow.ellipsis),
                    );
                  }).toList(),
                  onChanged: (val) {
                    controller.selectedProvince.value = val;
                    if (val != null) controller.fetchDistricts(val.id);
                  },
                )),
                const SizedBox(height: AppSizes.spaceBtwInputFields),

                // --- 4. QUẬN / HUYỆN (Thay vì WARD như code cũ, logic thực tế là Tỉnh -> Huyện -> Xã) ---
                Obx(() => DropdownButtonFormField<DistrictModel>(
                  decoration: const InputDecoration(prefixIcon: Icon(Iconsax.global), labelText: 'Quận / Huyện'),
                  value: controller.selectedDistrict.value,
                  onChanged: controller.districts.isEmpty ? null : (val) {
                    controller.selectedDistrict.value = val;
                    if (val != null) controller.fetchWards(val.id); // Huyện -> Xã
                  },
                  items: controller.districts.map((d) {
                    return DropdownMenuItem(
                      value: d,
                      child: Text(d.name, overflow: TextOverflow.ellipsis),
                    );
                  }).toList(),
                )),
                const SizedBox(height: AppSizes.spaceBtwInputFields),

                // --- 5. PHƯỜNG / XÃ ---
                Obx(() => DropdownButtonFormField<WardModel>(
                  decoration: const InputDecoration(prefixIcon: Icon(Iconsax.activity), labelText: 'Phường / Xã'),
                  value: controller.selectedWard.value,
                  onChanged: controller.wards.isEmpty ? null : (val) {
                    controller.selectedWard.value = val;
                  },
                  items: controller.wards.map((ward) {
                    return DropdownMenuItem(
                      value: ward,
                      child: Text(ward.name, overflow: TextOverflow.ellipsis),
                    );
                  }).toList(),
                )),
                const SizedBox(height: AppSizes.spaceBtwInputFields),

                // --- 6. ĐỊA CHỈ CHI TIẾT ---
                TextFormField(
                  controller: controller.detailController,
                  decoration: const InputDecoration(prefixIcon: Icon(Iconsax.textalign_left), labelText: 'Số nhà, tên đường...'),
                  maxLines: 2,
                ),
                const SizedBox(height: AppSizes.defaultSpace),

                // --- NÚT SAVE ---
                SizedBox(
                  width: double.infinity,
                  child: Obx(() => ElevatedButton(
                    onPressed: controller.isLoading.value ? null : () => controller.saveAddress(),
                    child: controller.isLoading.value 
                        ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(color: Colors.white)) 
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