import 'package:flutter/material.dart';
import 'package:flutter_app/constants/colors.dart';

class MyChoiceChip extends StatelessWidget {
  final String text;
  final bool selected;
  final void Function(bool)? onSelected;

  const MyChoiceChip({
    super.key,
    required this.text,
    required this.selected,
    this.onSelected,
  });

  @override
  Widget build(BuildContext context) {
    // Helper lấy màu từ tên (Bạn có thể mở rộng thêm các màu tiếng Việt)
    final color = _getColor(text);
    final isColor = color != null;

    return Theme(
      data: Theme.of(context).copyWith(canvasColor: Colors.transparent),
      child: ChoiceChip(
        // Nếu là màu -> Ẩn chữ, hiện vòng tròn màu
        label: isColor ? const SizedBox() : Text(text),
        selected: selected,
        onSelected: onSelected,
        
        labelStyle: TextStyle(color: selected ? Colors.white : null),
        
        avatar: isColor 
          ? CircleAvatar(backgroundColor: color) 
          : null,
        
        labelPadding: isColor ? const EdgeInsets.all(0) : null,
        padding: isColor ? const EdgeInsets.all(0) : const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
        
        // Màu nền khi được chọn
        selectedColor: AppColors.primary,
        backgroundColor: isColor ? color : null,
        shape: isColor ? const CircleBorder() : null,
      ),
    );
  }

  Color? _getColor(String value) {
    // Hỗ trợ cả tiếng Anh và tiếng Việt (theo DB của bạn)
    switch (value.toLowerCase()) {
      case 'green': case 'xanh lá': return Colors.green;
      case 'blue': case 'xanh dương': return Colors.blue;
      case 'red': case 'đỏ': return Colors.red;
      case 'yellow': case 'vàng': return Colors.yellow;
      case 'black': case 'đen': return Colors.black;
      case 'white': case 'trắng': return Colors.white;
      case 'grey': case 'xám': return Colors.grey;
      case 'purple': case 'tím': return Colors.purple;
      case 'pink': case 'hồng': return Colors.pink;
      default: return null;
    }
  }
}