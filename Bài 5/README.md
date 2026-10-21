### Họ và Tên: Võ Lê Nhật Hoàng
### MSSV: 2387700017
### Lớp: 23DATA1
# BÀI 5: PHÂN TÍCH VÀ KIỂM THỬ BẢO MẬT (SAST & DAST)

---

## 1. Giới thiệu chung
Bài thực hành số 5 trang bị kiến thức và kỹ năng thực hành về hai phương pháp kiểm thử bảo mật phần mềm trọng yếu:
1. **Static Analysis Security Testing (SAST)**: Phân tích mã nguồn tĩnh thông qua cây cú pháp trừu tượng AST (Abstract Syntax Tree), phát hiện các hàm thực thi nguy hiểm (`eval`), các mẫu mã nhạy cảm (hardcoded password, module không an toàn `pickle`), tích hợp `flake8` kiểm tra chuẩn PEP8, và xuất báo cáo kết quả phân tích theo chuẩn quốc tế **SARIF (Static Analysis Results Interchange Format 2.1.0)**.
2. **Dynamic Analysis Security Testing (DAST)**: Kiểm thử bảo mật động trong quá trình thực thi ứng dụng (runtime), bao gồm giám sát CPU/RAM/file descriptors qua `psutil`, phát hiện rò rỉ bộ nhớ (`memory leaks`) và nguy cơ tràn số nguyên 64-bit, phân tích lưu lượng mạng, kiểm tra hành vi nghi vấn runtime, môi trường thực thi hộp cát ảo (`VirtualSandbox`), và tích hợp hệ thống máy chủ **Flask REST API** phục vụ giám sát từ xa.

---

## 2. Cấu trúc tổng thể Bài 5

```text
Bài 5/
├── sast-tool/                       # Phần 1: Static Analysis Security Testing
│   ├── examples/                   # Các mẫu mã nguồn thử nghiệm
│   │   ├── vulnerable_01.py        # Mẫu chứa hardcoded password, pickle, eval
│   │   └── vulnerable_02.py        # Mẫu chứa eval tùy ý không kiểm soát
│   ├── rules/
│   │   └── default_rules.json      # Danh mục luật bảo mật và mức độ nghiêm trọng
│   ├── sast_tool/
│   │   ├── __init__.py
│   │   ├── ast_analyzer.py         # Phân tích cây AST tìm lời gọi eval
│   │   ├── vuln_pattern_matcher.py # Nhận diện mẫu mã rủi ro (Regex)
│   │   ├── code_quality_checker.py # Tích hợp Flake8 kiểm tra PEP8
│   │   ├── security_rule_engine.py # Đánh giá luật và phân loại severity
│   │   ├── sarif_reporter.py       # Xuất báo cáo chuẩn SARIF
│   │   └── main.py                 # Pipeline điều phối phân tích tĩnh
│   ├── tests/                      # Bộ kiểm thử Unit Test cho SAST
│   │   ├── __init__.py
│   │   ├── test_ast_analyzer.py
│   │   ├── test_code_quality_checker.py
│   │   ├── test_sarif_reporter.py
│   │   ├── test_security_rule_engine.py
│   │   └── test_vuln_pattern_matcher.py
│   ├── report.sarif                # Báo cáo chuẩn SARIF sinh ra sau khi quét
│   ├── requirements.txt         # Thư viện phụ thuộc (flake8, sarif-om, jsonpickle)
│   └── README.md                   # Báo cáo chi tiết Phần 1
│
├── dast-tool/                       # Phần 2: Dynamic Analysis Security Testing
│   ├── memory_analyzer.py          # Kiểm tra memory leaks và integer overflow
│   ├── network_traffic_analyzer.py # Thống kê lưu lượng mạng qua psutil
│   ├── runtime_monitor.py          # Giám sát CPU, RAM, open files
│   ├── security_behavior_checker.py# Phát hiện lời gọi hàm nguy hiểm runtime
│   ├── virtual_sandbox.py          # Môi trường hộp cát cô lập lệnh
│   ├── main.py                     # Console monitor kiểm thử nhanh
│   ├── app.py                      # Máy chủ Flask REST API giám sát runtime
│   ├── __init__.py
│   ├── tests/                      # Bộ kiểm thử Unit Test cho DAST
│   │   ├── test_memory_analyzer.py
│   │   ├── test_network_traffic_analyzer.py
│   │   ├── test_runtime_monitor.py
│   │   ├── test_security_behavior_checker.py
│   │   └── test_virtual_sandbox.py
│   ├── requirements.txt         # Thư viện phụ thuộc (psutil, Flask)
│   └── README.md                   # Báo cáo chi tiết Phần 2
└── README.md                        # Báo cáo tổng hợp Bài 5
```

---

## 3. Kết quả thực nghiệm

### 3.1. Phần 1: SAST-TOOL (Static Analysis Security Testing)

