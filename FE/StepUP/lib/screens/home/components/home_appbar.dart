import 'package:flutter/material.dart';
import 'package:flutter_app/screens/chatbox/chatbox.dart';
import 'package:flutter_app/screens/notification/notification_screen.dart';
import 'package:flutter_app/shop/controllers/notification_controller.dart';
import 'package:flutter_app/widgets/appbar/appbar.dart';
import 'package:iconsax_flutter/iconsax_flutter.dart';
import 'package:get/get.dart';

class HomeAppBar extends StatelessWidget {
  const HomeAppBar({
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    final notificationController = Get.put(NotificationController());
    
    return CusAppbar(
      showCart: true,
      iconColor: Colors.white,
      title: Column(
        crossAxisAlignment: CrossAxisAlignment.start, // Căn lề trái cho title
        children: [
          Text(
            "Xin chào!",
            style: Theme.of(context)
                .textTheme
                .headlineMedium!
                .copyWith(color: Colors.white, fontWeight: FontWeight.bold),
          ),
          // Bạn có thể thêm 1 dòng text nhỏ hơn ở đây nếu muốn
          // Text(
          //   "username@gmail.com",
          //   style: Theme.of(context)
          //       .textTheme
          //       .labelMedium!
          //       .copyWith(color: Colors.white),
          // ),
        ],
      ),
      actions: [
        // 2. Bổ sung Icon Button cho Chat
        IconButton(
          icon: const Icon(Iconsax.message, color: Colors.white),
          onPressed: () {
            // Xử lý khi nhấn vào biểu tượng chat
            Get.to(() => const MyChatScreen());
          },
        ),
        
        // Icon thông báo 
        Stack(
          children: [
            IconButton(
              icon: const Icon(Icons.notifications, color: Colors.white),
              onPressed: () {
                Get.to(() => const NotificationScreen());
              },
            ),
            Obx(() {
              if (notificationController.unreadCount.value > 0) {
                return Positioned(
                  right: 11,
                  top: 11,
                  child: Container(
                    padding: const EdgeInsets.all(2),
                    decoration: BoxDecoration(
                      color: Colors.red,
                      borderRadius: BorderRadius.circular(6),
                    ),
                    constraints: const BoxConstraints(
                      minWidth: 14,
                      minHeight: 14,
                    ),
                    child: Text(
                      '${notificationController.unreadCount.value}',
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 8,
                      ),
                      textAlign: TextAlign.center,
                    ),
                  ),
                );
              }
              return const SizedBox.shrink();
            })
          ],
        )
      ],
    );
  }
}