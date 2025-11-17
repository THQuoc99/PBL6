import 'package:flutter/material.dart';
import 'package:flutter_app/features/personalization/screens/address/address.dart';
import 'package:flutter_app/screens/account/profile/profile.dart';
import 'package:flutter_app/screens/home/components/section_heading.dart';
import 'package:flutter_app/widgets/list_title/setting_menu_title.dart';
import 'package:flutter_app/widgets/list_title/user_profile_title.dart';
import 'package:flutter_app/constants/sizes.dart';
import 'package:flutter_app/screens/home/components/primary_header_container.dart';
import 'package:flutter_app/widgets/appbar/appbar.dart';
import 'package:get/get.dart';
import 'package:iconsax_flutter/iconsax_flutter.dart';


class SettingScreen extends StatelessWidget{
  const SettingScreen(
    {
      super.key,
    }
  );

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SingleChildScrollView(
        child: Column(
          children: [
            //Header
            PrimaryHeaderContainer(
              child: Column(
                children: [
                  //App bar
                  CusAppbar(title: Text('Account', style: Theme.of(context).textTheme.headlineMedium!.apply(color: Colors.white)), ),
                  const SizedBox(height: AppSizes.spaceBtwSections,),

                  //Profile User
                  UserProfileTitle(onPressed: () => Get.to(()=>const ProfileScreen()),),
                  const SizedBox(height: AppSizes.spaceBtwSections,),
                ],
              ),
            ),

            // Body
            Padding(
              padding: EdgeInsets.all(AppSizes.defaultSpace),
              child: Column(
                children: [
                  SectionHeading(title: 'Account Settings', showActionButton: false,),
                  SizedBox(height: AppSizes.spaceBtwItems,),

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
                    onTap: () {},
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
                    onTap: () {},
                  ),
                  SettingMenuTitle(
                    icon: Iconsax.shield,
                    subtitle: 'Improve your account protect',
                    title: 'Privacy',
                    onTap: () {},
                  ),

                  // 
                  SizedBox(height: AppSizes.spaceBtwItems,),
                  SectionHeading(title: 'Customer Service', showActionButton: false,),
                  SizedBox(height: AppSizes.spaceBtwItems,),

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

