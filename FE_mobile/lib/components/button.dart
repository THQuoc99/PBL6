import 'package:flutter/material.dart';
import 'package:flutter_app/constants.dart'; 

class StartButton extends StatelessWidget {
  final String text;
  final VoidCallback? press;
  final Color color, textColor;
  final Size bsize;
  const StartButton({
    super.key,
    required this.text,
    this.press,
    this.color = kPrimaryColor,
    this.textColor = Colors.white,
    this.bsize = const Size(335, 61),
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: EdgeInsets.symmetric(vertical: 10),
      child: SizedBox(
        width: bsize.width,
        height: bsize.height,
        child: ClipRRect(
          child: TextButton(
            onPressed: press,
            style: TextButton.styleFrom(
              padding: EdgeInsets.symmetric(vertical: 15, horizontal: 40),
              backgroundColor: color,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(10),
              ),
            ),
            child: Text(
              text,
              style: TextStyle(color: textColor),
            ),
          ),
        ),
      ),
    );
  }
}