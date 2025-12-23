import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:flutter_app/constants/sizes.dart';
import 'package:flutter_app/constants/colors.dart';
import 'package:flutter_app/utils/helpers/helper_function.dart';
import 'package:flutter_app/widgets/appbar/appbar.dart';
import 'package:flutter_app/widgets/containers/rounded_container.dart';
import 'package:flutter_app/features/shop/screens/checkout/widgets/billing_address_section.dart';
import 'package:flutter_app/features/shop/screens/checkout/widgets/billing_amount_section.dart';
import 'package:flutter_app/features/shop/screens/checkout/widgets/billing_shipping_section.dart';
import 'widgets/billing_payment_section.dart';
import 'package:flutter_app/shop/controllers/cart_controller.dart';
import 'package:flutter_app/shop/controllers/order_controller.dart';
import 'package:flutter_app/shop/controllers/voucher_controller.dart';
import 'package:flutter_app/screens/home/components/section_heading.dart';
import 'package:flutter_app/shop/models/voucher_model.dart';
import 'package:flutter_app/shop/models/cart_item_model.dart'; // Đảm bảo import model này

class CheckoutScreen extends StatefulWidget {
  const CheckoutScreen({super.key});

  @override
  State<CheckoutScreen> createState() => _CheckoutScreenState();
}

