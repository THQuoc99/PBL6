import 'package:flutter/material.dart';
import 'package:flutter_app/constants/sizes.dart';
import 'package:flutter_app/widgets/appbar/appbar.dart';
import 'package:get/get.dart';
import '../checkout/checkout.dart';
import 'package:flutter_app/shop/controllers/cart_controller.dart';
import 'package:flutter_app/features/shop/screens/cart/widgets/cart_items.dart';

class CartScreen extends StatelessWidget {
  final bool showBackArrow;
  

  const CartScreen({
    super.key,
    this.showBackArrow = false,
  });

  @override
  Widget build(BuildContext context) {
    final controller = Get.put(CartController());

    return Scaffold(
      appBar: CusAppbar(
        title: Text('Cart', style: Theme.of(context).textTheme.headlineSmall),
        showBackArrow: showBackArrow, 
      ),
      body: Obx(() {
        if (controller.isLoading.value) {
          return const Center(child: CircularProgressIndicator());
        }
        
        if (controller.cartItems.isEmpty) {
          return const Center(child: Text("Giỏ hàng trống"));
        }

        return Padding(
          padding: const EdgeInsets.all(AppSizes.defaultSpace),
          child: const CartItems(), 
        );
      }),
      
      bottomNavigationBar: Obx(() {
        // Kiểm tra xem có sản phẩm nào được chọn không
        final hasSelectedItems = controller.cartItems.any((item) => item.isSelected.value);
        
        return Padding(
          padding: const EdgeInsets.all(AppSizes.defaultSpace),
          child: SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: hasSelectedItems
                  ? () => Get.to(() => const CheckoutScreen())
                  : null, // Disable nút nếu không chọn gì
              child: Text('Checkout \$${controller.totalAmount.value.toStringAsFixed(0)}'),
            ),
          ),
        );
      }),
    );
  }
}