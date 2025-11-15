import 'package:flutter/material.dart';

class ShadowStyle {
  static final verticalProductShadow = BoxShadow(
    color: Colors.grey,
    blurRadius: 50,
    spreadRadius: 7,
    offset: const Offset(0, 2)

  );
  static final horizontalProductShadow = BoxShadow(
    color: Colors.grey.withAlpha(25),
    blurRadius: 50,
    spreadRadius: 7,
    offset: const Offset(0, 2)

  );
}