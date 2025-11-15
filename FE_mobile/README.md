# Hướng dẫn chạy project Flutter (FE_mobile)

**Mục đích:** Tài liệu này hướng dẫn cách cài đặt môi trường và chạy project Flutter trong thư mục `FE_mobile` trên Windows (chạy lên Android, Web, hoặc Windows desktop). Nếu muốn build iOS, cần macOS.

**Yêu cầu trước:**
- **Flutter SDK**: cài đặt theo https://flutter.dev (phiên bản stable mới nhất khuyến nghị).
- **Android SDK & Android Studio** (hoặc chỉ cài command-line tools): để chạy trên thiết bị/emulator Android.
- **Visual Studio Code** hoặc **Android Studio**: IDE tiện lợi.
- **Java JDK**: nếu dùng Android build.

**Kiểm tra nhanh môi trường**
Mở terminal (terminal trong VS Code hoặc terminal hệ thống) và chạy các lệnh sau:

```
flutter doctor
```

Giải thích ngắn: `flutter doctor` sẽ báo xanh/đỏ cho Flutter, Android toolchain, Xcode (macOS), và trình biên dịch desktop.

Nếu có lỗi Android license bạn cần chấp nhận:

```
flutter doctor --android-licenses
```

**Lấy dependency**
Trong thư mục `FE_mobile`, chạy (mở terminal trong VS Code hoặc terminal hệ thống):

```
cd "c:\study\PBL6\New folder\PBL6\FE_mobile"
flutter pub get
```

**Chạy trên thiết bị Android (thiết bị thật hoặc emulator)**
1. Bật device hoặc khởi động Android emulator (ví dụ Android Studio AVD Manager).
2. Kiểm tra danh sách thiết bị:

```
flutter devices
```

3. Chạy ứng dụng trên thiết bị mặc định:

```
flutter run
```

Hoặc chỉ định thiết bị cụ thể (id lấy từ `flutter devices`):

```
flutter run -d <deviceId>
```

**Chạy trên Web (Chrome)**

```
flutter run -d chrome
```

**Chạy trên Windows desktop**
Yêu cầu: đã cài Flutter desktop support (Windows) và Visual Studio (MSVC). Kiểm tra bằng `flutter doctor`.

```
flutter run -d windows
```

**Build file xuất bản**
- Android APK (debug): `flutter build apk --debug`
- Android APK (release): `flutter build apk --release`
- App Bundle (Google Play): `flutter build appbundle`
- Web build: `flutter build web`
- Windows exe: `flutter build windows`

Ví dụ build release APK:

```
flutter build apk --release
```

**Lưu ý về `local.properties` và Android SDK**
- Thông thường `local.properties` chứa `sdk.dir` trỏ đến Android SDK. Nếu repository không có file hợp lệ, Flutter/Android Studio sẽ tạo khi build. Trên Windows, `local.properties` thường giống:

```
sdk.dir=C:\Users\<YourUser>\AppData\Local\Android\sdk
```

**Các lệnh hữu ích khác**
- Cài lại packages và clean:

```
flutter clean
flutter pub get
```
- Kiểm tra logs khi chạy app:

```powershell
flutter logs
```

**Xử lý lỗi thường gặp**
- Nếu `flutter doctor` báo thiếu Android SDK: cài Android Studio hoặc command-line tools và cập nhật PATH.
- Nếu bị lỗi plugin native: chạy `flutter pub get` rồi `flutter clean` và thử lại `flutter run`.
- iOS build chỉ chạy trên macOS với Xcode cài sẵn.

**Thông tin dự án**
- Thư mục chính app: `lib/` (mã nguồn Flutter).
- Tài nguyên hình ảnh: `assets/`.
- Android project: `android/`.
- iOS project: `ios/`.

**Gợi ý để dev nhanh**
- Dùng VS Code + extension Flutter để debug với hot reload (phím `r` trong terminal khi `flutter run` đang chạy, hoặc nhấn nút Hot Reload trong IDE).
- Dùng `flutter pub outdated` để kiểm tra package cần nâng cấp.

**Bổ sung assets để test local**

https://drive.google.com/file/d/1_qJABY9a_ip8LYFt3uHn2F2kjQ1ODjyD/view?usp=sharing

vào link tải file về và giải nén sau đó thay thế folder assets trong project

---






