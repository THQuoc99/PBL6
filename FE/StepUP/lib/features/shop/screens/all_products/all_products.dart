import 'package:flutter/material.dart';
import 'package:flutter_app/constants/sizes.dart';
import 'package:flutter_app/widgets/appbar/appbar.dart';
import 'package:flutter_app/widgets/layouts/grid_layout.dart';
import 'package:flutter_app/widgets/products/product_cards/product_card_vertical.dart';
import 'package:iconsax_flutter/iconsax_flutter.dart';
import 'package:get/get.dart';

import 'package:flutter_app/shop/controllers/all_products_controller.dart';

class AllProducts extends StatelessWidget {
  const AllProducts({super.key});

  @override
  Widget build(BuildContext context) {
    final controller = Get.put(AllProductsController());

    return Scaffold(
      appBar: const CusAppbar(title: Text('All Products'), showBackArrow: true,),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(AppSizes.defaultSpace),
          child: Column(
            children: [
              DropdownButtonFormField(
                decoration: const InputDecoration(prefixIcon: Icon(Iconsax.sort)),
                value: 'Name', // Giá trị mặc định
                onChanged: (value) {
                  if (value != null) {
                    controller.sortProducts(value.toString());
                  }
                },
                items: ['Name', 'Price', 'Sale']
                    .map((option) => DropdownMenuItem(value: option, child: Text(option)))
                    .toList(),
              ),
              const SizedBox(height: AppSizes.spaceBtwItems,),

              // ✅ Product List: Dùng Obx để lắng nghe dữ liệu
              Obx(() {
                if (controller.isLoading.value) {
                  return const Center(child: CircularProgressIndicator());
                }

                if (controller.productList.isEmpty) {
                  return const Center(child: Text('Không có sản phẩm nào'));
                }

                return GridLayout(
                  itemCount: controller.productList.length,
                  itemBuilder: (_, index) => ProductCardVertical(
                    product: controller.productList[index]
                  ),
                );
              }),
            ],
          ),
        ),
      ),
    );
  }
}