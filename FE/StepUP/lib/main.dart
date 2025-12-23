import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:flutter_app/utils/theme/theme.dart';
import 'package:flutter_app/navigation_menu.dart';
import 'package:flutter_app/shop/controllers/user_controller.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  // Put UserController early so other controllers (Wishlist, etc.) can find it
  Get.put(UserController());
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return GetMaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'E commerce App',
      themeMode: ThemeMode.system,
      theme: AppTheme.lightTheme,
      darkTheme: AppTheme.darkTheme,
      home: const NavigationMenu(), // Bắt đầu trực tiếp vào app (bỏ Welcome)
    );
  }
}

