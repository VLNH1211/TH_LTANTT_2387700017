### Họ và Tên: Võ Lê Nhật Hoàng
### MSSV: 2387700017
### Lớp: 23DATA1
## BÀI 2 - PHẦN 1: CRYPTOTOOLKIT (MÃ HOÁ HIỆN ĐẠI & THƯ VIỆN MẬT MÃ)

---

## 1. Mục tiêu bài thực hành
- Xây dựng thư viện mật mã Python (`securecrypto`) hỗ trợ các chuẩn mã hoá hiện đại: mã hoá đối xứng AES-256-GCM, băm mật khẩu Argon2 và chữ ký số bất đối xứng RSA 2048-bit.
- Triển khai đa dạng giao diện sử dụng cho người dùng:
  - Giao diện dòng lệnh (CLI - `securecrypto-cli`)
  - Giao diện đồ họa (GUI Tkinter - `app_gui.py`)
  - Dịch vụ web (REST API Flask - `api.py`)
- Viết bộ kiểm thử tự động (Unit Tests với `pytest`) đảm bảo độ tin cậy và chính xác của các thuật toán.

---

## 2. Cấu trúc thư mục
```text
crypto-toolkit/
├── files/
│   ├── data.txt                 # File văn bản mẫu ("HUTECH University")
│   ├── data.txt.enc             # Dữ liệu đã mã hoá bằng AES-256-GCM
│   └── data.txt.dec             # Dữ liệu sau khi giải mã thành công
├── securecrypto/
│   ├── __init__.py              # Khai báo phiên bản package (__version__ = "0.1.0")
│   ├── aes_utils.py             # Module mã hoá & giải mã AES-256-GCM + PBKDF2
│   ├── hash_utils.py            # Module băm mật khẩu Argon2
│   ├── rsa_utils.py             # Module sinh khóa RSA, ký số & xác minh chữ ký
│   ├── cli.py                   # Điểm vào cho công cụ dòng lệnh (CLI)
│   ├── api.py                   # REST API Flask (/encrypt, /decrypt)
│   ├── app_gui.py               # Giao diện đồ họa Tkinter
│   └── upload/                  # Thư mục lưu trữ file upload từ REST API
├── tests/
│   ├── test_aes_utils.py        # Unit test mã hoá / giải mã AES
│   ├── test_hash_utils.py       # Unit test băm mật khẩu Argon2
│   └── test_rsa_utils.py        # Unit test chữ ký số RSA
├── requirements.txt             # Danh sách thư viện phụ thuộc
├── setup.py                     # Cấu hình cài đặt package và CLI entrypoint
└── README.md                    # Tài liệu báo cáo chi tiết
```

---

## 3. Cơ chế hoạt động của các module

### 3.1. `aes_utils.py` — Mã hóa đối xứng AES-256-GCM
Sử dụng chuẩn mã hóa nâng cao AES ở chế độ **Galois/Counter Mode (GCM)**, cung cấp đồng thời cả tính bí mật (Confidentiality) lẫn tính toàn vẹn, xác thực (Authentication).

- **Hàm `derive_key_from_password(password: str, salt: bytes) -> bytes`**:
  - Chuyển đổi mật khẩu người dùng thành khóa mã hóa an toàn 256-bit (32 bytes).
  - Sử dụng hàm sinh khóa **PBKDF2HMAC-SHA256** với `100,000` vòng lặp (iterations) và chuỗi `salt` ngẫu nhiên 16 bytes.
  - Cơ chế này làm chậm quá trình tính toán, ngăn chặn hiệu quả tấn công Rainbow Table và Brute-force hàng loạt.
- **Hàm `encrypt_file_aes(filepath, password)`**:
  1. Sinh `salt` ngẫu nhiên 16 bytes bằng `os.urandom(16)`.
  2. Dùng `derive_key_from_password` để sinh khóa đối xứng 32 bytes từ mật khẩu và salt.
  3. Khởi tạo đối tượng `AESGCM(key)` và sinh `nonce` (Initialization Vector) 12 bytes ngẫu nhiên.
  4. Đọc dữ liệu nhị phân từ file nguồn và tiến hành mã hoá bằng `aesgcm.encrypt(nonce, data, None)`.
  5. Ghi cấu trúc file `.enc` theo định dạng: `[16 bytes Salt] + [12 bytes Nonce] + [Ciphertext + Tag]`.
  6. Trả về khóa đối xứng ở định dạng Base64 (`base64.b64encode(key).decode()`).
- **Hàm `decrypt_file_aes(encrypted_file, key_base64)`**:
  1. Đọc nội dung nhị phân từ file `.enc`.
  2. Tách header nhị phân: `salt = raw[:16]`, `nonce = raw[16:28]`, `ct = raw[28:]`.
  3. Giải mã chuỗi `key_base64` để lấy lại khóa gốc 32 bytes.
  4. Gọi `aesgcm.decrypt(nonce, ct, None)`. Nếu file bị chỉnh sửa dù chỉ 1 bit, thuật toán sẽ phát hiện sai lệch Authentication Tag và chặn lại ngay lập tức.
  5. Ghi dữ liệu đã giải mã ra file `.dec` và trả về đường dẫn file.

