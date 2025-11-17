import 'package:flutter/material.dart';

class Background extends StatelessWidget {
  final Widget child;
  const Background({
    super.key,  
    required this.child,
  });


  @override
  Widget build(BuildContext context) {
    Size size = MediaQuery.of(context).size;
    return SizedBox(
      height: size.height,
      width: double.infinity,
      child: Stack(
        alignment: Alignment.center,
        children: <Widget>[
          Positioned(
            top: -size.height * 0.15,
            child: Image.asset("assets/images/Bubbles.png",
                                width: size.width * 2.0,
            ),
          ),
          child,
        ],
      ),
    );
  }
}