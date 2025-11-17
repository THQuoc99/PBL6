import 'package:flutter/material.dart';
import 'package:flutter_app/constants/colors.dart';
import 'package:flutter_rating_bar/flutter_rating_bar.dart';
import 'package:iconsax_flutter/iconsax_flutter.dart';

class CusRatingBarIndicator extends StatelessWidget {
  final double rating;

  const CusRatingBarIndicator({
    super.key,
    required this.rating,
  });

  @override
  Widget build(BuildContext context) {
    return RatingBarIndicator(
        rating: rating,
        itemSize: 20,
        unratedColor: Colors.grey,
        itemBuilder: (_, __) => const Icon(Iconsax.star_1, color: AppColors.primary,),
    
    );
  }
}
