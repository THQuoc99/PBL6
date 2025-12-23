import 'package:flutter/material.dart';
import 'package:flutter_app/constants/colors.dart';
import 'package:flutter_app/constants/sizes.dart';
import 'package:flutter_app/utils/helpers/helper_function.dart';
import 'package:get/get.dart';
import 'package:flutter_app/shop/controllers/cart_controller.dart';
import 'package:flutter_app/features/shop/screens/cart/cart.dart';
import 'package:iconsax_flutter/iconsax_flutter.dart';

class CusAppbar extends StatelessWidget implements PreferredSizeWidget {
  final Widget? title;
  final List<Widget>? actions;
  final bool showBackArrow;
  final VoidCallback? leadingOnPressed;
  final IconData? leadingIcon;
  final bool showCart;
  final PreferredSizeWidget? bottom;
  final Color? iconColor;

  const CusAppbar({
    super.key,
    this.title,
    this.actions,
    this.showBackArrow = false,
    this.leadingOnPressed,
    this.leadingIcon,
    this.showCart = false,
    this.bottom,
    this.iconColor,
  });

  @override
  Widget build(BuildContext context) {
    final dark = HelperFunction.isDarkMode(context);
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: AppSizes.md),
      child: AppBar(
        backgroundColor: Colors.transparent,
        automaticallyImplyLeading: false,
        bottom: bottom,
        leading: showBackArrow
            ? IconButton(
                onPressed: () => Navigator.of(context).pop(), 
                icon: Icon(
                  Iconsax.arrow_left,
                  color: dark ? AppColors.white : AppColors.dark,
                ),
              )
            : leadingIcon != null
                ? IconButton(
                    onPressed: leadingOnPressed,
                    icon: Icon(leadingIcon),
                  )
                : null,
        title: title,
        actions: _buildActions(context, actions),
      ),
    );
  }
  List<Widget>? _buildActions(BuildContext context, List<Widget>? actions) {
    final dark = HelperFunction.isDarkMode(context);
    final Color resolvedIconColor = iconColor ?? (dark ? AppColors.white : AppColors.dark);
    final List<Widget> list = [];
    if (actions != null) list.addAll(actions);

    if (showCart) {
      // Ensure CartController is available
      final cartController = Get.put(CartController());
      list.add(
        Obx(() {
          final count = cartController.cartItems.length;
          return Stack(
            children: [
              IconButton(
                icon: Icon(Iconsax.shopping_cart, color: resolvedIconColor),
                onPressed: () {
                  Get.to(() => const CartScreen());
                },
              ),
              if (count > 0)
                Positioned(
                  right: 6,
                  top: 6,
                  child: Container(
                    padding: const EdgeInsets.all(2),
                    decoration: BoxDecoration(
                      color: Colors.red,
                      borderRadius: BorderRadius.circular(6),
                    ),
                    constraints: const BoxConstraints(minWidth: 14, minHeight: 14),
                    child: Text(
                      '$count',
                      style: const TextStyle(color: Colors.white, fontSize: 10),
                      textAlign: TextAlign.center,
                    ),
                  ),
                ),
            ],
          );
        }),
      );
    }

    return list.isEmpty ? null : list;
  }

  @override
  @override
  Size get preferredSize {
    final double bottomHeight = bottom?.preferredSize.height ?? 0.0;
    return Size.fromHeight(kToolbarHeight + bottomHeight);
  }
}