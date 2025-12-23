import 'dart:convert';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_app/constants/sizes.dart';
import 'package:flutter_app/widgets/appbar/appbar.dart';
import 'package:get/get.dart';
import 'package:flutter_app/shop/controllers/user_controller.dart';
import 'package:flutter_app/shop/services/auth_service.dart';
import 'package:iconsax_flutter/iconsax_flutter.dart';
import 'package:image_picker/image_picker.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:http/http.dart' as http;

class EditProfileScreen extends StatefulWidget {
  const EditProfileScreen({super.key});

  @override
  _EditProfileScreenState createState() => _EditProfileScreenState();
}

class _EditProfileScreenState extends State<EditProfileScreen> {
  final userController = Get.find<UserController>();
  final authService = AuthService();
  final ImagePicker _picker = ImagePicker();

  late final TextEditingController _nameController;
  late final TextEditingController _phoneController;
  late final TextEditingController _emailController;
  late final TextEditingController _dobController;

  bool _isLoading = false;
  XFile? _pickedImage;
  String? _currentAvatarUrl;

  @override
  void initState() {
    super.initState();
    _nameController = TextEditingController(text: userController.fullName.value);
    _phoneController = TextEditingController(text: userController.phone.value);
    _emailController = TextEditingController(text: userController.email.value);
    _dobController = TextEditingController(text: userController.birthDate.value);
    _loadCurrentProfile();
  }

  @override
  void dispose() {
    _nameController.dispose();
    _phoneController.dispose();
    _emailController.dispose();
    _dobController.dispose();
    super.dispose();
  }

  Future<void> _loadCurrentProfile() async {
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('token');
    if (token == null) return;
    final uri = Uri.parse('http://10.0.2.2:8000/api/users/profile/');
    final resp = await http.get(uri, headers: {'Authorization': 'Bearer $token'});
    if (resp.statusCode == 200) {
      final data = json.decode(resp.body);
      setState(() {
        // If your backend wraps data ({"data": {...}}) adjust accordingly
        _currentAvatarUrl = data['avatar'] ?? data['data']?['avatar'];
      });
    }
  }

  Future<void> _pick(ImageSource src) async {
    final img = await _picker.pickImage(source: src, imageQuality: 80);
    if (img != null) setState(() => _pickedImage = img);
  }

  void _showSourcePicker() {
    showModalBottomSheet(
      context: context,
      builder: (ctx) => SafeArea(
        child: Wrap(
          children: [
            ListTile(
              leading: const Icon(Icons.photo_library),
              title: const Text('Chọn từ thư viện'),
              onTap: () {
                Navigator.of(ctx).pop();
                _pick(ImageSource.gallery);
              },
            ),
            ListTile(
              leading: const Icon(Icons.camera_alt),
              title: const Text('Chụp ảnh'),
              onTap: () {
                Navigator.of(ctx).pop();
                _pick(ImageSource.camera);
              },
            ),
            ListTile(
              leading: const Icon(Icons.close),
              title: const Text('Hủy'),
              onTap: () => Navigator.of(ctx).pop(),
            ),
          ],
        ),
      ),
    );
  }

  Future<bool> _upload() async {
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('token');
    if (token == null) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Vui lòng đăng nhập')));
      return false;
    }
    setState(() => _isLoading = true);

