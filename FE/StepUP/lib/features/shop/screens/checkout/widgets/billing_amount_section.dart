import 'package:flutter/material.dart';
import 'package:flutter_app/constants/sizes.dart';
import 'package:get/get.dart';
import 'package:flutter_app/shop/controllers/cart_controller.dart';
import 'package:flutter_app/shop/controllers/shipping_controller.dart';
import 'package:flutter_app/shop/controllers/voucher_controller.dart';

class BillingAmountSection extends StatelessWidget {
  const BillingAmountSection({super.key});

  @override
  Widget build(BuildContext context) {
    final controller = Get.put(CartController());
    final shippingController = Get.put(ShippingController());
    final voucherController = Get.put(VoucherController());

    return Obx(() {
      final subTotal = controller.totalAmount.value;
      final shippingFee = shippingController.shippingFee;
      final selectedPlatform = voucherController.selectedVoucher.value;
      final selectedShipping = voucherController.selectedShipping.value;
      final selectedStores = voucherController.selectedStoreVouchers;

      // compute per-store subtotals
      final Map<String, double> storeSubtotals = {};
      for (var item in controller.selectedItems) {
        final sid = item.storeId ?? 'unknown';
        storeSubtotals[sid] = (storeSubtotals[sid] ?? 0) + item.subTotal;
      }

      // Auto-apply best vouchers if user hasn't manually selected any
      try {
        final noManual = voucherController.selectedVoucher.value == null && voucherController.selectedShipping.value == null && voucherController.selectedStoreVouchers.isEmpty;
        if (noManual) {
          // use controller helper which calculates shipping fee first and applies once
          voucherController.tryAutoApply(storeSubtotals);
        }
      } catch (e) {}

      // compute store-level discounts
      double storeDiscountTotal = 0.0;
      final Map<String, double> storeDiscountMap = {};
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
          storeDiscountMap[sid] = d;
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
      double shippingFeeToShow = shippingFee;
      if (selectedShipping != null) {
        if (selectedShipping.isFreeShipping) {
          shippingFeeToShow = 0.0;
        } else if (selectedShipping.discountType == 'fixed') {
          shippingFeeToShow = (shippingFeeToShow - selectedShipping.discountValue).clamp(0.0, double.infinity);
        } else if (selectedShipping.discountType == 'percent') {
          shippingFeeToShow = shippingFeeToShow - (shippingFeeToShow * (selectedShipping.discountValue / 100.0));
        }
      }

      // Note: platform vouchers should not implicitly zero shipping here.
      // Shipping reductions are shown based on `selectedShipping` (or backend-calculated amounts).

      final totalDiscount = storeDiscountTotal + platformDiscount;
      final taxFee = 0.0;
      final total = subTotal - totalDiscount + shippingFeeToShow + taxFee;

      return Column(
        children: [
          // Subtotal
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('Subtotal', style: Theme.of(context).textTheme.bodyMedium),
              Text('\$${subTotal.toStringAsFixed(0)}', style: Theme.of(context).textTheme.bodyMedium),
            ],
          ),
          const SizedBox(height: AppSizes.spaceBtwItems / 2),

          // Shipping
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('Shipping Fee', style: Theme.of(context).textTheme.bodyMedium),
              Text(
                shippingFeeToShow == 0 
                    ? 'Miễn phí'
                    : '\$${shippingFeeToShow.toStringAsFixed(0)}',
                style: Theme.of(context).textTheme.labelLarge?.apply(
                  color: shippingFeeToShow == 0 ? Colors.green : null,
                ),
              ),
            ],
          ),
          const SizedBox(height: AppSizes.spaceBtwItems / 2),

          // Store voucher lines (itemized with code)
              for (final entry in storeDiscountMap.entries) ...[
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      'Voucher cửa hàng (${selectedStores[entry.key]?.code ?? ''})',
                      style: Theme.of(context).textTheme.bodyMedium,
                    ),
                    Text('-\$${(entry.value).toStringAsFixed(0)}', style: Theme.of(context).textTheme.bodyMedium?.apply(color: Colors.red)),
                  ],
                ),
                const SizedBox(height: AppSizes.spaceBtwItems / 2),
              ],

          // Platform voucher
          if (selectedPlatform != null) ...[
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text('Voucher (${selectedPlatform.code})', style: Theme.of(context).textTheme.bodyMedium),
                Text('-\$${platformDiscount.toStringAsFixed(0)}', style: Theme.of(context).textTheme.bodyMedium?.apply(color: Colors.red)),
              ],
            ),
            const SizedBox(height: AppSizes.spaceBtwItems / 2),
          ],

          // Shipping voucher line (show even when freeship)
          if (selectedShipping != null) ...[
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text('Voucher vận chuyển (${selectedShipping.code})', style: Theme.of(context).textTheme.bodyMedium),
                Text('-\$${(shippingFee - shippingFeeToShow).toStringAsFixed(0)}', style: Theme.of(context).textTheme.bodyMedium?.apply(color: Colors.red)),
              ],
            ),
            const SizedBox(height: AppSizes.spaceBtwItems / 2),
          ],

          const SizedBox(height: AppSizes.spaceBtwItems / 2),

          // Total
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('Total', style: Theme.of(context).textTheme.bodyMedium?.copyWith(fontWeight: FontWeight.bold)),
              Text('\$${total.toStringAsFixed(0)}', style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
            ],
          ),
        ],
      );
    });
  }
}