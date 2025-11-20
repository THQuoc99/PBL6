import 'package:flutter/material.dart';
import 'package:flutter_app/constants/image_string.dart';
import 'package:flutter_app/constants/sizes.dart';
import 'package:flutter_app/screens/home/components/section_heading.dart';
import 'package:flutter_app/widgets/appbar/appbar.dart';
import 'package:flutter_app/widgets/image/circular_image.dart';
import './widgets/profile_menu.dart';
import 'package:get/get.dart'; // Import GetX
import 'package:flutter_app/shop/controllers/user_controller.dart'; // Import Controller
import 'package:flutter_app/screens/account/profile/edit_profile_screen.dart';

class ProfileScreen extends StatelessWidget
{
  const ProfileScreen({
    super.key,
    });

  @override
  Widget build(BuildContext context) {
    //  Lấy UserController
    final userController = Get.find<UserController>();

    void navigateToEditProfile() async {
      // Dùng `await` để chờ màn hình EditProfile đóng
      final result = await Get.to(() => const EditProfileScreen());

      // Sau khi màn hình EditProfile đóng (Get.back(result: true)),
      // kiểm tra kết quả trả về
      if (result == true) {
        // Hiển thị SnackBar thành công TẠI ĐÂY (màn hình Profile)
        Get.snackbar(
          'Thành công',
          'Cập nhật thông tin thành công!',
          snackPosition: SnackPosition.BOTTOM,
          backgroundColor: Colors.green,
          colorText: Colors.white,
        );
        
        // GHI CHÚ: Nếu dữ liệu không tự cập nhật sau khi sửa,
        // bạn có thể cần gọi lại hàm fetch user ở đây, ví dụ:
        // userController.fetchUserData();
      }
    }

    return Scaffold(
      appBar: CusAppbar(
        title: Text('Profile'),
        showBackArrow: true,
      ),

      body: SingleChildScrollView(
        child: Padding(
          padding: EdgeInsets.all(AppSizes.defaultSpace),
          child: Obx(() => Column(
            children: [
              // Profile Avatar
              SizedBox(
                width: double.infinity,
                child: Column(
                  children: [
                    CircularImage(image: AppImages.sabrina, width: 80, height: 80,),
                    TextButton(onPressed: (){}, child: const Text('Change profile image')),
                  ],
                ),
              ),

              // Detail
              const SizedBox(height: AppSizes.spaceBtwItems/2,),
              const Divider(),
              const SizedBox(height: AppSizes.spaceBtwItems,),

              const SectionHeading(title: 'Profile Infomation', showActionButton: false,),
              const SizedBox(height: AppSizes.spaceBtwItems,),

              // ✅ SỬA: Thay thế dữ liệu tĩnh bằng dữ liệu động
              ProfileMenu(title: 'Name', value: userController.fullName.value, onPressed: navigateToEditProfile,),
              ProfileMenu(title: 'Username', value: userController.username.value, onPressed: () {},),

              const SizedBox(height: AppSizes.spaceBtwItems/2,),
              const Divider(),
              const SizedBox(height: AppSizes.spaceBtwItems,),

              const SectionHeading(title: 'Personal Infomation', showActionButton: false,),
              const SizedBox(height: AppSizes.spaceBtwItems,),

              ProfileMenu(title: 'UserID', value: '#${userController.userID.value}', onPressed: () {}), 
              
              if (userController.phone.value.isNotEmpty)
                ProfileMenu(
                  title: 'Phone Number', 
                  value: userController.phone.value, 
                  onPressed: navigateToEditProfile,
                )
              else
                 ProfileMenu(
                  title: 'Phone Number', 
                  value: 'Chưa cập nhật', 
                  onPressed: navigateToEditProfile,
                ),
              
              ProfileMenu(
                title: 'Email', 
                value: userController.email.value, 
                onPressed: navigateToEditProfile,
              ),
              // (Các trường này chưa có trong Model, tạm thời giữ nguyên)
              ProfileMenu(title: 'Gender', value: 'Male', onPressed: () {},),
              ProfileMenu(title: 'Birthday', value: '28/08/2004', onPressed: () {},),
            ],
          )),
        ),
      ),
    );
  }
}