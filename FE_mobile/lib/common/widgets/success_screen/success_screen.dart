import 'package:flutter/material.dart';
import 'package:flutter_app/constants/device_utility.dart';
import 'package:flutter_app/constants/sizes.dart';

class SuccessScreen extends StatelessWidget {
  final String image, title, subTitle;
  final VoidCallback onPressed;
  const SuccessScreen({
    super.key,
    required this.image,
    required this.onPressed,
    required this.subTitle,
    required this.title
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(AppSizes.defaultSpace),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              // Thêm khoảng trống ở trên để căn giữa màn hình hơn
              const SizedBox(height: AppSizes.spaceBtwSections * 2),

              // Ảnh
              Image(
                image: AssetImage(image), // <-- Dùng tham số 'image'
                width: AppDeviceUtility.getScreenWidth(context) * 0.6,
              ),
              const SizedBox(height: AppSizes.spaceBtwSections),

              // Title
              Text(
                title, // <-- Dùng tham số 'title'
                style: Theme.of(context).textTheme.headlineMedium,
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: AppSizes.spaceBtwItems),

              // SubTitle
              Text(
                subTitle, // <-- Dùng tham số 'subTitle'
                style: Theme.of(context).textTheme.labelMedium,
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: AppSizes.spaceBtwSections * 2),

              // Button
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: onPressed, // <-- Dùng tham số 'onPressed'
                  child: const Text('Tiếp tục'),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}