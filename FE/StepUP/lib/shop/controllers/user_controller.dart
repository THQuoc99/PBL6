import 'package:get/get.dart';
import 'package:shared_preferences/shared_preferences.dart';

class UserController extends GetxController {
  // Biến 'Rx' (Reactive) sẽ tự động cập nhật UI khi giá trị thay đổi
  final fullName = 'Tên của bạn'.obs;
  final email = 'email@cuaban.com'.obs;
  final username = ''.obs;
  final phone = ''.obs;  
  final userID = ''.obs;
  
  // Dùng SharedPreferences để lưu/tải dữ liệu
  final Future<SharedPreferences> _prefs = SharedPreferences.getInstance();

  @override
  void onInit() {
    super.onInit();
    loadUserData(); // Tải dữ liệu khi controller khởi chạy
  }

  // Hàm lưu thông tin user khi đăng nhập/đăng ký
  Future<void> saveUser(Map<String, dynamic> userData) async {
    final SharedPreferences prefs = await _prefs;
    
    String nameToSave = userData['full_name'] ?? 'Người dùng mới';
    String emailToSave = userData['email'] ?? 'Không có email';
    String usernameToSave = userData['username'] ?? '';
    String phoneToSave = userData['phone'] ?? ''; 
    String userIDToSave = userData['user_id']?.toString() ?? ''; 
    
    await prefs.setString('fullName', nameToSave);
    await prefs.setString('email', emailToSave);
    await prefs.setString('username', usernameToSave);
    await prefs.setString('phone', phoneToSave);
    await prefs.setString('userID', userIDToSave);
    // Cập nhật trạng thái (State)
    fullName.value = nameToSave;
    email.value = emailToSave;
    username.value = usernameToSave;
    phone.value = phoneToSave;
    userID.value = userIDToSave;
  }

  // Hàm tải dữ liệu khi mở lại ứng dụng
  Future<void> loadUserData() async {
    final SharedPreferences prefs = await _prefs;
    fullName.value = prefs.getString('fullName') ?? 'Tên của bạn';
    email.value = prefs.getString('email') ?? 'email@cuaban.com';
    username.value = prefs.getString('username') ?? '';
    phone.value = prefs.getString('phone') ?? '';
    userID.value = prefs.getString('userID') ?? '';
  }

  // Hàm xóa dữ liệu khi đăng xuất
  Future<void> clearUser() async {
    final SharedPreferences prefs = await _prefs;
    await prefs.remove('fullName');
    await prefs.remove('email');
    await prefs.remove('username');
    await prefs.remove('phone');
    await prefs.remove('userID');
    

    // Reset về giá trị mặc định
    fullName.value = 'Tên của bạn';
    email.value = 'email@cuaban.com';
    username.value = '';
    phone.value = '';
    userID.value = '';
  }

  Future<void> updateSomeData(Map<String, dynamic> updatedData) async {
    final SharedPreferences prefs = await _prefs;

    // Cập nhật từng trường nếu nó tồn tại trong phản hồi
    if (updatedData['full_name'] != null) {
      String nameToSave = updatedData['full_name'];
      await prefs.setString('fullName', nameToSave);
      fullName.value = nameToSave;
    }
    if (updatedData['email'] != null) {
      String emailToSave = updatedData['email'];
      await prefs.setString('email', emailToSave);
      email.value = emailToSave;
    }
    if (updatedData['phone'] != null) {
      String phoneToSave = updatedData['phone'];
      await prefs.setString('phone', phoneToSave);
      phone.value = phoneToSave;
    }
  }
}