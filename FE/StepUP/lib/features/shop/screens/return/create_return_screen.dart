import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:iconsax_flutter/iconsax_flutter.dart';
import 'package:image_picker/image_picker.dart';
import 'package:flutter_app/shop/controllers/return_controller.dart';
import 'package:flutter_app/shop/models/order_model.dart';
import 'package:flutter_app/constants/colors.dart';

class CreateReturnScreen extends StatelessWidget {
  final OrderModel order;

  const CreateReturnScreen({super.key, required this.order});

  @override
  Widget build(BuildContext context) {
    final controller = Get.put(ReturnController());

    // Initialize với items từ order (chỉ lấy items đã completed)
    final availableItems = order.subOrders
        .where((sub) => sub.status == 'completed')
        .expand((sub) => sub.items)
        .toList();

    if (availableItems.isEmpty) {
      return Scaffold(
        appBar: AppBar(title: const Text('Tạo yêu cầu trả hàng')),
        body: const Center(
          child: Text('Đơn hàng chưa hoàn thành, không thể trả hàng'),
        ),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('Tạo yêu cầu trả hàng'),
        centerTitle: true,
      ),
      body: Obx(() => controller.isLoading.value
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _buildOrderInfo(),
                  const SizedBox(height: 20),
                  _buildReasonSection(controller),
                  const SizedBox(height: 20),
                  _buildDescriptionSection(controller),
                  const SizedBox(height: 20),
                  _buildItemsSection(controller, availableItems),
                  const SizedBox(height: 20),
                  _buildImageSection(controller),
                  const SizedBox(height: 30),
                  _buildSubmitButton(controller),
                  const SizedBox(height: 40),
                ],
              ),
            )),
    );
  }

  Widget _buildOrderInfo() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.blue.shade50,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          Icon(Iconsax.box, color: AppColors.primary, size: 32),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Đơn hàng #${order.id}',
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  'Đặt ngày ${order.formattedOrderDate}',
                  style: TextStyle(fontSize: 13, color: Colors.grey.shade600),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildReasonSection(ReturnController controller) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Lý do trả hàng *',
          style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
        ),
        const SizedBox(height: 12),
        Obx(() => Wrap(
              spacing: 8,
              runSpacing: 8,
              children: controller.reasonOptions.entries.map((entry) {
                final isSelected = controller.selectedReason.value == entry.key;
                return ChoiceChip(
                  label: Text(entry.value),
                  selected: isSelected,
                  onSelected: (selected) {
                    if (selected) {
                      controller.selectedReason.value = entry.key;
                    }
                  },
                  selectedColor: AppColors.primary.withOpacity(0.2),
                  labelStyle: TextStyle(
                    color: isSelected ? AppColors.primary : Colors.black87,
                    fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
                  ),
                );
              }).toList(),
            )),
      ],
    );
  }

  Widget _buildDescriptionSection(ReturnController controller) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Mô tả chi tiết *',
          style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
        ),
        const SizedBox(height: 12),
        TextField(
          controller: controller.descriptionController,
          maxLines: 4,
          maxLength: 500,
          decoration: InputDecoration(
            hintText: 'Vui lòng mô tả chi tiết vấn đề...',
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
            ),
            contentPadding: const EdgeInsets.all(16),
          ),
        ),
      ],
    );
  }

  Widget _buildItemsSection(ReturnController controller, List<OrderItemModel> items) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Chọn sản phẩm muốn trả *',
          style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
        ),
        const SizedBox(height: 12),
        ...items.map((item) => Obx(() {
              final isSelected = controller.selectedItems.contains(item);
              final currentQty = controller.itemQuantities[item.itemId] ?? item.quantity;

              return Container(
                margin: const EdgeInsets.only(bottom: 12),
                decoration: BoxDecoration(
                  border: Border.all(
                    color: isSelected ? AppColors.primary : Colors.grey.shade300,
                    width: isSelected ? 2 : 1,
                  ),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Column(
                  children: [
                    CheckboxListTile(
                      value: isSelected,
                      onChanged: (value) => controller.toggleItem(item),
                      title: Text(
                        item.productName,
                        style: const TextStyle(fontWeight: FontWeight.w600),
                      ),
                      subtitle: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          if (item.attributes.isNotEmpty)
                            Text(
                              item.attributes.entries
                                  .map((e) => '${e.key}: ${e.value}')
                                  .join(', '),
                              style: TextStyle(
                                fontSize: 13,
                                color: Colors.grey.shade600,
                              ),
                            ),
                          const SizedBox(height: 4),
                          Text(
                            '${item.priceAtOrder.toStringAsFixed(0)}đ x ${item.quantity}',
                            style: TextStyle(
                              color: AppColors.primary,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                        ],
                      ),
                      secondary: item.productImage != null
                          ? ClipRRect(
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
                            )
                          : null,
                    ),
                    if (isSelected && item.quantity > 1)
                      Padding(
                        padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
                        child: Row(
                          children: [
                            const Text('Số lượng trả: '),
                            const SizedBox(width: 12),
                            IconButton(
                              onPressed: currentQty > 1
                                  ? () => controller.updateItemQuantity(
                                      item.itemId, currentQty - 1)
                                  : null,
                              icon: const Icon(Icons.remove_circle_outline),
                            ),
                            Text(
                              currentQty.toString(),
                              style: const TextStyle(
                                fontSize: 16,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            IconButton(
                              onPressed: currentQty < item.quantity
                                  ? () => controller.updateItemQuantity(
                                      item.itemId, currentQty + 1)
                                  : null,
                              icon: const Icon(Icons.add_circle_outline),
                            ),
                            Expanded(
                              child: Text(
                                '(Tối đa: ${item.quantity})',
                                textAlign: TextAlign.end,
                                style: TextStyle(
                                  fontSize: 13,
                                  color: Colors.grey.shade600,
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                  ],
                ),
              );
            })),
      ],
    );
  }

  Widget _buildImageSection(ReturnController controller) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            const Text(
              'Ảnh chứng minh',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
            ),
            const SizedBox(width: 8),
            Obx(() => (controller.selectedReason.value == 'damaged' ||
                    controller.selectedReason.value == 'not_as_described')
                ? Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                    decoration: BoxDecoration(
                      color: Colors.red.shade100,
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: const Text(
                      'Bắt buộc',
                      style: TextStyle(fontSize: 11, color: Colors.red),
                    ),
                  )
                : const SizedBox()),
          ],
        ),
        const SizedBox(height: 8),
        Text(
          'Tối đa 5 ảnh',
          style: TextStyle(fontSize: 13, color: Colors.grey.shade600),
        ),
        const SizedBox(height: 12),
        Obx(() => Wrap(
              spacing: 12,
              runSpacing: 12,
              children: [
                ...controller.selectedImages.asMap().entries.map((entry) {
                  final index = entry.key;
                  final image = entry.value;
                  return Stack(
                    children: [
                      ClipRRect(
                        borderRadius: BorderRadius.circular(12),
                        child: Image.file(
                          image,
                          width: 100,
                          height: 100,
                          fit: BoxFit.cover,
                        ),
                      ),
                      Positioned(
                        top: 4,
                        right: 4,
                        child: GestureDetector(
                          onTap: () => controller.removeImage(index),
                          child: Container(
                            padding: const EdgeInsets.all(4),
                            decoration: const BoxDecoration(
                              color: Colors.red,
                              shape: BoxShape.circle,
                            ),
                            child: const Icon(
                              Icons.close,
                              color: Colors.white,
                              size: 16,
                            ),
                          ),
                        ),
                      ),
                    ],
                  );
                }),
                if (controller.selectedImages.length < 5)
                  GestureDetector(
                    onTap: () => _showImageSourceDialog(controller),
                    child: Container(
                      width: 100,
                      height: 100,
                      decoration: BoxDecoration(
                        color: Colors.grey.shade200,
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(
                          color: Colors.grey.shade400,
                          style: BorderStyle.solid,
                        ),
                      ),
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(Iconsax.camera, color: Colors.grey.shade600),
                          const SizedBox(height: 4),
                          Text(
                            'Thêm ảnh',
                            style: TextStyle(
                              fontSize: 12,
                              color: Colors.grey.shade600,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
              ],
            )),
      ],
    );
  }

  Widget _buildSubmitButton(ReturnController controller) {
    return Obx(() => Builder(
      builder: (context) => SizedBox(
        width: double.infinity,
        child: ElevatedButton(
          onPressed: controller.isLoading.value ? null : () async {
            print('Submit button pressed');
            print('Selected items: ${controller.selectedItems.length}');
            print('Description: ${controller.descriptionController.text}');
            print('Reason: ${controller.selectedReason.value}');
            
            final success = await controller.createReturnRequest(
              orderId: order.id,
            );
            if (success) {
              // Show success message using ScaffoldMessenger (safe)
              if (context.mounted) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content: Text('Yêu cầu trả hàng đã được gửi'),
                    backgroundColor: Colors.green,
                    duration: Duration(seconds: 2),
                  ),
                );
              }
              Get.back(); // Back to order detail
            } else {
              // Show error message
              if (context.mounted) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content: Text('Không thể tạo yêu cầu trả hàng. Vui lòng thử lại'),
                    backgroundColor: Colors.red,
                    duration: Duration(seconds: 2),
                  ),
                );
              }
            }
          },
          style: ElevatedButton.styleFrom(
            backgroundColor: AppColors.primary,
            padding: const EdgeInsets.symmetric(vertical: 16),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
          ),
          child: controller.isLoading.value
              ? const SizedBox(
                  height: 20,
                  width: 20,
                  child: CircularProgressIndicator(
                    color: Colors.white,
                    strokeWidth: 2,
                  ),
                )
              : const Text(
                  'Gửi yêu cầu trả hàng',
                  style: TextStyle(fontSize: 16, color: Colors.white),
                ),
        ),
      ),
    ));
  }

  void _showImageSourceDialog(ReturnController controller) {
    Get.dialog(
      AlertDialog(
        title: const Text('Chọn nguồn ảnh'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ListTile(
              leading: const Icon(Iconsax.camera),
              title: const Text('Chụp ảnh'),
              onTap: () {
                Get.back();
                controller.pickImage(source: ImageSource.camera);
              },
            ),
            ListTile(
              leading: const Icon(Iconsax.gallery),
              title: const Text('Chọn từ thư viện'),
              onTap: () {
                Get.back();
                controller.pickImage(source: ImageSource.gallery);
              },
            ),
          ],
        ),
      ),
    );
  }
}
