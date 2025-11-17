import 'package:flutter/material.dart';
import 'package:flutter_app/common/widgets/success_screen/success_screen.dart';
import 'package:flutter_app/constants/image_string.dart';
import 'package:flutter_app/navigation_menu.dart';
import 'package:get/get.dart';
import 'package:flutter_app/constants/sizes.dart';
import 'package:flutter_app/features/shop/screens/cart/widgets/cart_items.dart';
import 'package:flutter_app/features/shop/screens/checkout/widgets/billing_address_section.dart';
//import 'package:flutter_app/features/shop/screens/checkout/widgets/billing_address_section.dart';
import 'package:flutter_app/features/shop/screens/checkout/widgets/billing_amount_section.dart';
import 'package:flutter_app/utils/helpers/helper_function.dart';
import 'package:flutter_app/widgets/appbar/appbar.dart';
import 'package:flutter_app/common/widgets/products/cart/coupon_code_field.dart';
import 'package:flutter_app/widgets/containers/rounded_container.dart';
import 'package:flutter_app/constants/colors.dart';
import 'widgets/billing_payment_section.dart';


class CheckoutScreen extends StatelessWidget{
  const CheckoutScreen({
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    final dark = HelperFunction.isDarkMode(context);
    return Scaffold(
      appBar: CusAppbar(
        title: const Text('Checkout'),
        showBackArrow: true,
      ),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(AppSizes.defaultSpace),
          child: Column(
            children: [
              const CartItems(showRemoveButton: false,),
              const SizedBox(height: AppSizes.spaceBtwSections),

              // coupon
              CouponCode(),
              const SizedBox(height: AppSizes.spaceBtwSections),
              // billing & payment
              RoundedContainer(
                showBorder: true,
                bgcolor: dark ? AppColors.dark : AppColors.light,
                padding: const EdgeInsets.only(top: AppSizes.sm, bottom: AppSizes.sm, right: AppSizes.sm, left: AppSizes.md),
                child: Column(
                  children: [

                    BillingAmountSection(),
                    const SizedBox(height: AppSizes.spaceBtwItems),

                    // devider
                    const Divider(),
                    const SizedBox(height: AppSizes.spaceBtwItems),

                    BillingPaymentSection(),

                    const SizedBox(height: AppSizes.spaceBtwItems),
                    const Divider(),
                    const SizedBox(height: AppSizes.spaceBtwItems),

                    // Address
                    BillingAddressSection()

                  ],
                ),
              )
            ],
          ),
        ),
      ),

      // checkout button
      bottomNavigationBar: Padding(
        padding: const EdgeInsets.all(AppSizes.defaultSpace),
        child: ElevatedButton(
          onPressed: () => Get.to(
            () => SuccessScreen(
              image: AppImages.checkoutsuccess,
              onPressed: () => Get.offAll(()=> const NavigationMenu()),
              subTitle: 'Your item will be shipped soon',
              title: 'Payment Success'
            ),
          ),
          child: const Text('Checkout'),
        ),
      ),
    );
  }
}

