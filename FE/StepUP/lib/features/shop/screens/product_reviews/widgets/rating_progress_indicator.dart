import 'package:flutter/material.dart';
import 'product_indicator_and_rating.dart';

class OverallProductRating extends StatelessWidget {
  final double average;
  final Map<int, double> distribution; // key: rating (1..5), value: ratio 0..1
  final int total;

  const OverallProductRating({
    super.key,
    required this.average,
    required this.distribution,
    required this.total,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Expanded(
          flex: 3,
          child: Text(average.toStringAsFixed(1), style: Theme.of(context).textTheme.displayLarge),
        ),
        Expanded(
          flex: 7,
          child: Column(
            children: [
              RatingProgressIndicator(text: '5', value: distribution[5] ?? 0),
              RatingProgressIndicator(text: '4', value: distribution[4] ?? 0),
              RatingProgressIndicator(text: '3', value: distribution[3] ?? 0),
              RatingProgressIndicator(text: '2', value: distribution[2] ?? 0),
              RatingProgressIndicator(text: '1', value: distribution[1] ?? 0),
              const SizedBox(height: 8),
              Text('$total Ratings', style: Theme.of(context).textTheme.bodySmall),
            ],
          ),
        )
      ],
    );
  }
}