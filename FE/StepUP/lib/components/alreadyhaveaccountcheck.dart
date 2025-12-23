import 'package:flutter/material.dart';

class AlreadyHaveAccountCheck extends StatelessWidget {
  final bool login;
  final VoidCallback? press;
  const AlreadyHaveAccountCheck({
    super.key,
    this.login = true,
    this.press,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: <Widget>[
        Text(
          login ? "Bạn chưa có tài khoản?" : "Bạn đã có tài khoản?",
          style: TextStyle(fontSize: 16, color: Color.fromARGB(255, 48, 196, 230)),
        ),
        GestureDetector(
          onTap: press,
          child: Text(
            login ? "Đăng ký" : " Đăng nhập",
            style: TextStyle(
              fontSize: 16,
              color: Color.fromARGB(255, 48, 196, 230),
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
      ],
    );
  }
}