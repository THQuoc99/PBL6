import 'package:flutter/material.dart';
import 'package:flutter_app/widgets/image/rounded_image.dart';
import 'package:flutter_app/constants/image_string.dart';

class UserProfileTitle extends StatelessWidget {

  final String title;
  final String subtitle;
  final VoidCallback onPressed;

  const UserProfileTitle({
    super.key,
    required this.onPressed,
    required this.title, 
    required this.subtitle, 
  });

  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: const RoundedImage(imageUrl: AppImages.sabrina, radius: 180, applyImageRadius: true),
      
      title: Text(title), 
      subtitle: Text(subtitle),
      
      trailing: IconButton(onPressed: onPressed, icon: Icon(Icons.edit)),
    );
  }
}