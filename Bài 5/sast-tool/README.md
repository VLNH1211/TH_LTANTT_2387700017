# SAST Tool - Static Analysis Security Testing for Python

Công cụ phân tích bảo mật tĩnh (Static Analysis Security Testing - SAST) dành cho mã nguồn Python. Công cụ này kiểm tra mã nguồn mà không cần thực thi, phát hiện sớm các lỗ hổng tiềm ẩn, các mẫu mã không an toàn và các vấn đề về chất lượng mã nguồn theo chuẩn PEP8.

---

## 🏗️ Kiến trúc các thành phần

Hệ thống `sast-tool` bao gồm 5 module chính:

1. **`ASTAnalyzer` (`sast_tool/ast_analyzer.py`)**:
   - Sử dụng thư viện `ast` phân tích cây cú pháp trừu tượng của Python.
   - Phát hiện các lệnh gọi hàm rủi ro cao như `eval()` - nguy cơ dẫn đến lỗi Remote Code Execution (RCE).
2. **`VulnPatternMatcher` (`sast_tool/vuln_pattern_matcher.py`)**:
   - Dùng Regex đối sánh các mẫu mã độc hại: mật khẩu cố định (hardcoded password) hoặc import các module không an toàn (ví dụ: `pickle` với rủi ro Insecure Deserialization).
   - Tự động tính toán vị trí dòng và cột phát hiện lỗi.
3. **`CodeQualityChecker` (`sast_tool/code_quality_checker.py`)**:
   - Tích hợp `flake8` để phân tích tĩnh chất lượng code và chuẩn PEP8.
   - Bắt và bóc tách các cảnh báo linting (dòng, cột, mã lỗi).
4. **`SecurityRuleEngine` (`sast_tool/security_rule_engine.py`)**:
   - Quản lý tập luật từ file `rules/default_rules.json`.
   - Phân loại mức độ nghiêm trọng (`severity`): `high`, `medium`, `low`.
5. **`SarifReporter` (`sast_tool/sarif_reporter.py`)**:
   - Xuất toàn bộ kết quả phân tích ra định dạng chuẩn quốc tế **SARIF (Static Analysis Results Interchange Format 2.1.0)** bằng thư viện `sarif-om` và `jsonpickle`.

---

## 📁 Cấu trúc thư mục

```text
sast-tool/
├── requirements.txt            # Thư viện phụ thuộc (flake8, sarif-om, jsonpickle)
├── report.sarif                # Báo cáo kết quả phân tích theo chuẩn SARIF
├── examples/                   # Các file mã nguồn mẫu dùng để kiểm thử
│   ├── vulnerable_01.py        # Mẫu chứa hardcoded password, pickle, eval
│   └── vulnerable_02.py        # Mẫu chứa hàm eval không kiểm soát
├── rules/
│   └── default_rules.json      # File định nghĩa mức độ nghiêm trọng của luật
├── sast_tool/
│   ├── __init__.py
│   ├── ast_analyzer.py
│   ├── vuln_pattern_matcher.py
│   ├── code_quality_checker.py
│   ├── security_rule_engine.py
│   ├── sarif_reporter.py
│   └── main.py                 # File thực thi chính
└── tests/                      # Thư mục kiểm thử tự động (Unit Tests)
    ├── __init__.py
    ├── test_ast_analyzer.py
    ├── test_vuln_pattern_matcher.py
    ├── test_code_quality_checker.py
    ├── test_security_rule_engine.py
    └── test_sarif_reporter.py
```

---

## 🚀 Cài đặt & Hướng dẫn sử dụng

### 1. Cài đặt các gói phụ thuộc
```powershell
pip install -r requirements.txt
```

### 2. Chạy kiểm thử Unit Test
```powershell
python -m unittest discover tests
```
* **Kết quả:**
```text
......
----------------------------------------------------------------------
Ran 6 tests in 0.338s

OK
```
*(Đạt 6/6 test cases: AST Analyzer, Pattern Matcher, Flake8 Checker, Security Rule Engine, SARIF Reporter)*

### 3. Phân tích mã nguồn tĩnh

#### Phân tích mẫu 1: `examples/vulnerable_01.py`
```powershell
python -m sast_tool.main .\examples\vulnerable_01.py
```
* **Kết quả:**
```text
Analysis complete.
    Report saved to report.sarif with 8 issues.
```
*(Phát hiện 8 lỗi: 1 lỗi eval, 2 lỗi pattern password/pickle, 5 lỗi flake8 linting)*

#### Phân tích mẫu 2: `examples/vulnerable_02.py`
```powershell
python -m sast_tool.main .\examples\vulnerable_02.py
```
* **Kết quả:**
```text
Analysis complete.
    Report saved to report.sarif with 4 issues.
```
*(Phát hiện 4 lỗi: 1 lỗi eval, 3 lỗi flake8 linting)*

---

## 📊 Xem báo cáo bằng VS Code SARIF Viewer
1. Cài đặt tiện ích mở rộng **SARIF Viewer** trong Visual Studio Code.
2. Mở file `report.sarif`.
3. Bảng **SARIF Results** sẽ hiển thị danh sách các cảnh báo bảo mật trực quan kèm vị trí dòng/cột cụ thể trong mã nguồn.
