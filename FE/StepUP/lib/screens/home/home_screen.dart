import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:flutter_app/constants/sizes.dart';
import 'package:flutter_app/constants/image_string.dart';
import 'package:flutter_app/screens/home/components/primary_header_container.dart';
import 'package:flutter_app/screens/home/components/home_appbar.dart';
import 'package:flutter_app/screens/home/components/search_container.dart';
import 'package:flutter_app/screens/home/components/section_heading.dart';
import 'package:flutter_app/screens/home/components/home_category.dart';
import 'package:flutter_app/screens/home/components/promo_slider.dart';
import 'package:flutter_app/widgets/layouts/grid_layout.dart';
import 'package:flutter_app/widgets/products/product_cards/product_card_vertical.dart';
import 'package:flutter_app/features/shop/screens/all_products/all_products.dart';
import 'package:flutter_app/features/shop/screens/search/search_screen.dart';
import 'package:flutter_app/shop/controllers/home_controller.dart';
import 'package:flutter_app/shop/controllers/notification_controller.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final controller = Get.put(HomeController());
    final notificationController = Get.put(NotificationController());

    return Scaffold(
      body: SingleChildScrollView(
        child: Column(
          children: [
            // --- HEADER (Màu xanh + Tìm kiếm + Danh mục) ---
            PrimaryHeaderContainer(
              child: Column(
                children: [
                  // 1. Appbar
                  const HomeAppBar(),
                  
                  const SizedBox(height: AppSizes.spaceBtwItems), 

                  // 2. Thanh tìm kiếm
                  SearchContainer(
                    hintText: "Tìm kiếm sản phẩm",
                    ontap: () => Get.to(() => const SearchScreen()), 
                  ),
                  
                  const SizedBox(height: AppSizes.spaceBtwItems), 

                  // 3. Danh mục sản phẩm
                  const Padding(
                    padding: EdgeInsets.only(left: AppSizes.defaultSpace),
                    child: Column(
                      children: [
                        SectionHeading(
                          title: "Danh mục sản phẩm", 
                          showActionButton: false,
                          textColor: Colors.white,
                        ),
                        const SizedBox(height: AppSizes.spaceBtwItems),
                        HomeCategory(), 
                      ],
                    ),
                  ),
                  
                  // ✅ SỬA: Giảm khoảng cách cuối Header
                  const SizedBox(height: AppSizes.spaceBtwSections), 
                ],
              ),
            ),

            // --- BODY (Slider + Sản phẩm) ---
            Padding(
              padding: const EdgeInsets.all(AppSizes.defaultSpace),
              child: Column(
                children: [
                  // 4. Banner quảng cáo
                  const PromoSlider(banners: [
                    AppImages.banner1,
                    AppImages.banner2,
                    AppImages.banner3
                  ]),
                  const SizedBox(height: AppSizes.spaceBtwSections),

                  // 5. Heading Sản Phẩm
                  SectionHeading(
                    title: 'Sản phẩm phổ biến',
                    onButtonPressed: () => Get.to(() => const AllProducts()),
                  ),
                  const SizedBox(height: AppSizes.spaceBtwItems),

                  // 6. Lưới sản phẩm
                  Obx(() {
                    if (controller.isLoading.value) {
                      return const Center(child: CircularProgressIndicator());
                    }
                    
                    if (controller.productList.isEmpty) {
                      return const Center(child: Text('Không có sản phẩm nào từ Server'));
                    }

                    return GridLayout(
                      itemCount: controller.productList.length,
                      itemBuilder: (_, index) {
                        return ProductCardVertical(product: controller.productList[index]);
                      },
                    );
                  }),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}