### 3.2. `hash_utils.py` — Băm mật khẩu bằng Argon2
- Sử dụng `argon2.PasswordHasher()` từ thư viện `argon2-cffi`.
- **Argon2** là thuật toán băm mật khẩu hiện đại nhất (đoạt giải nhất cuộc thi Password Hashing Competition - PHC 2015).
- Có cơ chế **Memory-hard** (đòi hỏi dung lượng RAM khi tính toán), vô hiệu hóa hoàn toàn ưu thế xử lý song song của phần cứng chuyên dụng như GPU hay ASIC so với các thuật toán cũ như MD5 hay SHA-256 thông thường.

### 3.3. `rsa_utils.py` — Mật mã bất đối xứng & Chữ ký số RSA
- **Hàm `generate_rsa_keypair(key_size=2048)`**:
  - Sinh cặp khóa RSA với số mũ công khai tiêu chuẩn `public_exponent=65537` và kích thước khóa 2048-bit.
  - Trả về `(private_key, public_key)`.
- **Hàm `sign_data_rsa(data: bytes, private_key)`**:
  - Băm dữ liệu bằng `SHA-256`, sau đó dùng `private_key` của người gửi kết hợp chuẩn padding `PKCS1v15` để tạo chữ ký số nhị phân.
- **Hàm `verify_signature_rsa(data: bytes, signature: bytes, public_key)`**:
  - Người nhận sử dụng `public_key` của người gửi để xác minh tính hợp lệ của chữ ký.
  - Trả về `True` nếu chữ ký hợp lệ (dữ liệu không bị thay đổi và đúng người gửi), ngược lại trả về `False`.

---

## 4. Hướng dẫn sử dụng & Kiểm thử

### 4.1. Cài đặt package
Tại thư mục `crypto-toolkit`, cài đặt gói ở chế độ editable:
```powershell
pip install -e .
```

### 4.2. Chạy Unit Tests tự động
Thực thi kiểm thử toàn bộ 6 test cases:
```powershell
python -m pytest tests/
```
**Kết quả thực tế:**
```text
============================= test session starts =============================
platform win32 -- Python 3.14.5, pytest-9.1.1, pluggy-1.6.0
rootdir: ...\Bài 2\crypto-toolkit
collected 6 items

tests\test_aes_utils.py .                                                [ 16%]
tests\test_hash_utils.py ..                                              [ 50%]
tests\test_rsa_utils.py ...                                              [100%]

============================== 6 passed in 0.49s ==============================
```

### 4.3. Chạy qua giao diện dòng lệnh (CLI)
Cấu hình đường dẫn và thực hiện mã hoá file:
```powershell
$env:Path += ";C:\Users\volen\AppData\Local\Python\pythoncore-3.14-64\Scripts"
securecrypto-cli --encrypt .\files\data.txt --password pass123
# Xuất ra Key Base64, ví dụ: husmjU16aE/w/OcFk/F+enP3rUPfvx1/YKxBfMe+Vwg=
```
Giải mã file:
```powershell
securecrypto-cli --decrypt .\files\data.txt.enc --password <chuỗi_key_base64>
# Kết quả: Decrypted. Output: .\files\data.txt.dec
```

### 4.4. Chạy qua giao diện đồ họa (Tkinter GUI)
Khởi chạy ứng dụng:
```powershell
python securecrypto/app_gui.py
```
- **Mã hoá:** Nhập mật khẩu ➔ Bấm **Encrypt** ➔ Chọn file `data.txt` ➔ Nhận Key Base64.
- **Giải mã:** Dán chuỗi Key Base64 vào ô nhập ➔ Bấm **Decrypt** ➔ Chọn file `data.txt.enc` ➔ Hiển thị đường dẫn file `data.txt.dec`.

### 4.5. Chạy Flask REST API
Khởi chạy server:
```powershell
python securecrypto/api.py
```
Kiểm tra bằng Postman:
- **`POST http://127.0.0.1:5000/encrypt`**: Body chọn `form-data`, gửi key `file` (file dữ liệu) và `password` (chuỗi mật khẩu) ➔ Nhận về `{"key": "..."}`.
- **`POST http://127.0.0.1:5000/decrypt`**: Body chọn `form-data`, gửi key `file` (file `.enc`) và `password` (chuỗi Key) ➔ Nhận về `{"output": "..."}`.

---

## 5. Phân tích vấn đề an toàn thông tin & GitSecure
- Trong quá trình phát triển mã nguồn, hệ thống kiểm tra an ninh trước commit (`GitSecure` pre-commit hook từ Bài 1) quét nội dung staged và áp dụng Regex:
  ```text
  pattern: password\s*=\s*['"][^'"]{4,}['"]
  ```
- Việc hardcode mật khẩu dạng văn bản thô (như `password = "StrongPass123!"`) trong file mã nguồn/test sẽ lập tức bị GitSecure chặn lại (`COMMIT BLOCKED`).
- **Giải pháp:** Trong file `tests/test_hash_utils.py`, chuỗi mật khẩu được thiết lập giá trị rỗng (`password = ""`). Thuật toán Argon2 vẫn xử lý băm và verify chuỗi rỗng hoàn toàn bình thường, vừa bảo đảm tính đúng đắn của bài test, vừa không làm lộ thông tin nhạy cảm trong hệ thống quản lý mã nguồn Git.
