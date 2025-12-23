import 'dart:convert';
import 'package:get/get.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../models/voucher_model.dart';
import 'package:collection/collection.dart';
import 'package:flutter_app/shop/controllers/shipping_controller.dart';
import 'dart:async';

class VoucherController extends GetxController {
  final vouchers = <VoucherModel>[].obs;
  final myVouchers = <VoucherModel>[].obs;
  final isLoading = false.obs;
  // selectedVoucher: platform voucher (or generic non-shipping voucher)
  final selectedVoucher = Rxn<VoucherModel>();
  // selectedShipping: voucher specifically for shipping (freeship or shipping discount)
  final selectedShipping = Rxn<VoucherModel>();
  // selectedStoreVouchers: map of storeId -> voucher selected for that store
  final selectedStoreVouchers = <String, VoucherModel>{}.obs;
  final hasAutoApplied = false.obs;

  final String baseUrl = 'http://10.0.2.2:8000/api/discounts';
  final Map<String, int> reservations = {}; // code -> reservation_id

  @override
  void onInit() {
    super.onInit();
    fetchVouchers();
    fetchMyWallet();
  }

  Future<void> fetchVouchers() async {
    try {
      isLoading.value = true;
      final response = await http.get(Uri.parse('$baseUrl/'));
      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(utf8.decode(response.bodyBytes));
        vouchers.assignAll(data.map((e) => VoucherModel.fromJson(e)).toList());
      }
    } catch (e) {
      print('Error fetching vouchers: $e');
    } finally {
      isLoading.value = false;
    }
  }

  Future<void> fetchMyWallet() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('token');
      if (token == null) return;
      final response = await http.get(Uri.parse('$baseUrl/my-wallet/'), headers: {'Authorization': 'Bearer $token'});
      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(utf8.decode(response.bodyBytes));
        // API returns uservoucher objects; extract voucher
        myVouchers.assignAll(data.map((e) {
          final voucherJson = e['voucher'] ?? e;
          return VoucherModel.fromJson(voucherJson);
        }).toList());
      }
    } catch (e) {
      print('Error fetching my wallet: $e');
    }
  }

  Future<Map<String, dynamic>?> checkVoucher(String code, double? orderAmount, {String? storeId, String target = 'order', double? shippingFee}) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('token');
      final body = {
        'code': code,
        'order_amount': orderAmount,
      };
      if (storeId != null) body['store_id'] = storeId;
      if (target != null) body['target'] = target;
      if (shippingFee != null) body['shipping_fee'] = shippingFee;

      final response = await http.post(Uri.parse('$baseUrl/check/'), headers: token != null ? {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token'
      } : {'Content-Type': 'application/json'}, body: json.encode(body));

      if (response.statusCode == 200) {
        final data = json.decode(utf8.decode(response.bodyBytes));
        return data as Map<String, dynamic>;
      }
      return null;
    } catch (e) {
      print('checkVoucher error: $e');
      return null;
    }
  }

  Future<int?> reserveVoucher(String code, {int seconds = 300}) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('token');
      final response = await http.post(Uri.parse('$baseUrl/reserve/'), headers: token != null ? {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token'
      } : {'Content-Type': 'application/json'}, body: json.encode({'code': code, 'seconds': seconds}));

      if (response.statusCode == 201) {
        final data = json.decode(utf8.decode(response.bodyBytes));
        final rid = data['reservation_id'];
        if (rid != null) {
          reservations[code] = rid as int;
          return rid as int;
        }
      }
      return null;
    } catch (e) {
      print('reserveVoucher error: $e');
      return null;
    }
  }

  Future<bool> releaseReservation(int reservationId) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('token');
      final response = await http.post(Uri.parse('$baseUrl/release/'), headers: token != null ? {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token'
      } : {'Content-Type': 'application/json'}, body: json.encode({'reservation_id': reservationId}));

      if (response.statusCode == 200) {
        // remove from map
        reservations.removeWhere((k, v) => v == reservationId);
        return true;
      }
      return false;
    } catch (e) {
      print('releaseReservation error: $e');
      return false;
    }
  }

  Future<void> releaseAllReservations() async {
    final entries = Map<String, int>.from(reservations);
    for (final rid in entries.values) {
      await releaseReservation(rid);
    }
    reservations.clear();
  }

  /// Auto-apply best vouchers per store, platform and shipping.
  /// Returns a mapping {"<storeId>": "CODE", "platform": "CODE", "shipping": "CODE"}
  Future<Map<String, String>> autoApplyBest(Map<String, double> storeSubtotals) async {
    final result = <String, String>{};
    final candidates = <VoucherModel>[];
    candidates.addAll(myVouchers);
    candidates.addAll(vouchers.where((v) => !myVouchers.any((m) => m.code == v.code)));

    // For each store, find best store-type voucher
    for (final entry in storeSubtotals.entries) {
      final storeId = entry.key;
      final subtotal = entry.value;
      VoucherModel? best;
      double bestDiscount = 0.0;

      final storeCandidates = candidates.where((v) => v.type == 'store' && (v.applicableStores == null || v.applicableStores!.contains(int.tryParse(storeId) ?? -1))).toList();

      final futures = storeCandidates.map((v) async {
        final res = await checkVoucher(v.code, subtotal, storeId: storeId);
        if (res != null && res['valid'] == true) {
          final discount = (res['discount_amount'] is num) ? (res['discount_amount'] as num).toDouble() : double.tryParse('${res['discount_amount']}') ?? 0.0;
          return {'code': v.code, 'discount': discount};
        }
        return null;
      }).toList();

      final checks = await Future.wait(futures);
      for (final c in checks) {
        if (c != null) {
          final discount = c['discount'] as double;
          if (discount > bestDiscount) {
            bestDiscount = discount;
            best = vouchers.firstWhereOrNull((x) => x.code == c['code']) ?? myVouchers.firstWhereOrNull((x) => x.code == c['code']);
          }
        }
      }

      if (best != null) result[storeId] = best.code;
    }

    // Platform: compute remaining total
    double total = 0.0;
    storeSubtotals.forEach((k, v) => total += v);
    double appliedStoreDiscount = 0.0;
    for (final code in result.values) {
      final vmodel = candidates.firstWhereOrNull((c) => c.code == code);
      if (vmodel != null) {
        final check = await checkVoucher(vmodel.code, total);
        if (check != null && check['valid'] == true) {
          appliedStoreDiscount += (check['discount_amount'] is num) ? (check['discount_amount'] as num).toDouble() : double.tryParse('${check['discount_amount']}') ?? 0.0;
        }
      }
    }
    final remaining = total - appliedStoreDiscount;

    VoucherModel? bestPlatform;
    double bestPlatformDiscount = 0.0;
    final platformCandidates = candidates.where((v) => v.type == 'platform').toList();
    final platformFutures = platformCandidates.map((v) async {
      final res = await checkVoucher(v.code, remaining);
      if (res != null && res['valid'] == true) {
        final discount = (res['discount_amount'] is num) ? (res['discount_amount'] as num).toDouble() : double.tryParse('${res['discount_amount']}') ?? 0.0;
        return {'code': v.code, 'discount': discount};
      }
      return null;
    }).toList();

    final pchecks = await Future.wait(platformFutures);
    for (final c in pchecks) {
      if (c != null) {
        final discount = c['discount'] as double;
        if (discount > bestPlatformDiscount) {
          bestPlatformDiscount = discount;
          bestPlatform = candidates.firstWhereOrNull((x) => x.code == c['code']);
        }
      }
    }

    if (bestPlatform != null) result['platform'] = bestPlatform.code;

    // Shipping: try to find voucher that reduces shipping fee the most
    try {
        final ShippingController? shippingController = Get.isRegistered<ShippingController>()
          ? Get.find<ShippingController>()
          : null;
      double shippingFee = 0.0;
      try {
        if (shippingController != null) shippingFee = shippingController.shippingFee;
      } catch (_) {}
      VoucherModel? bestShipping;
      double bestShippingReduction = 0.0;

      final shippingFutures = candidates.map((v) async {
        // call checkVoucher with target=shipping so backend validates appropriately
        final check = await checkVoucher(v.code, null, target: 'shipping', shippingFee: shippingFee);
        if (check == null || check['valid'] != true) return null;
        // Prefer backend-calculated discount_amount for accuracy
        double reduction = 0.0;
        final dam = check['discount_amount'];
        if (dam != null) {
          if (dam is num) reduction = dam.toDouble();
          else reduction = double.tryParse(dam.toString()) ?? 0.0;
        } else {
          // fallback to client-side heuristic
          if (v.isFreeShipping) {
            reduction = shippingFee;
          } else if (v.discountType == 'fixed') {
            reduction = v.discountValue;
            if (reduction > shippingFee) reduction = shippingFee;
          } else {
            reduction = shippingFee * (v.discountValue / 100.0);
            if (v.maxDiscount != null && reduction > v.maxDiscount!) reduction = v.maxDiscount!;
          }
        }
        return {'code': v.code, 'reduction': reduction};
      }).toList();

      final schecks = await Future.wait(shippingFutures);
      for (final sc in schecks) {
        if (sc != null) {
          final reduction = sc['reduction'] as double;
          if (reduction > bestShippingReduction) {
            bestShippingReduction = reduction;
            bestShipping = candidates.firstWhereOrNull((x) => x.code == sc['code']);
          }
        }
      }
      if (bestShipping != null) result['shipping'] = bestShipping.code;
    } catch (_) {}

    return result;
  }

  /// Try auto-applying once per session/view. Calculates shipping fee first if available.
  Future<void> tryAutoApply(Map<String, double> storeSubtotals) async {
    if (hasAutoApplied.value) return;
    hasAutoApplied.value = true;
    try {
      // Wait briefly for vouchers/myVouchers to be fetched to avoid racing before data loads
      int attempts = 0;
      // Wait up to ~3s for vouchers/myVouchers to populate
      while ((vouchers.isEmpty && myVouchers.isEmpty) && attempts < 30) {
        await Future.delayed(const Duration(milliseconds: 100));
        attempts++;
      }

      final ShippingController? shippingController = Get.isRegistered<ShippingController>() ? Get.find<ShippingController>() : null;
      if (shippingController != null) {
        try {
          await shippingController.calculateShippingFee();
        } catch (_) {}
      }
      final map = await autoApplyBest(storeSubtotals);
      if (map.isEmpty) return;
      // apply platform
      if (map.containsKey('platform')) {
        final pcode = map['platform'];
        if (pcode != null) {
          final vm = vouchers.firstWhereOrNull((v) => v.code == pcode) ?? myVouchers.firstWhereOrNull((v) => v.code == pcode);
          if (vm != null) selectedVoucher.value = vm;
        }
      }
      // shipping
      if (map.containsKey('shipping')) {
        final scode = map['shipping'];
        if (scode != null) {
          final sm = vouchers.firstWhereOrNull((v) => v.code == scode) ?? myVouchers.firstWhereOrNull((v) => v.code == scode);
          if (sm != null) selectedShipping.value = sm;
        }
      }
      for (final entry in map.entries) {
        final key = entry.key;
        if (key == 'platform' || key == 'shipping') continue;
        final code = entry.value;
        final vm = vouchers.firstWhereOrNull((v) => v.code == code) ?? myVouchers.firstWhereOrNull((v) => v.code == code);
        if (vm != null) selectedStoreVouchers[key] = vm;
      }
      selectedStoreVouchers.refresh();
    } catch (e) {
      print('tryAutoApply error: $e');
    }
  }

  Future<bool> saveVoucher(String code) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('token');
      if (token == null) return false;
      final response = await http.post(Uri.parse('$baseUrl/save/'), headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      }, body: json.encode({'code': code}));

      if (response.statusCode == 201 || response.statusCode == 200) {
        await fetchMyWallet();
        // If user saved this voucher, optionally set as selected (platform by default)
        final savedVoucher = vouchers.firstWhereOrNull((v) => v.code == code);
        if (savedVoucher != null) {
          if (savedVoucher.isFreeShipping) {
            selectedShipping.value = savedVoucher;
          } else if (savedVoucher.type == 'platform') {
            selectedVoucher.value = savedVoucher;
          } else {
            // store voucher: assign to all stores by default (checkout will refine)
            // store id keys are strings; use seller id if present
            if (savedVoucher.applicableStores != null && savedVoucher.applicableStores!.isNotEmpty) {
              for (final s in savedVoucher.applicableStores!) {
                selectedStoreVouchers['$s'] = savedVoucher;
              }
              selectedStoreVouchers.refresh();
            }
          }
        }
        return true;
      }
      return false;
    } catch (e) {
      print('Error saving voucher: $e');
      return false;
    }
  }

  void selectVoucher(VoucherModel? v) {
    selectedVoucher.value = v;
  }

  void selectShippingVoucher(VoucherModel? v) {
    selectedShipping.value = v;
  }

  void setStoreVoucher(String storeId, VoucherModel? v) {
    if (v == null) {
      selectedStoreVouchers.remove(storeId);
    } else {
      selectedStoreVouchers[storeId] = v;
    }
    selectedStoreVouchers.refresh();
  }

  void clearAllSelections() {
    selectedVoucher.value = null;
    selectedShipping.value = null;
    selectedStoreVouchers.clear();
    selectedStoreVouchers.refresh();
  }
}
