import 'package:flutter/material.dart';
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

  Future<bool> _onWillPop() async {
    // If not on home tab, go back to home instead of exiting
    if (controller.selectedIndex.value != 0) {
      controller.selectedIndex.value = 0;
      return false;
    }
    
    // If on home tab, show exit confirmation dialog
    final shouldExit = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Thoát ứng dụng'),
        content: const Text('Bạn có chắc chắn muốn thoát?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('Không'),
          ),
          TextButton(
            onPressed: () => Navigator.of(context).pop(true),
            child: const Text('Thoát'),
          ),
        ],
      ),
    );
    return shouldExit ?? false;
  }

  @override
  Widget build(BuildContext context) {
    return WillPopScope(
      onWillPop: _onWillPop,
      child: Scaffold(
        bottomNavigationBar: ValueListenableBuilder<int>(
          valueListenable: controller.selectedIndex,
          builder: (context, selectedIndex, _) => NavigationBar(
            height: 70,
            elevation: 0,
            selectedIndex: selectedIndex,
            onDestinationSelected: (index) =>
                controller.selectedIndex.value = index,
            destinations: const [
            NavigationDestination(icon: Icon(Icons.home), label: 'Trang chủ'),
            NavigationDestination(icon: Icon(Icons.favorite), label: 'Yêu thích'),
            NavigationDestination(icon: Icon(Icons.shopping_basket), label: 'Đơn hàng'),
            //NavigationDestination(icon: Icon(Icons.shopping_bag), label: 'Giỏ hàng'),
            NavigationDestination(icon: Icon(Icons.person), label: 'Cá nhân'),
            ],
          ),
        ),
        body: ValueListenableBuilder<int>(
          valueListenable: controller.selectedIndex,
          builder: (context, selectedIndex, _) =>
              controller.screens[selectedIndex],
        ),
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
  //const CartScreen(),
  const SettingScreen(),
];

}
