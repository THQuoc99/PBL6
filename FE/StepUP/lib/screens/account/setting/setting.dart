import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:iconsax_flutter/iconsax_flutter.dart';
import 'package:flutter_app/features/personalization/screens/address/address.dart';
import 'package:flutter_app/screens/account/profile/profile.dart';
import 'package:flutter_app/screens/home/components/section_heading.dart';
import 'package:flutter_app/widgets/list_title/setting_menu_title.dart';
import 'package:flutter_app/widgets/list_title/user_profile_title.dart';
import 'package:flutter_app/constants/sizes.dart';
import 'package:flutter_app/screens/home/components/primary_header_container.dart';
import 'package:flutter_app/widgets/appbar/appbar.dart';
import 'package:flutter_app/shop/services/auth_service.dart';
import 'package:flutter_app/screens/login/login_screen.dart';
import 'package:flutter_app/shop/controllers/user_controller.dart';
import 'package:flutter_app/features/shop/screens/cart/cart.dart';
class SettingScreen extends StatelessWidget {
  const SettingScreen({super.key});

  @override
  Widget build(BuildContext context) {
    // Khởi tạo AuthService và lấy UserController
    final AuthService authService = AuthService();
    final UserController userController = Get.find<UserController>();

    return Scaffold(
      body: SingleChildScrollView(
        child: Column(
          children: [
            // --- HEADER ---
            PrimaryHeaderContainer(
              child: Column(
                children: [
                  // App bar với nút Logout
                  CusAppbar(
                    title: Text(
                      'Account',
                      style: Theme.of(context)
                          .textTheme
                          .headlineMedium!
                          .apply(color: Colors.white),
                    ),
                    actions: [
                      IconButton(
                        icon: const Icon(Iconsax.logout, color: Colors.white),
                        tooltip: 'Logout',
                        onPressed: () async {
                          try {
                            await authService.logout();
                            // Dùng offAll để xóa lịch sử điều hướng, tránh user back lại được
                            Get.offAll(() => const LoginScreen());
                          } catch (e) {
                            Get.snackbar(
                              'Lỗi',
                              'Không thể đăng xuất: $e',
                              snackPosition: SnackPosition.BOTTOM,
                              backgroundColor: Colors.redAccent,
                              colorText: Colors.white,
                            );
                          }
                        },
                      )
                    ],
                  ),
                  const SizedBox(height: AppSizes.spaceBtwSections),

                  // User Profile Card (Sử dụng Obx để cập nhật dữ liệu realtime)
                  Obx(
                    () => UserProfileTitle(
                      // Hiển thị loading nếu tên đang trống (tuỳ chọn)
                      title: userController.fullName.value.isEmpty 
                          ? 'Loading...' 
                          : userController.fullName.value,
                      subtitle: userController.email.value,
                      onPressed: () => Get.to(() => const ProfileScreen()),
                    ),
                  ),
                  const SizedBox(height: AppSizes.spaceBtwSections),
                ],
              ),
            ),

            // --- BODY ---
            Padding(
              padding: const EdgeInsets.all(AppSizes.defaultSpace),
              child: Column(
                children: [
                  const SectionHeading(
                    title: 'Account Settings',
                    showActionButton: false,
                  ),
                  const SizedBox(height: AppSizes.spaceBtwItems),

                  SettingMenuTitle(
                    icon: Iconsax.safe_home,
                    subtitle: 'Delivery Address',
                    title: 'My Address',
                    onTap: () => Get.to(() => const UserAddressScreen()),
                  ),
                  SettingMenuTitle(
                    icon: Iconsax.profile_2user,
                    subtitle: 'Edit your profile',
                    title: 'My profile',
                    // Điều hướng vào trang Profile giống như click vào header
                    onTap: () => Get.to(() => const ProfileScreen()),
                  ),
                  SettingMenuTitle(
                    icon: Iconsax.bank,
                    subtitle: 'Add your payment method',
                    title: 'Payment',
                    onTap: () {},
                  ),
                  SettingMenuTitle(
                    icon: Iconsax.notification,
                    subtitle: 'Check your noti',
                    title: 'Notification',
                    onTap: () {},
                  ),
                  SettingMenuTitle(
                    icon: Iconsax.shopping_cart,
                    subtitle: 'Your cart settings',
                    title: 'Cart',
                    onTap: () => Get.to(() => const CartScreen(showBackArrow: true)),
                  ),
                  SettingMenuTitle(
                    icon: Iconsax.shield,
                    subtitle: 'Improve your account protect',
                    title: 'Privacy',
                    onTap: () {},
                  ),

                  const SizedBox(height: AppSizes.spaceBtwItems),
                  const SectionHeading(
                    title: 'Customer Service',
                    showActionButton: false,
                  ),
                  const SizedBox(height: AppSizes.spaceBtwItems),

                  SettingMenuTitle(
                    icon: Iconsax.support,
                    subtitle: 'Inbox if you need help',
                    title: 'Help Center',
                    onTap: () {},
                  ),
                  SettingMenuTitle(
                    icon: Iconsax.star,
                    subtitle: 'Give us your feeling',
                    title: 'Feedback',
                    onTap: () {},
                  ),
                ],
              ),
            )
          ],
        ),
      ),
    );
  }
}