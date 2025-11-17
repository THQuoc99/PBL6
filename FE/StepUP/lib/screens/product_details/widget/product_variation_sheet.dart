import 'package:flutter/material.dart';
import 'package:flutter_app/constants/image_string.dart';

// 
enum SheetMode { addToCart, buyNow }

class ProductVariationSheet extends StatefulWidget {
  final SheetMode mode;
  const ProductVariationSheet({
    super.key,
    required this.mode,
  });

  @override
  State<ProductVariationSheet> createState() => _ProductVariationSheetState();
}

class _ProductVariationSheetState extends State<ProductVariationSheet> {
  // Biến để lưu trữ lựa chọn hiện tại
  String? _selectedColor;

  // Dữ liệu mẫu (bạn sẽ thay bằng dữ liệu thật)
  final List<Map<String, String>> variations = [
    {'name': 'F75 Xanh den', 'image': 'assets/images/blue.png'},
    {'name': 'F75 X-Đ silent', 'image': 'assets/images/black.png'},
    {'name': 'F75 xanh navy', 'image': 'assets/images/navy.png'},
    {'name': 'AU75 tím đỏ', 'image': 'assets/images/purple.png'},
    {'name': 'F75 Vàng Đen leobog', 'image': 'assets/images/yellow_black.png'},
    {'name': 'F75 white lines', 'image': 'assets/images/white.png'},
  ];

  @override
  Widget build(BuildContext context) {
    final String title = widget.mode == SheetMode.addToCart ? "Add to Cart" : "Buy Now";
    // Dùng Padding để tạo khoảng trống xung quanh nội dung
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        mainAxisSize: MainAxisSize.min, // Để sheet tự co lại theo nội dung
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 1. Phần thông tin sản phẩm (Ảnh, Giá, Kho)
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Giả lập ảnh sản phẩm được chọn
              Image.asset(AppImages.sabrina, width: 100, height: 100, fit: BoxFit.cover),
              const SizedBox(width: 16),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: const [
                  Text(
                    "976.800đ",
                    style: TextStyle(color: Colors.red, fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                  SizedBox(height: 4),
                  Text("Kho: 104", style: TextStyle(color: Colors.grey)),
                ],
              )
            ],
          ),
          const Divider(height: 24),

          // 2. Phần chọn Màu sắc
          const Text("Màu sắc", style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
          const SizedBox(height: 12),

          // Dùng Wrap để tự động xuống hàng
          Wrap(
            spacing: 8.0, // Khoảng cách ngang
            runSpacing: 8.0, // Khoảng cách dọc
            children: variations.map((variation) {
              final String name = variation['name']!;
              final String imagePath = variation['image']!; // Đường dẫn ảnh của bạn
              final bool isSelected = _selectedColor == name;

              return ChoiceChip(
                label: Text(name),
                // Dùng avatar để chèn ảnh nhỏ vào chip
                avatar: Image.asset(imagePath, width: 24, height: 24),
                selected: isSelected,
                onSelected: (selected) {
                  setState(() {
                    _selectedColor = name;
                  });
                },
                // Style cho chip
                selectedColor: Colors.lightBlueAccent.withAlpha(50),
                labelStyle: TextStyle(color: isSelected ? Colors.lightBlueAccent : Colors.black),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(4),
                  side: BorderSide(
                    color: isSelected ? Colors.lightBlueAccent : Colors.grey[300]!,
                  ),
                ),
                showCheckmark: false,
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              );
            }).toList(),
          ),
          const SizedBox(height: 24),

          // 3. Nút Thêm vào Giỏ hàng
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.blueAccent, // Dùng màu đã chọn
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 16),
              ),
              onPressed: _selectedColor != null ? () {
                // Xử lý logic dựa trên `widget.mode`
                if (widget.mode == SheetMode.buyNow) {
                  _handleBuyNow();
                } else {
                  _handleAddToCart();
                }
              } : null,
              child: Text(title, style: const TextStyle(fontSize: 16)), // Dùng chữ đã chọn
            ),
          ),
          // Thêm padding cho an toàn (tránh các thanh điều hướng của HĐH)
          SizedBox(height: MediaQuery.of(context).padding.bottom),
        ],
      ),
    );
  }
  void _handleAddToCart() {
    // Logic thêm vào giỏ hàng
    //print("Thêm vào giỏ hàng: $_selectedColor");
    Navigator.pop(context); // Đóng bottom sheet sau khi thêm vào giỏ
  }

  void _handleBuyNow() {
    // Logic mua ngay (ví dụ: chuyển đến trang thanh toán)
    //print("Mua ngay: $_selectedColor");
    Navigator.pop(context); 
    // Sau đó có thể điều hướng đến trang Checkout
    // Navigator.push(context, MaterialPageRoute(...));
  }
}