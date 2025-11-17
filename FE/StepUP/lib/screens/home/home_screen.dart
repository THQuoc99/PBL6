import 'package:flutter/material.dart';
import 'package:flutter_app/constants/sizes.dart';
import 'package:flutter_app/features/shop/screens/all_products/all_products.dart';
import 'package:flutter_app/screens/home/components/primary_header_container.dart';
import 'package:flutter_app/screens/home/components/home_appbar.dart';
import 'package:flutter_app/screens/home/components/search_container.dart';
import 'package:flutter_app/screens/home/components/section_heading.dart';
import 'package:flutter_app/screens/home/components/home_category.dart';
import 'package:flutter_app/screens/home/components/promo_slider.dart';
import 'package:flutter_app/constants/image_string.dart';
import 'package:flutter_app/widgets/layouts/grid_layout.dart';
import 'package:flutter_app/widgets/products/product_cards/product_card_vertical.dart';
import 'package:get/get.dart';
//import 'package:flutter_app/widgets/appbar/appbar.dart';
class HomeScreen extends StatelessWidget {
  //final bool showBackArrow;
  const HomeScreen({
    super.key,
    //this.showBackArrow = false
    });

  @override
  Widget build(BuildContext context) {
    //Size size = MediaQuery.of(context).size;
    return Scaffold(
      body: SingleChildScrollView(
        child: Column(
          children: [
            PrimaryHeaderContainer(
              child: Column(
                children: [
                  //AppBarWidget(),
                  HomeAppBar(),
                  SizedBox(height: 24),

                  // Search Container
                  SearchContainer(hintText: "Search your favorite",),
                  SizedBox(height: 24),

                  // Categories
                  Padding(
                    padding: const EdgeInsets.only(left: 20),
                    child: Column(
                      children: [

                        // Heading
                        SectionHeading(title: "Popular Categories", showActionButton: false,),
                        SizedBox(height: 16),
                        // Categories List
                        HomeCategory(),                     
                      
                      ],
                    ),
                    )
                ],
              )
            ),
            // Body 
            Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  // Promo slider
                  const PromoSlider(banners: [AppImages.banner1,AppImages.banner2,AppImages.banner3],),
                  const SizedBox(height: 30),

                  SectionHeading(title: 'Popular Product', onButtonPressed: () => Get.to(()=> const AllProducts(),)),
                  //Popular product
                  GridLayout(itemCount: 4, itemBuilder: (_,index)=> const ProductCardVertical(),),
                  
                ],
              ),            
            ),
            SizedBox(height: AppSizes.spaceBtwSections,)
          ],
        ),
      )
    );
  }
}













