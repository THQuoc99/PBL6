import 'package:flutter/widgets.dart';

class AppDeviceUtility {
  static double getScreenWidth(BuildContext context){
    return MediaQuery.of(context).size.width;
  }
}
