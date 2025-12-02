import 'package:get/get.dart';
import 'package:flutter_app/shop/models/product_model.dart';
import 'package:flutter_app/shop/models/product_variant_model.dart';

class VariationController extends GetxController {
  static VariationController get instance => Get.find();

  final selectedAttributes = <String, String>{}.obs;
  final variationStockStatus = ''.obs; 
  final selectedVariant = Rx<ProductVariantModel?>(null);

  // 1. Lấy danh sách thuộc tính để render UI (Chip)
  Map<String, Set<String>> getUniqueAttributes(ProductModel product) {
    Map<String, Set<String>> attributes = {};

    for (var variant in product.variants) {
      if (variant.stock > 0) { // Chỉ hiện attribute của sp còn hàng
        variant.attributeCombinations.forEach((key, value) {
          if (!attributes.containsKey(key)) {
            attributes[key] = {};
          }
          attributes[key]!.add(value);
        });
      }
    }
    return attributes;
  }

  // 2. Xử lý chọn Chip
  void onAttributeSelected(ProductModel product, String attributeName, String attributeValue) {
    if (selectedAttributes[attributeName] == attributeValue) {
      selectedAttributes.remove(attributeName); // Bỏ chọn
    } else {
      selectedAttributes[attributeName] = attributeValue; // Chọn mới
    }
    _updateSelectedVariant(product);
  }

  // 3. Tìm biến thể khớp
  void _updateSelectedVariant(ProductModel product) {
    // Tìm variant khớp với TẤT CẢ thuộc tính đã chọn
    final matchingVariant = product.variants.firstWhereOrNull((variant) {
      bool isMatch = true;
      for (var entry in selectedAttributes.entries) {
        // So sánh String vs String trong Map
        if (variant.attributeCombinations[entry.key] != entry.value) {
          isMatch = false;
          break;
        }
      }
      return isMatch;
    });

    if (matchingVariant != null) {
      // Kiểm tra đã chọn ĐỦ thuộc tính chưa
      final requiredCount = getUniqueAttributes(product).keys.length;
      
      if (selectedAttributes.length == requiredCount) {
        // Found!
        selectedVariant.value = matchingVariant;
        variationStockStatus.value = 'Kho: ${matchingVariant.stock}';
      } else {
        // Chưa chọn đủ
        selectedVariant.value = null;
        variationStockStatus.value = 'Vui lòng chọn đủ thông tin';
      }
    } else {
      // Chọn attribute không khớp (VD: Màu Đỏ + Size 45 không có)
      selectedVariant.value = null;
      variationStockStatus.value = 'Hết hàng';
      // Optional: Reset lựa chọn vừa rồi nếu muốn UX chặt chẽ hơn
    }
  }
  
  // Gọi hàm này khi vào trang chi tiết hoặc rời đi
  void reset() {
    selectedAttributes.clear();
    variationStockStatus.value = '';
    selectedVariant.value = null;
  }
}