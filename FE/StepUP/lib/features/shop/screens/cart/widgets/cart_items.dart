import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:flutter_slidable/flutter_slidable.dart';
import 'package:flutter_app/constants/sizes.dart';
import 'package:flutter_app/constants/colors.dart';
import 'package:flutter_app/shop/controllers/cart_controller.dart';
import 'package:flutter_app/widgets/texts/product_price_text.dart';
import 'package:flutter_app/common/widgets/products/cart/cart_item.dart'; 
import 'package:flutter_app/common/widgets/products/cart/product_quantity_add_minus.dart';

class CartItems extends StatelessWidget {
  final bool showAddRemoveButtons;

  const CartItems({
    super.key,
    this.showAddRemoveButtons = true,
  });

  @override
  Widget build(BuildContext context) {
    final controller = Get.find<CartController>();

    return Obx(
      () => ListView.separated(
        shrinkWrap: true,
        physics: const NeverScrollableScrollPhysics(),
        separatorBuilder: (_, __) => const SizedBox(height: AppSizes.spaceBtwSections),
        itemCount: controller.cartItems.length,
        itemBuilder: (_, index) {
          final item = controller.cartItems[index];

          return Slidable(
            key: ValueKey(item.itemId),
            endActionPane: ActionPane(
              motion: const ScrollMotion(),
              extentRatio: 0.25,
              children: [
                SlidableAction(
                  onPressed: (context) => controller.removeItem(item.itemId),
                  backgroundColor: Colors.red,
                  foregroundColor: Colors.white,
                  icon: Icons.delete,
                  label: 'Delete',
                  borderRadius: BorderRadius.circular(AppSizes.cardRadiusMd),
                ),
              ],
            ),
            child: Row(
              children: [
                // ✅ THÊM CHECKBOX (Chỉ hiện ở màn hình Cart, ẩn ở Checkout)
                if (showAddRemoveButtons) 
                  Obx(() => Checkbox(
                    value: item.isSelected.value,
                    activeColor: AppColors.primary,
                    onChanged: (value) {
                      // Gọi hàm toggleSelection trong controller
                      controller.toggleSelection(index);
                    },
                  )),

                // Phần nội dung chính (Expanded để chiếm hết phần còn lại)
                Expanded(
                  child: Column(
                    children: [
                      CartItem(cartItem: item), 

                      if (showAddRemoveButtons) 
                        const SizedBox(height: AppSizes.spaceBtwItems),

                      if (showAddRemoveButtons)
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Row(
                              children: [
                                const SizedBox(width: 70),
                                ProductQuantityAddMinus(
                                  quantity: item.quantity,
                                  add: () => controller.updateQuantity(item.itemId, item.quantity + 1),
                                  remove: () => controller.updateQuantity(item.itemId, item.quantity - 1),
                                ),
                              ],
                            ),
                            // ✅ Hiển thị giá tổng của item (Giá x Số lượng)
                            ProductPriceText(
                              price: (item.price * item.quantity).toStringAsFixed(0)
                            ),
                          ],
                        )
                    ],
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }
}