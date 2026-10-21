# DAST Tool - Dynamic Analysis Security Testing Platform for Python

Nền tảng kiểm thử bảo mật động (Dynamic Analysis Security Testing - DAST) dành cho ứng dụng Python. Khác với kiểm thử tĩnh phân tích mã nguồn trước khi chạy, DAST theo dõi hành vi của ứng dụng ngay trong quá trình thực thi (runtime) để phát hiện các bất thường về bộ nhớ, mạng, tài nguyên hệ thống và môi trường sandbox.

---

## 🏗️ Kiến trúc các thành phần

Hệ thống `dast-tool` bao gồm 6 thành phần cốt lõi:

1. **`RuntimeMonitor` (`runtime_monitor.py`)**:
   - Sử dụng thư viện `psutil` gắn vào tiến trình theo PID.
   - Giám sát CPU (`cpu_percent`), dung lượng bộ nhớ RAM (`memory_info().rss`) và danh sách tệp tin đang mở (`open_files`).
2. **`MemoryAnalyzer` (`memory_analyzer.py`)**:
   - Thu gom rác (`gc.collect`) phát hiện các đối tượng rò rỉ bộ nhớ (`memory leaks`).
   - Kiểm tra rủi ro tràn số nguyên 64-bit (`integer overflow`: $|value| > 2^{63}$).
3. **`NetworkTrafficAnalyzer` (`network_traffic_analyzer.py`)**:
   - Lấy số liệu lưu lượng mạng theo thời gian thực trên tất cả card mạng qua `psutil.net_io_counters(pernic=True)`.
4. **`SecurityBehaviorChecker` (`security_behavior_checker.py`)**:
   - Phân tích và phát hiện các lời gọi hàm nguy hiểm runtime (`os.system`, `eval`, `exec`).
5. **`VirtualSandbox` (`virtual_sandbox.py`)**:
   - Khởi tạo thư mục tạm cô lập (`tempfile.mkdtemp()`) và thực thi câu lệnh qua `subprocess.run` nhằm cách ly rủi ro với hệ điều hành thật.
6. **`Flask REST API` (`app.py`)**:
   - Cung cấp các endpoint HTTP JSON cho phép giám sát ứng dụng từ xa.

---

## 📁 Cấu trúc thư mục

```text
dast-tool/
├── requirements.txt            # Thư viện phụ thuộc (psutil, Flask)
├── memory_analyzer.py          # Module phân tích bộ nhớ
├── network_traffic_analyzer.py # Module phân tích lưu lượng mạng
├── runtime_monitor.py          # Module giám sát tiến trình runtime
├── security_behavior_checker.py# Module kiểm tra hành vi độc hại
├── virtual_sandbox.py          # Môi trường hộp cát ảo
├── main.py                     # Script thực thi console kiểm thử tổng thể
├── app.py                      # Máy chủ Flask REST API
├── __init__.py
└── tests/                      # Bộ kiểm thử Unit Test cho DAST
    ├── test_memory_analyzer.py
    ├── test_network_traffic_analyzer.py
    ├── test_runtime_monitor.py
    ├── test_security_behavior_checker.py
    └── test_virtual_sandbox.py
```

---

## 🚀 Cài đặt & Hướng dẫn sử dụng

### 1. Cài đặt các gói phụ thuộc
```powershell
pip install -r requirements.txt
```

### 2. Chạy kiểm thử Unit Test
```powershell
python -m unittest discover -s tests
```
* **Kết quả:**
```text
.....
----------------------------------------------------------------------
Ran 5 tests in 1.042s

OK
```
*(Đạt 5/5 test cases: MemoryAnalyzer, NetworkTrafficAnalyzer, RuntimeMonitor, SecurityBehaviorChecker, VirtualSandbox)*

### 3. Chạy Console Monitor (`main.py`)
Kiểm thử trực tiếp toàn bộ các chỉ số runtime trên terminal:

```powershell
python .\main.py
```
* **Kết quả:**
```text
[+] Monitoring current process: 14396
CPU Usage: 0.0
Memory Usage: 20819968
Open Files: [popenfile(path='C:\\Windows\\System32\\en-US\\KernelBase.dll.mui', fd=-1)]
Memory Leaks: []
Overflow Test: True
Network Stats: {'Wi-Fi': snetio(...), ...}
Suspicious Calls: ['os.system', 'eval', 'exec']
Sandbox stdout: Hello Sandbox

Sandbox stderr:
```

### 4. Giám sát từ xa qua Flask REST API (`app.py`)

Khởi động máy chủ API:
```powershell
python .\app.py
```
* **Nhật ký nhận request (HTTP 200 OK):**
```text
127.0.0.1 - - "GET /api/monitor HTTP/1.1" 200 -
127.0.0.1 - - "GET /api/memory HTTP/1.1" 200 -
127.0.0.1 - - "GET /api/network HTTP/1.1" 200 -
127.0.0.1 - - "GET /api/security HTTP/1.1" 200 -
```

---

## 🌐 Danh sách các API Endpoints

1. **`GET /api/security`**: Kiểm tra các hàm nguy hiểm runtime:
   ```json
   {
     "suspicious_calls": [
       "os.system",
       "eval",
       "exec"
     ]
   }
   ```

2. **`GET /api/monitor`**: Giám sát CPU, RAM, Open Files:
   ```json
   {
     "cpu_usage": 0,
     "memory_usage": 44142592,
     "open_files": [
       "C:\\Windows\\System32\\en-US\\KernelBase.dll.mui"
     ]
   }
   ```

3. **`GET /api/memory`**: Kiểm tra Memory Leaks & Overflow:
   ```json
   {
     "memory_leaks": "[]",
     "overflow_test": true
   }
   ```

4. **`GET /api/network`**: Thống kê lưu lượng mạng trên các card mạng:
   ```json
   {
     "network_stats": {
       "Wi-Fi": { "bytes_recv": 280744556, "bytes_sent": 24927332, ... }
     }
   }
   ```

5. **`POST /api/sandbox`**: Chạy lệnh trong môi trường hộp cát (Body: `{"command": "echo Hello API"}`).
