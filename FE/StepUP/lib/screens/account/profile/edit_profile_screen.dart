import 'package:flutter/material.dart';
import 'package:flutter_app/constants/sizes.dart';
import 'package:flutter_app/widgets/appbar/appbar.dart';
import 'package:get/get.dart';
import 'package:flutter_app/shop/controllers/user_controller.dart';
import 'package:flutter_app/shop/services/auth_service.dart';
import 'package:iconsax_flutter/iconsax_flutter.dart';
import 'dart:async';

class EditProfileScreen extends StatefulWidget {
  const EditProfileScreen({super.key});

  @override
  _EditProfileScreenState createState() => _EditProfileScreenState();
}

class _EditProfileScreenState extends State<EditProfileScreen> {
  final userController = Get.find<UserController>();
  final authService = AuthService();

  late final TextEditingController _nameController;
  late final TextEditingController _phoneController;
  late final TextEditingController _emailController;
  late final TextEditingController _dobController;

  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _nameController = TextEditingController(text: userController.fullName.value);
    _phoneController = TextEditingController(text: userController.phone.value);
    _emailController = TextEditingController(text: userController.email.value);
    _dobController = TextEditingController(text: userController.birthDate.value);
  }

  @override
  void dispose() {
    _nameController.dispose();
    _phoneController.dispose();
    _emailController.dispose();
    _dobController.dispose();
    super.dispose();
  }

  Future<void> _handleUpdateProfile() async {
    setState(() => _isLoading = true);

    final result = await authService.updateProfile(
      fullName: _nameController.text,
      phone: _phoneController.text,
      email: _emailController.text,
      birthDate: _dobController.text,
    );

    setState(() => _isLoading = false);

    if (result['success']) {
      // 1. Cập nhật dữ liệu cục bộ
      userController.updateSomeData({
        'full_name': _nameController.text,
        'phone': _phoneController.text,
        'email': _emailController.text,
        'birth_date': _dobController.text,
      });

      // 2. FIX CRASH: Đóng màn hình TRƯỚC (Ngay lập tức, không delay)
      // Việc này giúp GetX dọn dẹp màn hình Edit xong xuôi mới làm việc khác.
      Get.back(result: true);

      // 3. Hiện thông báo SAU (Ở màn hình Profile cũ)
      // Get.snackbar hoạt động toàn cục (Global) nên nó vẫn hiện đè lên màn hình cũ bình thường.
      Get.snackbar(
        'Thành công',
        'Cập nhật hồ sơ thành công',
        snackPosition: SnackPosition.BOTTOM,
        backgroundColor: Colors.green.withOpacity(0.2),
        colorText: Colors.green,
        duration: const Duration(seconds: 2),
        margin: const EdgeInsets.all(10),
        icon: const Icon(Iconsax.verify, color: Colors.green),
      );
    } else {
      // Nếu lỗi thì giữ nguyên màn hình để user sửa
      Get.snackbar(
        'Lỗi',
        result['message'] ?? 'Có lỗi xảy ra',
        snackPosition: SnackPosition.BOTTOM,
        backgroundColor: Colors.red.withOpacity(0.2),
        colorText: Colors.red,
        margin: const EdgeInsets.all(10),
        icon: const Icon(Iconsax.warning_2, color: Colors.red),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: const CusAppbar(title: Text('Edit Profile'), showBackArrow: true),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(AppSizes.defaultSpace),
        child: Column(
          children: [
            // --- Avatar Section ---
            Stack(
              children: [
                Obx(() {
                  final avatarUrl = userController.avatar.value;
                  return CircleAvatar(
                    radius: 50,
                    backgroundColor: Colors.grey.shade200,
                    // Thêm errorBuilder để xử lý nếu ảnh lỗi hoặc chưa có asset user.png
                    backgroundImage: (avatarUrl.isNotEmpty)
                        ? NetworkImage(avatarUrl)
                        : const AssetImage('assets/images/user.png') as ImageProvider,
                    onBackgroundImageError: (_, __) {},
                  );
                }),
                Positioned(
                  bottom: 0,
                  right: 0,
                  child: Container(
                    width: 30,
                    height: 30,
                    decoration: BoxDecoration(
                      color: Colors.blue,
                      borderRadius: BorderRadius.circular(100),
                    ),
                    child: IconButton(
                      padding: EdgeInsets.zero,
                      onPressed: () {
                        Get.snackbar('Thông báo', 'Tính năng upload ảnh đang phát triển');
                      },
                      icon: const Icon(Iconsax.camera, color: Colors.white, size: 18),
                    ),
                  ),
                )
              ],
            ),
            const SizedBox(height: AppSizes.spaceBtwSections),

            // --- Form Fields ---
            TextFormField(
              controller: _nameController,
              decoration: const InputDecoration(
                labelText: 'Họ và tên',
                prefixIcon: Icon(Iconsax.user),
              ),
            ),
            const SizedBox(height: AppSizes.spaceBtwItems),

            TextFormField(
              controller: _phoneController,
              decoration: const InputDecoration(
                labelText: 'Số điện thoại',
                prefixIcon: Icon(Iconsax.mobile),
              ),
              keyboardType: TextInputType.phone,
            ),
            const SizedBox(height: AppSizes.spaceBtwItems),

            TextFormField(
              controller: _emailController,
              decoration: const InputDecoration(
                labelText: 'Email',
                prefixIcon: Icon(Iconsax.direct),
              ),
              keyboardType: TextInputType.emailAddress,
            ),
            const SizedBox(height: AppSizes.spaceBtwItems),

            // --- Date Picker ---
            TextFormField(
              controller: _dobController,
              readOnly: true,
              decoration: const InputDecoration(
                labelText: 'Ngày sinh',
                prefixIcon: Icon(Iconsax.calendar),
              ),
              onTap: () async {
                DateTime? pickedDate = await showDatePicker(
                  context: context,
                  initialDate: DateTime.now(),
                  firstDate: DateTime(1900),
                  lastDate: DateTime.now(),
                );
                if (pickedDate != null) {
                  String formattedDate = 
                      "${pickedDate.year}-${pickedDate.month.toString().padLeft(2, '0')}-${pickedDate.day.toString().padLeft(2, '0')}";
                  _dobController.text = formattedDate;
                }
              },
            ),

            const SizedBox(height: AppSizes.spaceBtwSections),

            // --- Save Button ---
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: _isLoading ? null : _handleUpdateProfile,
                child: _isLoading
                    ? const SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2),
                      )
                    : const Text('Lưu thay đổi'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}