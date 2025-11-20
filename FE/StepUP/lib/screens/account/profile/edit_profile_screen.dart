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
  // Lấy controller
  final userController = Get.find<UserController>();
  final authService = AuthService();

  // Tạo các TextEditingController
  late final TextEditingController _nameController;
  late final TextEditingController _phoneController;
  late final TextEditingController _emailController;

  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _nameController = TextEditingController(text: userController.fullName.value);
    _phoneController = TextEditingController(text: userController.phone.value);
    _emailController = TextEditingController(text: userController.email.value);
  }

  @override
  void dispose() {
    _nameController.dispose();
    _phoneController.dispose();
    _emailController.dispose();
    super.dispose();
  }

  // Hàm xử lý cập nhật
  Future<void> _handleUpdateProfile() async {
    setState(() => _isLoading = true);

    final result = await authService.updateProfile(
      fullName: _nameController.text,
      phone: _phoneController.text,
      email: _emailController.text,
    );

    setState(() => _isLoading = false);

    if (result['success']) {
      Get.back(result: true);

    } else {
      // Hiển thị lỗi (giữ nguyên, vì khi lỗi chúng ta không quay về)
      Get.snackbar(
        'Lỗi',
        result['message'],
        snackPosition: SnackPosition.BOTTOM,
        backgroundColor: Colors.red,
        colorText: Colors.white,
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: CusAppbar(
        title: Text('Edit Profile'),
        showBackArrow: true,
      ),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(AppSizes.defaultSpace),
          child: Column(
            children: [
              TextFormField(
                controller: _nameController,
                decoration: const InputDecoration(
                  labelText: 'Họ và tên (Full Name)',
                  prefixIcon: Icon(Iconsax.user_copy),
                ),
              ),
              const SizedBox(height: AppSizes.spaceBtwItems),
              TextFormField(
                controller: _phoneController,
                decoration: const InputDecoration(
                  labelText: 'Số điện thoại (Phone)',
                  prefixIcon: Icon(Iconsax.call_copy),
                ),
                keyboardType: TextInputType.phone,
              ),
              const SizedBox(height: AppSizes.spaceBtwItems),
              TextFormField(
                controller: _emailController,
                decoration: const InputDecoration(
                  labelText: 'Email',
                  prefixIcon: Icon(Iconsax.direct_copy),
                ),
                keyboardType: TextInputType.emailAddress,
              ),
              const SizedBox(height: AppSizes.spaceBtwSections),
              // Nút Lưu
              SizedBox(
                width: double.infinity,
                child: _isLoading
                    ? const Center(child: CircularProgressIndicator())
                    : ElevatedButton(
                        onPressed: _handleUpdateProfile,
                        child: const Text('Lưu thay đổi'),
                      ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}