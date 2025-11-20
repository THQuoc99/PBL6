import 'package:flutter/material.dart';
import 'package:flutter_app/constants/sizes.dart';
import 'package:flutter_app/features/shop/screens/product_reviews/widgets/user_review_card.dart';
import 'package:flutter_app/widgets/appbar/appbar.dart';
import 'package:flutter_app/common/widgets/ratings/rating_indicator.dart';
import './widgets/rating_progress_indicator.dart';

class ProductReviewScreen extends StatelessWidget {
    const ProductReviewScreen({
        super.key,
    });

    @override
    Widget build(BuildContext context){
        return Scaffold(
            // AppBar
            appBar: CusAppbar(title: Text('Review and Rating'), showBackArrow: true,),

            // Body
            body: SingleChildScrollView(
                child: Padding(
                    padding: EdgeInsets.all(AppSizes.defaultSpace),
                    child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                            Text('Product Reviews will be shown here.'),
                            SizedBox(height: AppSizes.spaceBtwItems,),

                            //Overall Rating
                            OverallProductRating(),
                            CusRatingBarIndicator(rating: 4.5),
                            Text("120 Ratings and 30 Reviews", style: Theme.of(context).textTheme.bodySmall,),
                            const SizedBox(height: AppSizes.spaceBtwSections,),

                            // User review
                            UserReviewCard(),
                            UserReviewCard(),
                            UserReviewCard(),
                            UserReviewCard(),
                        ],
                    ),
                ),
            ),
        );
    }
}



