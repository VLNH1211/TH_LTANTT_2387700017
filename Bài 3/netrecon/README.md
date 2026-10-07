### Họ và Tên: Võ Lê Nhật Hoàng
### MSSV: 2387700017
### Lớp: 23DATA1
## BÀI 3 - PHẦN 2: NETRECON (BỘ CÔNG CỤ TRINH SÁT & KHÁM PHÁ MẠNG)

---

## 1. Mục tiêu bài thực hành
- Hiểu rõ các kỹ thuật quét cổng (Port Scanning), nhận dạng dịch vụ (Service Fingerprinting), thu thập Banner (Banner Grabbing) và khám phá sơ đồ mạng nội bộ.
- Xây dựng bộ công cụ khám phá mạng **NetRecon** hoàn chỉnh gồm 7 module chức năng:
  - `PortScanner`: Quét cổng TCP bất đồng bộ (`asyncio`) tích hợp giới hạn tốc độ (`Semaphore` rate-limiting).
  - `ServiceDetector`: Tích hợp **Nmap (`-sV`)** để phát hiện phiên bản dịch vụ đang chạy.
  - `BannerGrabber`: Thu thập thông tin phản hồi dịch vụ an toàn với cơ chế giới hạn thời gian chờ (`timeout`).
  - `NetworkMapper`: Khám phá sơ đồ mạng nội bộ thông qua bảng ánh xạ địa chỉ IP - MAC (`arp -a`).
  - `VulnChecker`: Đối chiếu các cổng dịch vụ với cơ sở dữ liệu lỗ hổng bảo mật đã biết (CVE).
  - `FilterUtils`: Hỗ trợ lọc mục tiêu theo danh sách trắng (`whitelist`) và danh sách đen (`blacklist`).
  - `EmailSender`: Tự động gửi báo cáo kết quả quét về hộp thư Gmail qua giao thức `SMTP_SSL`.
- Cung cấp đồng thời giao diện dòng lệnh (**CLI** với `Click`) và giao diện ứng dụng Web (**Flask**).

---

## 2. Cấu trúc thư mục
```text
netrecon/
├── modules/
│   ├── __init__.py              # Khai báo package modules
│   ├── port_scanner.py          # Quét cổng TCP bất đồng bộ với asyncio.Semaphore
│   ├── service_detector.py      # Nhận dạng phiên bản dịch vụ bằng Nmap (-sV)
│   ├── banner_grabber.py        # Thu thập banner dịch vụ qua socket TCP
│   ├── network_mapper.py        # Khám phá bảng ARP mạng nội bộ (arp -a)
│   ├── vuln_checker.py          # Kiểm tra lỗ hổng CVE cơ bản theo cổng dịch vụ
│   ├── filter_utils.py          # Bộ lọc IP theo Whitelist / Blacklist
│   └── email_sender.py          # Gửi báo cáo kết quả qua Gmail SMTP_SSL (cổng 465)
├── static/
│   └── style.css                # Giao diện Dark-mode cho ứng dụng Web
├── templates/
│   ├── layout.html              # Khung giao diện HTML chính
│   ├── index.html               # Biểu mẫu cấu hình quét mạng
│   └── result.html              # Trang hiển thị chi tiết kết quả trinh sát
├── cli.py                       # Công cụ dòng lệnh (CLI) sử dụng thư viện Click
├── app.py                       # Ứng dụng Web Flask (chạy trên cổng 5000)
├── requirements.txt             # Danh sách các gói thư viện Python cần thiết
├── netrecon.log                 # Nhật ký hoạt động (Activity Log) kèm dấu thời gian
├── .env                         # Biến môi trường lưu thông tin SMTP (được loại trừ trong .gitignore)
└── README.md                    # Tài liệu báo cáo chi tiết
```

---

## 3. Phân tích chi tiết các Module

