import 'package:flutter/material.dart';
import 'package:flutter_app/utils/helpers/auth_helper.dart';
import 'package:get/get.dart';
import 'package:iconsax_flutter/iconsax_flutter.dart';
import 'package:flutter_app/features/personalization/screens/address/address.dart';
import 'package:flutter_app/screens/account/profile/profile.dart';
import 'package:flutter_app/screens/notification/notification_screen.dart';
import 'package:flutter_app/screens/account/voucher/voucher_screen.dart';
import 'package:flutter_app/screens/account/security/security_screen.dart';
import 'package:flutter_app/screens/account/help/help_screen.dart';
import 'package:flutter_app/screens/home/components/section_heading.dart';
import 'package:flutter_app/widgets/list_title/setting_menu_title.dart';
import 'package:flutter_app/widgets/list_title/user_profile_title.dart';
import 'package:flutter_app/constants/sizes.dart';
import 'package:flutter_app/screens/home/components/primary_header_container.dart';
import 'package:flutter_app/widgets/appbar/appbar.dart';
import 'package:flutter_app/shop/services/auth_service.dart';
import 'package:flutter_app/screens/login/login_screen.dart';
import 'package:flutter_app/shop/controllers/user_controller.dart';

import 'package:flutter_app/screens/welcome/welcome_screen.dart';
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
                    showCart: true,
                    iconColor: Colors.white,
                    title: Text(
                      'Tài khoản của bạn',
                      style: Theme.of(context)
                          .textTheme
                          .headlineMedium!
                          .apply(color: Colors.white),
                    ),
                    actions: [],
                  ),
                  const SizedBox(height: AppSizes.spaceBtwSections),

                  // User Profile Card (Sử dụng Obx để cập nhật dữ liệu realtime)
                  Obx(
                    () {
                      final avatar = userController.avatar.value;
                      final isNetwork = avatar.isNotEmpty;
                      final display = isNetwork
                          ? (avatar.startsWith('/') ? 'http://10.0.2.2:8000$avatar' : avatar)
                          : null;
                      return UserProfileTitle(
                        title: userController.fullName.value.isEmpty ? 'Loading...' : userController.fullName.value,
                        subtitle: userController.email.value,
                        onPressed: () => Get.to(() => const ProfileScreen()),
                        imageUrl: display,
                        isNetwork: isNetwork,
                      );
                    },
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
                    title: 'Cài đặt',
                    showActionButton: false,
                  ),
                  const SizedBox(height: AppSizes.spaceBtwItems),

                  SettingMenuTitle(
                    icon: Iconsax.safe_home,
                    subtitle: 'Chỉnh sửa địa chỉ giao hàng',
                    title: 'Địa chỉ của tôi',
                    onTap: () async {
                      final ok = await requireLogin(context);
                      if (!ok) return;
                      Get.to(() => const UserAddressScreen());
                    },
                  ),
                  SettingMenuTitle(
                    icon: Iconsax.profile_2user,
                    subtitle: 'Chỉnh sửa thông tin cá nhân',
                    title: 'Hồ sơ của tôi',
                    // Điều hướng vào trang Profile giống như click vào header
                    onTap: () async {
                    final ok = await requireLogin(context);
                    if (!ok) return;
                    Get.to(() => const ProfileScreen());
                  },
                  ),
                  SettingMenuTitle(
                    icon: Iconsax.notification,
                    subtitle: 'Xem tất cả thông báo của bạn',
                    title: 'Thông báo',
                    onTap: () async {
                    final ok = await requireLogin(context);
                    if (!ok) return;
                    Get.to(() => const NotificationScreen());
                  },
                  ),
                  SettingMenuTitle(
                    icon: Iconsax.discount_shape,
                    subtitle: 'Voucher đã lưu và ưu đãi của bạn',
                    title: 'Voucher & Ưu đãi',
                    onTap: () async {
                    final ok = await requireLogin(context);
                    if (!ok) return;
                    Get.to(() => const VoucherScreen());
                  },
                  ),
                  SettingMenuTitle(
                    icon: Iconsax.shield_tick,
                    subtitle: 'Bảo mật tài khoản và xác thực',
                    title: 'Bảo mật',
                    onTap: () async {
                    final ok = await requireLogin(context);
                    if (!ok) return;
                    Get.to(() => const SecurityScreen());
                  },
                  ),
                 
                  const SizedBox(height: AppSizes.spaceBtwItems),
                  const SectionHeading(
                    title: 'Dịch vụ hỗ trợ khách hàng',
                    showActionButton: false,
                  ),
                  const SizedBox(height: AppSizes.spaceBtwItems),

                  SettingMenuTitle(
                    icon: Iconsax.support,
                    subtitle: 'Liên hệ nếu bạn cần trợ giúp',
                    title: 'Trợ giúp & Phản hồi',
                    onTap: () => Get.to(() => const HelpScreen()),
                  ),
                  const SizedBox(height: AppSizes.spaceBtwItems),

                  // --- ĐĂNG NHẬP / ĐĂNG XUẤT ---
                  Obx(() {
                    final isLoggedIn = userController.userID.value.isNotEmpty;
                    if (!isLoggedIn) {
                      return SettingMenuTitle(
                        icon: Iconsax.login,
                        subtitle: 'Đăng nhập để quản lý tài khoản',
                        title: 'Đăng nhập',
                        onTap: () async {
                          final result = await Get.to(() => const LoginScreen());
                          if (result == true) {
                            // Nếu login thành công, bạn có thể tải lại dữ liệu nếu cần
                            // userController.loadUserData(); // tuỳ chọn nếu muốn ép load lại
                          }
                        },
                      );
                    }

                    // Nếu đã đăng nhập — hiện nút Đăng xuất như trước
                    return SettingMenuTitle(
                      icon: Iconsax.logout,
                      subtitle: 'Thoát tài khoản hiện tại',
                      title: 'Đăng xuất',
                      onTap: () async {
                        final shouldLogout = await showDialog<bool>(
                          context: context,
                          builder: (BuildContext context) {
                            return AlertDialog(
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(12),
                              ),
                              title: const Text('Xác nhận đăng xuất'),
                              content: const Text('Bạn có chắc chắn muốn đăng xuất không?'),
                              actions: [
                                TextButton(
                                  onPressed: () => Navigator.of(context).pop(false),
                                  child: const Text('Hủy'),
                                ),
                                ElevatedButton(
                                  onPressed: () => Navigator.of(context).pop(true),
                                  style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
                                  child: const Text('Đăng xuất', style: TextStyle(color: Colors.white)),
                                ),
                              ],
                            );
                          },
                        );

                        if (shouldLogout == true) {
                          try {
                            await authService.logout();
                            Get.offAll(() => const WelcomeScreen());
                          } catch (e) {
                            ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Không thể đăng xuất: $e')));
                          }
                        }
                      },
                    );
                  }),
                ],
              ),
            )
          ],
        ),
      ),
    );
  }
}