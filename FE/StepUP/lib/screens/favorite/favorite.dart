import 'package:flutter/material.dart';
import 'package:flutter_app/constants/sizes.dart';
import 'package:flutter_app/screens/home/home_screen.dart';
import 'package:flutter_app/widgets/appbar/appbar.dart';
import 'package:flutter_app/widgets/icons/circular_icon.dart';
import 'package:flutter_app/widgets/layouts/grid_layout.dart';
import 'package:flutter_app/widgets/products/product_cards/product_card_vertical.dart';
import 'package:get/get.dart';
import 'package:iconsax_flutter/iconsax_flutter.dart';
import 'package:flutter_app/shop/controllers/wishlist_controller.dart';

class FavoriteScreen extends StatelessWidget {
  const FavoriteScreen({super.key});

  @override
  Widget build(BuildContext context) {
    // ✅ Khởi tạo Controller
    final controller = Get.put(WishlistController());

    return Scaffold(
      appBar: CusAppbar(
        title: Text(
          'Danh sách yêu thích',
          style: Theme.of(context).textTheme.headlineMedium,
        ),
        actions: [
          CircularIcon(
            icon: Iconsax.add,
            onpress: () => Get.to(() => const HomeScreen()),
          )
        ],
      ),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(AppSizes.defaultSpace),
          child: Column(
            children: [
              // ✅ Sử dụng Obx để tự động cập nhật khi danh sách thay đổi
              Obx(
                () {
                  if (controller.favorites.isEmpty) {
                    return const Center(
                      child: Column(
                        children: [
                           SizedBox(height: 100),
                           Icon(Iconsax.heart_slash, size: 60, color: Colors.grey),
                           SizedBox(height: 16),
                           Text('Danh sách yêu thích trống'),
                        ],
                      ),
                    );
                  }

                  return GridLayout(
                    itemCount: controller.favorites.length,
                    itemBuilder: (_, index) => ProductCardVertical(
                      product: controller.favorites[index],
                    ),
                  );
                },
              ),
            ],
          ),
        ),
      ),
    );
  }
}