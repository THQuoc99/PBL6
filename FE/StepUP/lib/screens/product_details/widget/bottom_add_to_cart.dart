import 'package:flutter/material.dart';
import 'package:flutter_app/constants/sizes.dart';
import 'package:flutter_app/screens/product_details/widget/product_variation_sheet.dart';
import 'package:flutter_app/shop/models/product_model.dart'; // Import Model

class BottomAddCart extends StatelessWidget {
  // ✅ Cần nhận ProductModel
  final ProductModel product;

  const BottomAddCart({
    super.key,
    required this.product,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: AppSizes.defaultSpace, vertical: AppSizes.defaultSpace / 2),
      decoration: const BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.only(
          topLeft: Radius.circular(AppSizes.cardRadiusLg),
          topRight: Radius.circular(AppSizes.cardRadiusLg),
        ),
      ),
      child: Row(
        children: [
          Expanded(
            child: ElevatedButton.icon(
              onPressed: () => showAddToCartSheet(context, SheetMode.addToCart),
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 16.0),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8.0)),
                backgroundColor: Colors.blue, 
                foregroundColor: Colors.white,
              ),
              label: const Text('Add to cart'),
              icon: const Icon(Icons.shopping_cart),
            ),
          ),
          const SizedBox(width: 16.0),
          Expanded(
            child: ElevatedButton(
              onPressed: () => showAddToCartSheet(context, SheetMode.buyNow),
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 16.0),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8.0)),
                backgroundColor: Colors.blue, // Màu nền xanh cho nút Buy
                foregroundColor: Colors.white,
              ),
              child: const Text('Buy Now'),
            ),
          ),
        ],
      ),
    );
  }

  void showAddToCartSheet(BuildContext context, SheetMode modes) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
      ),
      builder: (BuildContext ctx) {
        // ✅ Truyền product vào sheet
        return ProductVariationSheet(mode: modes, product: product);
      },
    );
  }
}