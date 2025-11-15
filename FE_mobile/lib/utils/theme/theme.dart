import 'package:flutter/material.dart';
import 'package:flutter_app/utils/theme/custom_themes/appbar_theme.dart';
import 'package:flutter_app/utils/theme/custom_themes/bottom_sheet_theme.dart';
import 'package:flutter_app/utils/theme/custom_themes/elevated_button_theme.dart';
import 'package:flutter_app/utils/theme/custom_themes/text_field_theme.dart';
import 'package:flutter_app/utils/theme/custom_themes/text_theme.dart';

class AppTheme {
  AppTheme._();

  static ThemeData lightTheme = ThemeData(
    useMaterial3: true,
    brightness: Brightness.light,
    primaryColor: Color.fromARGB(255, 48, 196, 230),
    scaffoldBackgroundColor: Colors.white,
    textTheme: AppTextTheme.lightTextTheme,
    elevatedButtonTheme: AppElevatedButtonTheme.lightElevatedButtonTheme,
    appBarTheme: MyAppbarTheme.lightAppbarTheme,
    bottomSheetTheme: AppBottomSheetTheme.lightBottomSheetTheme,
    inputDecorationTheme: AppTextFormFieldTheme.lightInputDecorationTheme
  );
  static ThemeData darkTheme = ThemeData(
    useMaterial3: true,
    brightness: Brightness.dark,
    primaryColor: Color.fromARGB(255, 48, 196, 230),
    scaffoldBackgroundColor: Colors.black,
    textTheme: AppTextTheme.darkTextTheme,
    elevatedButtonTheme: AppElevatedButtonTheme.darkElevatedButtonTheme,
    appBarTheme: MyAppbarTheme.darkAppbarTheme,
    bottomSheetTheme: AppBottomSheetTheme.darkBottomSheetTheme,
    inputDecorationTheme: AppTextFormFieldTheme.darkInputDecorationTheme
  );
}