import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:flutter_app/screens/chatbox/chatbox.dart';

class HelpScreen extends StatelessWidget {
  const HelpScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Trợ giúp & Phản hồi')),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            ListTile(
              leading: const Icon(Icons.chat_bubble_outline),
              title: const Text('Chat hỗ trợ'),
              onTap: () {
                // Mở màn chat bot
                Get.to(() => const MyChatScreen());
              },
            ),
           
            const SizedBox(height: 12),
            const Text('Bạn cũng có thể xem FAQ hoặc liên hệ CSKH nếu cần hỗ trợ.'),
          ],
        ),
      ),
    );
  }
}
