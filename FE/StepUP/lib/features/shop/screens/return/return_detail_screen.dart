import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:iconsax_flutter/iconsax_flutter.dart';
import 'package:flutter_app/shop/controllers/return_controller.dart';
import 'package:flutter_app/shop/controllers/order_list_controller.dart';
import 'package:flutter_app/shop/models/return_model.dart';
import 'package:flutter_app/constants/colors.dart';
import 'package:timeline_tile/timeline_tile.dart';

class ReturnDetailScreen extends StatelessWidget {
  final ReturnRequestModel returnRequest;

  const ReturnDetailScreen({super.key, required this.returnRequest});

  @override
  Widget build(BuildContext context) {
    final controller = Get.put(ReturnController());

    // Fetch latest data
    WidgetsBinding.instance.addPostFrameCallback((_) {
      controller.fetchReturnDetail(returnRequest.returnId);
    });

    return Scaffold(
      appBar: AppBar(
        title: Text('Yêu cầu #${returnRequest.returnId}'),
        centerTitle: true,
      ),
      body: Obx(() {
        final detail = controller.selectedReturn.value ?? returnRequest;

        return SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildStatusSection(detail),
              const SizedBox(height: 24),
              _buildInfoSection(detail),
              const SizedBox(height: 24),
              _buildItemsSection(detail),
              const SizedBox(height: 24),
              if (detail.images.isNotEmpty) ...[
                _buildImagesSection(detail),
                const SizedBox(height: 24),
              ],
              _buildTrackingTimeline(detail),
              const SizedBox(height: 24),
              _buildActionButtons(context, controller, detail),
              const SizedBox(height: 40),
            ],
          ),
        );
      }),
    );
  }

  Widget _buildStatusSection(ReturnRequestModel detail) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: _getStatusGradient(detail.status),
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: _getStatusGradient(detail.status)[0].withOpacity(0.3),
            blurRadius: 10,
            offset: const Offset(0, 5),
          ),
        ],
      ),
      child: Column(
        children: [
          Icon(
            _getStatusIcon(detail.status),
            size: 48,
            color: Colors.white,
          ),
          const SizedBox(height: 12),
          Text(
            detail.statusDisplay,
            style: const TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            detail.returnTypeDisplay,
            style: const TextStyle(
              fontSize: 14,
              color: Colors.white70,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildInfoSection(ReturnRequestModel detail) {
    return Card(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Thông tin yêu cầu',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const Divider(height: 24),
            _buildInfoRow(Iconsax.box, 'Đơn hàng', '#${detail.orderId}'),
            const SizedBox(height: 12),
            _buildInfoRow(Iconsax.message_question, 'Lý do', detail.reasonDisplay),
            const SizedBox(height: 12),
            _buildInfoRow(Iconsax.calendar, 'Ngày tạo', detail.formattedCreatedAt),
            if (detail.completedAt != null) ...[
              const SizedBox(height: 12),
              _buildInfoRow(Iconsax.tick_circle, 'Hoàn thành', detail.formattedCompletedAt!),
            ],
            if (detail.trackingCode != null) ...[
              const SizedBox(height: 12),
              _buildInfoRow(Iconsax.truck, 'Mã vận đơn', detail.trackingCode!),
            ],
            const Divider(height: 24),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'Số tiền hoàn',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
                ),
                Text(
                  '${detail.refundAmount.toStringAsFixed(0)}đ',
                  style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                    color: AppColors.primary,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildInfoRow(IconData icon, String label, String value) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Icon(icon, size: 20, color: Colors.grey.shade600),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                label,
                style: TextStyle(
                  fontSize: 13,
                  color: Colors.grey.shade600,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                value,
                style: const TextStyle(
                  fontSize: 15,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildItemsSection(ReturnRequestModel detail) {
    return Card(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Sản phẩm trả',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const Divider(height: 24),
            ...detail.items.map((item) => Padding(
                  padding: const EdgeInsets.only(bottom: 16),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      if (item.productImage != null)
                        ClipRRect(
                          borderRadius: BorderRadius.circular(8),
                          child: Image.network(
                            item.productImage!,
                            width: 60,
                            height: 60,
                            fit: BoxFit.cover,
                            errorBuilder: (_, __, ___) => Container(
                              width: 60,
                              height: 60,
                              color: Colors.grey.shade200,
                              child: const Icon(Iconsax.image),
                            ),
                          ),
                        ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              item.productName,
                              style: const TextStyle(
                                fontSize: 15,
                                fontWeight: FontWeight.w600,
                              ),
                              maxLines: 2,
                              overflow: TextOverflow.ellipsis,
                            ),
                            if (item.attributes.isNotEmpty) ...[
                              const SizedBox(height: 4),
                              Text(
                                item.attributes.entries
                                    .map((e) => '${e.key}: ${e.value}')
                                    .join(', '),
                                style: TextStyle(
                                  fontSize: 13,
                                  color: Colors.grey.shade600,
                                ),
                              ),
                            ],
                            const SizedBox(height: 8),
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Text(
                                  '${item.priceAtOrder.toStringAsFixed(0)}đ',
                                  style: TextStyle(
                                    fontSize: 14,
                                    color: AppColors.primary,
                                    fontWeight: FontWeight.w600,
                                  ),
                                ),
                                Text(
                                  'x${item.quantity}',
                                  style: TextStyle(
                                    fontSize: 14,
                                    color: Colors.grey.shade600,
                                  ),
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                )),
          ],
        ),
      ),
    );
  }

  Widget _buildImagesSection(ReturnRequestModel detail) {
    return Card(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Ảnh chứng minh',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            Wrap(
              spacing: 12,
              runSpacing: 12,
              children: detail.images.map((img) {
                return GestureDetector(
                  onTap: () => _showImageDialog(img.imageUrl),
                  child: ClipRRect(
                    borderRadius: BorderRadius.circular(8),
                    child: Image.network(
                      img.imageUrl,
                      width: 100,
                      height: 100,
                      fit: BoxFit.cover,
                      errorBuilder: (_, __, ___) => Container(
                        width: 100,
                        height: 100,
                        color: Colors.grey.shade200,
                        child: const Icon(Iconsax.image),
                      ),
                    ),
                  ),
                );
              }).toList(),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTrackingTimeline(ReturnRequestModel detail) {
    if (detail.trackingHistory.isEmpty) {
      return const SizedBox();
    }

    return Card(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Lịch sử xử lý',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            ...detail.trackingHistory.asMap().entries.map((entry) {
              final index = entry.key;
              final tracking = entry.value;
              final isFirst = index == 0;
              final isLast = index == detail.trackingHistory.length - 1;

              return TimelineTile(
                isFirst: isFirst,
                isLast: isLast,
                beforeLineStyle: LineStyle(
                  color: Colors.grey.shade300,
                  thickness: 2,
                ),
                indicatorStyle: IndicatorStyle(
                  width: 30,
                  height: 30,
                  indicator: Container(
                    decoration: BoxDecoration(
                      color: isFirst ? AppColors.primary : Colors.grey.shade300,
                      shape: BoxShape.circle,
                    ),
                    child: Icon(
                      isFirst ? Iconsax.tick_circle : Iconsax.record_circle,
                      size: 16,
                      color: isFirst ? Colors.white : Colors.grey.shade600,
                    ),
                  ),
                ),
                endChild: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        tracking.statusDisplay,
                        style: TextStyle(
                          fontSize: 15,
                          fontWeight: isFirst ? FontWeight.bold : FontWeight.w600,
                          color: isFirst ? AppColors.primary : Colors.black87,
                        ),
                      ),
                      if (tracking.note != null) ...[
                        const SizedBox(height: 4),
                        Text(
                          tracking.note!,
                          style: TextStyle(
                            fontSize: 13,
                            color: Colors.grey.shade600,
                          ),
                        ),
                      ],
                      const SizedBox(height: 4),
                      Text(
                        tracking.createdAt.toString().substring(0, 16),
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.grey.shade500,
                        ),
                      ),
                    ],
                  ),
                ),
              );
            }),
          ],
        ),
      ),
    );
  }

  Widget _buildActionButtons(BuildContext context, ReturnController controller, ReturnRequestModel detail) {
    return Column(
      children: [
        if (detail.canUpdateTracking)
          SizedBox(
            width: double.infinity,
            child: ElevatedButton.icon(
              onPressed: () => _showTrackingDialog(context, controller, detail),
              icon: const Icon(Iconsax.truck, color: Colors.white),
              label: const Text('Cập nhật mã vận đơn', style: TextStyle(color: Colors.white)),
              style: ElevatedButton.styleFrom(
                backgroundColor: AppColors.primary,
                padding: const EdgeInsets.symmetric(vertical: 14),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              ),
            ),
          ),
        if (detail.canCancel) ...[
          if (detail.canUpdateTracking) const SizedBox(height: 12),
          SizedBox(
            width: double.infinity,
            child: OutlinedButton.icon(
              onPressed: () => _showCancelDialog(context, controller, detail),
              icon: const Icon(Iconsax.close_circle, color: Colors.red),
              label: const Text('Hủy yêu cầu', style: TextStyle(color: Colors.red)),
              style: OutlinedButton.styleFrom(
                side: const BorderSide(color: Colors.red),
                padding: const EdgeInsets.symmetric(vertical: 14),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              ),
            ),
          ),
        ],
      ],
    );
  }

  List<Color> _getStatusGradient(String status) {
    switch (status) {
      case 'pending':
        return [Colors.orange.shade400, Colors.orange.shade600];
      case 'approved':
        return [Colors.blue.shade400, Colors.blue.shade600];
      case 'shipping_back':
        return [Colors.purple.shade400, Colors.purple.shade600];
      case 'received':
        return [Colors.teal.shade400, Colors.teal.shade600];
      case 'completed':
        return [Colors.green.shade400, Colors.green.shade600];
      case 'rejected':
      case 'cancelled':
        return [Colors.red.shade400, Colors.red.shade600];
      default:
        return [Colors.grey.shade400, Colors.grey.shade600];
    }
  }

  IconData _getStatusIcon(String status) {
    switch (status) {
      case 'pending':
        return Iconsax.clock;
      case 'approved':
        return Iconsax.tick_circle;
      case 'shipping_back':
        return Iconsax.truck;
      case 'received':
        return Iconsax.box_tick;
      case 'completed':
        return Iconsax.verify;
      case 'rejected':
      case 'cancelled':
        return Iconsax.close_circle;
      default:
        return Iconsax.info_circle;
    }
  }

  void _showImageDialog(String imageUrl) {
    Get.dialog(
      Dialog(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Stack(
              children: [
                Image.network(imageUrl),
                Positioned(
                  top: 8,
                  right: 8,
                  child: IconButton(
                    onPressed: () => Get.back(),
                    icon: const Icon(Icons.close),
                    style: IconButton.styleFrom(
                      backgroundColor: Colors.black54,
                      foregroundColor: Colors.white,
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  void _showTrackingDialog(BuildContext context, ReturnController controller, ReturnRequestModel detail) {
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
                detail.returnId,
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
            style: ElevatedButton.styleFrom(backgroundColor: AppColors.primary),
            child: const Text('Xác nhận', style: TextStyle(color: Colors.white)),
          ),
        ],
      ),
    );
  }

  void _showCancelDialog(BuildContext context, ReturnController controller, ReturnRequestModel detail) {
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
              final success = await controller.cancelReturn(detail.returnId);
              if (success) {
                // Refresh order list to update hasReturnRequest flag
                try {
                  final orderListController = Get.find<OrderListController>();
                  orderListController.fetchUserOrders();
                } catch (e) {
                  print('OrderListController not found: $e');
                }
                
                if (context.mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text('Đã hủy yêu cầu trả hàng'),
                      backgroundColor: Colors.green,
                    ),
                  );
                }
                Get.back(); // Back to list
              } else {
                if (context.mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text('Không thể hủy yêu cầu'),
                      backgroundColor: Colors.red,
                    ),
                  );
                }
              }
            },
            child: const Text('Hủy yêu cầu', style: TextStyle(color: Colors.red)),
          ),
        ],
      ),
    );
  }
}
