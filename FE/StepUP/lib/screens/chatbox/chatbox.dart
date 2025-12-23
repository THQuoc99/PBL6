import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:flutter_app/common/widgets/chat/message_bubble.dart';
import 'package:flutter_app/shop/controllers/chat_controller.dart';
import 'package:flutter_app/shop/controllers/product_controller.dart';
import 'package:flutter_app/screens/product_details/product_detail.dart';
import 'package:flutter_app/constants/colors.dart';

class MyChatScreen extends StatelessWidget {
  const MyChatScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final controller = Get.put(ChatController());

    return Scaffold(
      appBar: AppBar(
        title: const Text('AI Chatbot Shoex'),
        centerTitle: true,
        backgroundColor: Colors.white,
        elevation: 0,
        titleTextStyle: const TextStyle(color: Colors.black, fontWeight: FontWeight.bold, fontSize: 18),
        iconTheme: const IconThemeData(color: Colors.black),
      ),
      body: Column(
        children: [
          // --- DANH SÁCH TIN NHẮN ---
          Expanded(
            child: Obx(() => ListView.builder(
              controller: controller.scrollController,
              padding: const EdgeInsets.all(16),
              itemCount: controller.messages.length,
              itemBuilder: (context, index) {
                final msg = controller.messages[index];
                return Column(
                  crossAxisAlignment: msg.isUser ? CrossAxisAlignment.end : CrossAxisAlignment.start,
                  children: [
                    // Main message bubble
                    MessageBubble(
                      message: msg.text,
                      isUser: msg.isUser,
                    ),
                    
                    // Product cards (only for bot messages)
                    if (!msg.isUser && msg.products != null && msg.products!.isNotEmpty)
                      Padding(
                        padding: const EdgeInsets.only(left: 8, top: 8, bottom: 8),
                        child: Column(
                          children: msg.products!.map((product) {
                            return _buildProductCard(context, product, controller);
                          }).toList(),
                        ),
                      ),
                    
                    // Recommendation bubble (separate from main message)
                    if (!msg.isUser && msg.recommendation != null && msg.recommendation!.isNotEmpty)
                      Padding(
                        padding: const EdgeInsets.only(left: 8, top: 8),
                        child: MessageBubble(
                          message: msg.recommendation!,
                          isUser: false,
                        ),
                      ),
                  ],
                );
              },
            )),
          ),

          // --- INDICATOR KHI ĐANG TẢI ---
          Obx(() {
            if (controller.isLoading.value) {
              return const Padding(
                padding: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                child: Align(
                  alignment: Alignment.centerLeft,
                  child: Text("Shoex đang soạn tin...", style: TextStyle(color: Colors.grey, fontStyle: FontStyle.italic)),
                ),
              );
            }
            return const SizedBox.shrink();
          }),

          // --- Ô NHẬP LIỆU ---
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
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
            child: Row(
              children: [
                Expanded(
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 16),
                    decoration: BoxDecoration(
                      color: Colors.grey[100],
                      borderRadius: BorderRadius.circular(24),
                    ),
                    child: TextField(
                      controller: controller.textController,
                      textCapitalization: TextCapitalization.sentences,
                      decoration: const InputDecoration(
                        hintText: 'Hỏi gì đó về giày...',
                        border: InputBorder.none,
                      ),
                      onSubmitted: (_) => controller.sendMessage(),
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                
                // Nút gửi
                Obx(() => CircleAvatar(
                  backgroundColor: controller.isLoading.value ? Colors.grey : AppColors.primary,
                  child: IconButton(
                    icon: const Icon(Icons.send, color: Colors.white, size: 20),
                    onPressed: controller.isLoading.value ? null : controller.sendMessage,
                  ),
                )),
              ],
            ),
          ),
        ],
      ),
    );
  }
  
  Widget _buildProductCard(BuildContext context, ChatProduct product, ChatController controller) {
    String imageUrl = "http://10.0.2.2:8000/media/products/${product.id}/${product.id}_0.jpg";
    
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey.shade200),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.1),
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: InkWell(
        onTap: () async {
          // Fetch full product and navigate
          final productController = Get.put(ProductController());
          Get.dialog(
            const Center(child: CircularProgressIndicator()),
            barrierDismissible: false,
          );
          
          final fullProduct = await productController.fetchProductById(product.id);
          Get.back(); // Close loading
          
          if (fullProduct != null) {
            Get.to(() => ProductDetail(product: fullProduct));
          } else {
            Get.snackbar(
              'Lỗi',
              'Không thể tải thông tin sản phẩm',
              backgroundColor: Colors.red.withOpacity(0.1),
              colorText: Colors.red,
            );
          }
        },
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Row(
            children: [
              // Product image
              ClipRRect(
                borderRadius: BorderRadius.circular(8),
                child: Image.network(
                  imageUrl,
                  width: 60,
                  height: 60,
                  fit: BoxFit.cover,
                  errorBuilder: (_, __, ___) => Container(
                    width: 60,
                    height: 60,
                    color: Colors.grey.shade200,
                    child: const Icon(Icons.image, color: Colors.grey),
                  ),
                ),
              ),
              const SizedBox(width: 12),
              
              // Product info
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      product.name,
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(
                        fontSize: 14,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      '₫${product.price.toString().replaceAllMapped(RegExp(r'(\d{1,3})(?=(\d{3})+(?!\d))'), (Match m) => '${m[1]},')}',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: Colors.red.shade700,
                      ),
                    ),
                  ],
                ),
              ),
              
              // Arrow icon
              Icon(
                Icons.arrow_forward_ios,
                size: 16,
                color: Colors.grey.shade400,
              ),
            ],
          ),
        ),
      ),
    );
  }
}