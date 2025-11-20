import 'package:flutter/material.dart';
import 'package:flutter_app/constants/colors.dart';
import 'package:flutter_app/constants/image_string.dart';
import 'package:flutter_app/constants/sizes.dart';
import 'package:flutter_app/widgets/appbar/appbar.dart';
import 'package:flutter_app/widgets/containers/rounded_container.dart';
import 'package:flutter_app/widgets/image/circular_image.dart';
import 'package:flutter_app/widgets/layouts/grid_layout.dart';
import 'package:flutter_app/widgets/products/product_cards/product_card_vertical.dart'; // Giả sử bạn có card này
import 'package:flutter_app/widgets/products/brands/brand_titles.dart';
import 'package:flutter_app/utils/helpers/helper_function.dart';
import 'package:iconsax_flutter/iconsax_flutter.dart';
import 'package:flutter_app/shop/services/product_service.dart';

class StoreScreen extends StatelessWidget {
  const StoreScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final dark = HelperFunction.isDarkMode(context);

    // Dùng DefaultTabController để quản lý các tab
    return DefaultTabController(
      length: 2, // Số lượng tab (Products, Reviews)
      child: Scaffold(
        appBar: CusAppbar(
          title: Text('Nike Store'), // Tên cửa hàng
          showBackArrow: true,
          actions: [
            // Nút chia sẻ (ví dụ)
            IconButton(onPressed: () {}, icon: const Icon(Icons.share)),
          ],
        ),
        body: Padding(
          padding: const EdgeInsets.all(AppSizes.defaultSpace),
          child: Column(
            children: [
              // --- 1. Header của Store ---
              StoreHeader(dark: dark),
              const SizedBox(height: AppSizes.spaceBtwSections),

              // --- 2. Thanh Tab ---
              TabBar(
                tabs: [
                  Tab(text: 'Products'),
                  Tab(text: 'Reviews'),
                ],
                // Tùy chỉnh thêm cho đẹp
                indicatorColor: AppColors.primary,
                unselectedLabelColor: AppColors.darkGray,
                labelColor: dark ? AppColors.white : AppColors.primary,
              ),
              const SizedBox(height: AppSizes.spaceBtwSections),

              // --- 3. Nội dung Tab ---
              Expanded(
                child: TabBarView(
                  children: [
                    // --- Tab Sản phẩm ---
                    StoreProductsTab(),

                    // --- Tab Đánh giá ---
                    StoreReviewsTab(),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// --- TÁCH WIDGET CHO GỌN ---

// Header của Store
class StoreHeader extends StatelessWidget {
  const StoreHeader({
    super.key,
    required this.dark,
  });

  final bool dark;

  @override
  Widget build(BuildContext context) {
    return RoundedContainer(
      padding: const EdgeInsets.all(AppSizes.md),
      bgcolor: dark ? AppColors.darkGrey : AppColors.grey,
      child: Row(
        children: [
          // Logo cửa hàng
          CircularImage(
            image: AppImages.football1, // Dùng logo
            isNetworkImage: false,
            width: 80,
            height: 80,
            bgcolor: Colors.transparent,
          ),
          const SizedBox(width: AppSizes.spaceBtwItems),
          
          // Tên & Số sản phẩm
          Expanded(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const BrandTitlesVerify(title: 'Nike'),
                const SizedBox(height: AppSizes.spaceBtwItems / 2),
                Text('256 products', style: Theme.of(context).textTheme.labelMedium),
              ],
            ),
          ),

          // Nút Follow
          OutlinedButton(
            onPressed: () {},
            child: const Text('Follow'),
          ),
        ],
      ),
    );
  }
}

// Tab Sản phẩm
class StoreProductsTab extends StatelessWidget {
  const StoreProductsTab({
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    // Dùng GridView để hiển thị sản phẩm
    return Scaffold(
      body: SingleChildScrollView(
        child: Padding(
          padding: EdgeInsets.all(AppSizes.defaultSpace),
          child: Column(
            children: [
              // Dropdown
              DropdownButtonFormField(
                decoration: InputDecoration(prefixIcon: Icon(Iconsax.sort)),
                onChanged: (value){},
                items: ['Name', 'Price', 'Sale']
                  .map((option) => DropdownMenuItem( value: option,child: Text(option)))
                  .toList(),
              ),
              const SizedBox(height: AppSizes.spaceBtwItems,),

              //Product
              // Use featured products as placeholder for store products
              FutureBuilder(
                future: ProductService.getFeaturedProducts(first: 12),
                builder: (context, snapshot) {
                  if (snapshot.connectionState == ConnectionState.waiting) {
                    return const SizedBox(height: 200, child: Center(child: CircularProgressIndicator()));
                  }
                  final products = snapshot.data ?? [];
                  if (products.isEmpty) return const Text('Không có sản phẩm');
                  return GridLayout(itemCount: products.length, itemBuilder: (_, index) => ProductCardVertical(product: products[index]));
                },
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// Tab Đánh giá (Ví dụ)
class StoreReviewsTab extends StatelessWidget {
  const StoreReviewsTab({
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    return ListView.separated(
      itemCount: 5,
      shrinkWrap: true,
      separatorBuilder: (_, __) => const SizedBox(height: AppSizes.spaceBtwItems),
      itemBuilder: (context, index) {
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text("User $index", style: Theme.of(context).textTheme.titleMedium),
                Text("14 Nov, 2025", style: Theme.of(context).textTheme.bodySmall),
              ],
            ),
            // Thêm widget sao (RatingBar) ở đây
            const SizedBox(height: AppSizes.spaceBtwItems / 2),
            const Text('Sản phẩm rất tuyệt vời, đóng gói cẩn thận...'),
          ],
        );
      },
    );
  }
}