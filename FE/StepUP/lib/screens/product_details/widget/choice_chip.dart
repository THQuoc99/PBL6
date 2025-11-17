import 'package:flutter/material.dart';
import 'package:flutter_app/constants/image_string.dart';

class MyChoiceChip extends StatelessWidget {
  final bool selected;
  final void Function(bool)? onSelected;
  final String label;
  final String imagePath;
  const MyChoiceChip({
    super.key,
    this.selected = false,
    this.onSelected,
    this.label = 'Red Nike Shoes',
    this.imagePath = AppImages.sabrinaRed,
  });

  @override
  Widget build(BuildContext context) {
    return ChoiceChip(
      label: label.isNotEmpty ? Text(label) : const SizedBox.shrink(),
      selected: selected,
      onSelected: onSelected,
      avatar: CircleAvatar(
        backgroundImage: AssetImage(AppImages.sabrinaRed),
      ),
      
      selectedColor: Colors.blue.withAlpha((255 * 0.2).round()), 
      padding: const EdgeInsets.symmetric(horizontal: 8.0, vertical: 8.0),
    );
  }
}
