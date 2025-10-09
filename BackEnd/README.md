HƯỚNG DẪN THIẾT LẬP VÀ KIỂM THỬ THANH TOÁN (VNPAY & PAYPAL)
A. Chuẩn bị ngrok
Cài đặt & Xác thực: Tải xuống và cài đặt ngrok, sau đó chạy lệnh xác thực token của bạn.

Chạy ngrok: Chạy lệnh để tạo tunnel về cổng Django:

Bash

ngrok http 8000
Lấy URL: Ngrok sẽ cung cấp một URL công cộng (ví dụ: https://abc.ngrok-free.dev).

B.  Cập nhật Code Django
Thay thế các hằng số URL trong code của bạn bằng địa chỉ ngrok vừa lấy được:

Trong payments/views.py: Cập nhật NGROK_HOST, VNP_RETURN, và VNP_IPN_URL.

Khởi chạy Ngrok
ngrok http 8000

Trong settings.py: Thêm host ngrok vào ALLOWED_HOSTS (ví dụ: ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'abc-xyz.ngrok-free.dev']).

C. Cấu hình VNPAY Admin 
Đăng kí tài khoản test vnpay merchant
Đăng nhập vào trang quản trị VNPAY Sandbox và cấu hình IPN URL chính thức:

$$\text{IPN URL: https://[URL_NGROK_CỦA_BẠN]/payments/vnpay-ipn/}$$
Thay thế VNP_TMN VNP_SECRET trong file payment/views bằng mã vừa mới nhận được


B. PayPal (Execute API)
Tạo tk Paypal sandbox
Tạo app sandbox mới
Thay thế client_id và client_secret trong payment/views bằng mã mới
Tạo Account sandbox business và personal để test