### 3.1. `modules/port_scanner.py` — Quét cổng bất đồng bộ có giới hạn tốc độ
- Sử dụng `asyncio.open_connection(target, port)` kết hợp `asyncio.wait_for(..., timeout=1)` để kiểm tra trạng thái cổng TCP mà không gây nghẽn luồng chính.
- Áp dụng `asyncio.Semaphore(rate_limit)` (mặc định `rate_limit=100`) nhằm kiểm soát số lượng kết nối đồng thời tối đa, tuân thủ nguyên tắc giới hạn tốc độ (Rate Limiting) trong kiểm thử an ninh.
- Ghi nhận mọi cổng mở vào file nhật ký `netrecon.log` kèm dấu thời gian `YYYY-MM-DD HH:MM:SS`.

### 3.2. `modules/service_detector.py` — Nhận dạng phiên bản dịch vụ
- Gọi công cụ `nmap -sV -p <ports> <ip>` thông qua `subprocess.check_output` để phân tích dấu hiệu đặc trưng (Active Fingerprinting) và xác định tên dịch vụ, phiên bản phần mềm phía sau cổng mạng.

### 3.3. `modules/banner_grabber.py` — Thu thập Banner an toàn
- Thiết lập kết nối TCP với `s.settimeout(2)`, đọc tối đa `1024 bytes` dữ liệu chào mừng (Banner) từ dịch vụ và ghi log kết quả.

### 3.4. `modules/network_mapper.py` & `modules/vuln_checker.py`
- **`map_network()`**: Thực thi lệnh `arp -a` để trích xuất danh sách các thiết bị lân cận trong cùng phân đoạn mạng (IP Address, Physical MAC Address, Type).
- **`check_vulns(ports)`**: Đối chiếu danh sách cổng quét với từ điển `VULN_PORTS` chứa các mã lỗ hổng CVE tiêu biểu:
  - Port `21` (FTP): `CVE-2015-3306, CVE-2001-0261`
  - Port `22` (SSH): `CVE-2018-15473`
  - Port `23` (Telnet): `CVE-2011-4862`
  - Port `80` (HTTP): `CVE-2021-41773`
  - Port `443` (HTTPS): `CVE-2021-3449`

### 3.5. `modules/email_sender.py` — Gửi báo cáo tự động qua SMTP SSL
- Đọc thông tin xác thực `SMTP_USER` và `SMTP_PASS` (Google App Password) từ file `.env` thông qua `python-dotenv`.
- Thiết lập kết nối mã hóa tới `smtp.gmail.com` tại cổng `465` (`SMTP_SSL`) và gửi toàn bộ báo cáo kết quả quét tới địa chỉ email người nhận.

---

## 4. Hướng dẫn sử dụng & Kết quả thực nghiệm

### 4.1. Cài đặt thư viện
```powershell
cd netrecon
pip install -r requirements.txt
```

### 4.2. Chạy kiểm thử trên giao diện dòng lệnh (`cli.py`)
```powershell
# Chế độ tương tác mặc định
python .\cli.py

# Quét nhanh cổng mở (phát hiện cổng 8443 của SecureChat đang mở)
python .\cli.py --target 127.0.0.1 --ports 22,80,8443 --mode scan

# Chạy toàn bộ các tính năng (all)
python .\cli.py --target 127.0.0.1 --ports 21,22,80,443 --mode all
```
![Kiểm tra cli.py tương tác](../images/04_netrecon_cli_1.png)
![Kiểm tra cli.py với tham số scan và all](../images/05_netrecon_cli_2.png)

### 4.3. Chạy ứng dụng Web (`app.py`) và nhận báo cáo qua Gmail
```powershell
python .\app.py
```
Truy cập **http://localhost:5000/**, nhập thông số quét và địa chỉ email nhận kết quả:

![Flask server gửi email thành công](../images/06_netrecon_flask_console.png)
![Kết quả phản hồi trên giao diện Web](../images/07_netrecon_web_result.png)
![Email báo cáo nhận được trong hộp thư Gmail](../images/08_netrecon_email_result.png)
