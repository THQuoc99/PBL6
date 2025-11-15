import 'package:flutter/material.dart';
import 'package:flutter_app/constants/colors.dart';
import 'package:flutter_app/constants/image_string.dart';
import 'package:flutter_app/constants/sizes.dart';
import 'package:flutter_app/screens/home/components/curved_edges_widget.dart';
import 'package:flutter_app/widgets/appbar/appbar.dart';
import 'package:flutter_app/widgets/icons/circular_icon.dart';
import 'package:flutter_app/widgets/image/rounded_image.dart';
import 'package:iconsax_flutter/iconsax_flutter.dart';

class ProductSlider extends StatelessWidget {
  const ProductSlider({
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    return CurvedEdgeWidget(
      child: Container(
        color: AppColors.secondary,
        child: Stack(
          children: [
            SizedBox(
              height: 400,
              child: Padding(
                padding: const EdgeInsets.all(AppSizes.productImageRadius * 2),
                child: Center(child: Image(image: AssetImage(AppImages.sabrina))),
              )
            ),
    
            Positioned(
              right: 0,
              bottom: 30,
              left: AppSizes.defaultSpace,
              child: SizedBox(
                height: 80,
                child: ListView.separated(
                  itemBuilder: (_, index) => RoundedImage(
                    width: 80,
                    bgcolor: Colors.white,
                    border: Border.all(color: Colors.blueAccent),
                    padding: const EdgeInsets.all(AppSizes.sm),
                    imageUrl: AppImages.sabrina1,
                  ),
                  separatorBuilder: (_,__) => const SizedBox(width: AppSizes.spaceBtwItems,),
                  itemCount: 6,
                  shrinkWrap: true,
                  physics: AlwaysScrollableScrollPhysics(),
                  scrollDirection: Axis.horizontal,
                ),
              ),
            ),
    
            CusAppbar(
              showBackArrow: true,
              actions: [
                CircularIcon(icon: Iconsax.heart, color: Colors.blueAccent,)
              ],
            )
            
          ],
        ),
      ),
    );
  }
}