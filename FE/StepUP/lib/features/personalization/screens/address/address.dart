import 'package:flutter/material.dart';
import 'package:flutter_app/constants/colors.dart';
import 'package:flutter_app/constants/sizes.dart';
import 'package:flutter_app/features/personalization/screens/address/widgets/single_address.dart';
import 'package:flutter_app/widgets/appbar/appbar.dart';
import 'package:get/get.dart';
import 'add_new_address.dart';

class UserAddressScreen extends StatelessWidget {
  const UserAddressScreen({
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      floatingActionButton: FloatingActionButton(
        backgroundColor: AppColors.primary,
        onPressed: () => Get.to(() => const AddNewAddressScreen()),
        child: const Icon(Icons.add, color: Colors.white,),
      ),
      appBar: CusAppbar(
        showBackArrow: true,
        title: Text('Address', style: Theme.of(context).textTheme.headlineSmall,),
      ),

      body: SingleChildScrollView(
        child: Padding(
          padding: EdgeInsets.all(AppSizes.defaultSpace),
          child: Column(
            children: [
              SingleAddress(isSelected: true,),
              SingleAddress(isSelected: false,),
              SingleAddress(isSelected: false,),
              SingleAddress(isSelected: false,),
            ],
          ),
        ),
      ),
    );
  }
}