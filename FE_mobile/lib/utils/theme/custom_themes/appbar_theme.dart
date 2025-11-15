import 'package:flutter/material.dart';

class MyAppbarTheme {
  MyAppbarTheme._();

  static AppBarTheme lightAppbarTheme = AppBarTheme(
    backgroundColor: Colors.white,
    iconTheme: IconThemeData(color: Colors.black),
    titleTextStyle: TextStyle(
      color: Colors.black,
      fontSize: 20.0,
      fontWeight: FontWeight.bold,
    ),
    elevation: 0,
  );

  static AppBarTheme darkAppbarTheme = AppBarTheme(
    backgroundColor: Colors.black,
    iconTheme: IconThemeData(color: Colors.white),
    titleTextStyle: TextStyle(
      color: Colors.white,
      fontSize: 20.0,
      fontWeight: FontWeight.bold,
    ),
    elevation: 0,
  );
}