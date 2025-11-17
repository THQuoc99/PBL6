import 'package:flutter/material.dart';
import 'package:flutter_app/constants/sizes.dart';
import 'package:flutter_app/screens/product_details/widget/product_variation_sheet.dart';



class BottomAddCart extends StatelessWidget {
  const BottomAddCart({
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: AppSizes.defaultSpace, vertical: AppSizes.defaultSpace / 2),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: const BorderRadius.only(
          topLeft: Radius.circular(AppSizes.cardRadiusLg),
          topRight: Radius.circular(AppSizes.cardRadiusLg),
        ),
      ),
      child: Row(
        children: [
          Expanded(
            child: ElevatedButton.icon(
              onPressed: () {
                showAddToCartSheet(context, SheetMode.addToCart);
              },
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 16.0),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8.0),
                ),
              ),
              label: const Text('Add to cart'),
              icon: const Icon(Icons.shopping_cart),
            ),
          ),
          const SizedBox(width: 16.0),
          Expanded(
            child: ElevatedButton(
              onPressed: () {
                showAddToCartSheet(context, SheetMode.buyNow);
              },
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 16.0),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8.0),
                ),
              ),
              child: const Text('Buy Now'),
            ),
          ),
        ],
      ),
    );
  }
  void showAddToCartSheet(BuildContext context,SheetMode modes) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true, // Cho phép sheet cao hơn
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
      ),
      builder: (BuildContext ctx) {
        // Chúng ta dùng một StatefulWidget riêng để quản lý trạng thái chọn màu
        return ProductVariationSheet(mode: modes);
      },
    );
  }
}

