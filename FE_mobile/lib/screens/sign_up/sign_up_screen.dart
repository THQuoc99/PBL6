import 'package:flutter/material.dart';
import 'package:flutter_app/screens/login/login_screen.dart';
import 'package:flutter_app/components/rounded_iput.dart';
import 'package:flutter_app/components/rounded_password.dart';
import 'package:flutter_app/components/alreadyhaveaccountcheck.dart';
import 'package:flutter_app/screens/login/components/background.dart';
import 'package:flutter_svg/svg.dart';
import 'package:flutter_app/components/button.dart';


class SignUpScreen extends StatelessWidget {
  const SignUpScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(    
      body: Body(),
    );
  }
}

class Body extends StatelessWidget {
  const Body({
    super.key,
    
  });

  @override
  Widget build(BuildContext context) {
    Size size = MediaQuery.of(context).size;
    return Background(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,        
        children: <Widget>[
          SvgPicture.asset(
            "assets/logo/logo.svg",
            height: 150,
          ),
          Text(
            "SIGN UP",
            style: TextStyle(fontWeight: FontWeight.bold, fontSize: 52,),
          ),
          
          Text(
            "Create an account",
            style: TextStyle( fontSize: 19),
          ),
          SizedBox(height: 20),
          RoundedInputField(
            hintText: "Your Email",
            onChanged: (value) {},
            icon: Icons.person,
          ),
          RoundedPasswordField(
            onChanged: (value) {},
            hintText: "Password",
            icon: Icons.lock,
          ),
          RoundedInputField(
            hintText: "Your Phone Number",
            onChanged: (value) {},
            icon: Icons.phone,
          ),
          StartButton(
            text: "SIGN UP",
            press: () {},
            bsize: Size(size.width * 0.78, 61),
          ),
          SizedBox(height: size.height * 0.03),
          AlreadyHaveAccountCheck(
            press: () {
              Navigator.push(
                context, MaterialPageRoute(builder: (context) {
                  return LoginScreen();
                }
                )
              );
            },
            login: false,
          )
        ],
      ),
    );
  }
}