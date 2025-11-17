import 'package:flutter/material.dart';
//import 'package:flutter_app/constants.dart';
import 'package:flutter_app/screens/welcome/welcome_screen.dart';
import 'package:get/get.dart';
import 'package:flutter_app/utils/theme/theme.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return GetMaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'E commerce App',
      themeMode: ThemeMode.system,
      theme: AppTheme.lightTheme,
      darkTheme: AppTheme.darkTheme,
      home: WelcomeScreen(),
    );
  }
}

