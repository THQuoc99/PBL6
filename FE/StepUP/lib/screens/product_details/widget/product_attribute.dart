import 'package:flutter/material.dart';
import 'package:flutter_app/constants/sizes.dart';
import 'package:flutter_app/screens/home/components/section_heading.dart';
import 'package:flutter_app/screens/product_details/widget/choice_chip.dart'; // Đảm bảo bạn đã import đúng
import 'package:flutter_app/widgets/containers/rounded_container.dart';
import 'package:flutter_app/widgets/texts/product_price_text.dart';
import 'package:flutter_app/widgets/texts/product_title_text.dart';

class ProductAttribute extends StatelessWidget {
  const ProductAttribute({
    super.key
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start, // Thêm dòng này để căn trái cho toàn bộ
      children: [
        // --- PHẦN CẦN SỬA ---
        RoundedContainer(
          padding: const EdgeInsets.all(AppSizes.md),
          bgcolor: const Color.fromARGB(255, 218, 214, 214),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start, // Căn lề trái cho nội dung bên trong
            children: [
              // Title, price and stock status 
              const SectionHeading(title: 'Variation', showActionButton: false),
              const SizedBox(height: AppSizes.spaceBtwItems / 2),
              
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween, // Để giá và tồn kho tách ra
                children: [
                  // Cụm giá
                  Row(
                    children: [
                      const ProductTitleText(title: 'Price : ', smallSize: true),
                      Text(
                        '\$200',
                        style: Theme.of(context).textTheme.titleSmall!.apply(decoration: TextDecoration.lineThrough),
                      ),
                      const SizedBox(width: AppSizes.spaceBtwItems),
                      const ProductPriceText(price: '100'),
                    ],
                  ),
                  // Cụm tồn kho
                  Row(
                    children: [
                      const ProductTitleText(title: 'Stock : ', smallSize: true),
                      Text('In Stock', style: Theme.of(context).textTheme.titleMedium),
                    ],
                  )
                ],
              ),
              const SizedBox(height: AppSizes.spaceBtwItems / 2),

              // Descriptions
              const ProductTitleText(
                title: 'Up coming for new color',
                maxLines: 4,
                smallSize: true,
              )
            ],
          ),
        ),
        const SizedBox(height: AppSizes.spaceBtwItems),

        // Attribute
        // Color
        Column(
          crossAxisAlignment: CrossAxisAlignment.start, 
          children: [
            const SectionHeading(title: 'Color', showActionButton: false,), 
            const SizedBox(height: AppSizes.spaceBtwItems / 2),
            Wrap(
              spacing: 8.0,
              runSpacing: 4.0,
              children: [
                MyChoiceChip(label: 'red', selected: true, onSelected: (value){},),               
                MyChoiceChip(),  
                MyChoiceChip(),         
              ],
            ),
          ],
        ),
        const SizedBox(height: AppSizes.spaceBtwItems),
        // Size
        Column(
          crossAxisAlignment: CrossAxisAlignment.start, 
          children: [
            const SectionHeading(title: 'Size', showActionButton: false,), 
            const SizedBox(height: AppSizes.spaceBtwItems / 2),
            Wrap(
              spacing: 8.0,
              runSpacing: 4.0,
              children: [
                MyChoiceChip(label: '40', selected: false, onSelected: (value){},),              
                MyChoiceChip(label: '40', selected: true, onSelected: (value){},),    
                MyChoiceChip(label: '40', selected: false, onSelected: (value){},),
              ],
            ),
          ],
        ),
      ],
    );
  }
}