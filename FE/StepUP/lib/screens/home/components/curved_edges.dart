import 'package:flutter/material.dart';

class CustomCurvedEdges extends CustomClipper<Path> {
  @override
  Path getClip(Size size) {
    Path path = Path();
    path.lineTo(0, size.height);
    
    final afirstCurve = Offset(0, size.height - 20);
    final alastCirve = Offset(30, size.height - 20);
    path.quadraticBezierTo(
        afirstCurve.dx, afirstCurve.dy, alastCirve.dx, alastCirve.dy);

    final bfirstCurve = Offset(0, size.height - 20);
    final blastCirve = Offset(size.width - 30, size.height - 20);
    path.quadraticBezierTo(
        bfirstCurve.dx, bfirstCurve.dy, blastCirve.dx, blastCirve.dy);

    final cfirstCurve = Offset(size.width, size.height - 20);
    final clastCirve = Offset(size.width, size.height);
    path.quadraticBezierTo(
        cfirstCurve.dx, cfirstCurve.dy, clastCirve.dx, clastCirve.dy);

    path.lineTo(size.width, 0);
    path.close();
    return path;
  }

  @override
  bool shouldReclip(covariant CustomClipper<Path> oldClipper) {
    return true;
  }
}