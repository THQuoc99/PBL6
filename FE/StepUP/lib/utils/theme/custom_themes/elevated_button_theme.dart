import 'package:flutter/material.dart';

class AppElevatedButtonTheme {
  AppElevatedButtonTheme._();

  static final ElevatedButtonThemeData lightElevatedButtonTheme =
      ElevatedButtonThemeData(
    style: ElevatedButton.styleFrom(
      backgroundColor: Colors.blue,
      foregroundColor: Colors.white,
      disabledBackgroundColor: Colors.grey,
      disabledForegroundColor: Colors.white70,
      textStyle: const TextStyle(
        fontSize: 16.0,
        fontWeight: FontWeight.bold,
      ),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(8.0),
      ),
      padding: const EdgeInsets.symmetric(
        vertical: 12.0,
        horizontal: 24.0,
      ),
    ),
  );

  static final ElevatedButtonThemeData darkElevatedButtonTheme =
      ElevatedButtonThemeData(
    style: ElevatedButton.styleFrom(
      backgroundColor: Colors.blueAccent,
      foregroundColor: Colors.black,
      disabledBackgroundColor: Colors.grey,
      disabledForegroundColor: Colors.black54,
      textStyle: const TextStyle(
        fontSize: 16.0,
        fontWeight: FontWeight.bold,
      ),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(8.0),
      ),
      padding: const EdgeInsets.symmetric(
        vertical: 12.0,
        horizontal: 24.0,
      ),
    ),
  );
}
