import 'package:flutter/material.dart';
import 'package:flutter_app/features/shop/screens/cart/cart.dart';
import 'package:flutter_app/features/shop/screens/order/order.dart';
import 'package:flutter_app/screens/account/setting/setting.dart';
import 'package:flutter_app/screens/favorite/favorite.dart';
import 'package:flutter_app/screens/home/home_screen.dart';

class NavigationMenu extends StatefulWidget {
  const NavigationMenu({super.key});

  @override
  State<NavigationMenu> createState() => _NavigationMenuState();
}

class _NavigationMenuState extends State<NavigationMenu> {
  final controller = NavigationController();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      bottomNavigationBar: ValueListenableBuilder<int>(
        valueListenable: controller.selectedIndex,
        builder: (context, selectedIndex, _) => NavigationBar(
          height: 70,
          elevation: 0,
          selectedIndex: selectedIndex,
          onDestinationSelected: (index) =>
              controller.selectedIndex.value = index,
          destinations: const [
            NavigationDestination(icon: Icon(Icons.home), label: 'Home'),
            NavigationDestination(icon: Icon(Icons.favorite), label: 'Favorite'),
            NavigationDestination(icon: Icon(Icons.shopping_basket), label: 'My Order'),
            NavigationDestination(icon: Icon(Icons.shopping_bag), label: 'Cart'),
            NavigationDestination(icon: Icon(Icons.person), label: 'Profile'),
          ],
        ),
      ),
      body: ValueListenableBuilder<int>(
        valueListenable: controller.selectedIndex,
        builder: (context, selectedIndex, _) =>
            controller.screens[selectedIndex],
      ),
    );
  }
}

class NavigationController {
  final ValueNotifier<int> selectedIndex = ValueNotifier<int>(0);

  final List<Widget> screens = [
  const HomeScreen(),
  const FavoriteScreen(),
  const OrderScreen(),
  const CartScreen(),
  const SettingScreen(),
];

}
