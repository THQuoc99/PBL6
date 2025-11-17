import 'package:flutter/material.dart';
import 'package:carousel_slider/carousel_slider.dart';
import 'package:flutter_app/screens/home/components/circular_container.dart';
import 'package:flutter_app/shop/controllers/home_controller.dart';
import 'package:flutter_app/widgets/image/rounded_image.dart';
import 'package:flutter_app/constants/sizes.dart';
import 'package:get/get.dart';

class PromoSlider extends StatelessWidget {
  final List<String> banners;

  const PromoSlider({
    super.key,
    required this.banners
  });

  @override
  Widget build(BuildContext context) {
    final controller = Get.put(HomeController());
    return Column(
      children: [
        CarouselSlider(
          options: CarouselOptions(
            viewportFraction: 1,
            onPageChanged: (index, _) => controller.updatePageIndicator(index)
          ),
          items: banners.map((url) => RoundedImage(imageUrl: url)).toList(),
        ),
        const SizedBox(height: AppSizes.xs),
        Center(
          child: Obx(
            () => Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                for(int i = 0;i<banners.length;i++)
                CircularContainer(
                  height: 4,
                  width: 20,
                  color: controller.carousalCurrentIndex.value == i ? Colors.blueAccent : Colors.grey,
                  margin: const EdgeInsets.only(right: 10)
                )
                
              ],
            ),
          ),
        )
      ]
    );
  }
}
