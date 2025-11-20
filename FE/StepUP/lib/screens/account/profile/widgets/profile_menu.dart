import 'package:flutter/material.dart';
import 'package:flutter_app/constants/sizes.dart';

class ProfileMenu extends StatelessWidget {
  final IconData icon;
  final String title, value;
  final VoidCallback onPressed;

  const ProfileMenu({
    super.key,
    required this.onPressed,
    required this.title,
    required this.value,
    this.icon = Icons.arrow_right_rounded,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: AppSizes.spaceBtwItems/1.5),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: onPressed,
          borderRadius: BorderRadius.circular(6),
          child: Row(
            children: [
              Expanded(flex: 3, child: Text(title, style: Theme.of(context).textTheme.bodySmall,overflow: TextOverflow.ellipsis,)),
              Expanded(
                flex: 5,
                child: Text(value, style: Theme.of(context).textTheme.bodyMedium,overflow: TextOverflow.ellipsis,)),
              Expanded(child: Icon(icon, size: 18,))
            ],
          ),
        ),
      ),
    );
  }
}