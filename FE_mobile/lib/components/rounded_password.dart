import 'package:flutter/material.dart';
import 'text_field_container.dart';
class RoundedPasswordField extends StatelessWidget {
  final String? hintText;
  final IconData? icon;
  final ValueChanged<String>? onChanged;
  const RoundedPasswordField({
    super.key,
    this.hintText,
    this.icon = Icons.lock,
    this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    return TextFieldContainer(
      child: TextField(
        onChanged: onChanged,
        obscureText: true,
        decoration: InputDecoration(
          hintText: "Password",
          icon: Icon(
            Icons.lock,
            color: Color.fromARGB(255, 48, 196, 230),
          ),
          suffixIcon: Icon(
            Icons.visibility,
            color: Color.fromARGB(255, 48, 196, 230),
          ),
          border: InputBorder.none,
          
        ),
      ),
    );
  }
}