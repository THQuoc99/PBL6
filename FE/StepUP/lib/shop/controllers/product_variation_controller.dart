import 'package:get/get.dart';
import 'package:flutter_app/shop/models/product_model.dart';
import 'package:flutter_app/shop/models/product_variant_model.dart';

class VariationController extends GetxController {
  static VariationController get instance => Get.find();

  // Lưu trạng thái đã chọn: {"Màu sắc": "Đỏ", "Kích cỡ": "39"}
  final selectedAttributes = <String, String>{}.obs;
  
  final variationStockStatus = ''.obs; 
  final selectedVariant = Rx<ProductVariantModel?>(null);

  // ✅ Hàm quan trọng: Quét variants để lấy danh sách thuộc tính có sẵn
  Map<String, Set<String>> getAvailableAttributes(ProductModel product) {
    Map<String, Set<String>> attributes = {};

    if (product.variants.isEmpty) return attributes;

    for (var variant in product.variants) {
      // Chỉ lấy thuộc tính của các variant còn hàng (stock > 0)
      if (variant.stock > 0) {
        variant.attributes.forEach((key, value) {
          // key: "Màu sắc", value: "Đỏ"
          if (!attributes.containsKey(key)) {
            attributes[key] = {};
          }
          attributes[key]!.add(value);
        });
      }
    }
    return attributes;
  }

  // Khi người dùng chọn 1 chip
  void onAttributeSelected(ProductModel product, String attributeName, String attributeValue) {
    // 1. Cập nhật map đã chọn
    selectedAttributes[attributeName] = attributeValue;

    // 2. Tìm variant khớp với TẤT CẢ các thuộc tính đã chọn
    final matchingVariant = product.variants.firstWhereOrNull((variant) {
      bool isMatch = true;
      // Kiểm tra từng thuộc tính đã chọn xem variant này có khớp không
      selectedAttributes.forEach((key, value) {
        if (variant.attributes[key] != value) {
          isMatch = false;
        }
      });
      return isMatch;
    });

    // 3. Cập nhật UI
    if (matchingVariant != null) {
      // Nếu tìm thấy variant khớp hoàn toàn
      // Kiểm tra xem người dùng đã chọn ĐỦ thuộc tính chưa?
      // (Ví dụ sản phẩm có Màu + Size, nhưng mới chọn Màu -> chưa xác định được variant cuối cùng)
      // Logic đơn giản: Nếu số lượng thuộc tính đã chọn == số lượng key trong variant -> Đã chọn xong
      if (selectedAttributes.length == matchingVariant.attributes.length) {
         selectedVariant.value = matchingVariant;
         variationStockStatus.value = 'Kho: ${matchingVariant.stock}';
      } else {
         // Chưa chọn đủ (mới chọn Màu, chưa chọn Size)
         selectedVariant.value = null;
         variationStockStatus.value = 'Vui lòng chọn thêm thuộc tính';
      }
    } else {
      selectedVariant.value = null;
      variationStockStatus.value = 'Phiên bản này không có hàng';
      // Có thể thêm logic reset lựa chọn nếu muốn
    }
  }
  
  // Reset khi vào màn hình mới
  void reset() {
    selectedAttributes.clear();
    variationStockStatus.value = '';
    selectedVariant.value = null;
  }
}