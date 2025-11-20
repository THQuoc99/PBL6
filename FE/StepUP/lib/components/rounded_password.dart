import 'package:flutter/material.dart';
import 'text_field_container.dart';
import '../constants/colors.dart';

// 1. Chuyển thành StatefulWidget
class RoundedPasswordField extends StatefulWidget {
  final ValueChanged<String> onChanged;
  final TextEditingController controller;
  final String hintText;
  final IconData icon;

  const RoundedPasswordField({
    Key? key,
    required this.onChanged,
    required this.controller,
    this.hintText = "Password",
    this.icon = Icons.lock,
  }) : super(key: key);

  @override
  // 2. Tạo State
  _RoundedPasswordFieldState createState() => _RoundedPasswordFieldState();
}

// 3. Tạo class State
class _RoundedPasswordFieldState extends State<RoundedPasswordField> {
  // 4. Thêm biến để quản lý trạng thái ẩn/hiện
  bool _isObscure = true;

  @override
  Widget build(BuildContext context) {
    return TextFieldContainer(
      child: TextField(
        controller: widget.controller, // 5. Dùng "widget." để truy cập
        obscureText: _isObscure, // 6. Dùng biến state
        onChanged: widget.onChanged, // 5. Dùng "widget."
        decoration: InputDecoration(
          hintText: widget.hintText,
          icon: Icon(
            widget.icon,
            color: AppColors.primary,
          ),
          suffixIcon: IconButton(
            icon: Icon(
              _isObscure ? Icons.visibility_off : Icons.visibility,
              color: AppColors.primary,
            ),
            onPressed: () {
              setState(() {
                _isObscure = !_isObscure;
              });
            },
          ),
          border: InputBorder.none,
        ),
      ),
    );
  }
}