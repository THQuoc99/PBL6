import 'package:flutter/material.dart';
import 'package:flutter_app/constants/image_string.dart';
import 'package:flutter_app/constants/sizes.dart';
import 'package:flutter_app/screens/home/components/section_heading.dart';
import 'package:flutter_app/widgets/appbar/appbar.dart';
import 'package:flutter_app/widgets/image/rounded_image.dart';
import 'package:flutter_app/widgets/products/product_cards/product_card_horizontal.dart';

class SubCategoriesScreen extends StatelessWidget{
  const SubCategoriesScreen({
    super.key
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: CusAppbar(title: Text('Sport'), showBackArrow: true,),
      body: SingleChildScrollView(
        child: Padding(
          padding: EdgeInsets.all(AppSizes.defaultSpace),
          child: Column(
            children: [
              //banner
              RoundedImage(width: double.infinity, imageUrl: AppImages.footballbanner1,applyImageRadius: true,),
              SizedBox(height: AppSizes.spaceBtwSections,),
              //sub categoies
              Column(
                children: [
                  SectionHeading(title: 'Football shoes', onButtonPressed: (){},),
                  const SizedBox(height: AppSizes.spaceBtwItems/2,),

                  SizedBox(
                    height: 120,
                    child: ListView.separated(
                      itemBuilder: (context, index) => const ProductCardHorizontal(),
                      separatorBuilder: (context, index) => const SizedBox(width: AppSizes.spaceBtwItems,),
                      itemCount: 4,
                      scrollDirection: Axis.horizontal,
                    ),
                  )
                ],
              )
            ],
          ),
        ),
      ),
    );
  }
}