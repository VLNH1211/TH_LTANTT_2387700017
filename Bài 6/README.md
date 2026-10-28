# BÀI 6: BẢO MẬT VỚI DEVSECOPS VÀ GITLAB CI/CD

## 1. Mục tiêu bài thực hành
- Thiết kế và triển khai quy trình CI/CD an toàn theo tiêu chuẩn DevSecOps trên nền tảng GitLab.
- Xây dựng pipeline kiểm thử cơ bản (Mục 6.2.1) gồm 3 giai đoạn: `build`, `test` (chạy song song 2 job `test-job1` và `test-job2`), và `deploy`.
- Xây dựng pipeline biên dịch và xuất bản website tài liệu kỹ thuật Docusaurus lên GitLab Pages (Mục 6.2.2) với cơ chế quản lý `artifacts`.
- Tích hợp các chốt kiểm tra bảo mật tự động (Security Gates) theo nguyên lý Shift-Left: Secret Scanning, Software Composition Analysis (SCA) và Static Application Security Testing (SAST).

---

## 2. Cấu trúc thư mục Bài 6

- `docusaurus.config.js`: Tệp cấu hình website Docusaurus (`url: 'https://VLNH1211.gitlab.io'`, `baseUrl: '/my-pipeline-tutorial-project/'`).
- `package.json`, `package-lock.json`: Định nghĩa các gói phụ thuộc Node.js của Docusaurus.
- `docs/`, `blog/`, `src/`, `static/`: Mã nguồn giao diện và nội dung tài liệu kỹ thuật.
- `.gitlab-ci.yml`: Cấu hình pipeline chính thức thực hiện biên dịch (`build-job`) và xuất bản lên GitLab Pages (`pages`).
- `.gitlab-ci-basic.yml`: Cấu hình pipeline 3 giai đoạn cơ bản (`build`, `test`, `deploy`) theo Mục 6.2.1 giáo trình.
- `.gitlab-ci-devsecops.yml`: Cấu hình mở rộng tích hợp chốt kiểm tra bảo mật tự động DevSecOps (Secret Scanning, npm audit SCA, SAST).
- `push_to_gitlab.bat`, `push_to_gitlab.ps1`: Kịch bản hỗ trợ đẩy mã nguồn tự động lên GitLab repository.

---

## 3. Hướng dẫn chạy và kiểm thử

### 3.1. Chạy website trên máy cục bộ
```bash
npm install
npm run build
npm run serve
```
Truy cập: `http://localhost:3000/my-pipeline-tutorial-project/`

### 3.2. Triển khai qua GitLab CI/CD & GitLab Pages
- Đẩy mã nguồn lên GitLab repository.
- GitLab Runner tự động thực thi các giai đoạn trong `.gitlab-ci.yml`.
- Truy cập trang web xuất bản tại: `https://VLNH1211.gitlab.io/my-pipeline-tutorial-project/`.
