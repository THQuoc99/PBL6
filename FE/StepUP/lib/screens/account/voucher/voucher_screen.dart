import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:flutter_app/shop/controllers/voucher_controller.dart';
import 'package:flutter_app/shop/models/voucher_model.dart';
import 'package:flutter_app/features/shop/screens/cart/cart.dart';

class VoucherScreen extends StatelessWidget {
  const VoucherScreen({super.key});

  @override
  Widget build(BuildContext context) {
    // Đảm bảo controller được put
    final controller = Get.put(VoucherController());

    return DefaultTabController(
      length: 2,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('Kho Voucher'),
          bottom: const TabBar(
            tabs: [
              Tab(text: 'Tất cả'),
              Tab(text: 'Ví của tôi'),
            ],
          ),
        ),
        body: Padding(
          padding: const EdgeInsets.all(12.0),
          child: Column(
            children: [
              Obx(() {
                if (controller.isLoading.value) return const LinearProgressIndicator();
                return const SizedBox.shrink();
              }),
              const SizedBox(height: 8),

              Expanded(
                child: TabBarView(
                  children: [
                    // Tab 1: All available vouchers from API (fetchVouchers)
                    Obx(() {
                      // Note: In VoucherController, make sure 'vouchers' list is populated by fetchVouchers() 
                      // which calls GET /api/discounts/ (public list)
                      final list = controller.allVouchers; 
                      if (list.isEmpty) {
                        return const Center(child: Text('Không có voucher nào hiện tại'));
                      }
                      return ListView.builder(
                        itemCount: list.length,
                        itemBuilder: (context, index) {
                          final VoucherModel v = list[index];
                          // Check if saved in 'myVouchers' list
                          final isSaved = controller.myWalletVouchers.any((m) => m.code == v.code);
                          
                          return Card(
                            margin: const EdgeInsets.only(bottom: 10),
                            child: ListTile(
                              leading: const Icon(Icons.confirmation_number_outlined, color: Colors.blue),
                              title: Text(v.code, style: const TextStyle(fontWeight: FontWeight.bold)),
                              subtitle: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(v.discountString), // e.g. "-10%" or "-50k"
                                  Text('Hết hạn: ${v.endDate}', style: const TextStyle(fontSize: 12)),
                                  if (v.minOrderAmount > 0)
                                    Text('Đơn tối thiểu: ${v.minOrderAmount.toStringAsFixed(0)}đ', style: const TextStyle(fontSize: 12, color: Colors.grey)),
                                ],
                              ),
                              trailing: ElevatedButton(
                                onPressed: isSaved
                                    ? null
                                    : () async {
                                        final ok = await controller.saveVoucher(v.code);
                                        Get.snackbar(
                                          'Thông báo', 
                                          ok ? 'Lưu voucher thành công' : 'Không thể lưu voucher',
                                          snackPosition: SnackPosition.BOTTOM
                                        );
                                      },
                                style: ElevatedButton.styleFrom(
                                  backgroundColor: isSaved ? Colors.grey : Colors.blue,
                                  foregroundColor: Colors.white
                                ),
                                child: Text(isSaved ? 'Đã lưu' : 'Lưu'),
                              ),
                            ),
                          );
                        },
                      );
                    }),

                    // Tab 2: My Wallet (Saved Vouchers)
                    Obx(() {
                      final list = controller.myWalletVouchers; // populated by fetchMyWallet()
                      if (list.isEmpty) {
                        return const Center(child: Text('Bạn chưa lưu voucher nào'));
                      }
                      return ListView.builder(
                        itemCount: list.length,
                        itemBuilder: (context, index) {
                          final VoucherModel v = list[index];
                          return Card(
                            margin: const EdgeInsets.only(bottom: 10),
                            child: ListTile(
                              leading: const Icon(Icons.account_balance_wallet_outlined, color: Colors.green),
                              title: Text(v.code, style: const TextStyle(fontWeight: FontWeight.bold)),
                              subtitle: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(v.discountString),
                                  Text('Hết hạn: ${v.endDate}', style: const TextStyle(fontSize: 12)),
                                ],
                              ),
                              trailing: ElevatedButton(
                                onPressed: () {
                                  // Chuyển sang giỏ hàng để dùng ngay
                                  Get.to(() => const CartScreen());
                                },
                                child: const Text('Dùng ngay'),
                              ),
                            ),
                          );
                        },
                      );
                    }),
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