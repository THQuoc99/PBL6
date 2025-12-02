import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

// Model tin nhắn đơn giản
class ChatMessage {
  final String text;
  final bool isUser;
  ChatMessage({required this.text, required this.isUser});
}

class ChatController extends GetxController {
  final messages = <ChatMessage>[].obs;
  final isLoading = false.obs;
  final textController = TextEditingController();
  final scrollController = ScrollController();

  // URL Backend (Thay đổi nếu đã deploy)
  final String baseUrl = "http://10.0.2.2:8000/chatbot/chat/";

  @override
  void onInit() {
    super.onInit();
    // Tin nhắn chào mừng
    messages.add(ChatMessage(text: "Xin chào! Tôi là trợ lý ảo Shoex. Bạn cần tìm giày gì không?", isUser: false));
  }

  Future<void> sendMessage() async {
    final text = textController.text.trim();
    if (text.isEmpty) return;

    // 1. Thêm tin nhắn của User lên UI
    messages.add(ChatMessage(text: text, isUser: true));
    textController.clear();
    isLoading.value = true;
    _scrollToBottom();

    try {
      // 2. Lấy Token
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('token');

      Map<String, String> headers = {
        "Content-Type": "application/json",
      };
      if (token != null && token.isNotEmpty) {
        headers["Authorization"] = "Bearer $token";
      }

      // 3. Gọi API
      final response = await http.post(
        Uri.parse(baseUrl),
        headers: headers,
        body: jsonEncode({"message": text}),
      );

      // 4. Xử lý phản hồi
      if (response.statusCode == 200) {
        final data = jsonDecode(utf8.decode(response.bodyBytes));
        final botReply = data['response'];
        messages.add(ChatMessage(text: botReply, isUser: false));
      } else {
        messages.add(ChatMessage(text: "Lỗi server: ${response.statusCode}", isUser: false));
      }
    } catch (e) {
      print("Chat Error: $e");
      messages.add(ChatMessage(text: "Không thể kết nối tới máy chủ.", isUser: false));
    } finally {
      isLoading.value = false;
      _scrollToBottom();
    }
  }

  void _scrollToBottom() {
    Future.delayed(const Duration(milliseconds: 100), () {
      if (scrollController.hasClients) {
        scrollController.animateTo(
          scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }
  
  @override
  void onClose() {
    textController.dispose();
    scrollController.dispose();
    super.onClose();
  }
}