    try {
      final uri = Uri.parse('http://10.0.2.2:8000/api/users/avatar/');
      final req = http.MultipartRequest('POST', uri);
      req.headers['Authorization'] = 'Bearer $token';

      if (_pickedImage != null) {
        req.files.add(await http.MultipartFile.fromPath('avatar', File(_pickedImage!.path).path));
      } else {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Chưa chọn ảnh')));
        return false;
      }

      final streamed = await req.send();
      final resp = await http.Response.fromStream(streamed);

      if (streamed.statusCode == 200 || streamed.statusCode == 201) {
        final data = json.decode(resp.body);
        final avatarUrl = data['avatar'] ?? data['data']?['avatar'] ?? '';
        // cập nhật UserController + SharedPreferences
        final userCtrl = userController;
        if (avatarUrl != null && avatarUrl.toString().isNotEmpty) {
          final normalized = avatarUrl.toString().startsWith('/') ? 'http://10.0.2.2:8000${avatarUrl.toString()}' : avatarUrl.toString();
          final ts = DateTime.now().millisecondsSinceEpoch;
          final normalizedWithTs = normalized.contains('?') ? '$normalized&ts=$ts' : '$normalized?ts=$ts';
          userCtrl.avatar.value = normalizedWithTs;
          await prefs.setString('avatar', normalizedWithTs);
          setState(() {}); // đảm bảo rebuild nếu cần
        }
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Cập nhật avatar thành công')));
        return true;
      } else {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Lỗi: ${resp.body}')));
        return false;
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Lỗi: $e')));
      return false;
    } finally {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _handleUpdateProfile() async {
    setState(() => _isLoading = true);

    final result = await authService.updateProfile(
      fullName: _nameController.text,
      phone: _phoneController.text,
      email: _emailController.text,
      birthDate: _dobController.text,
    );

    setState(() => _isLoading = false);

    if (result['success']) {
      // 1. Cập nhật dữ liệu cục bộ
      userController.updateSomeData({
        'full_name': _nameController.text,
        'phone': _phoneController.text,
        'email': _emailController.text,
        'birth_date': _dobController.text,
      });

      // 2. FIX CRASH: Đóng màn hình TRƯỚC (Ngay lập tức, không delay)
      // Việc này giúp GetX dọn dẹp màn hình Edit xong xuôi mới làm việc khác.
      Get.back(result: true);

      // 3. Hiện thông báo SAU (Ở màn hình Profile cũ)
      // Get.snackbar hoạt động toàn cục (Global) nên nó vẫn hiện đè lên màn hình cũ bình thường.
      Get.snackbar(
        'Thành công',
        'Cập nhật hồ sơ thành công',
        snackPosition: SnackPosition.BOTTOM,
        backgroundColor: Colors.green.withOpacity(0.2),
        colorText: Colors.green,
        duration: const Duration(seconds: 2),
        margin: const EdgeInsets.all(10),
        icon: const Icon(Iconsax.verify, color: Colors.green),
      );
    } else {
      // Nếu lỗi thì giữ nguyên màn hình để user sửa
      Get.snackbar(
        'Lỗi',
        result['message'] ?? 'Có lỗi xảy ra',
        snackPosition: SnackPosition.BOTTOM,
        backgroundColor: Colors.red.withOpacity(0.2),
        colorText: Colors.red,
        margin: const EdgeInsets.all(10),
        icon: const Icon(Iconsax.warning_2, color: Colors.red),
      );
    }
  }

  Widget _avatarWidget() {
    final placeholder = CircleAvatar(radius: 40, child: Icon(Icons.person, size: 40));
    if (_pickedImage != null) {
      return CircleAvatar(radius: 40, backgroundImage: FileImage(File(_pickedImage!.path)));
    }
    if (_currentAvatarUrl != null && _currentAvatarUrl!.isNotEmpty) {
      final url = _normalizeUrl(_currentAvatarUrl!);
      return CircleAvatar(radius: 40, backgroundImage: NetworkImage(url));
    }
    return placeholder;
  }

  String _normalizeUrl(String url) {
    if (url.startsWith('/')) {
      return 'http://10.0.2.2:8000$url';
    }
    return url;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: const CusAppbar(title: Text('Edit Profile'), showBackArrow: true),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(AppSizes.defaultSpace),
        child: Column(
          children: [
            // --- Avatar Section ---
            Stack(
              children: [
                Obx(() {
                  final avatarUrl = userController.avatar.value;
                  String? normalized;
                  if (avatarUrl != null && avatarUrl.isNotEmpty) {
                    normalized = avatarUrl.startsWith('/') ? 'http://10.0.2.2:8000$avatarUrl' : avatarUrl;
                  }
                  return CircleAvatar(
                    radius: 50,
                    backgroundColor: Colors.grey.shade200,
                    backgroundImage: (normalized != null && normalized.isNotEmpty)
                        ? NetworkImage(normalized)
                        : const AssetImage('assets/images/user.png') as ImageProvider,
                    onBackgroundImageError: (_, __) {},
                  );
                }),
                Positioned(
                  bottom: 0,
                  right: 0,
                  child: Container(
                    width: 30,
                    height: 30,
                    decoration: BoxDecoration(
                      color: Colors.blue,
                      borderRadius: BorderRadius.circular(100),
                    ),
                    child: IconButton(
                      padding: EdgeInsets.zero,
                      onPressed: () {
                        _showSourcePicker();
                      },
                      icon: const Icon(Iconsax.camera, color: Colors.white, size: 18),
                    ),
                  ),
                )
              ],
            ),
            const SizedBox(height: AppSizes.spaceBtwSections),

            // --- Form Fields ---
            TextFormField(
              controller: _nameController,
              decoration: const InputDecoration(
                labelText: 'Họ và tên',
                prefixIcon: Icon(Iconsax.user),
              ),
            ),
            const SizedBox(height: AppSizes.spaceBtwItems),

            TextFormField(
              controller: _phoneController,
              decoration: const InputDecoration(
                labelText: 'Số điện thoại',
                prefixIcon: Icon(Iconsax.mobile),
              ),
              keyboardType: TextInputType.phone,
            ),
            const SizedBox(height: AppSizes.spaceBtwItems),

            TextFormField(
              controller: _emailController,
              decoration: const InputDecoration(
                labelText: 'Email',
                prefixIcon: Icon(Iconsax.direct),
              ),
              keyboardType: TextInputType.emailAddress,
            ),
            const SizedBox(height: AppSizes.spaceBtwItems),

            // --- Date Picker ---
            TextFormField(
              controller: _dobController,
              readOnly: true,
              decoration: const InputDecoration(
                labelText: 'Ngày sinh',
                prefixIcon: Icon(Iconsax.calendar),
              ),
              onTap: () async {
                DateTime? pickedDate = await showDatePicker(
                  context: context,
                  initialDate: DateTime.now(),
                  firstDate: DateTime(1900),
                  lastDate: DateTime.now(),
                );
                if (pickedDate != null) {
                  String formattedDate = 
                      "${pickedDate.year}-${pickedDate.month.toString().padLeft(2, '0')}-${pickedDate.day.toString().padLeft(2, '0')}";
                  _dobController.text = formattedDate;
                }
              },
            ),

            const SizedBox(height: AppSizes.spaceBtwSections),

            // --- Save Button ---
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: _isLoading ? null : () async {
                  setState(() => _isLoading = true);
                  // nếu user đã chọn ảnh thì upload trước
                  if (_pickedImage != null) {
                    await _upload();
                  }
                  // sau đó cập nhật thông tin text
                  await _handleUpdateProfile();
                  setState(() => _isLoading = false);
                },
                child: _isLoading
                    ? const SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2),
                      )
                    : const Text('Lưu thay đổi'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}