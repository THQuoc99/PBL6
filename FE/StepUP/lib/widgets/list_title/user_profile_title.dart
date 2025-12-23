import 'package:flutter/material.dart';
import 'package:flutter_app/widgets/image/rounded_image.dart';
import 'package:flutter_app/constants/image_string.dart';

class UserProfileTitle extends StatelessWidget {
  final String title;
  final String subtitle;
  final VoidCallback onPressed;
  final String? imageUrl; // optional: network url or asset
  final bool isNetwork;

  const UserProfileTitle({
    super.key,
    required this.onPressed,
    required this.title,
    required this.subtitle,
    this.imageUrl,
    this.isNetwork = false,
  });

  @override
  Widget build(BuildContext context) {
    final img = imageUrl ?? AppImages.sabrina;
    return ListTile(
      leading: RoundedImage(
        imageUrl: img,
        radius: 180,
        applyImageRadius: true,
        isNetworkImage: isNetwork,
      ),
      title: Text(title),
      subtitle: Text(subtitle),
      trailing: IconButton(onPressed: onPressed, icon: const Icon(Icons.edit)),
    );
  }
}