import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:flutter_app/constants/colors.dart';
import 'package:flutter_app/constants/sizes.dart';
import 'package:flutter_app/shop/models/product_model.dart';
import 'package:flutter_app/widgets/containers/rounded_container.dart';
import 'package:flutter_app/screens/home/components/section_heading.dart';
import 'package:flutter_app/shop/controllers/product_variation_controller.dart';
import 'package:flutter_app/screens/product_details/widget/choice_chip.dart'; 

class ProductAttribute extends StatelessWidget {
  final ProductModel product; 

  const ProductAttribute({
    super.key,
    required this.product,
  });

  @override
  Widget build(BuildContext context) {
    final dark = Theme.of(context).brightness == Brightness.dark;
    
    final controller = Get.put(VariationController());
    final availableAttributes = controller.getAvailableAttributes(product);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // --- PHẦN 1: Variation (Không hiển thị giá / tồn kho / SKU) ---
        RoundedContainer(
          padding: const EdgeInsets.all(AppSizes.md),
          bgcolor: dark ? AppColors.darkerGrey : AppColors.grey.withOpacity(0.3),
          child: const Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              SectionHeading(title: 'Variation', showActionButton: false),
              SizedBox(height: AppSizes.spaceBtwItems),

              // Chỉ hiển thị dòng này, không có giá / stock
              Text(
                "Chọn màu sắc và kích thước sản phẩm",
                style: TextStyle(fontSize: 13),
              ),
            ],
          ),
        ),

        const SizedBox(height: AppSizes.spaceBtwItems),

        // --- PHẦN 2: DANH SÁCH THUỘC TÍNH (Color / Size) ---
        if (availableAttributes.isNotEmpty)
          ...availableAttributes.entries.map((entry) {
            final attributeName = entry.key; 
            final attributeValues = entry.value.toList(); 

            return Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                SectionHeading(title: attributeName, showActionButton: false),
                const SizedBox(height: AppSizes.spaceBtwItems / 2),
                
                Obx(() => Wrap(
                  spacing: 8,
                  children: attributeValues.map((value) {
                    final isSelected = controller.selectedAttributes[attributeName] == value;
                    return MyChoiceChip(
                      text: value,
                      selected: isSelected,
                      onSelected: (selected) {
                        if (selected) {
                          controller.onAttributeSelected(product, attributeName, value);
                        }
                      },
                    );
                  }).toList(),
                )),
                const SizedBox(height: AppSizes.spaceBtwItems),
              ],
            );
          }).toList()
        else 
          const Padding(
            padding: EdgeInsets.symmetric(vertical: 10),
            child: Text("Sản phẩm này không có tùy chọn nào."),
          ),
      ],
    );
  }
}
