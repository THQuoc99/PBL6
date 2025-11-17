import 'package:flutter/material.dart';
import 'package:chat_bubbles/chat_bubbles.dart'; // Import package

class MyChatScreen extends StatefulWidget {
  const MyChatScreen({super.key});

  @override
  State<MyChatScreen> createState() => _MyChatScreenState();
}

class _MyChatScreenState extends State<MyChatScreen> {
  // 1. Tạo một danh sách dữ liệu mẫu
  // Trong app thật, bạn sẽ thêm tin nhắn vào đây
  final List<Map<String, dynamic>> _messages = [
    {'text': 'Xin chào! Tôi là AI.', 'isSender': false},  
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('AI Chatbox')),
      body: Column(
        children: [
          // 2. Dùng Expanded để ListView lấp đầy phần còn lại
          Expanded(
            child: ListView.builder(
              // 3. Đếm số lượng tin nhắn
              itemCount: _messages.length,
              
              // 4. Hàm này sẽ được gọi để "vẽ" từng tin nhắn
              itemBuilder: (context, index) {
                final message = _messages[index];
                
                // 5. Trả về bong bóng chat
                return BubbleSpecialThree(
                  text: message['text'],
                  isSender: message['isSender'],
                  color: message['isSender'] 
                      ? Colors.blue 
                      : const Color(0xFFE8E8EE),
                  textStyle: TextStyle(
                    color: message['isSender'] ? Colors.white : Colors.black,
                  ),
                );
              },
            ),
          ),

          // 6. Khu vực nhập liệu (Giả lập)
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.white,
              boxShadow: [
                BoxShadow(
                  color: Colors.grey,
                  blurRadius: 5,
                )
              ]
            ),
            child: const TextField(
              decoration: InputDecoration(
                hintText: 'Nhập tin nhắn...',
                border: InputBorder.none,
              ),
            ),
          )
        ],
      ),
    );
  }
}