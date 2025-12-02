import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:flutter_app/common/widgets/chat/message_bubble.dart'; // Import widget đã tạo
import 'package:flutter_app/shop/controllers/chat_controller.dart'; // Import controller vừa tạo
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
                // Sử dụng MessageBubble custom để hỗ trợ Markdown và Link
                return MessageBubble(
                  message: msg.text,
                  isUser: msg.isUser,
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
}