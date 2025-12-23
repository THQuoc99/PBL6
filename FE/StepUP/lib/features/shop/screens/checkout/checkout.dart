import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:flutter_app/constants/sizes.dart';
import 'package:flutter_app/constants/colors.dart';
import 'package:flutter_app/utils/helpers/helper_function.dart';
import 'package:flutter_app/widgets/appbar/appbar.dart';
import 'package:flutter_app/widgets/containers/rounded_container.dart';
import 'package:flutter_app/common/widgets/products/cart/coupon_code_field.dart';
import 'package:flutter_app/features/shop/screens/checkout/widgets/billing_address_section.dart';
import 'package:flutter_app/features/shop/screens/checkout/widgets/billing_amount_section.dart';
import 'package:flutter_app/features/shop/screens/checkout/widgets/billing_shipping_section.dart';
import 'widgets/billing_payment_section.dart';
import 'package:flutter_app/shop/controllers/cart_controller.dart';
import 'package:flutter_app/shop/controllers/order_controller.dart';
import 'package:flutter_app/shop/controllers/address_controller.dart';
import 'package:flutter_app/shop/controllers/shipping_controller.dart';
import 'package:flutter_app/shop/controllers/voucher_controller.dart';
import 'package:flutter_app/screens/home/components/section_heading.dart';

class CheckoutScreen extends StatelessWidget {
  const CheckoutScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final dark = HelperFunction.isDarkMode(context);
    final cartController = Get.put(CartController()); 
    Get.put(AddressController());
    final orderController = Get.put(OrderController());
    final shippingController = Get.put(ShippingController());

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
              // 1. List Items by Shop
              Obx(() => _buildItemsByShop(context, cartController, dark)),
              const SizedBox(height: AppSizes.spaceBtwSections),

              // 2. Coupon
              const CouponCode(),
              const SizedBox(height: AppSizes.spaceBtwSections),

              const SizedBox(height: AppSizes.spaceBtwSections),

              // 3. Billing Info
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

