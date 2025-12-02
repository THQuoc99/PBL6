import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:flutter_app/constants/sizes.dart';
import 'package:flutter_app/constants/colors.dart';
import 'package:flutter_app/utils/helpers/helper_function.dart';
import 'package:flutter_app/widgets/appbar/appbar.dart';
import 'package:flutter_app/widgets/containers/rounded_container.dart';
import 'package:flutter_app/common/widgets/products/cart/coupon_code_field.dart';
import 'package:flutter_app/features/shop/screens/cart/widgets/cart_items.dart';
import 'package:flutter_app/features/shop/screens/checkout/widgets/billing_address_section.dart';
import 'package:flutter_app/features/shop/screens/checkout/widgets/billing_amount_section.dart';
import 'widgets/billing_payment_section.dart';
import 'package:flutter_app/shop/controllers/cart_controller.dart';
import 'package:flutter_app/shop/controllers/order_controller.dart';
import 'package:flutter_app/shop/controllers/address_controller.dart'; // Import AddressController

class CheckoutScreen extends StatelessWidget {
  const CheckoutScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final dark = HelperFunction.isDarkMode(context);
    final cartController = Get.put(CartController()); 
    Get.put(AddressController());
    final orderController = Get.put(OrderController());

    return Scaffold(
      appBar: CusAppbar(
        title: Text('Checkout', style: Theme.of(context).textTheme.headlineSmall),
        showBackArrow: true,
      ),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(AppSizes.defaultSpace),
          child: Column(
            children: [
              // 1. List Items (Chỉ hiện những món được chọn)
              const CartItems(showAddRemoveButtons: false), 
              const SizedBox(height: AppSizes.spaceBtwSections),

              // 2. Coupon
              const CouponCode(),
              const SizedBox(height: AppSizes.spaceBtwSections),

              // 3. Billing Info
              RoundedContainer(
                showBorder: true,
                bgcolor: dark ? AppColors.dark : AppColors.light,
                padding: const EdgeInsets.all(AppSizes.md),
                child: const Column(
                  children: [
                    BillingAmountSection(), 
                    SizedBox(height: AppSizes.spaceBtwItems),
                    Divider(),
                    SizedBox(height: AppSizes.spaceBtwItems),
                    
                    BillingPaymentSection(), 
                    
                    SizedBox(height: AppSizes.spaceBtwItems),
                    Divider(),
                    SizedBox(height: AppSizes.spaceBtwItems),
                    
                    BillingAddressSection() 
                  ],
                ),
              )
            ],
          ),
        ),
      ),

      // 4. Checkout Button
      bottomNavigationBar: Padding(
        padding: const EdgeInsets.all(AppSizes.defaultSpace),
        child: Obx(() => ElevatedButton(
          // Gọi hàm processOrder khi nhấn
          onPressed: orderController.isLoading.value 
              ? null 
              : () => orderController.processOrder(),
          child: orderController.isLoading.value
              ? const SizedBox(
                  width: 20, 
                  height: 20, 
                  child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2)
                )
              : Text('Checkout \$${cartController.totalAmount.value.toStringAsFixed(0)}'),
        )),
      ),
    );
  }
}