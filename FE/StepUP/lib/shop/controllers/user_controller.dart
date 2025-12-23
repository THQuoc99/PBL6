import 'package:get/get.dart';
import 'package:shared_preferences/shared_preferences.dart';

class UserController extends GetxController {
  final fullName = 'Tên của bạn'.obs;
  final email = 'email@cuaban.com'.obs;
  final username = ''.obs;
  final phone = ''.obs;
  final userID = ''.obs;
  final avatar = ''.obs; // Mới
  final birthDate = ''.obs; // Mới
  
  final Future<SharedPreferences> _prefs = SharedPreferences.getInstance();

  @override
  void onInit() {
    super.onInit();
    loadUserData();
  }

  Future<void> saveUser(Map<String, dynamic> userData) async {
    final SharedPreferences prefs = await _prefs;
    
    String nameToSave = userData['full_name'] ?? 'Người dùng mới';
    String emailToSave = userData['email'] ?? '';
    String usernameToSave = userData['username'] ?? '';
    String phoneToSave = userData['phone'] ?? ''; 
    String userIDToSave = userData['user_id']?.toString() ?? ''; 
    String avatarToSave = userData['avatar'] ?? '';
    String birthDateToSave = userData['birth_date'] ?? '';
    
    await prefs.setString('fullName', nameToSave);
    await prefs.setString('email', emailToSave);
    await prefs.setString('username', usernameToSave);
    await prefs.setString('phone', phoneToSave);
    await prefs.setString('userID', userIDToSave);
    await prefs.setString('avatar', avatarToSave);
    await prefs.setString('birthDate', birthDateToSave);

    fullName.value = nameToSave;
    email.value = emailToSave;
    username.value = usernameToSave;
    phone.value = phoneToSave;
    userID.value = userIDToSave;
    avatar.value = avatarToSave;
    birthDate.value = birthDateToSave;
  }

  Future<void> loadUserData() async {
    final SharedPreferences prefs = await _prefs;
    fullName.value = prefs.getString('fullName') ?? 'Tên của bạn';
    email.value = prefs.getString('email') ?? 'email@cuaban.com';
    username.value = prefs.getString('username') ?? '';
    phone.value = prefs.getString('phone') ?? '';
    userID.value = prefs.getString('userID') ?? '';
    avatar.value = prefs.getString('avatar') ?? '';
    birthDate.value = prefs.getString('birthDate') ?? '';
  }

  Future<void> clearUser() async {
    final SharedPreferences prefs = await _prefs;
    await prefs.clear(); // Xóa sạch luôn cho nhanh

    fullName.value = 'Tên của bạn';
    email.value = 'email@cuaban.com';
    username.value = '';
    phone.value = '';
    userID.value = '';
    avatar.value = '';
    birthDate.value = '';
  }
  
  Future<void> updateSomeData(Map<String, dynamic> updatedData) async {
    final SharedPreferences prefs = await _prefs;

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

    if (updatedData['birth_date'] != null) {
      String birthDateToSave = updatedData['birth_date'];
      await prefs.setString('birthDate', birthDateToSave);
      birthDate.value = birthDateToSave;
    }

    // MỚI: cập nhật avatar nếu backend trả về
    if (updatedData['avatar'] != null) {
      String avatarToSave = updatedData['avatar'];
      await prefs.setString('avatar', avatarToSave);
      avatar.value = avatarToSave;
    }
  }
}
