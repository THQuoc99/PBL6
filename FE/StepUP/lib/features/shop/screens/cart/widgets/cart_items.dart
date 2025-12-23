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
    // Sử dụng Get.put để đảm bảo controller được khởi tạo nếu chưa có
    final controller = Get.put(CartController());

    return Obx(() {
      // Lọc danh sách item cần hiển thị
      // Nếu ở trang Checkout (showAddRemoveButtons = false) -> Chỉ lấy item được chọn
      // Nếu ở trang Cart (showAddRemoveButtons = true) -> Lấy tất cả
      final itemsToShow = showAddRemoveButtons 
          ? controller.cartItems 
          : controller.selectedItems;

      return ListView.separated(
        shrinkWrap: true,
        physics: const NeverScrollableScrollPhysics(),
        separatorBuilder: (_, __) => const SizedBox(height: AppSizes.spaceBtwSections),
        itemCount: itemsToShow.length,
        itemBuilder: (_, index) {
          final item = itemsToShow[index];

          // Nếu ở Checkout thì không cho vuốt xóa (Slidable)
          if (!showAddRemoveButtons) {
            return _buildItemContent(item, controller, context);
          }

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
                  label: 'Xóa',
                  borderRadius: BorderRadius.circular(AppSizes.cardRadiusMd),
                ),
              ],
            ),
            child: _buildItemContent(item, controller, context),
          );
        },
      );
    });
  }

  // Tách widget con để tái sử dụng
  Widget _buildItemContent(var item, var controller, BuildContext context) {
    return Row(
      children: [
        // CHECKBOX (Chỉ hiện ở màn hình Cart)
        if (showAddRemoveButtons) 
          Obx(() => Checkbox(
            value: item.isSelected.value,
            activeColor: AppColors.primary,
            // Tìm index thực trong list gốc để toggle chính xác
            onChanged: (value) {
               final realIndex = controller.cartItems.indexOf(item);
               if (realIndex != -1) controller.toggleSelection(realIndex);
            },
          )),

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
                          remove: (){
                            if (item.quantity > 1) { 
                              controller.updateQuantity(item.itemId, item.quantity - 1);
                            }
                          }
                        ),
                      ],
                    ),
                    // Hiển thị giá
                    ProductPriceText(
                      price: (item.subTotal > 0 
                          ? item.subTotal 
                          : item.price * item.quantity
                      ).toStringAsFixed(0)
                    ),
                  ],
                )
            ],
          ),
        ),
      ],
    );
  }
}