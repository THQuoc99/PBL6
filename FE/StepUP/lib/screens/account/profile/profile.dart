import 'package:flutter/material.dart';
import 'package:flutter_app/constants/image_string.dart';
import 'package:flutter_app/constants/sizes.dart';
import 'package:flutter_app/screens/home/components/section_heading.dart';
import 'package:flutter_app/widgets/appbar/appbar.dart';
import 'package:flutter_app/widgets/image/circular_image.dart';
import './widgets/profile_menu.dart';

class ProfileScreen extends StatelessWidget
{
  

  const ProfileScreen({
    super.key,
    
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: CusAppbar(
        title: Text('Profile'),
        showBackArrow: true,
      ),


      body: SingleChildScrollView(
        child: Padding(
          padding: EdgeInsets.all(AppSizes.defaultSpace),
          child: Column(
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

              ProfileMenu(title: 'Name', value: 'Nguyen Viet', onPressed: () {},),
              ProfileMenu(title: 'Username', value: 'TestUser', onPressed: () {},),

              const SizedBox(height: AppSizes.spaceBtwItems/2,),
              const Divider(),
              const SizedBox(height: AppSizes.spaceBtwItems,),

              const SectionHeading(title: 'Profile Infomation', showActionButton: false,),
              const SizedBox(height: AppSizes.spaceBtwItems,),

              ProfileMenu(title: 'UserID', value: 'A00001', onPressed: () {},),
              ProfileMenu(title: 'Phone Number', value: '0122032120', onPressed: () {},),
              ProfileMenu(title: 'Email', value: 'vietnguyen@gmail.com', onPressed: () {},),
              ProfileMenu(title: 'Gender', value: 'Male', onPressed: () {},),
              ProfileMenu(title: 'Birthday', value: '28/08/2004', onPressed: () {},),
              //ProfileMenu(title: 'Username', value: '0122032120', onPressed: () {},),
            ],
          ),
        ),
      ),
    );
  }
}



