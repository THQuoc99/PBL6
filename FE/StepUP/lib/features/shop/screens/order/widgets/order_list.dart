import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:flutter_app/constants/colors.dart';
import 'package:flutter_app/constants/sizes.dart';
import 'package:flutter_app/utils/helpers/helper_function.dart';
import 'package:flutter_app/widgets/containers/rounded_container.dart';
import 'package:iconsax_flutter/iconsax_flutter.dart';
import 'package:flutter_app/shop/controllers/order_list_controller.dart';
import 'package:flutter_app/shop/models/order_model.dart';
import 'package:flutter_app/features/shop/screens/order/order_detail_screen.dart';

class OrderListItems extends StatelessWidget {
  const OrderListItems({super.key});

  @override
  Widget build(BuildContext context) {
    final dark = HelperFunction.isDarkMode(context);
    final controller = Get.put(OrderListController());

    return Obx(() {
      if (controller.isLoading.value) {
        return const Center(child: CircularProgressIndicator());
      }

      if (controller.orders.isEmpty) {
        return const Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Iconsax.box, size: 60, color: Colors.grey),
              SizedBox(height: 16),
              Text("Bạn chưa có đơn hàng nào."),
            ],
          ),
        );
      }

      return ListView.separated(
        shrinkWrap: true,
        itemCount: controller.orders.length,
        separatorBuilder: (_, __) => const SizedBox(height: AppSizes.spaceBtwItems),
        itemBuilder: (_, index) {
          final order = controller.orders[index];
          return _buildOrderCard(context, dark, order);
        },
      );
    });
  }

  Widget _buildOrderCard(BuildContext context, bool dark, OrderModel order) {
    return RoundedContainer(
      showBorder: true,
      padding: const EdgeInsets.all(AppSizes.md),
      bgcolor: dark ? AppColors.dark : AppColors.light,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Row(
            children: [
              const Icon(Iconsax.ship),
              const SizedBox(width: AppSizes.spaceBtwItems / 2),

              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      order.orderStatusText,
                      style: Theme.of(context).textTheme.bodyLarge!.apply(
                        color: AppColors.primary,
                        fontWeightDelta: 1,
                      ),
                    ),
                    Text(
                      order.formattedOrderDate,
                      style: Theme.of(context).textTheme.headlineSmall,
                    ),
                  ],
                ),
              ),

              IconButton(
                onPressed: () {
                  Get.to(() => OrderDetailScreen(order: order));
                },
                icon: const Icon(Iconsax.arrow_right_3, size: AppSizes.iconSm),
              ),
            ],
          ),

          const SizedBox(height: AppSizes.spaceBtwItems),

          Row(
            children: [
              Expanded(
                child: Row(
                  children: [
                    const Icon(Iconsax.tag),
                    const SizedBox(width: AppSizes.spaceBtwItems / 2),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('Order ID', style: Theme.of(context).textTheme.labelMedium),
                          Text('#${order.id}', style: Theme.of(context).textTheme.titleMedium),
                        ],
                      ),
                    )
                  ],
                ),
              ),

              Expanded(
                child: Row(
                  children: [
                    const Icon(Iconsax.money),
                    const SizedBox(width: AppSizes.spaceBtwItems / 2),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('Total Amount', style: Theme.of(context).textTheme.labelMedium),
                          Text('\$${order.totalAmount.toStringAsFixed(0)}',
                              style: Theme.of(context).textTheme.titleMedium),
                        ],
                      ),
                    )
                  ],
                ),
              ),
            ],
          )
        ],
      ),
    );
  }
}
