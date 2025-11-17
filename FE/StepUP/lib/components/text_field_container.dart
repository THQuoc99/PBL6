import 'package:flutter/material.dart';

class TextFieldContainer extends StatelessWidget {
  final Widget? child;
  const TextFieldContainer({
    super.key,
    this.child,
  });

  @override
  Widget build(BuildContext context) {
    Size size = MediaQuery.of(context).size;
    return Container(
      padding: EdgeInsets.symmetric(horizontal: 20, vertical: 10),
      margin: EdgeInsets.symmetric(vertical: 10),
      width: size.width * 0.8,
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(29),
        boxShadow: [
          BoxShadow(
            offset: Offset(0, 10),
            blurRadius: 50,
            color: Color(0xffEEEEEE),
          ),
        ],
      ),
      child: child,
    );
  }
}
