# Script hỗ trợ kết nối và đẩy mã nguồn lên kho lưu trữ GitLab
$currentRemote = git remote get-url origin 2>$null

if (-not $currentRemote) {
    $currentRemote = "https://gitlab.com/VLNH1211/my-pipeline-tutorial-project.git"
    git remote add origin $currentRemote
}

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   TIỆN ÍCH ĐẨY MÃ NGUỒN DỰ ÁN DOCUSAURUS LÊN GITLAB" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "[*] Kho lưu trữ đích: $currentRemote" -ForegroundColor Green
Write-Host "[*] Đang tiến hành đẩy toàn bộ mã nguồn lên nhánh main..." -ForegroundColor Yellow

git push -u origin main --force

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "[+] CHÚC MỪNG! ĐẨY MÃ NGUỒN THÀNH CÔNG!" -ForegroundColor Green
    Write-Host "[+] Runner trên máy bạn sẽ tự động biên dịch và triển khai lên GitLab Pages." -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "[!] Đẩy mã nguồn chưa thành công. Vui lòng kiểm tra lại quyền đăng nhập." -ForegroundColor Red
}

Write-Host ""
pause
