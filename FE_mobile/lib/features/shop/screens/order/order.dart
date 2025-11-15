import 'package:flutter/material.dart';
import 'package:flutter_app/constants/sizes.dart';
import 'package:flutter_app/features/shop/screens/order/widgets/order_list.dart';
import 'package:flutter_app/widgets/appbar/appbar.dart';

class OrderScreen extends StatelessWidget{
  const OrderScreen({
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: CusAppbar(showBackArrow: false, title: Text('My Order'), ),
      body: const Padding(
        padding: EdgeInsets.all(AppSizes.defaultSpace),

        // order
        child: OrderListItem(),
      ),
    );
  }
}