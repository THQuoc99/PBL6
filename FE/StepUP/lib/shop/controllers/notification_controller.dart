import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class NotificationModel {
  final int id;
  final String title;
  final String message;
  final String type; // order, promotion, system, shop_follow, platform
  final bool isRead;
  final DateTime createdAt;
  final int? orderId;
  final int? shopId;
  final String? shopName;
  
  NotificationModel({
    required this.id,
    required this.title,
    required this.message,
    required this.type,
    required this.isRead,
    required this.createdAt,
    this.orderId,
    this.shopId,
    this.shopName,
  });
  
  factory NotificationModel.fromJson(Map<String, dynamic> json) {
    return NotificationModel(
      id: json['id'],
      title: json['title'],
      message: json['message'],
      type: json['type'],
      isRead: json['is_read'],
      createdAt: DateTime.parse(json['created_at']),
      orderId: json['order_id'],      shopId: json['shop_id'],
      shopName: json['shop_name'],    );
  }
}

class NotificationController extends GetxController {
  final notifications = <NotificationModel>[].obs;
  final isLoading = false.obs;
  final unreadCount = 0.obs;
  
  final String baseUrl = "http://10.0.2.2:8000/api";
  
  @override
  void onInit() {
    super.onInit();
    fetchNotifications();
  }
  
  Future<void> fetchNotifications() async {
    try {
      isLoading.value = true;
      
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('token');
      
      if (token == null) {
        return;
      }
      
      final response = await http.get(
        Uri.parse('$baseUrl/notifications/'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
      );
      
      if (response.statusCode == 200) {
        final List<dynamic> data = jsonDecode(utf8.decode(response.bodyBytes));
        notifications.value = data.map((json) => NotificationModel.fromJson(json)).toList();
        
        // Calculate unread count
        unreadCount.value = notifications.where((n) => !n.isRead).length;
      }
    } catch (e) {
      print("Error fetching notifications: $e");
    } finally {
      isLoading.value = false;
    }
  }
  
  Future<void> markAsRead(int notificationId) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('token');
      
      if (token == null) return;
      
      final response = await http.post(
        Uri.parse('$baseUrl/notifications/$notificationId/mark-read/'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
      );
      
      if (response.statusCode == 200) {
        // Update local state
        final index = notifications.indexWhere((n) => n.id == notificationId);
        if (index != -1) {
          final notification = notifications[index];
          notifications[index] = NotificationModel(
            id: notification.id,
            title: notification.title,
            message: notification.message,
            type: notification.type,
            isRead: true,
            createdAt: notification.createdAt,
            orderId: notification.orderId,
          );
          notifications.refresh();
          unreadCount.value = notifications.where((n) => !n.isRead).length;
        }
      }
    } catch (e) {
      print("Error marking notification as read: $e");
    }
  }
  
  Future<void> markAllAsRead() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('token');
      
      if (token == null) return;
      
      final response = await http.post(
        Uri.parse('$baseUrl/notifications/mark-all-read/'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
      );
      
      if (response.statusCode == 200) {
        await fetchNotifications();
      }
    } catch (e) {
      print("Error marking all as read: $e");
    }
  }
  
  Future<void> deleteNotification(int notificationId) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('token');
      
      if (token == null) return;
      
      final response = await http.delete(
        Uri.parse('$baseUrl/notifications/$notificationId/'),
        headers: {
          'Authorization': 'Bearer $token',
        },
      );
      
      if (response.statusCode == 204) {
        notifications.removeWhere((n) => n.id == notificationId);
        unreadCount.value = notifications.where((n) => !n.isRead).length;
      }
    } catch (e) {
      print("Error deleting notification: $e");
    }
  }
}
