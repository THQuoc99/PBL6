import 'package:flutter/material.dart' ;
import 'package:flutter_app/screens/login/login_screen.dart';
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
                  Text(
                    "StepUP",
                    style: TextStyle(fontWeight: FontWeight.bold, fontSize: 22,
                    color: Color.fromARGB(255, 48, 196, 230)
                    ),
                  ),
                  SizedBox(height: size.height * 0.02),
                  Text(
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
              StartButton(
                text: "Let's get started",
                press: () {},
                bsize: Size(335, 61),
              ),
              StartButton(
                text: "I have an account",
                color: Colors.white,
                textColor: Colors.black,
                press: () {Navigator.push(context, MaterialPageRoute(builder: (context) {
                        return LoginScreen();
                      }
                    )
                  );
                },
              ),
              SizedBox(height: 40), // cách mép dưới
            ],
          ),
        ],
      ),
    );
  }
}
