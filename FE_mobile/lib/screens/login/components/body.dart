import 'package:flutter/material.dart';
import 'package:flutter_app/components/button.dart';
import 'package:flutter_svg/svg.dart';
import 'background.dart';
import 'package:flutter_app/components/rounded_iput.dart';
import 'package:flutter_app/components/rounded_password.dart';
import 'package:flutter_app/components/alreadyhaveaccountcheck.dart';
import 'package:flutter_app/screens/sign_up/sign_up_screen.dart';
import 'package:flutter_app/navigation_menu.dart';
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
            "LOGIN",
            style: TextStyle(fontWeight: FontWeight.bold, fontSize: 52,),
          ),
          
          Text(
            "Welcome Back",
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
          StartButton(
            text: "LOGIN",
            press: () {
              Navigator.push(
                context, MaterialPageRoute(builder: (context) {
                  return NavigationMenu();
                }
                )
              );
            },
            bsize: Size(size.width * 0.78, 61),
          ),
          SizedBox(height: size.height * 0.03),
          AlreadyHaveAccountCheck(
            press: () {
              Navigator.push(
                context, MaterialPageRoute(builder: (context) {
                  return SignUpScreen();
                }
                )
              );
            },
            login: true,
          )
        ],
      ),
    );
  }
}








