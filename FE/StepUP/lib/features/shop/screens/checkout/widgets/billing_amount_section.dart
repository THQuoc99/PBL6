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
    final cartController = Get.find<CartController>();
    final shippingController = Get.find<ShippingController>();
    final voucherController = Get.find<VoucherController>();

    return Obx(() {
      final subTotal = cartController.totalAmount.value;
      final shippingFee = shippingController.shippingFee;
      
      // Calculate Discounts (Client Side Estimate)
      double totalDiscount = 0.0;
      
      // 1. Store Discounts
      double storeDiscount = 0.0;
      // Note: This is simplified. Real calculation needs to map items to stores.
      // Assuming VoucherController's calculateTotalDiscount is implemented or we calculate here.
      voucherController.selectedStoreVouchers.forEach((storeId, voucher) {
         if(voucher.discountType == 'fixed') {
           storeDiscount += voucher.discountValue;
         } else {
           // Estimate percent on total (not accurate without per-store subtotal)
           // In real app, calculate subtotal per store
         }
      });

      // 2. Platform Discount
      double platformDiscount = 0.0;
      final pVoucher = voucherController.selectedPlatformVoucher.value;
      if (pVoucher != null) {
         if (pVoucher.discountType == 'fixed') {
           platformDiscount = pVoucher.discountValue;
         } else {
           platformDiscount = (subTotal - storeDiscount) * (pVoucher.discountValue / 100);
           if (pVoucher.maxDiscount != null && platformDiscount > pVoucher.maxDiscount!) {
             platformDiscount = pVoucher.maxDiscount!;
           }
         }
      }

      // 3. Shipping Discount
      double shippingDiscount = 0.0;
      final sVoucher = voucherController.selectedShippingVoucher.value;
      if (sVoucher != null) {
        if (sVoucher.isFreeShipping) {
          shippingDiscount = shippingFee;
        } else if (sVoucher.discountType == 'fixed') {
          shippingDiscount = sVoucher.discountValue;
        } else {
          shippingDiscount = shippingFee * (sVoucher.discountValue / 100);
        }
      }
      // Cap shipping discount
      if (shippingDiscount > shippingFee) shippingDiscount = shippingFee;

      totalDiscount = storeDiscount + platformDiscount + shippingDiscount;
      final total = subTotal + shippingFee - totalDiscount;

      return Column(
        children: [
          // Subtotal
          _buildRow('Tổng tiền hàng', subTotal),
          const SizedBox(height: AppSizes.spaceBtwItems / 2),

          // Shipping
          _buildRow('Phí vận chuyển', shippingFee),
          const SizedBox(height: AppSizes.spaceBtwItems / 2),

          // Discounts
          if (storeDiscount > 0)
            _buildRow('Voucher Shop', -storeDiscount, isDiscount: true),
          if (platformDiscount > 0)
            _buildRow('Voucher Sàn', -platformDiscount, isDiscount: true),
          if (shippingDiscount > 0)
            _buildRow('Voucher Vận chuyển', -shippingDiscount, isDiscount: true),

          const SizedBox(height: AppSizes.spaceBtwItems / 2),
          const Divider(),
          const SizedBox(height: AppSizes.spaceBtwItems / 2),

          // Total
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('Tổng thanh toán', style: Theme.of(context).textTheme.headlineSmall),
              Text('\$${total.toStringAsFixed(0)}', style: Theme.of(context).textTheme.headlineSmall),
            ],
          ),
        ],
      );
    });
  }

  Widget _buildRow(String label, double value, {bool isDiscount = false}) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(label, style: const TextStyle(fontSize: 14)),
        Text(
          '${isDiscount ? "" : ""}\$${value.abs().toStringAsFixed(0)}',
          style: TextStyle(
            fontSize: 14, 
            fontWeight: FontWeight.w600,
            color: isDiscount ? Colors.green : null
          ),
        ),
      ],
    );
  }
}