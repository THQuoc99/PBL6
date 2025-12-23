import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:flutter_app/shop/controllers/voucher_controller.dart';
import 'package:flutter_app/shop/models/voucher_model.dart';
import 'package:flutter_app/features/shop/screens/cart/cart.dart';

class VoucherScreen extends StatelessWidget {
  const VoucherScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final controller = Get.put(VoucherController());

    return DefaultTabController(
      length: 2,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('Voucher & Ưu đãi'),
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
                    // Tab 1: All vouchers (available to save)
                    Obx(() {
                      final list = controller.vouchers;
                      if (list.isEmpty) {
                        return const Center(child: Text('Không có voucher nào hiện tại'));
                      }
                      return ListView.builder(
                        itemCount: list.length,
                        itemBuilder: (context, index) {
                          final VoucherModel v = list[index];
                          final saved = controller.myVouchers.any((m) => m.code == v.code);
                          return Card(
                            child: ListTile(
                              title: Text(v.title.isNotEmpty ? v.title : v.code),
                              subtitle: Text('${v.code} • Hết hạn: ${v.endDate}'),
                              trailing: ElevatedButton(
                                onPressed: saved
                                    ? null
                                    : () async {
                                        final ok = await controller.saveVoucher(v.code);
                                        Get.snackbar('Voucher', ok ? 'Lưu voucher thành công' : 'Không thể lưu voucher');
                                      },
                                child: Text(saved ? 'Đã lưu' : 'Lưu'),
                              ),
                            ),
                          );
                        },
                      );
                    }),

                    // Tab 2: My wallet
                    Obx(() {
                      final list = controller.myVouchers;
                      if (list.isEmpty) {
                        return const Center(child: Text('Bạn chưa lưu voucher nào'));
                      }
                      return ListView.builder(
                        itemCount: list.length,
                        itemBuilder: (context, index) {
                          final VoucherModel v = list[index];
                          return Card(
                            child: ListTile(
                              title: Text(v.title.isNotEmpty ? v.title : v.code),
                              subtitle: Text('${v.code} • Hết hạn: ${v.endDate}'),
                              trailing: ElevatedButton(
                                onPressed: () async {
                                  // Assign voucher type: shipping vs platform vs store
                                  if (v.isFreeShipping) {
                                    controller.selectShippingVoucher(v);
                                  } else if (v.type == 'platform') {
                                    controller.selectVoucher(v);
                                  } else if (v.type == 'store') {
                                    // assign to applicable stores if provided
                                    if (v.applicableStores != null && v.applicableStores!.isNotEmpty) {
                                      for (final s in v.applicableStores!) {
                                        controller.setStoreVoucher('$s', v);
                                      }
                                    } else {
                                      // fallback: treat as platform/store-agnostic
                                      controller.selectVoucher(v);
                                    }
                                  }
                                  // Navigate to cart screen to use the voucher
                                  Get.to(() => const CartScreen());
                                },
                                child: const Text('Dùng'),
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
