import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:chat_bubbles/chat_bubbles.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart'; // ✅ Đổi từ get_storage sang shared_preferences

class MyChatScreen extends StatefulWidget {
  const MyChatScreen({super.key});

  @override
  State<MyChatScreen> createState() => _MyChatScreenState();
}

class _MyChatScreenState extends State<MyChatScreen> {
  final TextEditingController _textController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  
  final ValueNotifier<bool> _isTypingNotifier = ValueNotifier(false);

  bool _isLoading = false;

  final List<Map<String, dynamic>> _messages = [
    {'text': 'Xin chào! Tôi là trợ lý ảo Shoex. Bạn cần tìm giày gì không?', 'isSender': false},
  ];

  @override
  void dispose() {
    _textController.dispose();
    _scrollController.dispose();
    _isTypingNotifier.dispose();
    super.dispose();
  }

  Future<void> _sendMessage() async {
    final text = _textController.text.trim();
    if (text.isEmpty) return;

    setState(() {
      _messages.add({'text': text, 'isSender': true});
      _isLoading = true;
    });
    
    _textController.clear();
    _isTypingNotifier.value = false;
    
    _scrollToBottom();

    try {
      // ✅ SỬA LỖI TOKEN: Dùng SharedPreferences thay vì GetStorage
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('token'); 

      print("DEBUG CHAT: Token từ SharedPreferences: $token");

      Map<String, String> headers = {
        "Content-Type": "application/json",
      };
      if (token != null && token.isNotEmpty) {
        headers["Authorization"] = "Bearer $token";
      }

      final url = Uri.parse('http://10.0.2.2:8000/chatbot/chat/'); 
      
      final response = await http.post(
        url,
        headers: headers,
        body: jsonEncode({"message": text}),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(utf8.decode(response.bodyBytes)); 
        final botReply = data['response'];

        setState(() {
          _messages.add({'text': botReply, 'isSender': false});
        });
      } else {
        setState(() {
          _messages.add({'text': "Lỗi server: ${response.statusCode}", 'isSender': false});
        });
      }
    } catch (e) {
      setState(() {
        _messages.add({'text': "Lỗi kết nối: $e", 'isSender': false});
      });
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
        _scrollToBottom();
      }
    }
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('AI Chatbot Shoex'),
        centerTitle: true,
      ),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              controller: _scrollController,
              padding: const EdgeInsets.only(bottom: 10),
              itemCount: _messages.length,
              itemBuilder: (context, index) {
                final message = _messages[index];
                return BubbleSpecialThree(
                  text: message['text'],
                  isSender: message['isSender'],
                  color: message['isSender']
                      ? const Color(0xFF1B97F3)
                      : const Color(0xFFE8E8EE),
                  tail: true,
                  textStyle: TextStyle(
                    color: message['isSender'] ? Colors.white : Colors.black,
                    fontSize: 16,
                  ),
                );
              },
            ),
          ),

          if (_isLoading)
             const Padding(
               padding: EdgeInsets.all(8.0),
               child: Align(
                 alignment: Alignment.centerLeft,
                 child: Text("  Shoex đang soạn tin...", style: TextStyle(color: Colors.grey, fontStyle: FontStyle.italic)),
               ),
             ),

          Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
            color: Colors.white,
            child: Row(
              children: [
                Expanded(
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 15),
                    decoration: BoxDecoration(
                      color: Colors.grey[200],
                      borderRadius: BorderRadius.circular(30),
                    ),
                    child: TextField(
                      controller: _textController,
                      textCapitalization: TextCapitalization.sentences,
                      onChanged: (value) {
                        _isTypingNotifier.value = value.trim().isNotEmpty;
                      },
                      decoration: const InputDecoration(
                        hintText: 'Nhập tin nhắn...',
                        border: InputBorder.none,
                      ),
                      onSubmitted: (_) => _sendMessage(),
                    ),
                  ),
                ),
                
                const SizedBox(width: 8),
                
                ValueListenableBuilder<bool>(
                  valueListenable: _isTypingNotifier,
                  builder: (context, isTyping, child) {
                    return CircleAvatar(
                      backgroundColor: (isTyping && !_isLoading) 
                          ? const Color(0xFF1B97F3) 
                          : Colors.grey,
                      child: IconButton(
                        icon: const Icon(Icons.send, color: Colors.white, size: 20),
                        onPressed: (isTyping && !_isLoading) ? _sendMessage : null,
                      ),
                    );
                  },
                ),
              ],
            ),
          ),
          const SizedBox(height: 10),
        ],
      ),
    );
  }
}