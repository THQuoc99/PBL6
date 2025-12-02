import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:flutter_app/constants/sizes.dart';
import 'package:flutter_app/constants/image_string.dart'; 
import 'package:flutter_app/screens/home/components/section_heading.dart';
import 'package:flutter_app/widgets/appbar/appbar.dart';
import 'package:flutter_app/widgets/image/rounded_image.dart';
import 'package:flutter_app/widgets/products/product_cards/product_card_horizontal.dart';
import 'package:flutter_app/shop/models/category_model.dart';
import 'package:flutter_app/shop/controllers/category_products_controller.dart';

class SubCategoriesScreen extends StatelessWidget {
  final CategoryModel category;

  const SubCategoriesScreen({
    super.key,
    required this.category,
  });

  @override
  Widget build(BuildContext context) {
    // Khởi tạo controller và gọi API
    final controller = Get.put(CategoryProductsController());
    controller.fetchProductsByCategory(category.id);

    // Xử lý ảnh banner (Dùng ảnh category hoặc ảnh mặc định)
    String bannerUrl = category.image ?? "";
    if (bannerUrl.startsWith("/media")) {
       bannerUrl = "http://10.0.2.2:8000$bannerUrl";
    }
    final bool hasNetworkImage = bannerUrl.startsWith("http");

    return Scaffold(
      appBar: CusAppbar(
        title: Text(category.name), // Hiển thị tên danh mục động
        showBackArrow: true,
      ),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(AppSizes.defaultSpace),
          child: Column(
            children: [
              // --- 1. Banner ---
              RoundedImage(
                width: double.infinity,
                height: 180, // Set chiều cao cố định cho đẹp
                imageUrl: hasNetworkImage ? bannerUrl : AppImages.footballbanner1,
                isNetworkImage: hasNetworkImage,
                applyImageRadius: true,
                fit: BoxFit.cover,
              ),
              
              const SizedBox(height: AppSizes.spaceBtwSections),
              
              // --- 2. Danh sách sản phẩm ---
              Column(
                children: [
                  SectionHeading(
                    title: 'Sản phẩm nổi bật', 
                    onButtonPressed: (){},
                    showActionButton: false,
                  ),
                  const SizedBox(height: AppSizes.spaceBtwItems / 2),

                  Obx(() {
                    if (controller.isLoading.value) {
                      return const Center(child: CircularProgressIndicator());
                    }

                    if (controller.products.isEmpty) {
                      return const Center(child: Text("Chưa có sản phẩm nào trong danh mục này."));
                    }

                    return SizedBox(
                      height: 120,
                      child: ListView.separated(
                        itemCount: controller.products.length,
                        scrollDirection: Axis.horizontal,
                        separatorBuilder: (context, index) => const SizedBox(width: AppSizes.spaceBtwItems),
                        itemBuilder: (context, index) {
                          final product = controller.products[index];
                          // Truyền product vào Card
                          return ProductCardHorizontal(product: product); 
                        },
                      ),
                    );
                  })
                ],
              )
            ],
          ),
        ),
      ),
    );
  }
}