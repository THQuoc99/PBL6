import 'package:flutter/material.dart';
import 'package:flutter_app/features/shop/screens/sub_category/sub_categories.dart';
import 'package:get/get.dart';
import 'package:get/route_manager.dart';
import 'virtical_image_text.dart';

class HomeCategory extends StatelessWidget {
  const HomeCategory({
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 100,
      child: ListView.builder(
        shrinkWrap: true,
        itemCount: 6,
        scrollDirection: Axis.horizontal,
        itemBuilder: (_, index) {
          return VirticalImageText(bgcolor: Colors.white, ontap: () => Get.to(()=> const SubCategoriesScreen()),);
        }
      ),
    );
  }
}