import 'package:flutter_app/utils/helpers/auth_helper.dart';
import 'package:get/get.dart';
import 'package:flutter_app/shop/controllers/user_controller.dart';
import 'package:flutter_app/screens/account/profile/edit_profile_screen.dart'; // Check đường dẫn import
import 'package:flutter/material.dart';
import 'package:flutter_app/constants/image_string.dart';
import 'package:flutter_app/constants/sizes.dart';
import 'package:flutter_app/screens/home/components/section_heading.dart';
import 'package:flutter_app/widgets/appbar/appbar.dart';
import 'package:flutter_app/widgets/image/circular_image.dart';
import './widgets/profile_menu.dart';


class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final userController = Get.find<UserController>();

    return Scaffold(
      appBar: const CusAppbar(title: Text('Profile'), showBackArrow: true,),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(AppSizes.defaultSpace),
        child: Obx(() => Column(
          children: [
            // Profile Avatar
            SizedBox(
              width: double.infinity,
              child: Column(
                children: [
                  // Hiển thị ảnh từ mạng hoặc fallback ảnh nội bộ
                  userController.avatar.value.isNotEmpty
                      ? CircularImage(
                          image: userController.avatar.value, 
                          isNetworkImage: true, 
                          width: 80, height: 80
                        )
                      
                      : CircularImage(image: AppImages.sabrina, width: 80, height: 80),
                  
                  TextButton(
                    onPressed: () async {
                      final ok = await requireLogin(context);
                      if (ok) Get.to(() => const EditProfileScreen());
                    },
                    child: const Text('Thay đổi ảnh đại diện')
                  ),
                ],
              ),
            ),

            const SizedBox(height: AppSizes.spaceBtwItems / 2),
            const Divider(),
            const SizedBox(height: AppSizes.spaceBtwItems),

            const SectionHeading(title: 'Thông tin cá nhân', showActionButton: false,),
            const SizedBox(height: AppSizes.spaceBtwItems),

            ProfileMenu(title: 'Họ tên', value: userController.fullName.value, onPressed: () async {
    final ok = await requireLogin(context);
    if (ok) Get.to(() => const EditProfileScreen());
  },),
            ProfileMenu(title: 'Tên đăng nhập', value: userController.username.value, onPressed: () {}),

            const SizedBox(height: AppSizes.spaceBtwItems / 2),
            const Divider(),
            const SizedBox(height: AppSizes.spaceBtwItems),

            const SectionHeading(title: 'Thông tin cá nhân', showActionButton: false,),
            const SizedBox(height: AppSizes.spaceBtwItems),

            ProfileMenu(title: 'ID', value: userController.userID.value, icon: Icons.copy, onPressed: () {}),
            ProfileMenu(title: 'E-mail', value: userController.email.value, onPressed: () async {
    final ok = await requireLogin(context);
    if (ok) Get.to(() => const EditProfileScreen());
  },),
            ProfileMenu(title: 'Số điện thoại', value: userController.phone.value, onPressed: () async {
    final ok = await requireLogin(context);
    if (ok) Get.to(() => const EditProfileScreen());
  },),
            
            ProfileMenu(
                title: 'Ngày sinh', 
                value: userController.birthDate.value.isNotEmpty ? userController.birthDate.value : "Chưa cập nhật", 
                onPressed: () async {
    final ok = await requireLogin(context);
    if (ok) Get.to(() => const EditProfileScreen());
  },
            ),
          ],
        )),
      ),
    );
  }
}