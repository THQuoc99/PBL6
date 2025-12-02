import 'dart:async'; // Import để dùng Timer
import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:flutter_app/shop/controllers/search_controller.dart' as my_search;
import 'package:flutter_app/widgets/layouts/grid_layout.dart';
import 'package:flutter_app/widgets/products/product_cards/product_card_vertical.dart';
import 'package:flutter_app/constants/sizes.dart';
import 'package:iconsax_flutter/iconsax_flutter.dart';

class SearchScreen extends StatefulWidget {
  const SearchScreen({super.key});

  @override
  State<SearchScreen> createState() => _SearchScreenState();
}

class _SearchScreenState extends State<SearchScreen> {
  // Dùng Timer để Debounce (chống spam API)
  Timer? _debounce;

  @override
  void dispose() {
    _debounce?.cancel();
    super.dispose();
  }

  void _onSearchChanged(String query, my_search.SearchController controller) {
    if (_debounce?.isActive ?? false) _debounce!.cancel();
    
    // Chỉ gọi API sau khi người dùng ngừng gõ 500ms
    _debounce = Timer(const Duration(milliseconds: 500), () {
      controller.searchProducts(query);
    });
  }

  @override
  Widget build(BuildContext context) {
    final controller = Get.put(my_search.SearchController());

    return Scaffold(
      appBar: AppBar(
        title: const Text('Tìm kiếm sản phẩm'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(AppSizes.defaultSpace),
        child: Column(
          children: [
            // --- THANH TÌM KIẾM ---
            TextField(
              autofocus: true, 
              onChanged: (value) => _onSearchChanged(value, controller),
              decoration: InputDecoration(
                prefixIcon: const Icon(Iconsax.search_normal),
                hintText: 'Nhập tên giày, thương hiệu...',
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
                filled: true,
                fillColor: Colors.grey[100],
              ),
            ),
            const SizedBox(height: 20),

            // --- KẾT QUẢ TÌM KIẾM ---
            Expanded(
              child: Obx(() {
                if (controller.isLoading.value) {
                  return const Center(child: CircularProgressIndicator());
                }

                // Trường hợp tìm không thấy
                if (controller.searchText.value.isNotEmpty && controller.searchResults.isEmpty) {
                  return Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const Icon(Iconsax.search_status, size: 60, color: Colors.grey),
                        const SizedBox(height: 10),
                        Text("Không tìm thấy sản phẩm nào cho '${controller.searchText.value}'"),
                      ],
                    ),
                  );
                }
                
                // Màn hình chờ ban đầu
                if (controller.searchText.value.isEmpty) {
                   return const Center(
                     child: Column(
                       mainAxisAlignment: MainAxisAlignment.center,
                       children: [
                         Icon(Iconsax.global_search, size: 60, color: Colors.grey),
                         SizedBox(height: 10),
                         Text("Nhập từ khóa để tìm kiếm"),
                       ],
                     ),
                   );
                }

                // Hiển thị danh sách
                return SingleChildScrollView(
                  child: GridLayout(
                    itemCount: controller.searchResults.length,
                    itemBuilder: (_, index) => ProductCardVertical(
                      product: controller.searchResults[index],
                    ),
                  ),
                );
              }),
            ),
          ],
        ),
      ),
    );
  }
}