import 'package:flutter/material.dart';
import 'package:flutter_app/constants/sizes.dart';
import 'package:flutter_app/screens/home/home_screen.dart';
import 'package:flutter_app/widgets/appbar/appbar.dart';
import 'package:flutter_app/widgets/icons/circular_icon.dart';
import 'package:flutter_app/widgets/layouts/grid_layout.dart';
import 'package:flutter_app/widgets/products/product_cards/product_card_vertical.dart';
import 'package:get/get.dart';

class FavoriteScreen extends StatelessWidget
{
  const FavoriteScreen(
    {
      super.key,
    }
  );

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: CusAppbar(
        title: Text('Favorite Product', style: Theme.of(context).textTheme.headlineMedium ),
        actions: [
          CircularIcon(
            icon: Icons.add, 
            onpress: ()=> Get.to(const HomeScreen()),
          )
        ],
        
      ),
      body: SingleChildScrollView(
        child: Padding(
          padding: EdgeInsets.all(AppSizes.defaultSpace),
          child: Column(
            children: [
              GridLayout(itemCount: 7, itemBuilder: (_,index)=>ProductCardVertical())
            ],
          ),
        ),
      ),
    );
  }
}