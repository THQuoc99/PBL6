import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:flutter_app/constants/sizes.dart';
import 'package:flutter_app/constants/colors.dart';
import 'package:flutter_app/widgets/appbar/appbar.dart';
import 'package:flutter_app/features/shop/screens/order/widgets/order_list.dart';
import 'package:flutter_app/features/shop/screens/return/return_list_screen.dart';
import 'package:flutter_app/shop/controllers/order_list_controller.dart';

class OrderScreen extends StatefulWidget {
  const OrderScreen({super.key});

  @override
  State<OrderScreen> createState() => _OrderScreenState();
}

class _OrderScreenState extends State<OrderScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  late final OrderListController controller;

  @override
  void initState() {
    super.initState();
    // Use Get.find() to get existing instance or create if not exists
    controller = Get.put(OrderListController(), permanent: true);
    _tabController = TabController(length: tabs.length, vsync: this);
    _tabController.addListener(_handleTabChange);
    // Set initial filter
    controller.setFilterStatus(null);
    
    // Ensure data is loaded after frame is built
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (controller.orders.isEmpty) {
        controller.fetchUserOrders();
      }
    });
  }

  final tabs = [
    {'label': 'Tất cả', 'status': null, 'isReturn': false},
    {'label': 'Chờ xác nhận', 'status': 'pending', 'isReturn': false},
    {'label': 'Đang giao', 'status': 'shipping', 'isReturn': false},
    {'label': 'Đã giao', 'status': 'completed', 'isReturn': false},
    {'label': 'Đã hủy', 'status': 'cancelled', 'isReturn': false},
    {'label': 'Trả hàng', 'status': null, 'isReturn': true},
  ];

  @override
  void dispose() {
    _tabController.removeListener(_handleTabChange);
    _tabController.dispose();
    super.dispose();
  }

  void _handleTabChange() {
    if (!_tabController.indexIsChanging) {
      final tab = tabs[_tabController.index];
      if (tab['isReturn'] != true) {
        controller.setFilterStatus(tab['status'] as String?);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: CusAppbar(
        title: Text('Đơn hàng của tôi', style: Theme.of(context).textTheme.headlineSmall),
        showCart: true,
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(48),
          child: Container(
            color: Colors.white,
            child: TabBar(
              controller: _tabController,
              isScrollable: true,
              labelColor: AppColors.primary,
              unselectedLabelColor: Colors.grey,
              indicatorColor: AppColors.primary,
              labelStyle: const TextStyle(fontWeight: FontWeight.w600),
              tabs: tabs.map((tab) => Tab(text: tab['label'] as String)).toList(),
            ),
          ),
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: tabs.map((tab) {
          if (tab['isReturn'] == true) {
            return const ReturnListScreen();
          } else {
            return Padding(
              padding: const EdgeInsets.all(AppSizes.defaultSpace),
              child: Obx(() {
                // Show loading indicator while fetching
                if (controller.isLoading.value) {
                  return const Center(child: CircularProgressIndicator());
                }
                
                // Show empty state or order list
                return OrderListItems(orders: controller.filteredOrders);
              }),
            );
          }
        }).toList(),
      ),
    );
  }
}