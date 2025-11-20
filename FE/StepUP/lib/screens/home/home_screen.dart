import 'package:flutter/material.dart';
import 'package:flutter_app/constants/sizes.dart';
import 'package:flutter_app/features/shop/screens/all_products/all_products.dart';
import 'package:flutter_app/screens/home/components/primary_header_container.dart';
import 'package:flutter_app/screens/home/components/home_appbar.dart';
import 'package:flutter_app/screens/home/components/search_container.dart';
import 'package:flutter_app/screens/home/components/section_heading.dart';
import 'package:flutter_app/screens/home/components/home_category.dart';
import 'package:flutter_app/screens/home/components/promo_slider.dart';
import 'package:flutter_app/constants/image_string.dart';
import 'package:flutter_app/widgets/layouts/grid_layout.dart';
import 'package:flutter_app/widgets/products/product_cards/product_card_vertical.dart';
import 'package:get/get.dart';
import 'package:flutter_app/shop/controllers/home_controller.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final controller = Get.put(HomeController());

    return Scaffold(
      body: SingleChildScrollView(
        child: Column(
          children: [
            // --- HEADER ---
            PrimaryHeaderContainer(
              child: Column(
                children: [
                  const HomeAppBar(),
                  const SizedBox(height: 24),
                  const SearchContainer(hintText: "Search your favorite"),
                  const SizedBox(height: 24),

                  // Categories
                  const Padding(
                    padding: EdgeInsets.only(left: 20),
                    child: Column(
                      children: [
                        SectionHeading(title: "Popular Categories", showActionButton: false),
                        SizedBox(height: 16),
                        HomeCategory(), 
                      ],
                    ),
                  ),
                  const SizedBox(height: 32),
                ],
              ),
            ),

            // --- BODY ---
            Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  // Promo slider
                  const PromoSlider(banners: [
                    AppImages.banner1,
                    AppImages.banner2,
                    AppImages.banner3
                  ]),
                  const SizedBox(height: 30),

                  // Heading Sản Phẩm
                  SectionHeading(
                    title: 'Popular Product',
                    onButtonPressed: () => Get.to(() => const AllProducts()),
                  ),
                  const SizedBox(height: 16),

                  Obx(() {
                    // 1. Đang tải
                    if (controller.isLoading.value) {
                      return const Center(child: CircularProgressIndicator());
                    }
                    
                    // 2. Không có dữ liệu
                    if (controller.productList.isEmpty) {
                      return const Center(child: Text('Không có sản phẩm nào từ Server'));
                    }

                    // 3. Có dữ liệu -> Hiển thị Grid
                    return GridLayout(
                      itemCount: controller.productList.length,
                      itemBuilder: (_, index) {
                        // Truyền product model vào card
                        return ProductCardVertical(product: controller.productList[index]);
                      },
                    );
                  }),
                ],
              ),
            ),
            const SizedBox(height: AppSizes.spaceBtwSections),
          ],
        ),
      ),
    );
  }
}