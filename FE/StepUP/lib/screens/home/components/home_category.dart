import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:flutter_app/shop/controllers/home_controller.dart';
import 'package:flutter_app/features/shop/screens/sub_category/sub_categories.dart'; 

class HomeCategory extends StatelessWidget {
  const HomeCategory({super.key});

  @override
  Widget build(BuildContext context) {
    final controller = Get.find<HomeController>();

    return Obx(() {
      if (controller.isLoading.value) {
        return const Center(child: CircularProgressIndicator(color: Colors.white));
      }
      if (controller.categoryList.isEmpty) {
        return Center(
          child: Text(
            "No categories",
            style: Theme.of(context).textTheme.bodyMedium!.apply(color: Colors.white),
          ),
        );
      }

      return SizedBox(
        height: 100, 
        child: ListView.builder(
          itemCount: controller.categoryList.length,
          scrollDirection: Axis.horizontal,
          padding: const EdgeInsets.only(left: 20),
          itemBuilder: (_, index) {
            final category = controller.categoryList[index];
            
            String imageUrl = category.image ?? "";
            if (imageUrl.startsWith("/media")) {
              imageUrl = "http://10.0.2.2:8000$imageUrl";
            }
            final isNetworkImage = imageUrl.startsWith("http");

            return Padding(
              padding: const EdgeInsets.only(right: 16),
              child: GestureDetector(
                onTap: () {
                   // ✅ SỬA LỖI: Truyền biến 'category' vào và bỏ 'const'
                   Get.to(() => SubCategoriesScreen(category: category));
                },
                child: Column(
                  children: [
                    Container(
                      width: 56,
                      height: 56,
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(100),
                      ),
                      child: Center(
                        child: isNetworkImage
                            ? ClipRRect(
                                borderRadius: BorderRadius.circular(100),
                                child: Image.network(
                                  imageUrl,
                                  fit: BoxFit.cover,
                                  width: 40, 
                                  height: 40,
                                  errorBuilder: (context, error, stackTrace) => const Icon(Icons.category, color: Colors.black),
                                ),
                              )
                            : const Icon(Icons.category, color: Colors.black),
                      ),
                    ),
                    const SizedBox(height: 8),
                    
                    SizedBox(
                      width: 55,
                      child: Text(
                        category.name,
                        style: Theme.of(context).textTheme.labelMedium!.apply(color: Colors.white),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        textAlign: TextAlign.center,
                      ),
                    )
                  ],
                ),
              ),
            );
          },
        ),
      );
    });
  }
}