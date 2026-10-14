### Họ và Tên: Võ Lê Nhật Hoàng
### MSSV: 2387700017
### Lớp: 23DATA1
# BÀI 4 - PHẦN 1: WEB VULNERABILITY SCANNER (CÔNG CỤ QUÉT LỖ HỔNG WEB)

---

## 1. Giới thiệu chức năng
Ứng dụng **WebVulnScanner** là công cụ quét và phát hiện các lỗ hổng bảo mật phổ biến trên Web Application theo tiêu chuẩn OWASP:

1. **XSSScanner (`scanners/xss_scanner.py`)**:
   - Phát hiện lỗ hổng **Cross-Site Scripting (Reflected XSS)**.
   - Sử dụng thư viện payload chuẩn hóa: `<script>alert(1)</script>` và `'><svg/onload=alert(1)>`.
   - Gửi yêu cầu HTTP GET tới URL mục tiêu kèm tham số kiểm thử và phân tích phản hồi để xác định mã độc có bị phản chiếu lại trên trình duyệt hay không.

2. **SQLInjectionTester (`scanners/sql_injection_tester.py`)**:
   - Phân tích các tham số trên Query String URL để phát hiện các dấu hiệu tấn công **SQL Injection (SQLi)**.
   - Thư viện mẫu nhận dạng: `' OR '1'='1`, `'; DROP TABLE users;--`, `" OR 1=1--`, `' UNION SELECT NULL--`.

3. **CSRFDetector (`scanners/csrf_detector.py`)**:
   - Phân tích mã HTML của các form nhập liệu nhằm phát hiện nguy cơ **Cross-Site Request Forgery (CSRF)**.
   - Sử dụng biểu thức chính quy (Regex) kiểm tra token bảo vệ chống CSRF: `csrf_token`, `_csrf`, `csrfmiddlewaretoken`.

4. **SSRFTester (`scanners/ssrf_tester.py`)**:
   - Kiểm tra các tham số URL truyền vào có nguy cơ trỏ tới mạng nội bộ hoặc máy chủ nội bộ (**Server-Side Request Forgery - SSRF**).
   - Regex nhận diện dải IP nhạy cảm: `127.0.0.1`, `localhost`, `10.0.0.0/8`, `192.168.0.0/16`, `172.16.0.0/12`.

5. **ReportGenerator (`report/report_generator.py`)**:
   - Thu thập kết quả từ toàn bộ các scanner, phân loại và chuẩn hóa danh sách lỗ hổng kèm vị trí (`param`), mô tả (`desc`) và mức độ rủi ro (`risk`).

6. **Web UI (`ui/app.py`)**:
   - Giao diện trực quan viết bằng **Flask** và template **Jinja2**.
   - Cho phép người dùng chọn linh hoạt các scanner cần chạy và hiển thị báo cáo phân loại màu theo mức độ nguy hiểm: Đỏ (**HIGH/Critical**), Vàng (**Medium**), Xanh (**LOW**).

---

## 2. Cấu trúc thư mục
```text
web-vuln-scanner/
├── scanners/                    # Các module phát hiện lỗ hổng
│   ├── __init__.py
│   ├── csrf_detector.py         # Kiểm tra CSRF token
│   ├── sql_injection_tester.py  # Phát hiện SQL Injection
│   ├── ssrf_tester.py           # Phát hiện SSRF vào IP nội bộ
│   └── xss_scanner.py           # Kiểm thử Reflected XSS
├── report/                      # Xử lý và tổng hợp báo cáo
│   ├── __init__.py
│   └── report_generator.py
├── tests/                       # Bộ kiểm thử Unit Test
│   ├── __init__.py
│   ├── test_csrf.py
│   ├── test_sql_injection.py
│   ├── test_ssrf.py
│   ├── test_xss.py
│   └── test_report.py
├── ui/                          # Ứng dụng Web giao diện người dùng
│   ├── templates/
│   │   ├── index.html           # Trang chủ nhập URL kiểm thử
│   │   └── result.html          # Trang hiển thị kết quả phân loại màu
│   └── app.py                   # Server Flask chạy tại cổng 5000
├── images/                      # Hình ảnh kết quả thực nghiệm của phần 1
├── main.py                      # File chạy kiểm tra dòng lệnh (CLI)
├── requirements.txt             # Thư viện phụ thuộc (Flask, requests)
├── __init__.py
└── README.md                    # Tài liệu báo cáo chi tiết Phần 1
```

---

## 3. Hình ảnh kết quả thực nghiệm

### 3.1. Chạy bộ kiểm thử tự động Unit Test (`python -m unittest discover tests`)
Toàn bộ 9/9 test cases đều vượt qua thành công (`OK`):
![Kiểm thử Unit Test](./images/01_web_vuln_unittest.png)

### 3.2. Chạy chương trình chính dòng lệnh (`python .\main.py`)
Kết xuất báo cáo lỗ hổng trực tiếp ra console:
![Chạy main.py dòng lệnh](./images/02_web_vuln_main.png)

### 3.3. Khởi chạy máy chủ Web UI Flask (`python .\ui\app.py`)
Server Flask lắng nghe kết nối tại `http://127.0.0.1:5000`:
![Khởi chạy Web UI Flask](./images/03_web_vuln_flask_run.png)

### 3.4. Giao diện trang chủ Web Vulnerability Scanner
Người dùng có thể nhập URL và chọn các module kiểm thử:
![Giao diện Web Scanner](./images/04_web_vuln_ui_index.png)

### 3.5. Nhập URL mục tiêu kiểm thử `http://testphp.vulnweb.com/artists.php?artist=1'`
![Nhập URL kiểm thử](./images/05_web_vuln_ui_input.png)

### 3.6. Kết quả báo cáo lỗ hổng trực quan trên trình duyệt
Hiển thị cảnh báo trực quan: 2 khối đỏ phát hiện lỗ hổng **Reflected XSS** (mức độ **HIGH**) và 1 khối cảnh báo thiếu **CSRF Token** (mức độ **Medium**):
![Báo cáo lỗ hổng](./images/06_web_vuln_ui_report.png)

---

## 4. Hướng dẫn sử dụng

```powershell
cd web-vuln-scanner

# Cài đặt thư viện
pip install -r requirements.txt

# Chạy Unit Test kiểm thử
python -m unittest discover tests

# Chạy giao diện Web
python .\ui\app.py

# Mở trình duyệt tại: http://127.0.0.1:5000
```
