import 'package:flutter/material.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'package:get/get.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:flutter_app/constants/colors.dart';
import 'package:flutter_app/screens/product_details/product_detail.dart';
import 'package:flutter_app/shop/controllers/product_controller.dart'; // Đảm bảo bạn có controller này

class MessageBubble extends StatelessWidget {
  final String message;
  final bool isUser;

  const MessageBubble({
    super.key,
    required this.message,
    required this.isUser,
  });

  @override
  Widget build(BuildContext context) {
    return Align(
      alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.symmetric(vertical: 4, horizontal: 8),
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: isUser ? AppColors.primary : Colors.grey[200],
          borderRadius: BorderRadius.only(
            topLeft: const Radius.circular(12),
            topRight: const Radius.circular(12),
            bottomLeft: isUser ? const Radius.circular(12) : const Radius.circular(0),
            bottomRight: isUser ? const Radius.circular(0) : const Radius.circular(12),
          ),
        ),
        constraints: BoxConstraints(maxWidth: MediaQuery.of(context).size.width * 0.75),
        child: isUser
            ? Text(
                message,
                style: const TextStyle(color: Colors.white, fontSize: 15),
              )
            : MarkdownBody(
                data: message,
                selectable: true, // Cho phép copy text
                styleSheet: MarkdownStyleSheet(
                  p: const TextStyle(color: Colors.black87, fontSize: 15),
                  strong: const TextStyle(fontWeight: FontWeight.bold, color: Colors.black),
                  // Style cho Link màu xanh và gạch chân
                  a: TextStyle(
                    color: AppColors.primary,
                    decoration: TextDecoration.underline,
                    fontWeight: FontWeight.bold
                  ),
                ),
                onTapLink: (text, href, title) {
                  if (href != null) {
                    _handleLinkTap(href);
                  }
                },
              ),
      ),
    );
  }

  // --- LOGIC XỬ LÝ LINK ---
  void _handleLinkTap(String url) {
    print("🔗 Tapped link: $url");

    // 1. Nếu là Deep Link sản phẩm (myapp://product/123)
    if (url.startsWith("myapp://product/")) {
      var idString = url.split("/").last;
      int? productId = int.tryParse(idString);

      if (productId != null) {
        _navigateToProductDetail(productId);
      }
    } 
    // 2. Nếu là Link Web bình thường (http...)
    else {
      _launchWebUrl(url);
    }
  }

  void _navigateToProductDetail(int productId) {
    // Hiển thị loading hoặc xử lý chuyển trang
    // Giả sử bạn có ProductController với hàm fetchProductById
    final controller = Get.put(ProductController());
    
    // Show loading dialog cho chuyên nghiệp
    Get.dialog(
      const Center(child: CircularProgressIndicator()), 
      barrierDismissible: false
    );

    controller.fetchProductById(productId).then((product) {
      Get.back(); // Đóng loading
      
      if (product != null) {
        Get.to(() => ProductDetail(product: product));
      } else {
        Get.snackbar("Lỗi", "Không tìm thấy sản phẩm này", backgroundColor: Colors.red.withOpacity(0.1), colorText: Colors.red);
      }
    }).catchError((e) {
      Get.back(); // Đóng loading nếu lỗi
      print("Lỗi navigate: $e");
    });
  }

  Future<void> _launchWebUrl(String url) async {
    final uri = Uri.parse(url);
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    } else {
      print("Không thể mở link: $url");
    }
  }
}