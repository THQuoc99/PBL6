import 'package:flutter/material.dart';
import 'package:flutter_app/components/button.dart';
import 'package:flutter_svg/svg.dart';
import 'background.dart';
import 'package:flutter_app/components/rounded_input.dart';
import 'package:flutter_app/components/rounded_password.dart';
import 'package:flutter_app/components/alreadyhaveaccountcheck.dart';
import 'package:flutter_app/screens/sign_up/sign_up_screen.dart';
import 'package:flutter_app/constants/colors.dart';

class Body extends StatelessWidget {
  final TextEditingController usernameController;
  final TextEditingController passwordController;
  final bool isLoading;
  final VoidCallback onLogin;

  const Body({
    super.key,
    required this.usernameController,
    required this.passwordController,
    required this.isLoading,
    required this.onLogin,
  });

  @override
  Widget build(BuildContext context) {
    Size size = MediaQuery.of(context).size;
    return Background(
      child: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 20),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: <Widget>[
              const SizedBox(height: 50),
              SvgPicture.asset(
                "assets/logo/logo.svg",
                height: 150,
              ),
              const SizedBox(height: 20),
              Text(
                "LOGIN",
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 52,
                  color: AppColors.primary,
                ),
              ),
              const SizedBox(height: 10),
              Text(
                "Welcome Back",
                style: TextStyle(
                  fontSize: 19,
                  color: Colors.grey[700],
                ),
              ),
              const SizedBox(height: 30),
              RoundedInputField(
                controller: usernameController,
                hintText: "Username",
                onChanged: (value) {},
                icon: Icons.person,
              ),
              const SizedBox(height: 10),
              RoundedPasswordField(
                controller: passwordController,
                onChanged: (value) {},
                hintText: "Password",
                icon: Icons.lock,
              ),
              const SizedBox(height: 20),
              if (isLoading)
                CircularProgressIndicator(
                  valueColor: AlwaysStoppedAnimation<Color>(AppColors.primary),
                )
              else
                StartButton(
                  text: "LOGIN",
                  press: onLogin,
                  bsize: Size(size.width * 0.8, 55),
                ),
              const SizedBox(height: 20),
              AlreadyHaveAccountCheck(
                login: true,
                press: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (context) => const SignUpScreen(),
                    ),
                  );
                },
              ),
              const SizedBox(height: 20),
            ],
          ),
        ),
      ),
    );
  }
}








