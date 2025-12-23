import 'package:get/get.dart';
import 'package:flutter/material.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'package:flutter_app/shop/models/shipping_method_model.dart';
import 'package:flutter_app/shop/controllers/cart_controller.dart';
import 'package:flutter_app/shop/controllers/address_controller.dart';

class ShippingController extends GetxController {
  static ShippingController get instance => Get.find();

  final selectedShippingMethod = Rx<ShippingMethodModel?>(null);
  final shippingMethods = <ShippingMethodModel>[].obs;
  final isLoading = false.obs;

  final String baseUrl = "http://10.0.2.2:8000";
  
  // Lazy initialization - get controllers in onInit()
  late final CartController cartController;
  late final AddressController addressController;

  @override
  void onInit() {
    super.onInit();
    
    // Initialize controllers
    cartController = Get.find<CartController>();
    addressController = Get.find<AddressController>();
    
    // Load default shipping methods
    loadDefaultShippingMethods();
    
    // Listen to address changes and recalculate shipping fee
    ever(addressController.selectedAddress, (_) {
      if (addressController.selectedAddress.value != null) {
        print('🔄 Address changed, recalculating shipping fee...');
        calculateShippingFee();
      }
    });
  }

  /// Load default shipping methods (static options)
  void loadDefaultShippingMethods() {
    shippingMethods.value = [
      ShippingMethodModel(
        id: 'ghtk_standard',
        name: 'Giao hàng tiết kiệm',
        description: 'Giao hàng tiêu chuẩn',
        fee: 0,
        estimatedDays: '3-5 ngày',
        icon: 'truck',
        isFreeShip: false,
      ),
      ShippingMethodModel(
        id: 'ghtk_express',
        name: 'Giao hàng nhanh',
        description: 'Giao hàng trong ngày',
        fee: 0,
        estimatedDays: '1-2 ngày',
        icon: 'truck_fast',
        isFreeShip: false,
      ),
    ];
  }

  /// Calculate shipping fee from GHTK API
  /// Tính phí ship riêng cho từng shop và cộng tổng
  Future<void> calculateShippingFee() async {
    try {
      print('=== calculateShippingFee called ===');
      isLoading.value = true;

      // Check if address is selected
      if (addressController.selectedAddress.value == null) {
        print('ERROR: No address selected');
        WidgetsBinding.instance.addPostFrameCallback((_) {
          Get.snackbar(
            'Thông báo',
            'Vui lòng chọn địa chỉ giao hàng',
            snackPosition: SnackPosition.BOTTOM,
          );
        });
        return;
      }

      final address = addressController.selectedAddress.value!;
      final selectedItems = cartController.selectedItems;
      
      if (selectedItems.isEmpty) {
        print('⚠️ No items selected for shipping calculation');
        return;
      }

      // Group items by store
      final itemsByStore = <String, List<dynamic>>{};
      for (var item in selectedItems) {
        final storeId = item.storeId ?? 'default';
        itemsByStore.putIfAbsent(storeId, () => []).add(item);
      }

      print('📦 Calculating shipping for ${itemsByStore.length} stores');
      print('📍 Delivery to: ${address.province} - ${address.hamlet} (${address.ward})');

      double totalShippingFee = 0;
      double totalInsurance = 0;

      // Get auth token
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('token');
      
      if (token == null) {
        print('ERROR: No auth token found');
        return;
      }

      // Calculate shipping for each store
      for (var entry in itemsByStore.entries) {
        final storeId = entry.key;
        final items = entry.value;
        final storeAddress = items.first.storeAddress;
        
        // Weight calculation (500g per item)
        final weight = items.fold<int>(0, (sum, item) => sum + ((item.quantity as int) * 500));
        
        print('🏪 Store $storeId: ${items.length} items, weight: ${weight}g');

        // Prepare request body
        final requestBody = {
          'province': address.province,
          'district': address.hamlet,
          'weight': weight,
          'deliver_option': 'none',
        };
        
        // Override warehouse address if store has specific address
        if (storeAddress != null && storeAddress['province'] != null) {
          requestBody['pick_province'] = storeAddress['province'];
          requestBody['pick_district'] = storeAddress['district'] ?? storeAddress['ward'];
          print('  📍 Store warehouse: ${storeAddress['province']} - ${storeAddress['district']}');
        }

        // Call GHTK API for this store
        try {
          final response = await http.post(
            Uri.parse('$baseUrl/api/shipments/calculate-fee/'),
            headers: {
              'Content-Type': 'application/json',
              'Authorization': 'Bearer $token',
            },
            body: json.encode(requestBody),
          );

          if (response.statusCode == 200) {
            final data = json.decode(utf8.decode(response.bodyBytes));
            if (data['fee'] != null) {
              final fee = (data['fee']['fee'] ?? 0).toDouble();
              final insurance = (data['fee']['insurance_fee'] ?? 0).toDouble();
              totalShippingFee += fee;
              totalInsurance += insurance;
              print('  ✅ Fee: $fee, Insurance: $insurance');
            }
          } else {
            print('  ❌ API error: ${response.statusCode}');
          }
        } catch (e) {
          print('  ❌ Exception: $e');
        }
      }

      print('💰 Total shipping: $totalShippingFee + $totalInsurance = ${totalShippingFee + totalInsurance}');

      // Update shipping methods with total fee
      final totalFee = totalShippingFee + totalInsurance;
      if (totalFee > 0) {
        final standardIndex = shippingMethods.indexWhere((m) => m.id == 'ghtk_standard');
        if (standardIndex >= 0) {
          shippingMethods[standardIndex] = ShippingMethodModel(
            id: 'ghtk_standard',
            name: 'Giao hàng tiết kiệm',
            description: 'Giao hàng tiêu chuẩn qua GHTK${itemsByStore.length > 1 ? ' (${itemsByStore.length} shop)' : ''}',
            fee: totalFee,
            estimatedDays: '3-5 ngày',
            icon: 'truck',
            isFreeShip: false,
          );
        }

        // Calculate express fee (usually 1.5x standard)
        final expressIndex = shippingMethods.indexWhere((m) => m.id == 'ghtk_express');
        if (expressIndex >= 0) {
          shippingMethods[expressIndex] = ShippingMethodModel(
            id: 'ghtk_express',
            name: 'Giao hàng nhanh',
            description: 'Giao hàng nhanh trong 1-2 ngày${itemsByStore.length > 1 ? ' (${itemsByStore.length} shop)' : ''}',
            fee: totalFee * 1.5,
            estimatedDays: '1-2 ngày',
            icon: 'truck_fast',
            isFreeShip: false,
          );
        }

        shippingMethods.refresh();
        print('Updated shipping methods: ${shippingMethods.map((m) => '${m.name}: ${m.fee}').join(', ')}');
        
        // Auto-update selected method with new fee
        if (selectedShippingMethod.value != null) {
          final currentMethodId = selectedShippingMethod.value!.id;
          final updatedMethod = shippingMethods.firstWhereOrNull((m) => m.id == currentMethodId);
          if (updatedMethod != null) {
            selectedShippingMethod.value = updatedMethod;
            print('✅ Auto-updated selected method: ${updatedMethod.name} - ${updatedMethod.fee}đ');
          }
        } else {
          // Auto-select standard method if none selected
          final standardMethod = shippingMethods.firstWhereOrNull((m) => m.id == 'ghtk_standard');
          if (standardMethod != null) {
            selectedShippingMethod.value = standardMethod;
            print('✅ Auto-selected standard method: ${standardMethod.fee}đ');
          }
        }
      }
    } catch (e) {
      print('Error calculating shipping fee: $e');
      // Keep default fees on error
    } finally {
      isLoading.value = false;
    }
  }

