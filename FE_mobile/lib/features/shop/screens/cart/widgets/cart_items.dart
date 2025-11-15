import 'package:flutter/material.dart';
import 'package:flutter_app/widgets/texts/product_price_text.dart';
import '../../../../../common/widgets/products/cart/cart_item.dart';
import '../../../../../common/widgets/products/cart/product_quantity_add_minus.dart';
import 'package:flutter_slidable/flutter_slidable.dart';
import 'package:flutter_app/constants/sizes.dart';

class CartItems extends StatelessWidget {
  final bool showRemoveButton;
  const CartItems({
    super.key,
    this.showRemoveButton = true,
  });

  @override
  Widget build(BuildContext context) {
    return ListView.separated(
      shrinkWrap: true,
      separatorBuilder: (_, __) => const SizedBox(height: AppSizes.spaceBtwSections),
      itemCount: 2,
      itemBuilder: (_, index) => Slidable(
        
        key: ValueKey(index), // Thay 'index' bằng product.id khi có dữ liệu thật
        
        // Hành động khi vuốt từ phải sang trái
        endActionPane: ActionPane(
          motion: const ScrollMotion(),
          extentRatio: 0.2,
          children: [
            SlidableAction(
              
              onPressed: (context) {
                // Thêm logic xóa item tại đây
                debugPrint('Delete item $index');
              },
              backgroundColor: Colors.red,
              foregroundColor: Colors.white,
              icon: Icons.delete,
              label: 'Delete',
              borderRadius: BorderRadius.circular(AppSizes.cardRadiusMd),
            ),
          ],
        ),
        
        // Nội dung của item 
        child: Column(
          children: [
            // Thông tin chính của item 
            const CartItem(),
            if (showRemoveButton)
              const SizedBox(height: AppSizes.spaceBtwItems),
            
            // Hàng chứa Tăng/Giảm số lượng và Giá
            if (showRemoveButton)
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                
                const ProductQuantityAddMinus(),
                
                const ProductPriceText(price: '250')
              ],
            )
          ],
        ),
      ),
    );
  }
}