                    // Voucher selector placed above payment methods
                    Builder(builder: (ctx) {
                      final voucherController = Get.put(VoucherController());
                      return Obx(() {
                        final selPlatform = voucherController.selectedVoucher.value;
                        final selShipping = voucherController.selectedShipping.value;
                        final selStores = voucherController.selectedStoreVouchers;
                        final codes = <String>[];
                        if (selPlatform != null) codes.add('Nền tảng:${selPlatform.code}');
                        if (selShipping != null) codes.add('Vận chuyển:${selShipping.code}');
                        if (selStores.isNotEmpty) codes.addAll(selStores.values.map((v) => 'Shop:${v.code}'));
                        final hasSelection = codes.isNotEmpty;
                        final title = hasSelection ? 'Voucher đã chọn (${codes.length})' : 'Chọn voucher';
                        final subtitle = hasSelection ? codes.join(' • ') : '';
                        return Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            SectionHeading(
                              title: 'Voucher',
                              buttonTitle: 'Thay đổi',
                              onButtonPressed: () => _showVoucherPicker(ctx),
                            ),
                            const SizedBox(height: AppSizes.spaceBtwItems / 2),
                            RoundedContainer(
                              showBorder: true,
                              padding: const EdgeInsets.all(AppSizes.md),
                              bgcolor: dark ? AppColors.dark : AppColors.light,
                              child: ListTile(
                                onTap: () => _showVoucherPicker(ctx),
                                title: Text(title),
                                subtitle: subtitle.isNotEmpty ? Text(subtitle) : null,
                                trailing: Row(
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    if (hasSelection)
                                      IconButton(
                                        icon: const Icon(Icons.clear, size: 20),
                                        onPressed: () {
                                          voucherController.clearAllSelections();
                                        },
                                      ),
                                    const SizedBox(width: 4),
                                    const Icon(Icons.arrow_forward_ios, size: 16),
                                  ],
                                ),
                              ),
                            ),
                          ],
                        );
                      });
                    }),
                    const SizedBox(height: AppSizes.spaceBtwItems),
                    const Divider(),
                    const SizedBox(height: AppSizes.spaceBtwItems),

                    const BillingPaymentSection(), 
                    
                    const SizedBox(height: AppSizes.spaceBtwItems),
                    const Divider(),
                    const SizedBox(height: AppSizes.spaceBtwItems),
                    
                    // Shipping Section
                    const BillingShippingSection(),
                    
                    const SizedBox(height: AppSizes.spaceBtwItems),
                    const Divider(),
                    const SizedBox(height: AppSizes.spaceBtwItems),
                    
                    const BillingAddressSection(),
                    
                    const SizedBox(height: AppSizes.spaceBtwItems),
                    const Divider(),
                    const SizedBox(height: AppSizes.spaceBtwItems),
                    
                    // Order Note
                    TextField(
                      controller: orderController.noteController,
                      maxLines: 3,
                      decoration: const InputDecoration(
                        labelText: 'Ghi chú đơn hàng',
                        hintText: 'Nhập ghi chú cho shop (tùy chọn)',
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

      // 4. Checkout Button
      bottomNavigationBar: Padding(
        padding: const EdgeInsets.all(AppSizes.defaultSpace),
        child: Obx(() {
            final subTotal = cartController.totalAmount.value;
            final voucherController = Get.put(VoucherController());
            final selectedPlatform = voucherController.selectedVoucher.value;
            final selectedShipping = voucherController.selectedShipping.value;
            final selectedStores = voucherController.selectedStoreVouchers;

            // compute per-store subtotals
            final Map<String, double> storeSubtotals = {};
            for (var item in cartController.selectedItems) {
              final sid = item.storeId ?? 'unknown';
              storeSubtotals[sid] = (storeSubtotals[sid] ?? 0) + item.subTotal;
            }

            // compute store-level discounts
            double storeDiscountTotal = 0.0;
            for (final entry in storeSubtotals.entries) {
              final sid = entry.key;
              final subtotal = entry.value;
              final v = selectedStores[sid];
              if (v != null) {
                double d = 0.0;
                if (v.discountType == 'fixed') {
                  d = v.discountValue;
                  if (d > subtotal) d = subtotal;
                } else {
                  d = subtotal * (v.discountValue / 100.0);
                  if (v.maxDiscount != null) d = d > v.maxDiscount! ? v.maxDiscount! : d;
                }
                storeDiscountTotal += d;
              }
            }

            // apply platform voucher on remaining subtotal
            double platformDiscount = 0.0;
            final remaining = subTotal - storeDiscountTotal;
            if (selectedPlatform != null) {
              if (selectedPlatform.discountType == 'fixed') {
                platformDiscount = selectedPlatform.discountValue;
                if (platformDiscount > remaining) platformDiscount = remaining;
              } else {
                platformDiscount = remaining * (selectedPlatform.discountValue / 100.0);
                if (selectedPlatform.maxDiscount != null) platformDiscount = platformDiscount > selectedPlatform.maxDiscount! ? selectedPlatform.maxDiscount! : platformDiscount;
              }
            }

            // shipping adjustments from selected shipping voucher
            double shippingFeeToShow = shippingController.shippingFee;
            if (selectedShipping != null) {
              if (selectedShipping.isFreeShipping) {
                shippingFeeToShow = 0.0;
              } else if (selectedShipping.discountType == 'fixed') {
                shippingFeeToShow = (shippingFeeToShow - selectedShipping.discountValue).clamp(0.0, double.infinity);
              } else if (selectedShipping.discountType == 'percent') {
                shippingFeeToShow = shippingFeeToShow - (shippingFeeToShow * (selectedShipping.discountValue / 100.0));
              }
            }

            // platform fixed voucher can also cover shipping
            if (selectedPlatform != null && selectedPlatform.discountType == 'fixed') {
              if (selectedPlatform.discountValue >= shippingFeeToShow) shippingFeeToShow = 0.0;
            }

            final total = subTotal - (storeDiscountTotal + platformDiscount) + shippingFeeToShow;

          return ElevatedButton(
            // Gọi hàm processOrder khi nhấn
            onPressed: orderController.isLoading.value 
                ? null 
                : () => orderController.processOrder(),
            child: orderController.isLoading.value
                ? const SizedBox(
                    width: 20, 
                    height: 20, 
                    child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2)
                  )
                : Text('Thanh toán \$${total.toStringAsFixed(0)}'),
          );
        }),
      ),
    );
  }

  void _showVoucherPicker(BuildContext context) {
    final voucherController = Get.put(VoucherController());
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      builder: (ctx) {
        return Padding(
          padding: const EdgeInsets.all(12.0),
          child: SafeArea(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const SizedBox(height: 8),
                Text('Chọn voucher', style: Theme.of(context).textTheme.titleMedium),
                const SizedBox(height: 12),
                // My Wallet
                Obx(() {
                  final my = voucherController.myVouchers;
                  return Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text('Ví của tôi', style: TextStyle(fontWeight: FontWeight.bold)),
                      const SizedBox(height: 8),
                      if (my.isEmpty) const Text('Bạn chưa lưu voucher nào'),
                      ...my.map((v) => ListTile(
                        title: Text(v.title.isNotEmpty ? v.title : v.code),
                        subtitle: Text('${v.code} • Hết hạn: ${v.endDate}'),
                        onTap: () {
                          // If voucher is explicitly a shipping-type voucher, treat as shipping.
                          if (v.type == 'shipping') {
                            voucherController.selectShippingVoucher(v);
                          } else {
                            // For platform/store vouchers that also have free-shipping flag,
                            // select them as platform/store AND also set selectedShipping so UI shows freeship effect.
                            voucherController.selectVoucher(v);
                            if (v.isFreeShipping) voucherController.selectedShipping.value = v;
                          }
                          Navigator.of(ctx).pop();
                        },
                      ))
                    ],
                  );
                }),
                const Divider(),
                // All vouchers
                Obx(() {
                  final all = voucherController.vouchers;
                  return Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text('Tất cả', style: TextStyle(fontWeight: FontWeight.bold)),
                      const SizedBox(height: 8),
                      if (all.isEmpty) const Text('Không có voucher nào'),
                      ...all.map((v) => ListTile(
                        title: Text(v.title.isNotEmpty ? v.title : v.code),
                        subtitle: Text('${v.code} • Hết hạn: ${v.endDate}'),
                        onTap: () {
                          if (v.type == 'shipping') {
                            voucherController.selectShippingVoucher(v);
                          } else {
                            voucherController.selectVoucher(v);
                            if (v.isFreeShipping) voucherController.selectedShipping.value = v;
                          }
                          Navigator.of(ctx).pop();
                        },
                      ))
                    ],
                  );
                }),
                const SizedBox(height: 12),
              ],
            ),
          ),
        );
      }
    );
  }

  // Build items grouped by shop
  Widget _buildItemsByShop(BuildContext context, CartController cartController, bool dark) {
    // Group selected items by store
    final itemsByStore = <String, List>{};
    
    for (var item in cartController.selectedItems) {
      final storeName = item.storeName ?? 'Unknown Shop';
      if (!itemsByStore.containsKey(storeName)) {
        itemsByStore[storeName] = [];
      }
      itemsByStore[storeName]!.add(item);
    }

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
              // Shop Header
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
                    const Icon(Icons.store, size: 20),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        storeName,
                        style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
              
              // Items in this shop
              ListView.separated(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                padding: const EdgeInsets.all(AppSizes.md),
                separatorBuilder: (_, __) => const Divider(height: 20),
                itemCount: items.length,
                itemBuilder: (_, index) {
                  final item = items[index];
                  
                  return Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // Product Image
                      Container(
                        width: 60,
                        height: 60,
                        decoration: BoxDecoration(
                          color: dark ? AppColors.darkGrey : AppColors.light,
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Builder(builder: (context) {
                          String imageUrl = item.image ?? '';
                          if (imageUrl.startsWith('/media')) {
                            imageUrl = 'http://10.0.2.2:8000$imageUrl';
                          }

                          if (imageUrl.isNotEmpty) {
                            return ClipRRect(
                              borderRadius: BorderRadius.circular(8),
                              child: Image.network(
                                imageUrl,
                                fit: BoxFit.cover,
                                errorBuilder: (context, error, stackTrace) {
                                  return const Icon(Icons.image, color: Colors.grey);
                                },
                                loadingBuilder: (context, child, loadingProgress) {
                                  if (loadingProgress == null) return child;
                                  return const Center(
                                    child: CircularProgressIndicator(strokeWidth: 2),
                                  );
                                },
                              ),
                            );
                          }

                          return const Icon(Icons.image, color: Colors.grey);
                        }),
                      ),
                      const SizedBox(width: 12),
                      
                      // Product Info
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              item.productName,
                              maxLines: 2,
                              overflow: TextOverflow.ellipsis,
                              style: const TextStyle(fontWeight: FontWeight.w600),
                            ),
                            const SizedBox(height: 4),
                            // Attributes (Size/Color)
                            if (item.selectedVariation.isNotEmpty)
                              Text(
                                item.selectedVariation.values.join(' - '),
                                style: const TextStyle(color: Colors.grey, fontSize: 12),
                              ),
                            const SizedBox(height: 4),
                            Text(
                              "x${item.quantity}",
                              style: const TextStyle(color: Colors.black),
                            ),
                          ],
                        ),
                      ),
                      
                      // Price
                      Text(
                        "\$${(item.quantity * item.price).toStringAsFixed(0)}",
                        style: const TextStyle(fontWeight: FontWeight.bold),
                      ),
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