import 'package:flutter/material.dart';
import 'package:flutter_app/screens/welcome/components/body.dart';
class WelcomeScreen extends StatelessWidget {
  const WelcomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Body(),
    );
  }
}