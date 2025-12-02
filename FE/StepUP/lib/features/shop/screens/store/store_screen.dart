import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:flutter_app/constants/colors.dart';
import 'package:flutter_app/constants/image_string.dart';
import 'package:flutter_app/constants/sizes.dart';
import 'package:flutter_app/widgets/appbar/appbar.dart';
import 'package:flutter_app/widgets/containers/rounded_container.dart';
import 'package:flutter_app/widgets/image/circular_image.dart';
import 'package:flutter_app/widgets/layouts/grid_layout.dart';
import 'package:flutter_app/widgets/products/product_cards/product_card_vertical.dart';
import 'package:flutter_app/widgets/products/brands/brand_titles.dart';
import 'package:flutter_app/utils/helpers/helper_function.dart';
import 'package:iconsax_flutter/iconsax_flutter.dart';
import 'package:flutter_app/utils/constants/enums.dart';
import 'package:flutter_app/shop/controllers/store_controller.dart';

class StoreScreen extends StatelessWidget {
  // Nhận storeId từ màn hình trước (ví dụ từ Product Detail bấm vào tên shop)
  final String storeId;

  const StoreScreen({super.key, required this.storeId});

  @override
  Widget build(BuildContext context) {
    final dark = HelperFunction.isDarkMode(context);
    
    // Khởi tạo controller và gọi hàm fetch data ngay khi build
    final controller = Get.put(StoreController());
    // Gọi fetch nếu chưa có dữ liệu hoặc id khác (để refresh)
    controller.fetchStoreData(storeId);

    return DefaultTabController(
      length: 2, 
      child: Scaffold(
        appBar: CusAppbar(
          // Hiển thị tên shop trên AppBar
          title: Obx(() => Text(controller.store.value?.name ?? 'Loading...')), 
          showBackArrow: true,
          actions: [
            IconButton(onPressed: () {}, icon: const Icon(Icons.share)),
          ],
        ),
        body: Obx(() {
          if (controller.isLoading.value) {
            return const Center(child: CircularProgressIndicator());
          }
          
          final storeData = controller.store.value;
          if (storeData == null) return const Center(child: Text("Không tìm thấy cửa hàng"));

          return Padding(
            padding: const EdgeInsets.all(AppSizes.defaultSpace),
            child: Column(
              children: [
                // --- 1. Header Store (Dữ liệu thật) ---
                _buildStoreHeader(context, dark, storeData, controller),
                const SizedBox(height: AppSizes.spaceBtwSections),

                // --- 2. Tab Bar ---
                TabBar(
                  tabs: const [
                    Tab(text: 'Sản phẩm'),
                    Tab(text: 'Giới thiệu'), // Hoặc Reviews
                  ],
                  indicatorColor: AppColors.primary,
                  unselectedLabelColor: Colors.grey,
                  labelColor: dark ? Colors.white : AppColors.primary,
                ),
                const SizedBox(height: AppSizes.spaceBtwSections),

                // --- 3. Nội dung Tab ---
                Expanded(
                  child: TabBarView(
                    children: [
                      // Tab Sản phẩm (Dữ liệu thật)
                      _buildProductsTab(controller),
                      
                      // Tab Giới thiệu (Ví dụ hiển thị mô tả)
                      SingleChildScrollView(
                        child: Text(storeData.description.isNotEmpty ? storeData.name : "Chưa có mô tả."),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          );
        }),
      ),
    );
  }

  Widget _buildStoreHeader(BuildContext context, bool dark, var store, StoreController controller) {
    return RoundedContainer(
      padding: const EdgeInsets.all(AppSizes.md),
      bgcolor: dark ? AppColors.darkGrey : AppColors.grey,
      child: Row(
        children: [
          // Logo
          CircularImage(
            image: (store.avatar != null && store.avatar!.isNotEmpty) 
                ? store.avatar! 
                : AppImages.football1, 
            isNetworkImage: (store.avatar != null && store.avatar!.isNotEmpty),
            width: 60, // Giảm size logo một chút nếu cần (từ 80 -> 60) cho cân đối
            height: 60,
            bgcolor: Colors.transparent,
          ),
          const SizedBox(width: AppSizes.spaceBtwItems),
          
          // Thông tin
          Expanded(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                BrandTitlesVerify(title: store.name, brandTextSize: TextSizes.large),
                const SizedBox(height: 4),
                
                // Số follower
                Obx(() => Text(
                  '${controller.followerCount.value} người theo dõi', 
                  style: Theme.of(context).textTheme.labelSmall // Dùng labelSmall cho gọn
                )),
                
                Row(children: [
                   const Icon(Iconsax.star, size: 12, color: Colors.amber),
                   Text(' ${store.rating}', style: Theme.of(context).textTheme.labelSmall),
                ]),
              ],
            ),
          ),

          Obx(() {
            final isFollowing = controller.isFollowing.value;
            
            return SizedBox(
              height: 32, // 1. Giới hạn chiều cao
              width: isFollowing ? 110 : 90, // 2. Giới hạn chiều rộng (tùy chỉnh theo text)
              child: OutlinedButton(
                onPressed: () => controller.followStore(store.storeId),
                style: OutlinedButton.styleFrom(
                  // 3. Đổi màu nền/viền
                  backgroundColor: isFollowing ? AppColors.primary : Colors.transparent,
                  side: BorderSide(color: isFollowing ? Colors.transparent : AppColors.primary),
                  // 4. Giảm padding để nội dung không bị chèn ép
                  padding: const EdgeInsets.symmetric(horizontal: 8), 
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                ),
                child: Text(
                  isFollowing ? 'Đang theo dõi' : 'Theo dõi',
                  style: TextStyle(
                    color: isFollowing ? Colors.white : AppColors.primary,
                    fontSize: 12, // 5. Giảm kích thước chữ
                    fontWeight: FontWeight.w600,
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ),
            );
          }),
        ],
      ),
    );
  }

  Widget _buildProductsTab(StoreController controller) {
    return Obx(() {
      if (controller.storeProducts.isEmpty) {
        return const Center(child: Text("Shop chưa có sản phẩm nào."));
      }
      
      return SingleChildScrollView(
        child: Column(
           children: [
              const SizedBox(height: AppSizes.spaceBtwItems),
              
              GridLayout(
                  itemCount: controller.storeProducts.length, 
                  itemBuilder: (_, index) => ProductCardVertical(product: controller.storeProducts[index])
              ),
           ],
        ),
      );
    });
  }
}