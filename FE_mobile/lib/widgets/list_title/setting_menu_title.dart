import 'package:flutter/material.dart';

class SettingMenuTitle extends StatelessWidget {
  final String title, subtitle;
  final IconData icon;
  final Widget? trailing;
  final VoidCallback? onTap;

  const SettingMenuTitle({
    super.key,
    required this.icon,
    required this.subtitle,
    required this.title,
    this.trailing,
    this.onTap
  });

  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: Icon(icon, size: 28, color: Colors.blueAccent,),
      title: Text(title, style: Theme.of(context).textTheme.titleMedium,),
      subtitle: Text(subtitle, style: Theme.of(context).textTheme.labelMedium,),
      trailing: trailing,
      onTap: onTap,
    );
  }
}