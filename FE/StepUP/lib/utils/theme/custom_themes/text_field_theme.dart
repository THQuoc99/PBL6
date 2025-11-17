import 'package:flutter/material.dart';
import 'package:flutter_app/constants/colors.dart';
import 'package:flutter_app/constants/sizes.dart';

class AppTextFormFieldTheme{
  AppTextFormFieldTheme._();

  static InputDecorationTheme lightInputDecorationTheme = InputDecorationTheme(
    errorMaxLines: 3,
    prefixIconColor: AppColors.darkGray,
    suffixIconColor: AppColors.darkGray,

    labelStyle: const TextStyle().copyWith(fontSize: AppSizes.fontSizeMd, color: AppColors.black),
    hintStyle: const TextStyle().copyWith(fontSize: AppSizes.fontSizeMd, color: AppColors.grey),
    errorStyle: const TextStyle().copyWith(fontStyle: FontStyle.normal),
    floatingLabelStyle: const TextStyle().copyWith(color: AppColors.black.withAlpha(200)),

    border: const OutlineInputBorder().copyWith(
      borderRadius: BorderRadius.circular(AppSizes.inputFieldRadius),
      borderSide: const BorderSide(width: 1, color: AppColors.grey),
    ),

    enabledBorder: const OutlineInputBorder().copyWith(
      borderRadius: BorderRadius.circular(AppSizes.inputFieldRadius),
      borderSide: const BorderSide(width: 1, color: AppColors.grey),
    ),

    focusedBorder:const OutlineInputBorder().copyWith(
      borderRadius: BorderRadius.circular(AppSizes.inputFieldRadius),
      borderSide: const BorderSide(width: 1, color: AppColors.dark),
    ),
    errorBorder: const OutlineInputBorder().copyWith(
      borderRadius: BorderRadius.circular(AppSizes.inputFieldRadius),
      borderSide: const BorderSide(width: 1, color: AppColors.warning),
    ),
    focusedErrorBorder: const OutlineInputBorder().copyWith(
      borderRadius: BorderRadius.circular(AppSizes.inputFieldRadius),
      borderSide: const BorderSide(width: 2, color: AppColors.warning),
    ),
  );

  static InputDecorationTheme darkInputDecorationTheme = InputDecorationTheme(
    errorMaxLines: 3,
    prefixIconColor: AppColors.grey,
    suffixIconColor: AppColors.grey,

    labelStyle: const TextStyle().copyWith(fontSize: AppSizes.fontSizeMd, color: AppColors.white),
    hintStyle: const TextStyle().copyWith(fontSize: AppSizes.fontSizeMd, color: AppColors.grey),
    errorStyle: const TextStyle().copyWith(fontStyle: FontStyle.normal),
    floatingLabelStyle: const TextStyle().copyWith(color: AppColors.white.withAlpha(200)),

    border: const OutlineInputBorder().copyWith(
      borderRadius: BorderRadius.circular(AppSizes.inputFieldRadius),
      borderSide: const BorderSide(width: 1, color: AppColors.grey),
    ),

    enabledBorder: const OutlineInputBorder().copyWith(
      borderRadius: BorderRadius.circular(AppSizes.inputFieldRadius),
      borderSide: const BorderSide(width: 1, color: AppColors.grey),
    ),

    focusedBorder:const OutlineInputBorder().copyWith(
      borderRadius: BorderRadius.circular(AppSizes.inputFieldRadius),
      borderSide: const BorderSide(width: 1, color: AppColors.light),
    ),

    errorBorder: const OutlineInputBorder().copyWith(
      borderRadius: BorderRadius.circular(AppSizes.inputFieldRadius),
      borderSide: const BorderSide(width: 1, color: AppColors.warning),
    ),

    focusedErrorBorder: const OutlineInputBorder().copyWith(
      borderRadius: BorderRadius.circular(AppSizes.inputFieldRadius),
      borderSide: const BorderSide(width: 2, color: AppColors.warning),
    ),

    
  );
}