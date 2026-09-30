### Họ và Tên: Võ Lê Nhật Hoàng
### MSSV: 2387700017
### Lớp: 23DATA1
## BÀI 2 - PHẦN 2: MINI-CA (HẠ TẦNG KHÓA CÔNG KHAI PKI & QUẢN LÝ CHỨNG CHỈ X.509)

---

## 1. Mục tiêu bài thực hành
- Xây dựng mô phỏng hoàn chỉnh một hệ thống Nhà cấp phát chứng chỉ số (Certificate Authority - CA) đa cấp theo chuẩn quốc tế X.509.
- Hiện thực hóa và kiểm thử trọn vẹn vòng đời của chứng chỉ số (Certificate Lifecycle):
  1. Khởi tạo Root CA tự ký (Self-signed Root CA).
  2. Tạo CA trung gian (Intermediate CA) được Root CA ký ủy quyền.
  3. Cấp phát chứng chỉ cho thực thể cuối (End-Entity / User Certificate).
  4. Xác minh chuỗi tin cậy (Chain of Trust Verification).
  5. Thu hồi chứng chỉ (Revocation) và ghi nhận vào Danh sách thu hồi chứng chỉ (CRL).
  6. Kiểm tra trạng thái chứng chỉ trực tuyến mô phỏng giao thức OCSP.

---

## 2. Cấu trúc thư mục
```text
mini-ca/
├── ca_utils.py                  # Module tạo Root CA, Intermediate CA, cấp User Cert, xác minh chuỗi
├── revoke_utils.py              # Module tạo CRL, thu hồi chứng chỉ và kiểm tra trạng thái OCSP
├── demo.py                      # Kịch bản dòng lệnh chạy toàn bộ quy trình PKI tự động
├── demo_ui.py                   # Giao diện đồ họa Tkinter tương tác 5 bước
├── requirements.txt             # Thư viện phụ thuộc (cryptography)
├── certs/                       # Thư mục lưu trữ khóa riêng tư (.pem) và chứng chỉ X.509 (.pem)
└── README.md                    # Tài liệu báo cáo chi tiết
```

---

## 3. Kiến trúc hệ thống CA phân cấp (Hierarchical PKI Model)

Hệ thống được thiết kế theo mô hình phân cấp chuẩn gồm 3 tầng:

```text
               +-------------------------------------------+
               |                  Root CA                  |
               |         (Tự ký, thời hạn 10 năm)          |
               |        CN = Mini Root CA Root, C = VN     |
               |   BasicConstraints: ca=True, path_len=1   |
               +-------------------------------------------+
                                     |
                                     v Ký ủy quyền
               +-------------------------------------------+
               |              Intermediate CA              |
               |         (CA trung gian, hạn 5 năm)        |
               |        CN = Mini Intermediate CA, C = VN  |
               |   BasicConstraints: ca=True, path_len=0   |
               +-------------------------------------------+
                                     |
                                     v Ký cấp phát
               +-------------------------------------------+
               |          End-Entity Certificate           |
               |          (User: Phuoc_Nguyen, 1 năm)      |
               |        CN = Phuoc_Nguyen, C = VN          |
               |   BasicConstraints: ca=False              |
               +-------------------------------------------+
```

### Ý nghĩa của cơ chế phân cấp:
- **Bảo vệ Root CA tối thượng:** Khóa riêng tư của Root CA có giá trị sinh tử đối với toàn bộ hệ sinh thái bảo mật. Bằng cách ủy quyền cho Intermediate CA đảm nhận việc cấp phát chứng chỉ hàng ngày, khóa Root CA có thể được cất giữ ở trạng thái ngoại tuyến (Offline), giảm thiểu tối đa nguy cơ bị xâm nhập.
- **Phần mở rộng BasicConstraints:**
  - `Root CA`: `ca=True, path_length=1` ➔ Cho phép đóng vai trò CA và chỉ được phép cấp tối đa thêm 1 cấp CA trung gian bên dưới.
  - `Intermediate CA`: `ca=True, path_length=0` ➔ Được phép cấp phát chứng chỉ cho người dùng, nhưng không được phép cấp tiếp thêm bất kỳ CA con nào nữa.
  - `End-Entity`: `ca=False` ➔ Chứng chỉ người dùng cuối, hoàn toàn không có quyền ký cấp chứng chỉ cho bên khác.

---

## 4. Cơ chế hoạt động của các chức năng PKI

### 4.1. Module `ca_utils.py`
- **`create_root_ca()`**:
  - Sinh cặp khóa RSA 2048-bit (`public_exponent=65537`).
  - Tạo cấu trúc chứng chỉ X.509 với `subject` trùng với `issuer` (chứng chỉ tự ký).
  - Thiết lập hiệu lực 10 năm (`3650 ngày`) và gán extension `BasicConstraints(ca=True, path_length=1)`.
  - Tự ký chứng chỉ bằng chính khóa riêng tư của Root CA với thuật toán `SHA-256`.
  - Lưu trữ thành `certs/root_ca_key.pem` và `certs/root_ca_cert.pem`.
