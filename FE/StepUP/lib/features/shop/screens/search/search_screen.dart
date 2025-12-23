import 'package:flutter/services.dart';
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
  final TextEditingController _textController = TextEditingController();

  @override
  void dispose() {
    _textController.dispose();
    super.dispose();
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
            // --- THANH TÌM KIẾM (có nút Search) ---
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _textController,
                    autofocus: true,
                    textInputAction: TextInputAction.search,
                    onSubmitted: (value) => controller.searchProducts(value.trim()),
                    decoration: InputDecoration(
                      hintText: 'Nhập tên giày, thương hiệu...',
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                      filled: true,
                      fillColor: Colors.grey[100],
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                ElevatedButton(
                  onPressed: () => controller.searchProducts(_textController.text.trim()),
                  child: const Icon(Iconsax.search_normal),
                  style: ElevatedButton.styleFrom(
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 14),
                  ),
                ),
              ],
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