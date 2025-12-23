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
    final controller = Get.put(VariationController());
    final availableAttributes = controller.getUniqueAttributes(product);

    if (availableAttributes.isEmpty) {
      return const SizedBox.shrink();
    }

    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.grey.shade50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.grey.shade200),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Text(
                'Tùy chọn',
                style: TextStyle(
                  fontSize: 15,
                  fontWeight: FontWeight.w600,
                ),
              ),
              const Spacer(),
              ...availableAttributes.entries.map((entry) {
                final attributeName = entry.key;
                final attributeValues = entry.value.toList();
                return Padding(
                  padding: const EdgeInsets.only(left: 8),
                  child: Text(
                    '$attributeName: ${attributeValues.length} loại',
                    style: TextStyle(
                      fontSize: 13,
                      color: Colors.grey.shade600,
                    ),
                  ),
                );
              }).toList(),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            'Vui lòng chọn tùy chọn sản phẩm',
            style: TextStyle(
              fontSize: 13,
              color: Colors.grey.shade600,
            ),
          ),
        ],
      ),
    );
  }
}
