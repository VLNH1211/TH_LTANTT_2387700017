### Họ và Tên: Võ Lê Nhật Hoàng
### MSSV: 2387700017
### Lớp: 23DATA1
# BÀI 4 - PHẦN 2: JWT SECURITY TOOLS & API GATEWAY (BẢO MẬT TOKEN & CỔNG API)

---

## 1. Giới thiệu chức năng
Bộ công cụ **JWTSecure** cung cấp giải pháp toàn diện về kiểm thử, phân tích lỗ hổng và quản lý vòng đời xác thực bằng JSON Web Token (**JWT**) kết hợp chuẩn **OAuth 2.0**:

1. **APIGateway (`api_gateway/gateway.py`)**:
   - Triển khai cổng API backend sử dụng **Flask**.
   - Bảo vệ endpoint nhạy cảm `/protected` bằng xác thực tiêu đề HTTP: `Authorization: Bearer <access_token>`.
   - Nếu token hợp lệ: Giải mã payload và trả về `{"message": "Access granted", "user": "<sub_claim>"}` kèm mã trạng thái `200`.
   - Nếu token không hợp lệ hoặc thiếu: Trả về `{"message": "Access denied"}` kèm mã lỗi `401`.

2. **JWTCracker (`jwt_cracker/cracker.py`)**:
   - Công cụ kiểm tra độ mạnh của khóa bí mật (secret key) dùng ký token thuật toán **HS256**.
   - Tối ưu hóa hiệu năng tấn công brute-force từ điển (wordlist dictionary attack) bằng kỹ thuật xử lý đa luồng với `ThreadPoolExecutor(max_workers=10)`.

3. **JWTValidator (`jwt_validator/validator.py`)**:
   - Thẩm định toàn diện tính an toàn của JWT.
   - Kiểm tra tính toàn vẹn của chữ ký số (`InvalidSignatureError`).
   - Kiểm tra thời gian hết hạn (`ExpiredSignatureError`).
   - Xử lý các ngoại lệ cấu trúc token (`InvalidTokenError`).

4. **OAuthClient (`oauth_client/client.py`)**:
   - Triển khai máy khách tuân thủ quy trình chuẩn **Authorization Code Flow** của **OAuth 2.0**:
     - `get_auth_url()`: Tạo URL điều hướng người dùng tới máy chủ xác thực với các tham số `response_type=code`, `client_id`, `redirect_uri`, `scope`.
     - `get_token()`: Gửi yêu cầu POST trao đổi `code` lấy `access_token` từ token endpoint.

5. **TokenManager (`token_manager/manager.py`)**:
   - Quản lý vòng đời token xác thực:
     - `generate_tokens()`: Phát hành đồng thời cặp **Access Token** (hạn dùng ngắn 15 phút) và **Refresh Token** (hạn dùng dài 24 giờ).
     - `refresh_access_token()`: Kiểm tra tính hợp lệ của Refresh Token để tự động cấp mới Access Token mà không bắt người dùng phải đăng nhập lại.

---

## 2. Cấu trúc thư mục
```text
jwt-security-tools/
├── api_gateway/                 # Cổng API Gateway
│   ├── __init__.py
│   └── gateway.py               # Lắng nghe tại cổng 5000, bảo vệ endpoint /protected
├── jwt_cracker/                 # Công cụ brute-force khóa bí mật
│   ├── __init__.py
│   └── cracker.py
├── jwt_validator/               # Công cụ thẩm định chữ ký và hạn dùng JWT
│   ├── __init__.py
│   └── validator.py
├── oauth_client/                # Client triển khai luồng OAuth 2.0
│   ├── __init__.py
│   └── client.py
├── token_manager/               # Quản lý phát hành và làm mới Token
│   ├── __init__.py
│   └── manager.py
├── tests/                       # Bộ kiểm thử tự động với Pytest
│   ├── __init__.py
│   ├── test_api_gateway.py      # Test endpoint với token hợp lệ & không hợp lệ
│   ├── test_cracker.py          # Test brute-force dò tìm secret
│   ├── test_oauth_client.py     # Test sinh URL xác thực OAuth 2.0
│   ├── test_token_manager.py    # Test cấp phát & refresh token
│   └── test_validator.py        # Test kiểm tra chữ ký và hạn dùng
├── images/                      # Hình ảnh kết quả thực nghiệm của phần 2
├── main.py                      # Khởi chạy API Gateway & phát hành Token cho user "Hoang"
├── pytest.ini                   # Cấu hình Pytest
├── requirements.txt             # Thư viện phụ thuộc (PyJWT, requests, flask, pytest)
└── README.md                    # Tài liệu báo cáo chi tiết Phần 2
```

---

## 3. Hình ảnh kết quả thực nghiệm

### 3.1. Chạy bộ kiểm thử tự động với Pytest (`pytest tests/`)
Toàn bộ 7/7 test cases đều vượt qua thành công:
![Kiểm thử Pytest](./images/07_jwt_pytest.png)

### 3.2. Khởi chạy API Gateway và tự động phát hành Token cho user `Hoang`
Chạy `python .\main.py`, chương trình in ra Access Token & Refresh Token và khởi động API server:
![Khởi chạy API Gateway và sinh Token](./images/08_jwt_main_running.png)

### 3.3. Kiểm thử bảo mật: Yêu cầu bị từ chối (`401 Access denied`) khi gửi Token không hợp lệ
Khi gửi token sai hoặc không đúng định dạng, API Gateway lập tức từ chối truy cập:
![Token không hợp lệ bị từ chối](./images/09_jwt_curl_invalid_token.png)

### 3.4. Xác thực thành công: Gửi kèm JWT Bearer Token hợp lệ đến `/protected`
Lệnh `curl` với header `Authorization: Bearer <access_token>` nhận được phản hồi cấp quyền truy cập chính xác với `user: "Hoang"`:
![Xác thực JWT thành công](./images/10_jwt_curl_hoang.png)

---

## 4. Hướng dẫn sử dụng

```powershell
cd jwt-security-tools

# Cài đặt thư viện
pip install -r requirements.txt

# Chạy Pytest
pytest tests/

# Khởi chạy API Gateway
python .\main.py

# Trong cửa sổ Command Prompt (cmd) khác, kiểm tra xác thực bằng curl:
curl -H "Authorization: Bearer <access_token>" http://127.0.0.1:5000/protected
```