class _CheckoutScreenState extends State<CheckoutScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _fetchVouchers();
    });
  }

  void _fetchVouchers() {
    final cartController = Get.find<CartController>();
    final voucherController = Get.put(VoucherController());

    // [FIX] Lấy storeId dạng String
    final storeIds = cartController.selectedItems
        .map((e) => e.storeId?.toString() ?? '')
        .where((id) => id.isNotEmpty)
        .toSet()
        .toList();
    
    final totalAmount = cartController.totalAmount.value; 

    print("🛒 CHECKOUT INIT: Stores=$storeIds Total=$totalAmount");

    voucherController.fetchAvailableVouchers(
      storeIds: storeIds, 
      totalOrderAmount: totalAmount
    );
  }

  @override
  Widget build(BuildContext context) {
    final dark = HelperFunction.isDarkMode(context);
    final cartController = Get.find<CartController>(); 
    final orderController = Get.put(OrderController());
    final voucherController = Get.put(VoucherController());

    return Scaffold(
      appBar: CusAppbar(
        title: Text('Thanh toán', style: Theme.of(context).textTheme.headlineSmall),
        showBackArrow: true,
      ),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(AppSizes.defaultSpace),
          child: Column(
            children: [
              Obx(() => _buildItemsByShop(context, cartController, dark)),
              const SizedBox(height: AppSizes.spaceBtwSections),

              _buildVoucherSelector(context, dark, voucherController),
              const SizedBox(height: AppSizes.spaceBtwSections),

              RoundedContainer(
                showBorder: true,
                bgcolor: dark ? AppColors.dark : AppColors.light,
                padding: const EdgeInsets.all(AppSizes.md),
                child: Column(
                  children: [
                    const BillingAmountSection(), 
                    const SizedBox(height: AppSizes.spaceBtwItems),
                    const Divider(),
                    const SizedBox(height: AppSizes.spaceBtwItems),

                    const BillingPaymentSection(), 
                    const SizedBox(height: AppSizes.spaceBtwItems),
                    const Divider(),
                    const SizedBox(height: AppSizes.spaceBtwItems),
                    
                    const BillingShippingSection(),
                    const SizedBox(height: AppSizes.spaceBtwItems),
                    const Divider(),
                    const SizedBox(height: AppSizes.spaceBtwItems),
                    
                    const BillingAddressSection(),
                    const SizedBox(height: AppSizes.spaceBtwItems),
                    const Divider(),
                    const SizedBox(height: AppSizes.spaceBtwItems),
                    
                    TextField(
                      controller: orderController.noteController,
                      maxLines: 3,
                      decoration: const InputDecoration(
                        labelText: 'Ghi chú',
                        hintText: 'Lời nhắn cho người bán...',
                        border: OutlineInputBorder(),
                        alignLabelWithHint: true,
                      ),
                    ),
                  ],
                ),
              )
            ],
          ),
        ),
      ),

      bottomNavigationBar: Padding(
        padding: const EdgeInsets.all(AppSizes.defaultSpace),
        child: Obx(() {
            return ElevatedButton(
              onPressed: orderController.isLoading.value 
                  ? null 
                  : () => orderController.processOrder(),
              child: orderController.isLoading.value
                  ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                  : const Text('Đặt hàng'),
            );
        }),
      ),
    );
  }

  Widget _buildVoucherSelector(BuildContext context, bool dark, VoucherController controller) {
    return Obx(() {
      final selPlatform = controller.selectedPlatformVoucher.value;
      final selShipping = controller.selectedShippingVoucher.value;
      final selStores = controller.selectedStoreVouchers;

      int count = 0;
      if (selPlatform != null) count++;
      if (selShipping != null) count++;
      count += selStores.length;

      String subtitle = count > 0 ? "Đã chọn $count voucher" : "Chọn hoặc nhập mã";

      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SectionHeading(
            title: 'Shoex Voucher',
            buttonTitle: 'Chọn Mã',
            onButtonPressed: () => _showVoucherPicker(context),
          ),
          const SizedBox(height: AppSizes.spaceBtwItems / 2),
          
          InkWell(
            onTap: () => _showVoucherPicker(context),
            child: RoundedContainer(
              showBorder: true,
              padding: const EdgeInsets.all(AppSizes.md),
              bgcolor: dark ? AppColors.dark : AppColors.light,
              child: Row(
                children: [
                  const Icon(Icons.confirmation_number_outlined, color: AppColors.primary),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(subtitle, style: Theme.of(context).textTheme.bodyLarge),
                        if (selPlatform != null) 
                          Text("Sàn: ${selPlatform.code}", style: const TextStyle(fontSize: 12, color: Colors.green)),
                        if (selShipping != null)
                          Text("Ship: ${selShipping.code}", style: const TextStyle(fontSize: 12, color: Colors.blue)),
                      ],
                    ),
                  ),
                  const Icon(Icons.arrow_forward_ios, size: 14),
                ],
              ),
            ),
          ),
        ],
      );
    });
  }

  void _showVoucherPicker(BuildContext context) {
    final controller = Get.find<VoucherController>();
    
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      useSafeArea: true,
      builder: (ctx) {
        return DefaultTabController(
          length: 3,
          child: Scaffold(
            appBar: AppBar(
              title: const Text("Chọn Shoex Voucher"),
              leading: IconButton(onPressed: () => Get.back(), icon: const Icon(Icons.close)),
              bottom: const TabBar(
                tabs: [
                  Tab(text: "Shop"),
                  Tab(text: "Sàn"),
                  Tab(text: "Vận chuyển"),
                ],
              ),
            ),
            body: TabBarView(
              children: [
                // [FIX UI 1] Bọc Obx trực tiếp vào từng tab để nó lắng nghe chính xác
                Obx(() {
                  // Mẹo: Truy cập biến length hoặc value để GetX biết cần lắng nghe thay đổi
                  final _ = controller.selectedStoreVouchers.length; 
                  return _buildVoucherList(controller.availableStoreVouchers, controller, "Không có voucher Shop phù hợp", isStore: true);
                }),

                Obx(() {
                  final _ = controller.selectedPlatformVoucher.value;
                  return _buildVoucherList(controller.availablePlatformVouchers, controller, "Không có voucher Sàn phù hợp", isPlatform: true);
                }),

                Obx(() {
                  final _ = controller.selectedShippingVoucher.value;
                  return _buildVoucherList(controller.availableShippingVouchers, controller, "Không có voucher Ship phù hợp", isShipping: true);
                }),
              ],
            ),
            bottomNavigationBar: Padding(
              padding: const EdgeInsets.all(16),
              child: ElevatedButton(
                onPressed: () => Get.back(),
                child: const Text("Đồng ý"),
              ),
            ),
          ),
        );
      },
    );
  }

  Widget _buildVoucherList(List<VoucherModel> list, VoucherController controller, String emptyText, {bool isStore=false, bool isPlatform=false, bool isShipping=false}) {
    if (list.isEmpty) return Center(child: Text(emptyText));
    
    return ListView.builder(
      padding: const EdgeInsets.all(12),
      itemCount: list.length,
      itemBuilder: (_, i) => _buildVoucherItem(list[i], controller, isStore: isStore, isPlatform: isPlatform, isShipping: isShipping),
    );
  }

  Widget _buildVoucherItem(VoucherModel v, VoucherController controller, {bool isStore=false, bool isPlatform=false, bool isShipping=false}) {
    bool isSelected = false;
    
    if (isStore) {
      String vStoreId = v.storeId?.toString() ?? '';
      if (controller.selectedStoreVouchers.containsKey(vStoreId)) {
         isSelected = controller.selectedStoreVouchers[vStoreId]?.code == v.code;
      }
    } else if (isPlatform) {
      isSelected = controller.selectedPlatformVoucher.value?.code == v.code;
    } else if (isShipping) {
      isSelected = controller.selectedShippingVoucher.value?.code == v.code;
    }

    return Card(
      color: v.isUsable ? Colors.white : Colors.grey[200],
      margin: const EdgeInsets.only(bottom: 12),
      child: CheckboxListTile(
        title: Text(v.code, style: const TextStyle(fontWeight: FontWeight.bold)),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(v.discountString, style: const TextStyle(color: Colors.red)),
            if (!v.isUsable) 
              Text(v.reason ?? "Chưa đủ điều kiện", style: const TextStyle(color: Colors.grey, fontSize: 11)),
            if (v.minOrderAmount > 0) 
              Text("Đơn tối thiểu: ${v.minOrderAmount.toStringAsFixed(0)}", style: const TextStyle(fontSize: 11)),
            if (v.storeName != null)
              Text("Shop: ${v.storeName}", style: const TextStyle(fontSize: 11, fontStyle: FontStyle.italic)),
          ],
        ),
        value: isSelected,
        enabled: v.isUsable || isSelected, 
        onChanged: (val) {
          if (!v.isUsable && !isSelected) return;

          if (isStore) {
            if (v.storeId != null) {
               controller.selectStoreVoucher(v.storeId.toString(), val == true ? v : null);
            }
          } else if (isPlatform) {
            controller.selectPlatformVoucher(val == true ? v : null);
          } else if (isShipping) {
            controller.selectShippingVoucher(val == true ? v : null);
          }
        },
      ),
    );
  }

  // --- [FIX UI 2] Hàm xử lý URL ảnh sản phẩm sạch sẽ hơn ---
  Widget _getProductImage(CartItemModel item) {
    String imageUrl = item.image ?? '';
    
    // Logic fallback nếu ảnh trống
    if (imageUrl.isEmpty && item.productId != null) {
      // Giả sử backend host ở 10.0.2.2:8000
      imageUrl = "/media/products/${item.productId}/${item.productId}_0.jpg";
    }

    // Nếu đường dẫn là tương đối, thêm domain
    if (!imageUrl.startsWith('http')) {
      // Xử lý dấu gạch chéo kép nếu có
      if (imageUrl.startsWith('/')) {
        imageUrl = 'http://10.0.2.2:8000$imageUrl';
      } else {
        imageUrl = 'http://10.0.2.2:8000/$imageUrl';
      }
    }

    // Xử lý trường hợp null hoặc rỗng lần cuối
    if (imageUrl.isEmpty || imageUrl == 'http://10.0.2.2:8000/') {
       return const Icon(Icons.image, color: Colors.grey);
    }

    return Image.network(
      imageUrl,
      fit: BoxFit.cover,
      errorBuilder: (context, error, stackTrace) {
        // Nếu load ảnh lỗi (404), hiện icon thay thế
        return const Icon(Icons.broken_image, color: Colors.grey);
      },
    );
  }

  Widget _buildItemsByShop(BuildContext context, CartController cartController, bool dark) {
    final itemsByStore = <String, List>{};
    for (var item in cartController.selectedItems) {
      final storeName = item.storeName ?? 'Unknown Shop';
      if (!itemsByStore.containsKey(storeName)) {
        itemsByStore[storeName] = [];
      }
      itemsByStore[storeName]!.add(item);
    }

    if (itemsByStore.isEmpty) return const SizedBox();

    return Column(
      children: itemsByStore.entries.map((entry) {
        final storeName = entry.key;
        final items = entry.value;
        return Container(
          margin: const EdgeInsets.only(bottom: AppSizes.spaceBtwItems),
          decoration: BoxDecoration(
            color: dark ? AppColors.dark : Colors.white,
            borderRadius: BorderRadius.circular(AppSizes.cardRadiusMd),
            border: Border.all(color: dark ? AppColors.darkGrey : AppColors.grey),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                padding: const EdgeInsets.all(AppSizes.md),
                decoration: BoxDecoration(
                  color: dark ? AppColors.darkGrey : AppColors.light,
                  borderRadius: const BorderRadius.only(
                    topLeft: Radius.circular(AppSizes.cardRadiusMd),
                    topRight: Radius.circular(AppSizes.cardRadiusMd),
                  ),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.store, size: 18),
                    const SizedBox(width: 8),
                    Text(storeName, style: Theme.of(context).textTheme.titleSmall),
                  ],
                ),
              ),
              ListView.separated(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                padding: const EdgeInsets.all(AppSizes.md),
                separatorBuilder: (_, __) => const Divider(),
                itemCount: items.length,
                itemBuilder: (_, index) {
                  final item = items[index];
                  return Row(
                    children: [
                      RoundedContainer(
                        width: 50, height: 50,
                        padding: EdgeInsets.zero,
                        // Gọi hàm xử lý ảnh mới
                        child: _getProductImage(item),
                      ),
                      const SizedBox(width: 10),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(item.productName, maxLines: 1, overflow: TextOverflow.ellipsis),
                            Text("x${item.quantity}   \$${item.price.toStringAsFixed(0)}", style: const TextStyle(fontWeight: FontWeight.bold)),
                          ],
                        ),
                      )
                    ],
                  );
                },
              ),
            ],
          ),
        );
      }).toList(),
    );
  }
}