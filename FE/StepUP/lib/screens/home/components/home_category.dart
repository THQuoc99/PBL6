import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:flutter_app/shop/controllers/home_controller.dart';
import 'package:flutter_app/features/shop/screens/sub_category/sub_categories.dart'; // Giữ navigation cũ của bạn

class HomeCategory extends StatelessWidget {
  const HomeCategory({super.key});

  @override
  Widget build(BuildContext context) {
    // 1. Tìm Controller đã được khởi tạo ở HomeScreen
    final controller = Get.find<HomeController>();

    return Obx(() {
      // 2. Kiểm tra trạng thái Loading hoặc Rỗng
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

      // 3. Hiển thị danh sách
      return SizedBox(
        height: 80, // Chiều cao vừa đủ cho icon + text
        child: ListView.builder(
          shrinkWrap: true,
          itemCount: controller.categoryList.length,
          scrollDirection: Axis.horizontal,
          itemBuilder: (_, index) {
            final category = controller.categoryList[index];
            
            // Xử lý URL ảnh (nếu backend trả về đường dẫn tương đối)
            String imageUrl = category.image ?? "";
            if (imageUrl.startsWith("/media")) {
              imageUrl = "http://10.0.2.2:8000$imageUrl";
            }
            final isNetworkImage = imageUrl.startsWith("http");

            return Padding(
              padding: const EdgeInsets.only(right: 16),
              child: GestureDetector(
                // Chuyển sang màn hình con (bạn có thể truyền category.id vào đây sau này)
                onTap: () => Get.to(() => const SubCategoriesScreen()),
                child: Column(
                  children: [
                    // --- Vòng tròn chứa ảnh ---
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
                            ? Image.network(
                                imageUrl,
                                fit: BoxFit.cover,
                                errorBuilder: (context, error, stackTrace) => const Icon(Icons.category, color: Colors.black),
                              )
                            : const Icon(Icons.category, color: Colors.black),
                      ),
                    ),
                    const SizedBox(height: 8),
                    
                    // --- Tên danh mục ---
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