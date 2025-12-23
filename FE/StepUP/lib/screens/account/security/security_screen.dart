import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'change_password_screen.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';

class SecurityScreen extends StatefulWidget {
  const SecurityScreen({super.key});

  @override
  State<SecurityScreen> createState() => _SecurityScreenState();
}

class _SecurityScreenState extends State<SecurityScreen> {
  bool _twoFaEnabled = false;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Bảo mật')),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            const SizedBox(height: 12),
            ListTile(
              leading: const Icon(Icons.lock_outline),
              title: const Text('Đổi mật khẩu'),
              onTap: () {
                Navigator.of(context).push(MaterialPageRoute(builder: (_) => const ChangePasswordScreen()));
              },
            ),
          ],
        ),
      ),
    );
  }

  void _showChangePasswordDialog(BuildContext context) {
    final _currentCtrl = TextEditingController();
    final _newCtrl = TextEditingController();
    final _confirmCtrl = TextEditingController();
    final _formKey = GlobalKey<FormState>();

    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Đổi mật khẩu'),
        content: Form(
          key: _formKey,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextFormField(
                controller: _currentCtrl,
                obscureText: true,
                decoration: const InputDecoration(labelText: 'Mật khẩu hiện tại'),
                validator: (v) => (v == null || v.isEmpty) ? 'Vui lòng nhập mật khẩu hiện tại' : null,
              ),
              TextFormField(
                controller: _newCtrl,
                obscureText: true,
                decoration: const InputDecoration(labelText: 'Mật khẩu mới'),
                validator: (v) => (v == null || v.length < 6) ? 'Mật khẩu phải >= 6 ký tự' : null,
              ),
              TextFormField(
                controller: _confirmCtrl,
                obscureText: true,
                decoration: const InputDecoration(labelText: 'Xác nhận mật khẩu mới'),
                validator: (v) => (v != _newCtrl.text) ? 'Mật khẩu không khớp' : null,
              ),
            ],
          ),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.of(context).pop(), child: const Text('Hủy')),
          ElevatedButton(
            onPressed: () async {
              if (!_formKey.currentState!.validate()) return;
              Navigator.of(context).pop();
              // Gọi API đổi mật khẩu
              try {
                final prefs = await SharedPreferences.getInstance();
                final token = prefs.getString('token');
                final url = Uri.parse('http://10.0.2.2:8000/api/users/change_password/');
                final resp = await http.post(
                  url,
                  headers: token != null
                      ? {
                          'Content-Type': 'application/json',
                          'Authorization': 'Bearer $token',
                        }
                      : {'Content-Type': 'application/json'},
                  body: json.encode({
                    'current_password': _currentCtrl.text,
                    'new_password': _newCtrl.text,
                  }),
                );

                if (resp.statusCode == 200 || resp.statusCode == 204) {
                  Get.snackbar('Thành công', 'Đổi mật khẩu thành công');
                } else {
                  String msg = 'Lỗi khi đổi mật khẩu';
                  try {
                    final j = json.decode(resp.body);
                    msg = j['error'] ?? j['detail'] ?? msg;
                  } catch (e) {}
                  Get.snackbar('Lỗi', msg);
                }
              } catch (e) {
                Get.snackbar('Lỗi', 'Không thể kết nối đến máy chủ');
              }
            },
            child: const Text('Xác nhận'),
          ),
        ],
      ),
    );
  }
}
