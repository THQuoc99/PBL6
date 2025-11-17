import 'package:flutter/material.dart';
import 'package:flutter_app/constants/sizes.dart';
import 'package:flutter_app/widgets/appbar/appbar.dart';
import 'package:iconsax_flutter/iconsax_flutter.dart';

class AddNewAddressScreen extends StatelessWidget {
  const AddNewAddressScreen({
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: CusAppbar(
        title: const Text('Add New Address'),
        showBackArrow: true,
      ),
      body: SingleChildScrollView(
        child: Padding(
          padding: EdgeInsets.all(AppSizes.defaultSpace),
          child: Form(
            child: Column(
              children: [
                TextFormField(decoration: const InputDecoration(prefixIcon: Icon(Iconsax.user), labelText: 'Name'),),
                const SizedBox(height: AppSizes.spaceBtwInputFields,),
                TextFormField(decoration: const InputDecoration(prefixIcon: Icon(Iconsax.mobile), labelText: 'Phone Number'),),
                const SizedBox(height: AppSizes.spaceBtwInputFields,),
                Row(
                  children: [
                    Expanded(child: TextFormField(decoration: const InputDecoration(prefixIcon: Icon(Iconsax.building_3), labelText: 'Street'),)),
                    const SizedBox(width: AppSizes.spaceBtwInputFields,),
                    Expanded(child: TextFormField(decoration: const InputDecoration(prefixIcon: Icon(Iconsax.location), labelText: 'Ward - District'),)),
                  ],
                ),
                const SizedBox(height: AppSizes.spaceBtwInputFields,),
                TextFormField(decoration: const InputDecoration(prefixIcon: Icon(Iconsax.building), labelText: 'City'),),
                const SizedBox(height: AppSizes.defaultSpace,),
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(onPressed: (){}, child: Text('Save')),
                )
              ],
            ),
          ),
        ),
      )
    );
  }
}