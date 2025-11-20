import 'package:flutter/material.dart';
import 'package:flutter_app/screens/login/login_screen.dart';
import 'package:flutter_app/screens/sign_up/sign_up_screen.dart';
import 'package:flutter_app/screens/welcome/components/background.dart';
import 'package:flutter_svg/svg.dart';
import 'package:flutter_app/components/button.dart';

class Body extends StatelessWidget {
  const Body({super.key});

  @override
  Widget build(BuildContext context) {
    Size size = MediaQuery.of(context).size;
    return Background(
      child: Column(
        children: <Widget>[
          // Logo + Text ở giữa
          Expanded(
            child: Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  SvgPicture.asset(
                    "assets/logo/logo.svg",
                    height: size.height * 0.2,
                  ),
                  const Text(
                    "StepUP",
                    style: TextStyle(
                      fontWeight: FontWeight.bold, 
                      fontSize: 22,
                      color: Color.fromARGB(255, 48, 196, 230)
                    ),
                  ),
                  SizedBox(height: size.height * 0.02),
                  const Text(
                    "Welcome",
                    style: TextStyle(fontWeight: FontWeight.bold, fontSize: 22),
                  ),
                ],
              ),
            ),
          ),

          // Button ở dưới cùng
          Column(
            children: [
              // Nút 1: Let's get started -> Chuyển sang ĐĂNG KÝ (SignUpScreen)
              StartButton(
                text: "Let's get started",
                press: () {
                  Navigator.push(
                    context, 
                    MaterialPageRoute(builder: (context) => const SignUpScreen())
                  );
                },
                bsize: const Size(335, 61),
              ),
              
              // Nút 2: I have an account -> Chuyển sang ĐĂNG NHẬP (LoginScreen)
              StartButton(
                text: "I have an account",
                color: Colors.white,
                textColor: Colors.black,
                press: () {
                  Navigator.push(
                    context, 
                    MaterialPageRoute(builder: (context) => const LoginScreen())
                  );
                },
              ),
              const SizedBox(height: 40), // cách mép dưới
            ],
          ),
        ],
      ),
    );
  }
}