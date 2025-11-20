import 'package:flutter/material.dart';
import 'package:flutter_app/screens/login/login_screen.dart';
import 'package:flutter_app/components/rounded_input.dart'; 
import 'package:flutter_app/components/rounded_password.dart'; 
import 'package:flutter_app/components/alreadyhaveaccountcheck.dart'; 
import 'package:flutter_app/screens/login/components/background.dart';
import 'package:flutter_svg/svg.dart';
import 'package:flutter_app/components/button.dart'; 
// Kiểm tra lại đường dẫn import AuthService cho đúng với dự án của bạn
import 'package:flutter_app/shop/services/auth_service.dart'; 

class SignUpScreen extends StatelessWidget {
  const SignUpScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: const Body(),
    );
  }
}

class Body extends StatefulWidget {
  const Body({
    super.key,
  });

  @override
  _BodyState createState() => _BodyState();
}

class _BodyState extends State<Body> {
  // Khởi tạo Controllers
  final _usernameController = TextEditingController();
  final _emailController = TextEditingController();
  final _fullNameController = TextEditingController();
  final _phoneController = TextEditingController();
  final _passwordController = TextEditingController();
  final _password2Controller = TextEditingController();

  final _authService = AuthService();
  bool _isLoading = false;

  // Hàm xử lý logic đăng ký
  Future<void> _register() async {
    
    // ✅ 1. KIỂM TRA NHẬP THIẾU TRƯỜNG (VALIDATION)
    if (_usernameController.text.isEmpty ||
        _emailController.text.isEmpty ||
        _fullNameController.text.isEmpty ||
        _phoneController.text.isEmpty ||
        _passwordController.text.isEmpty ||
        _password2Controller.text.isEmpty) {
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Vui lòng nhập đầy đủ tất cả thông tin!'),
            backgroundColor: Colors.orange,
          ),
        );
      }
      return; // Dừng lại, không gọi API
    }

    // ✅ 2. KIỂM TRA MẬT KHẨU KHỚP
    if (_passwordController.text != _password2Controller.text) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Mật khẩu xác nhận không khớp!'),
            backgroundColor: Colors.redAccent,
          ),
        );
      }
      return;
    }

    // Bắt đầu gọi API
    setState(() => _isLoading = true);

    try {
      final result = await _authService.register(
        username: _usernameController.text,
        email: _emailController.text,
        fullName: _fullNameController.text,
        phone: _phoneController.text,
        password: _passwordController.text,
        password2: _password2Controller.text,
      );

      setState(() => _isLoading = false);

      if (result['success']) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Đăng ký thành công! Vui lòng đăng nhập.'),
              backgroundColor: Colors.green,
            ),
          );
          // Chuyển qua trang đăng nhập
          Navigator.pushReplacement(
            context,
            MaterialPageRoute(builder: (context) => const LoginScreen()),
          );
        }
      } else {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Lỗi: ${result['message']}'),
              backgroundColor: Colors.red,
            ),
          );
        }
      }
    } catch (e) {
      setState(() => _isLoading = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Lỗi đăng ký: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  @override
  void dispose() {
    _usernameController.dispose();
    _emailController.dispose();
    _fullNameController.dispose();
    _phoneController.dispose();
    _passwordController.dispose();
    _password2Controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    Size size = MediaQuery.of(context).size;
    return Background(
      child: SingleChildScrollView(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            SvgPicture.asset(
              "assets/logo/logo.svg",
              height: 100,
            ),
            const Text(
              "SIGN UP",
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 48),
            ),
            const Text(
              "Create an account",
              style: TextStyle(fontSize: 19),
            ),
            const SizedBox(height: 20),

            RoundedInputField(
              controller: _usernameController,
              hintText: "Username",
              onChanged: (value) {},
              icon: Icons.person_outline,
            ),
            RoundedInputField(
              controller: _emailController,
              hintText: "Your Email",
              onChanged: (value) {},
              icon: Icons.email,
            ),
            RoundedInputField(
              controller: _fullNameController,
              hintText: "Full Name",
              onChanged: (value) {},
              icon: Icons.badge,
            ),
            RoundedInputField(
              controller: _phoneController,
              hintText: "Your Phone Number",
              onChanged: (value) {},
              icon: Icons.phone,
            ),
            RoundedPasswordField(
              controller: _passwordController,
              onChanged: (value) {},
              hintText: "Password",
              icon: Icons.lock,
            ),
            RoundedPasswordField(
              controller: _password2Controller,
              onChanged: (value) {},
              hintText: "Confirm Password",
              icon: Icons.lock_outline,
            ),
            
            const SizedBox(height: 20), // Thêm khoảng cách
            
            _isLoading
                ? const CircularProgressIndicator()
                : StartButton(
                    text: "SIGN UP",
                    press: _register, 
                    bsize: Size(size.width * 0.78, 61),
                  ),
            SizedBox(height: size.height * 0.03),
            AlreadyHaveAccountCheck(
              press: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (context) {
                    return const LoginScreen();
                  }),
                );
              },
              login: false,
            )
          ],
        ),
      ),
    );
  }
}