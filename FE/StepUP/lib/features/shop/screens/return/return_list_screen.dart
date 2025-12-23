import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:iconsax_flutter/iconsax_flutter.dart';
import 'package:flutter_app/shop/controllers/return_controller.dart';
import 'package:flutter_app/shop/controllers/order_list_controller.dart';
import 'package:flutter_app/shop/models/return_model.dart';
import 'package:flutter_app/features/shop/screens/return/return_detail_screen.dart';
import 'package:flutter_app/constants/colors.dart';

class ReturnListScreen extends StatelessWidget {
  const ReturnListScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final controller = Get.put(ReturnController());

    // Fetch returns khi mở màn hình
    WidgetsBinding.instance.addPostFrameCallback((_) {
      controller.fetchMyReturns();
    });

    return Scaffold(
      body: Obx(() {
        if (controller.isLoading.value) {
          return const Center(child: CircularProgressIndicator());
        }

        if (controller.returns.isEmpty) {
          return _buildEmptyState();
        }

        return RefreshIndicator(
          onRefresh: controller.fetchMyReturns,
          child: ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: controller.returns.length,
            itemBuilder: (context, index) {
              final returnRequest = controller.returns[index];
              return _buildReturnCard(context, returnRequest);
            },
          ),
        );
      }),
    );
  }

  Widget _buildFilterChips(ReturnController controller) {
    final filters = [
      {'label': 'Tất cả', 'value': null},
      {'label': 'Chờ duyệt', 'value': 'pending'},
      {'label': 'Đã duyệt', 'value': 'approved'},
      {'label': 'Đang gửi về', 'value': 'shipping_back'},
      {'label': 'Hoàn thành', 'value': 'completed'},
    ];

    return Container(
      padding: const EdgeInsets.symmetric(vertical: 12),
      child: SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 16),
        child: Obx(() => Row(
          children: filters.map((filter) {
            final filterValue = filter['value'] as String?;
            final isSelected = controller.selectedFilterStatus.value == filterValue;
            
            return Padding(
              padding: const EdgeInsets.only(right: 8),
              child: FilterChip(
                label: Text(filter['label'] as String),
                selected: isSelected,
                onSelected: (selected) {
                  controller.setFilterStatus(filterValue);
                },
                selectedColor: AppColors.primary.withOpacity(0.2),
                labelStyle: TextStyle(
                  color: isSelected ? AppColors.primary : Colors.black87,
                  fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
                ),
              ),
            );
          }).toList(),
        )),
      ),
    );
  }

  Widget _buildReturnCard(BuildContext context, ReturnRequestModel returnRequest) {
    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      elevation: 2,
      child: InkWell(
        onTap: () => Get.to(() => ReturnDetailScreen(returnRequest: returnRequest)),
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header: Return ID + Status
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'Yêu cầu #${returnRequest.returnId}',
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  _buildStatusChip(returnRequest.status),
                ],
              ),
              const Divider(height: 24),
              
              // Order info
              Row(
                children: [
                  Icon(Iconsax.box, size: 18, color: Colors.grey.shade600),
                  const SizedBox(width: 8),
                  Text(
                    'Đơn hàng #${returnRequest.orderId}',
                    style: TextStyle(fontSize: 14, color: Colors.grey.shade700),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              
              // Reason
              Row(
                children: [
                  Icon(Iconsax.message_question, size: 18, color: Colors.grey.shade600),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      returnRequest.reasonDisplay,
                      style: TextStyle(fontSize: 14, color: Colors.grey.shade700),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              
              // Items count + Refund amount
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    '${returnRequest.items.length} sản phẩm',
                    style: const TextStyle(fontSize: 14),
                  ),
                  Text(
                    '${returnRequest.refundAmount.toStringAsFixed(0)}đ',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: AppColors.primary,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              
              // Created date
              Text(
                'Tạo lúc: ${returnRequest.formattedCreatedAt}',
                style: TextStyle(fontSize: 12, color: Colors.grey.shade500),
              ),
              
              // Action buttons for certain statuses
              if (returnRequest.canCancel || returnRequest.canUpdateTracking) ...[
                const SizedBox(height: 12),
                Row(
                  children: [
                    if (returnRequest.canCancel)
                      Expanded(
                        child: OutlinedButton(
                          onPressed: () => _showCancelDialog(context, returnRequest),
                          style: OutlinedButton.styleFrom(
                            side: const BorderSide(color: Colors.red),
                          ),
                          child: const Text(
                            'Hủy yêu cầu',
                            style: TextStyle(color: Colors.red),
                          ),
                        ),
                      ),
                    if (returnRequest.canUpdateTracking) ...[
                      if (returnRequest.canCancel) const SizedBox(width: 12),
                      Expanded(
                        child: ElevatedButton(
                          onPressed: () => _showTrackingDialog(context, returnRequest),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: AppColors.primary,
                          ),
                          child: const Text(
                            'Cập nhật vận đơn',
                            style: TextStyle(color: Colors.white),
                          ),
                        ),
                      ),
                    ],
                  ],
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildStatusChip(String status) {
    Color bgColor;
    Color textColor;

    switch (status) {
      case 'pending':
        bgColor = Colors.orange.shade100;
        textColor = Colors.orange.shade700;
        break;
      case 'approved':
        bgColor = Colors.blue.shade100;
        textColor = Colors.blue.shade700;
        break;
      case 'shipping_back':
        bgColor = Colors.purple.shade100;
        textColor = Colors.purple.shade700;
        break;
      case 'received':
        bgColor = Colors.teal.shade100;
        textColor = Colors.teal.shade700;
        break;
      case 'completed':
        bgColor = Colors.green.shade100;
        textColor = Colors.green.shade700;
        break;
      case 'rejected':
      case 'cancelled':
        bgColor = Colors.red.shade100;
        textColor = Colors.red.shade700;
        break;
      default:
        bgColor = Colors.grey.shade200;
        textColor = Colors.grey.shade700;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: bgColor,
        borderRadius: BorderRadius.circular(20),
      ),
      child: Text(
        _getStatusDisplay(status),
        style: TextStyle(
          fontSize: 12,
          fontWeight: FontWeight.w600,
          color: textColor,
        ),
      ),
    );
  }

  String _getStatusDisplay(String status) {
    const statusMap = {
      'pending': 'Chờ duyệt',
      'approved': 'Đã duyệt',
      'rejected': 'Từ chối',
      'shipping_back': 'Đang gửi về',
      'received': 'Đã nhận',
      'completed': 'Hoàn thành',
      'cancelled': 'Đã hủy',
    };
    return statusMap[status] ?? status;
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Iconsax.box_remove, size: 80, color: Colors.grey.shade400),
          const SizedBox(height: 16),
          Text(
            'Chưa có yêu cầu trả hàng nào',
            style: TextStyle(
              fontSize: 16,
              color: Colors.grey.shade600,
            ),
          ),
        ],
      ),
    );
  }

  void _showCancelDialog(BuildContext context, ReturnRequestModel returnRequest) {
    Get.dialog(
      AlertDialog(
        title: const Text('Hủy yêu cầu'),
        content: const Text('Bạn có chắc chắn muốn hủy yêu cầu trả hàng này?'),
        actions: [
          TextButton(
            onPressed: () => Get.back(),
            child: const Text('Không'),
          ),
          TextButton(
            onPressed: () async {
              Get.back();
              final controller = ReturnController.instance;
              final success = await controller.cancelReturn(returnRequest.returnId);
              if (success) {
                // Refresh order list to update hasReturnRequest flag
                try {
                  final orderListController = Get.find<OrderListController>();
                  orderListController.fetchUserOrders();
                } catch (e) {
                  print('OrderListController not found: $e');
                }
              }
              if (context.mounted) {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text(success ? 'Đã hủy yêu cầu trả hàng' : 'Không thể hủy yêu cầu'),
                    backgroundColor: success ? Colors.green : Colors.red,
                  ),
                );
              }
            },
            child: const Text(
              'Hủy yêu cầu',
              style: TextStyle(color: Colors.red),
            ),
          ),
        ],
      ),
    );
  }

  void _showTrackingDialog(BuildContext context, ReturnRequestModel returnRequest) {
    final controller = ReturnController.instance;
    controller.trackingCodeController.clear();

    Get.dialog(
      AlertDialog(
        title: const Text('Cập nhật mã vận đơn'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text(
              'Nhập mã vận đơn khi bạn đã gửi hàng về cho shop',
              style: TextStyle(fontSize: 14),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: controller.trackingCodeController,
              decoration: const InputDecoration(
                labelText: 'Mã vận đơn',
                hintText: 'VD: GHTK123456789',
                border: OutlineInputBorder(),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Get.back(),
            child: const Text('Hủy'),
          ),
          ElevatedButton(
            onPressed: () async {
              Get.back();
              final success = await controller.updateTrackingCode(
                returnRequest.returnId,
                controller.trackingCodeController.text,
              );
              if (context.mounted) {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text(success ? 'Đã cập nhật mã vận đơn' : 'Không thể cập nhật mã vận đơn'),
                    backgroundColor: success ? Colors.green : Colors.red,
                  ),
                );
              }
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: AppColors.primary,
            ),
            child: const Text('Xác nhận', style: TextStyle(color: Colors.white)),
          ),
        ],
      ),
    );
  }
}