#### Chạy kiểm thử tự động Unit Test (`python -m unittest discover tests`):
Toàn bộ 6/6 test cases của các module AST, Pattern Matcher, Flake8, Rule Engine và Sarif Reporter đều vượt qua thành công:
```text
PS C:\...\sast-tool> python -m unittest discover tests
......
----------------------------------------------------------------------
Ran 6 tests in 0.338s

OK
```

#### Quét phân tích mẫu mã nguồn `examples/vulnerable_01.py`:
```powershell
python -m sast_tool.main .\examples\vulnerable_01.py
```
* **Kết quả:** Phát hiện chính xác **8 issues** và lưu vào file `report.sarif`:
  - 01 lỗi rủi ro cao (`Use of eval`): lời gọi hàm `eval(data)` tùy ý.
  - 02 lỗi rủi ro trung bình (`Pattern Match`): `password = "123456"` và import module `pickle`.
  - 05 lỗi linting (`Lint Issue`): các lỗi chuẩn PEP8 qua Flake8 (F401, E402, E302, E305).
```text
Analysis complete.
    Report saved to report.sarif with 8 issues.
```

#### Quét phân tích mẫu mã nguồn `examples/vulnerable_02.py`:
```powershell
python -m sast_tool.main .\examples\vulnerable_02.py
```
* **Kết quả:** Phát hiện chính xác **4 issues**:
  - 01 lỗi `Use of eval` tại hàm `dangerous_eval`.
  - 03 lỗi linting Flake8 (khoảng cách dòng trống giữa các hàm).
```text
Analysis complete.
    Report saved to report.sarif with 4 issues.
```

---

### 3.2. Phần 2: DAST-TOOL (Dynamic Analysis Security Testing)

#### Chạy kiểm thử tự động Unit Test (`python -m unittest discover -s tests`):
Toàn bộ 5/5 test cases của các module kiểm thử động đạt chuẩn:
```text
PS C:\...\dast-tool> python -m unittest discover -s tests
.....
----------------------------------------------------------------------
Ran 5 tests in 1.042s

OK
```

#### Chạy chương trình console monitor `main.py`:
```powershell
python .\main.py
```
* **Kết quả hiển thị:**
```text
[+] Monitoring current process: 14396
CPU Usage: 0.0
Memory Usage: 20819968
Open Files: [popenfile(path='C:\\Windows\\System32\\en-US\\KernelBase.dll.mui', fd=-1)]
Memory Leaks: []
Overflow Test: True
Network Stats: {'Wi-Fi': snetio(bytes_sent=24927332, bytes_recv=280744556, ...), ...}
Suspicious Calls: ['os.system', 'eval', 'exec']
Sandbox stdout: Hello Sandbox

Sandbox stderr:
```

#### Khởi chạy máy chủ Flask REST API (`python .\app.py`):
```text
 * Serving Flask app 'app'
 * Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://10.12.44.121:5000
Press CTRL+C to quit
127.0.0.1 - - "GET /api/monitor HTTP/1.1" 200 -
127.0.0.1 - - "GET /api/memory HTTP/1.1" 200 -
127.0.0.1 - - "GET /api/network HTTP/1.1" 200 -
127.0.0.1 - - "GET /api/security HTTP/1.1" 200 -
```

#### Kết quả kiểm tra các API Endpoints trên trình duyệt:
1. **`GET /api/security`**:
   ```json
   {
     "suspicious_calls": [
       "os.system",
       "eval",
       "exec"
     ]
   }
   ```
2. **`GET /api/monitor`**:
   ```json
   {
     "cpu_usage": 0,
     "memory_usage": 44142592,
     "open_files": [
       "C:\\Windows\\System32\\en-US\\KernelBase.dll.mui"
     ]
   }
   ```
3. **`GET /api/memory`**:
   ```json
   {
     "memory_leaks": "[]",
     "overflow_test": true
   }
   ```
4. **`GET /api/network`**:
   ```json
   {
     "network_stats": {
       "Bluetooth Network Connection": { "bytes_recv": 0, "bytes_sent": 0, ... },
       "Ethernet": { "bytes_recv": 0, "bytes_sent": 0, ... },
       "Wi-Fi": { "bytes_recv": 280744556, "bytes_sent": 24927332, ... }
     }
   }
   ```

---

## 4. Hướng dẫn cài đặt và chạy thử nghiệm

### 4.1. Chạy SAST-TOOL:
```powershell
cd "Bài 5/sast-tool"
pip install -r requirements.txt

# Chạy Unit Test
python -m unittest discover tests

# Phân tích file mẫu
python -m sast_tool.main .\examples\vulnerable_01.py
python -m sast_tool.main .\examples\vulnerable_02.py
```

### 4.2. Chạy DAST-TOOL:
```powershell
cd "Bài 5/dast-tool"
pip install -r requirements.txt

# Chạy Unit Test
python -m unittest discover -s tests

# Chạy console monitor
python .\main.py

# Chạy Flask REST API
python .\app.py
# Truy cập trình duyệt tại: http://127.0.0.1:5000/api/security
```
