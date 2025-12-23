import 'package:flutter/material.dart';
import 'package:flutter_app/constants/sizes.dart';
import 'package:flutter_app/constants/colors.dart';
import 'package:flutter_app/widgets/appbar/appbar.dart';
import 'package:flutter_app/utils/helpers/helper_function.dart';
import 'package:get/get.dart';
import '../checkout/checkout.dart';
import 'package:flutter_app/shop/controllers/cart_controller.dart';
import 'package:flutter_slidable/flutter_slidable.dart';
import 'package:flutter_app/common/widgets/products/cart/product_quantity_add_minus.dart';
import 'package:flutter_app/widgets/texts/product_price_text.dart';

class CartScreen extends StatelessWidget {
  final bool showBackArrow;
  
  const CartScreen({
    super.key,
    this.showBackArrow = true,
  });

  @override
  Widget build(BuildContext context) {
    final controller = Get.put(CartController());
    final dark = HelperFunction.isDarkMode(context);

    return Scaffold(
      appBar: CusAppbar(
        title: Text('Giỏ hàng', style: Theme.of(context).textTheme.headlineSmall),
        showBackArrow: showBackArrow, 
      ),
      body: Obx(() {
        if (controller.isLoading.value) {
          return const Center(child: CircularProgressIndicator());
        }
        
        if (controller.cartItems.isEmpty) {
          return const Center(child: Text("Giỏ hàng trống"));
        }

        return SingleChildScrollView(
          padding: const EdgeInsets.all(AppSizes.defaultSpace),
          child: _buildCartByShop(context, controller, dark),
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
              child: Text('Thanh toán \$${controller.totalAmount.value.toStringAsFixed(0)}'),
            ),
          ),
        );
      }),
    );
  }

  // Build cart items grouped by shop
  Widget _buildCartByShop(BuildContext context, CartController controller, bool dark) {
    // Group items by store
    final itemsByStore = <String, List>{};
    
    for (var item in controller.cartItems) {
      final storeName = item.storeName ?? 'Unknown Shop';
      if (!itemsByStore.containsKey(storeName)) {
        itemsByStore[storeName] = [];
      }
      itemsByStore[storeName]!.add(item);
    }

    return Column(
      children: itemsByStore.entries.map((entry) {
        final storeName = entry.key;
        final items = entry.value;
        
        return Container(
          margin: const EdgeInsets.only(bottom: AppSizes.spaceBtwItems),
          decoration: BoxDecoration(
            color: dark ? AppColors.dark : Colors.white,
            borderRadius: BorderRadius.circular(AppSizes.cardRadiusMd),
            border: Border.all(color: dark ? AppColors.darkGrey : AppColors.grey),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Shop Header
              Container(
                padding: const EdgeInsets.all(AppSizes.md),
                decoration: BoxDecoration(
                  color: dark ? AppColors.darkGrey : AppColors.light,
                  borderRadius: const BorderRadius.only(
                    topLeft: Radius.circular(AppSizes.cardRadiusMd),
                    topRight: Radius.circular(AppSizes.cardRadiusMd),
                  ),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.store, size: 20),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        storeName,
                        style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
              
              // Items in this shop
              ListView.separated(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                padding: const EdgeInsets.all(AppSizes.md),
                separatorBuilder: (_, __) => const SizedBox(height: AppSizes.spaceBtwItems),
                itemCount: items.length,
                itemBuilder: (_, index) {
                  final item = items[index];
                  
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
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        // Checkbox
                        Obx(() => Checkbox(
                          value: item.isSelected.value,
                          activeColor: AppColors.primary,
                          onChanged: (value) {
                            final realIndex = controller.cartItems.indexOf(item);
                            if (realIndex != -1) controller.toggleSelection(realIndex);
                          },
                        )),
                        
                        // Product Image
                        Container(
                          width: 60,
                          height: 60,
                          decoration: BoxDecoration(
                            color: dark ? AppColors.darkGrey : AppColors.light,
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Builder(builder: (context) {
                            String imageUrl = item.image ?? '';
                            if ((imageUrl.isEmpty || imageUrl == null) && item.productId != null) {
                              imageUrl = "http://10.0.2.2:8000/media/products/${item.productId}/${item.productId}_0.jpg";
                            }
                            if (imageUrl.startsWith('/media')) {
                              imageUrl = 'http://10.0.2.2:8000$imageUrl';
                            }
                          
                            if (imageUrl.isNotEmpty) {
                              return ClipRRect(
                                borderRadius: BorderRadius.circular(8),
                                child: Image.network(
                                  imageUrl,
                                  fit: BoxFit.cover,
                                  errorBuilder: (context, error, stackTrace) {
                                    return const Icon(Icons.image, color: Colors.grey);
                                  },
                                  loadingBuilder: (context, child, loadingProgress) {
                                    if (loadingProgress == null) return child;
                                    return const Center(
                                      child: CircularProgressIndicator(strokeWidth: 2),
                                    );
                                  },
                               ),
                             );
                            }
                          
                            return const Icon(Icons.image, color: Colors.grey);
                          }),
                        ),
                        const SizedBox(width: 12),
                        
                        // Product Info
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                item.productName,
                                maxLines: 2,
                                overflow: TextOverflow.ellipsis,
                                style: const TextStyle(fontWeight: FontWeight.w600),
                              ),
                              const SizedBox(height: 4),
                              // Attributes (Size/Color)
                              if (item.selectedVariation.isNotEmpty)
                                Text(
                                  item.selectedVariation.values.join(' - '),
                                  style: const TextStyle(color: Colors.grey, fontSize: 12),
                                ),
                              const SizedBox(height: 8),
                              // Quantity & Price
                              Row(
                                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                children: [
                                  ProductQuantityAddMinus(
                                    quantity: item.quantity,
                                    add: () => controller.updateQuantity(item.itemId, item.quantity + 1),
                                    remove: () {
                                      if (item.quantity > 1) {
                                        controller.updateQuantity(item.itemId, item.quantity - 1);
                                      }
                                    },
                                  ),
                                  ProductPriceText(
                                    price: (item.subTotal > 0 
                                        ? item.subTotal 
                                        : item.price * item.quantity
                                    ).toStringAsFixed(0),
                                  ),
                                ],
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  );
                },
              ),
            ],
          ),
        );
      }).toList(),
    );
  }
}