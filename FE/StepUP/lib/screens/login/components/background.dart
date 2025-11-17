import 'package:flutter/material.dart';

class Background extends StatelessWidget {
  final Widget? child;
  const Background({
    super.key,   
    @required this.child,
  });

  @override
  Widget build(BuildContext context) {
    Size size = MediaQuery.of(context).size;
    return SizedBox(
      width: double.infinity,
      height: size.height,
      child: Stack(
        alignment: Alignment.center,
        children: <Widget>[
          Positioned(
            top: 0,
            left: 0,
            child: Image.asset("assets/images/log_top2.png"),
          ),
          Positioned(
            top: 0,
            left: 0,
            child: Image.asset("assets/images/log_top1.png"),
          ),
          Positioned(
            top: size.height * 0.3,
            right: 0,
            child: Image.asset("assets/images/log_middle.png"),
          ),
          Positioned(
            bottom: 0,
            right: 0,
            child: Image.asset("assets/images/log_bot.png"),
          ),
          child!,
        ],
      ),
    );
  }
}