  /// Show shipping method selection dialog
  Future<void> selectShippingMethod(BuildContext context) async {
    // Recalculate fees before showing
    await calculateShippingFee();

    await Get.bottomSheet(
      Container(
        padding: const EdgeInsets.all(24),
        decoration: const BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Chọn phương thức vận chuyển',
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            const SizedBox(height: 16),
            Obx(() {
              if (isLoading.value) {
                return const Center(
                  child: Padding(
                    padding: EdgeInsets.all(24.0),
                    child: CircularProgressIndicator(),
                  ),
                );
              }

              return Column(
                children: shippingMethods.map((method) {
                  final isSelected = selectedShippingMethod.value?.id == method.id;
                  
                  return Container(
                    margin: const EdgeInsets.only(bottom: 12),
                    child: InkWell(
                      onTap: () {
                        selectedShippingMethod.value = method;
                        Navigator.of(context).pop();
                      },
                      child: Container(
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          border: Border.all(
                            color: isSelected 
                                ? Theme.of(context).primaryColor 
                                : Colors.grey.shade300,
                            width: isSelected ? 2 : 1,
                          ),
                          borderRadius: BorderRadius.circular(12),
                          color: isSelected 
                              ? Theme.of(context).primaryColor.withOpacity(0.05)
                              : Colors.white,
                        ),
                        child: Row(
                          children: [
                            Radio<String>(
                              value: method.id,
                              groupValue: selectedShippingMethod.value?.id,
                              onChanged: (value) {
                                selectedShippingMethod.value = method;
                                Navigator.of(context).pop();
                              },
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Row(
                                    children: [
                                      Text(
                                        method.name,
                                        style: Theme.of(context).textTheme.titleMedium,
                                      ),
                                      if (method.isFreeShip) ...[
                                        const SizedBox(width: 8),
                                        Container(
                                          padding: const EdgeInsets.symmetric(
                                            horizontal: 6,
                                            vertical: 2,
                                          ),
                                          decoration: BoxDecoration(
                                            color: Colors.green,
                                            borderRadius: BorderRadius.circular(4),
                                          ),
                                          child: const Text(
                                            'FREESHIP',
                                            style: TextStyle(
                                              color: Colors.white,
                                              fontSize: 9,
                                              fontWeight: FontWeight.bold,
                                            ),
                                          ),
                                        ),
                                      ],
                                    ],
                                  ),
                                  const SizedBox(height: 4),
                                  Text(
                                    method.description,
                                    style: Theme.of(context).textTheme.bodySmall,
                                  ),
                                  const SizedBox(height: 4),
                                  Text(
                                    'Dự kiến: ${method.estimatedDays}',
                                    style: Theme.of(context).textTheme.bodySmall?.apply(
                                      color: Colors.grey,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                            Text(
                              method.isFreeShip 
                                  ? 'Miễn phí'
                                  : '\$${method.fee.toStringAsFixed(0)}',
                              style: Theme.of(context).textTheme.titleMedium?.apply(
                                color: method.isFreeShip 
                                    ? Colors.green 
                                    : Theme.of(context).primaryColor,
                                fontWeightDelta: 2,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  );
                }).toList(),
              );
            }),
          ],
        ),
      ),
      isDismissible: true,
      enableDrag: true,
    );
  }

  /// Get total order amount including shipping
  double get totalWithShipping {
    final cartTotal = cartController.totalAmount.value;
    final shippingFee = selectedShippingMethod.value?.fee ?? 0;
    return cartTotal + shippingFee;
  }

  /// Get shipping fee
  double get shippingFee {
    return selectedShippingMethod.value?.fee ?? 0;
  }
}
