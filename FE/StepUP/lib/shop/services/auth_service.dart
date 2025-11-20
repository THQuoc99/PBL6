import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'package:get/get.dart';
import 'package:flutter_app/shop/controllers/user_controller.dart';

class AuthService {
  final String baseUrl = "http://10.0.2.2:8000";
  
  // Tìm UserController (đảm bảo controller này đã được Get.put ở main hoặc binding)
  final UserController userController = Get.put(UserController());

  // Hàm tiện ích lưu token
  Future<void> saveToken(String token) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('token', token);
  }

  // 3. HÀM ĐĂNG NHẬP
  Future<Map<String, dynamic>> login(String username, String password) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/users/login/'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({'username': username, 'password': password}),
      );

      // Decode UTF8 để tránh lỗi font nếu backend trả về tiếng Việt
      final data = json.decode(utf8.decode(response.bodyBytes));

      if (response.statusCode == 200) {
        // Kiểm tra success hoặc nếu có token là thành công
        if (data['success'] == true || data.containsKey('token') || data.containsKey('access')) {
          // Lấy token (support cả key 'token' và 'access' của SimpleJWT)
          String token = data['token'] ?? data['access'];
          
      
          await saveToken(token);
          try {
             // Giả sử data có chứa thông tin user, nếu không hàm saveUser cần handle null
             await userController.saveUser(data); 
          } catch (e) {
            print("Lỗi lưu user controller: $e");
          }
          
          return {'success': true, 'message': 'Đăng nhập thành công', 'data': data};
        }
      }

      if (response.statusCode == 401) {
         return {'success': false, 'message': 'Sai tên đăng nhập hoặc mật khẩu.'};
      }
      
      return {'success': false, 'message': data['message'] ?? data['detail'] ?? 'Lỗi không xác định.'};

    } catch (e) {
      return {'success': false, 'message': 'Lỗi kết nối: $e'};
    }
  }

  // 4. HÀM ĐĂNG KÝ
  Future<Map<String, dynamic>> register({
    required String username,
    required String email,
    required String password,
    required String password2,
    required String fullName,
    required String phone,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/users/register/'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'username': username,
          'email': email,
          'password': password,
          'password2': password2,
          'full_name': fullName,
          'phone': phone,
          'role': 'buyer'
        }),
      );
      
      final data = json.decode(utf8.decode(response.bodyBytes));

      if (response.statusCode == 201) {
         if (data['success'] == true || data.containsKey('token') || data.containsKey('access')) {
          String token = data['token'] ?? data['access'];
          await saveToken(token);
          
          try {
            await userController.saveUser(data);
          } catch(e) {
             print("Lỗi lưu user controller: $e");
          }
          return {'success': true, 'message': 'Đăng ký thành công'};
        }
      }
      
      // Xử lý lỗi validation (400)
      String errorMessage = data.toString();
      // Trích xuất lỗi cụ thể nếu backend trả về dạng {"username": ["Lỗi..."]}
      if (data is Map) {
         if (data['username'] != null) errorMessage = data['username'][0];
         else if (data['email'] != null) errorMessage = data['email'][0];
         else if (data['message'] != null) errorMessage = data['message'];
      }
      
      return {'success': false, 'message': errorMessage};

    } catch (e) {
      return {'success': false, 'message': 'Lỗi kết nối: $e'};
    }
  }

  // 5. HÀM ĐĂNG XUẤT
  Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('token');
    // Xóa thông tin User khỏi Controller
    // userController.clearUser(); // Bỏ comment nếu hàm này có trong controller
  }

  // 6. CẬP NHẬT PROFILE
   Future<Map<String, dynamic>> updateProfile({
    String? fullName,
    String? phone,
    String? email,
  }) async {
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('token');
    
    if (token == null) {
      return {'success': false, 'message': 'Bạn chưa đăng nhập.'};
    }

    try {
      // Xây dựng body chỉ với các trường có giá trị (không gửi null)
      Map<String, String> body = {};
      if (fullName != null) body['full_name'] = fullName;
      if (phone != null) body['phone'] = phone;
      if (email != null) body['email'] = email;

      final response = await http.patch( // Sử dụng PATCH
        Uri.parse('$baseUrl/api/users/profile/'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token', // Gửi token
        },
        body: json.encode(body),
      );

      final data = json.decode(utf8.decode(response.bodyBytes)); 

      if (response.statusCode == 200) {
        // Cập nhật lại UserController với dữ liệu mới
        // Backend trả về {full_name, phone, email}
        // await userController.updateSomeData(data); // Bỏ comment nếu hàm này có
        
        return {'success': true, 'message': 'Cập nhật thành công!'};
      }
      
      return {'success': false, 'message': data.toString()};

    } catch (e) {
      print('Lỗi cập nhật profile: $e');
      return {'success': false, 'message': 'Lỗi kết nối: $e'};
    }
  }
}