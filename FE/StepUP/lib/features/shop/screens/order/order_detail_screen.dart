import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:iconsax_flutter/iconsax_flutter.dart';
import 'package:flutter_app/shop/models/order_model.dart';
import 'package:flutter_app/shop/controllers/order_controller.dart';
import 'package:flutter_app/constants/colors.dart';

class OrderDetailScreen extends StatelessWidget {
  final OrderModel order;

  const OrderDetailScreen({super.key, required this.order});

  @override
  Widget build(BuildContext context) {
    final controller = Get.put(OrderController());

    final bool isCOD = order.paymentMethod.toUpperCase() == 'COD';
    // Logic hiển thị nút thanh toán lại: Chỉ hiện khi pending/failed VÀ không phải COD
    final bool showRepayButton = (order.paymentStatus == 'pending' || order.paymentStatus == 'failed') 
                                  && !isCOD 
                                  && order.status != 'cancelled';

    return Scaffold(
      appBar: AppBar(
        title: Text("Đơn hàng #${order.id}"),
        centerTitle: true,
      ),
      bottomNavigationBar: showRepayButton
          ? Container(
              padding: const EdgeInsets.all(16.0),
              decoration: BoxDecoration(
                color: Colors.white,
                boxShadow: [
                  BoxShadow(
                    color: Colors.grey.withOpacity(0.1),
                    blurRadius: 10,
                    offset: const Offset(0, -5),
                  ),
                ],
              ),
              child: ElevatedButton(
                onPressed: () => controller.repayOrder(order),
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppColors.primary,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                ),
                child: const Text("Thanh toán ngay", style: TextStyle(fontSize: 16, color: Colors.white)),
              ),
            )
          : null,
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            _buildTrackingSection(context, isCOD),
            const SizedBox(height: 20),
            _buildAddressSection(context),
            const SizedBox(height: 20),
            _buildPaymentSection(context, isCOD),
            const SizedBox(height: 20),
            _buildItemsByShopSection(context),
            const SizedBox(height: 20),
            _buildTotalSection(context),
            const SizedBox(height: 40),
          ],
        ),
      ),
    );
  }

  // 1. Widget Tracking (Trạng thái đơn hàng)
  Widget _buildTrackingSection(BuildContext context, bool isCOD) {
    int currentStep = 0;
    String statusText = "";
    Color statusColor = Colors.blue;
    String step1Label = isCOD ? "Duyệt đơn" : "Thanh toán";

    switch (order.status.toLowerCase()) {
      case 'pending':
        if (isCOD) {
          currentStep = 1; 
          statusText = "Đang chuẩn bị hàng";
          statusColor = Colors.teal;
        } else {
          currentStep = 0;
          statusText = "Chờ thanh toán";
          statusColor = Colors.orange;
        }
        break;
      case 'paid': 
        currentStep = 1;
        statusText = "Đang chuẩn bị hàng";
        statusColor = Colors.teal;
        break;
      case 'shipped':
        currentStep = 2;
        statusText = "Đang giao hàng";
        statusColor = Colors.blue;
        break;
      case 'completed':
        currentStep = 3;
        statusText = "Giao hàng thành công";
        statusColor = Colors.green;
        break;
      case 'cancelled':
      case 'failed':
        currentStep = -1;
        statusText = "Đã hủy";
        statusColor = Colors.red;
        break;
      default:
        statusText = "Chờ xử lý";
        statusColor = Colors.grey;
    }

    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Iconsax.truck_fast, color: statusColor),
                const SizedBox(width: 10),
                Text("Thông tin vận chuyển", style: Theme.of(context).textTheme.titleLarge!.copyWith(fontSize: 16)),
              ],
            ),
            const Divider(height: 20),

            Text(
              statusText.toUpperCase(),
              style: TextStyle(color: statusColor, fontWeight: FontWeight.w900, fontSize: 18),
            ),
            const SizedBox(height: 4),
            Text("Cập nhật: ${order.formattedOrderDate}", style: const TextStyle(color: Colors.grey, fontSize: 12)),
            
            const SizedBox(height: 20),

            // TIMELINE
            if (currentStep != -1)
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  _buildStepIcon(0, currentStep, Iconsax.box, "Đặt hàng"),
                  _buildStepLine(0, currentStep),
                  _buildStepIcon(1, currentStep, isCOD ? Iconsax.box_add : Iconsax.card, step1Label),
                  _buildStepLine(1, currentStep),
                  _buildStepIcon(2, currentStep, Iconsax.truck, "Vận chuyển"),
                  _buildStepLine(2, currentStep),
                  _buildStepIcon(3, currentStep, Iconsax.box_tick, "Nhận hàng"),
                ],
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildStepIcon(int stepIndex, int currentStep, IconData icon, String label) {
    bool isActive = currentStep >= stepIndex;
    return Column(
      children: [
        Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: isActive ? AppColors.primary : Colors.grey[200],
            shape: BoxShape.circle,
          ),
          child: Icon(icon, size: 16, color: isActive ? Colors.white : Colors.grey),
        ),
        const SizedBox(height: 4),
        Text(
          label,
          style: TextStyle(
            fontSize: 10,
            color: isActive ? AppColors.primary : Colors.grey,
            fontWeight: isActive ? FontWeight.bold : FontWeight.normal,
          ),
        )
      ],
    );
  }

  Widget _buildStepLine(int stepIndex, int currentStep) {
    bool isActive = currentStep > stepIndex;
    return Expanded(
      child: Container(
        height: 2,
        color: isActive ? AppColors.primary : Colors.grey[300],
        margin: const EdgeInsets.only(bottom: 14),
      ),
    );
  }

  // 2. Widget Địa chỉ
  Widget _buildAddressSection(BuildContext context) {
    final addr = order.address;
    if (addr == null) return const SizedBox.shrink();
    return Card(
      elevation: 2, shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _sectionHeader(Iconsax.location, "Địa chỉ nhận hàng"),
            const SizedBox(height: 10),
            Text(addr.name, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
            const SizedBox(height: 4),
            Text(addr.phoneNumber, style: const TextStyle(color: Colors.grey)),
            const SizedBox(height: 8),
            Text(addr.fullAddress, style: const TextStyle(fontSize: 14, height: 1.4)),
          ],
        ),
      ),
    );
  }

  // 3. Widget Thanh toán
  Widget _buildPaymentSection(BuildContext context, bool isCOD) {
    String paymentStatusText = "CHƯA THANH TOÁN";
    Color paymentColor = Colors.orange;
    IconData paymentIcon = Icons.error;

    if (order.status == 'completed' || order.status == 'paid' || order.status == 'shipped' || order.paymentStatus == 'paid') {
      paymentStatusText = "ĐÃ THANH TOÁN";
      paymentColor = Colors.green;
      paymentIcon = Icons.check_circle;
    } else if (order.status == 'cancelled') {
      paymentStatusText = "ĐÃ HỦY";
      paymentColor = Colors.grey;
      paymentIcon = Icons.cancel;
    } else if (isCOD) {
      paymentStatusText = "THANH TOÁN KHI NHẬN";
      paymentColor = Colors.blue;
      paymentIcon = Icons.money;
    }

    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            _sectionHeader(Iconsax.card, "Thanh toán"),
            const SizedBox(height: 10),
            _detailRow("Phương thức", order.paymentMethod, isBold: true),
            const SizedBox(height: 8),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text("Trạng thái", style: TextStyle(color: Colors.grey)),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: paymentColor.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Row(
                    children: [
                      Icon(paymentIcon, size: 14, color: paymentColor),
                      const SizedBox(width: 4),
                      Text(
                        paymentStatusText,
                        style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: paymentColor),
                      ),
                    ],
                  ),
                )
              ],
            )
          ],
        ),
      ),
    );
  }

  // 4. Widget Danh sách sản phẩm (Chia theo Shop)
  Widget _buildItemsByShopSection(BuildContext context) {
    return Column(
      children: order.subOrders.map((subOrder) {
        return Card(
          elevation: 2,
          margin: const EdgeInsets.only(bottom: 16),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Header Shop
                Row(
                  children: [
                    const Icon(Iconsax.shop, size: 20, color: AppColors.primary),
                    const SizedBox(width: 8),
                    Text(
                      subOrder.storeName, 
                      style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)
                    ),
                    const Spacer(),
                    // Trạng thái riêng của gói hàng này
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                      decoration: BoxDecoration(
                        color: Colors.grey[100],
                        borderRadius: BorderRadius.circular(4)
                      ),
                      child: Text(subOrder.status.toUpperCase(), style: const TextStyle(fontSize: 10, fontWeight: FontWeight.bold)),
                    )
                  ],
                ),
                const Divider(height: 20),
                
                // Danh sách items trong shop này
                ...subOrder.items.map((item) => Padding(
                  padding: const EdgeInsets.symmetric(vertical: 8.0),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // Ảnh sản phẩm
                      Container(
                        width: 60, height: 60,
                        decoration: BoxDecoration(
                          color: Colors.grey[200],
                          borderRadius: BorderRadius.circular(8),
                          image: item.productImage != null 
                              ? DecorationImage(image: NetworkImage(item.productImage!), fit: BoxFit.cover)
                              : null
                        ),
                        child: item.productImage == null ? const Icon(Iconsax.image, color: Colors.grey) : null,
                      ),
                      const SizedBox(width: 12),
                      
                      // Thông tin
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(item.productName, maxLines: 2, overflow: TextOverflow.ellipsis, style: const TextStyle(fontWeight: FontWeight.w600)),
                            const SizedBox(height: 4),
                            // Hiển thị thuộc tính (Màu/Size)
                            if (item.attributes.isNotEmpty)
                              Text(item.attributes.values.join(' - '), style: const TextStyle(color: Colors.grey, fontSize: 12)),
                            const SizedBox(height: 4),
                            Text("x${item.quantity}", style: const TextStyle(color: Colors.black)),
                          ],
                        )
                      ),
                      
                      // Giá
                      Text("\$${(item.quantity * item.priceAtOrder).toStringAsFixed(0)}", style: const TextStyle(fontWeight: FontWeight.bold)),
                    ],
                  ),
                )),
                
                const Divider(height: 20),
                
                // Tổng tiền của shop này (Subtotal)
                Row(
                  mainAxisAlignment: MainAxisAlignment.end,
                  children: [
                    const Text("Tổng shop: ", style: TextStyle(color: Colors.grey)),
                    Text("\$${subOrder.subTotal.toStringAsFixed(0)}", style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                  ],
                )
              ],
            ),
          ),
        );
      }).toList(),
    );
  }

  // 5. Widget Tổng tiền đơn hàng
  Widget _buildTotalSection(BuildContext context) {
    double shippingFee = 0.0; 
    double total = order.totalAmount + shippingFee;
    return Card(
      elevation: 2, shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            _detailRow("Tạm tính", "\$${order.totalAmount.toStringAsFixed(0)}"),
            const SizedBox(height: 8),
            _detailRow("Phí vận chuyển", "\$0"), 
            const Divider(height: 24),
            _detailRow("Tổng cộng", "\$${total.toStringAsFixed(0)}", isBold: true, fontSize: 18, color: AppColors.primary),
          ],
        ),
      ),
    );
  }

  // Helpers
  Widget _sectionHeader(IconData icon, String title) {
    return Row(children: [Icon(icon, size: 18, color: AppColors.primary), const SizedBox(width: 8), Text(title, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16))]);
  }

  Widget _detailRow(String label, String value, {bool isBold = false, double fontSize = 14, Color? color}) {
    return Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [Text(label, style: const TextStyle(color: Colors.grey)), Text(value, style: TextStyle(fontWeight: isBold ? FontWeight.bold : FontWeight.normal, fontSize: fontSize, color: color ?? Colors.black))]);
  }
}