- **`create_intermediate_ca(root_key, root_cert)`**:
  - Sinh cặp khóa RSA mới cho Intermediate CA.
  - Thiết lập `issuer` lấy từ `root_cert.subject`.
  - Thiết lập hiệu lực 5 năm (`1825 ngày`) và extension `BasicConstraints(ca=True, path_length=0)`.
  - Ký chứng chỉ bằng `root_key` (khóa riêng của Root CA).
  - Lưu trữ thành `certs/intermediate_key.pem` và `certs/intermediate_cert.pem`.
- **`issue_certificate(ca_key, ca_cert, subject_info)`**:
  - Nhận thông tin thực thể cuối (Common Name, Tổ chức, Quốc gia).
  - Sinh cặp khóa RSA mới, gán `issuer` là `ca_cert.subject` (Intermediate CA) và hiệu lực 1 năm (`365 ngày`).
  - Gán `BasicConstraints(ca=False)`.
  - Ký bằng `ca_key` (khóa riêng của Intermediate CA).
  - Lưu thành `certs/<common_name>_key.pem` và `certs/<common_name>_cert.pem`.
- **`verify_certificate_chain(cert_to_verify, chain)`**:
  - Lặp tuần tự qua danh sách các chứng chỉ trong chuỗi (`Intermediate CA` ➔ `Root CA`).
  - Dùng `issuer_cert.public_key()` để xác minh chữ ký số (`signature`) trên dữ liệu `tbs_certificate_bytes` của chứng chỉ con.
  - Trả về `True` nếu toàn bộ chuỗi được chứng minh tính liên tục và hợp lệ; trả về `False` nếu xảy ra lỗi (chữ ký sai, chứng chỉ bị giả mạo).

### 4.2. Module `revoke_utils.py`
- **`create_empty_crl(issuer_cert, issuer_key)`**:
  - Khởi tạo Danh sách thu hồi chứng chỉ (CRL) rỗng theo chuẩn X.509.
  - Gán `last_update` thời điểm hiện tại và `next_update` sau 7 ngày.
  - Được ký bởi khóa riêng của CA và lưu vào file `certs/ca_crl.pem`.
- **`revoke_certificate(cert_file, issuer_cert, issuer_key, reason)`**:
  - Đọc file chứng chỉ cần thu hồi, trích xuất `serial_number`.
  - Khởi tạo bản ghi thu hồi `RevokedCertificateBuilder` kèm thời điểm và lý do thu hồi (mặc định: `ReasonFlags.key_compromise` - lộ khóa riêng).
  - Cập nhật bản ghi vào danh sách CRL hiện hữu, tiến hành ký lại CRL bằng khóa của CA và ghi đè vào `ca_crl.pem`.
- **`check_revocation_status(cert_file)`**:
  - Đọc chứng chỉ và kiểm tra xem `serial_number` của nó có tồn tại trong danh sách đen `ca_crl.pem` hay không.
  - Trả về `True` nếu chứng chỉ đã bị thu hồi; trả về `False` nếu chứng chỉ còn hiệu lực.

---

## 5. Hướng dẫn sử dụng & Kết quả thực nghiệm

### 5.1. Chạy kịch bản tự động (`demo.py`)
```powershell
python demo.py
```
**Kết quả hiển thị trên Terminal:**
```text
Tạo Root CA...
Root CA: <RSAPrivateKey>, <Certificate(CN=Mini Root CA Root)>
Tạo Intermediate CA...
Intermediate CA: <RSAPrivateKey>, <Certificate(CN=Mini Intermediate CA)>
Phát hành chứng chỉ người dùng cuối...
Đã phát hành: certs\Phuoc_Nguyen_cert.pem, certs\Phuoc_Nguyen_key.pem
Kiểm tra chuỗi chứng chỉ...
Chuỗi hợp lệ: True
Thu hồi chứng chỉ user1...
Đã thu hồi
Kiểm tra trạng thái OCSP của Phuoc_Nguyen_cert.pem...
Trạng thái: Revoked
```

### 5.2. Chạy giao diện đồ họa tương tác (`demo_ui.py`)
Khởi chạy ứng dụng:
```powershell
python demo_ui.py
```
Giao diện **Mini CA Demo UI** hỗ trợ thực hiện trực quan 5 thao tác:
1. **Nút 1 - Tạo Root & Intermediate CA**: Sinh cặp CA 2 tầng và lưu file PEM.
2. **Nút 2 - Phát hành User Cert**: Tạo khóa và chứng chỉ cho `Phuoc_Nguyen`.
3. **Nút 3 - Kiểm tra Chuỗi Cert**: Hộp thoại thông báo chuỗi hợp lệ (`True`).
4. **Nút 4 - Thu hồi User Cert**: Cập nhật chứng chỉ vào CRL với lý do lộ khóa.
5. **Nút 5 - Kiểm tra Trạng thái OCSP**: Hộp thoại thông báo chứng chỉ `Đã thu hồi`.

---

## 6. Chính sách bảo mật kho lưu trữ (Git Management)
- Toàn bộ các khóa riêng tư (`*_key.pem`) và chứng chỉ số sinh ra trong quá trình thực hành đều được lưu trữ tập trung tại thư mục `certs/`.
- File `.gitignore` ở thư mục gốc được cấu hình nghiêm ngặt:
  ```text
  certs/
  *.pem
  ```
- Quy tắc này đảm bảo rằng **không có bất kỳ khóa bí mật hay chứng chỉ nào bị commit lên GitHub**, ngăn ngừa triệt để nguy cơ lộ lọt thông tin mật của hệ thống PKI.
