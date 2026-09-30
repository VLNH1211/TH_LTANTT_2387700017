from flask import Flask, request, jsonify, render_template_string, send_file
from securecrypto import aes_utils
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILES_DIR = os.path.join(BASE_DIR, 'upload')
os.makedirs(FILES_DIR, exist_ok=True)

HOME_HTML = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>SecureCrypto Web API</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif; max-width: 600px; margin: 40px auto; padding: 20px; background: #f0f2f5; color: #333; }
        .card { background: white; padding: 25px; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); margin-bottom: 25px; }
        h2 { color: #1a73e8; margin-top: 0; font-size: 20px; }
        label { font-weight: 600; display: block; margin-top: 10px; margin-bottom: 5px; font-size: 14px; }
        input[type="text"], input[type="password"], input[type="file"] { width: 100%; padding: 10px; box-sizing: border-box; border: 1px solid #ccd0d5; border-radius: 6px; font-size: 14px; }
        button { background: #1a73e8; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; font-size: 15px; font-weight: 600; margin-top: 15px; width: 100%; }
        button:hover { background: #1557b0; }
        .result { margin-top: 15px; padding: 12px; border-radius: 4px; word-break: break-all; font-size: 14px; }
    </style>
</head>
<body>
    <div class="card">
        <h2>🔒 Mã hóa File (/encrypt)</h2>
        <form id="encryptForm">
            <label>Chọn file cần mã hóa:</label>
            <input type="file" name="file" required>
            <label>Mật khẩu:</label>
            <input type="password" name="password" required placeholder="Nhập mật khẩu (vd: pass123)">
            <button type="submit">Mã hóa (Encrypt)</button>
        </form>
        <div id="encResult" class="result" style="display:none;"></div>
    </div>

    <div class="card">
        <h2>🔓 Giải mã File (/decrypt)</h2>
        <form id="decryptForm">
            <label>Chọn file đã mã hóa (.enc):</label>
            <input type="file" name="file" required>
            <label>Khóa Base64 Key:</label>
            <input type="text" name="password" required placeholder="Dán chuỗi Key Base64 vào đây">
            <button type="submit">Giải mã (Decrypt)</button>
        </form>
        <div id="decResult" class="result" style="display:none;"></div>
    </div>

    <script>
        document.getElementById('encryptForm').onsubmit = async (e) => {
            e.preventDefault();
            const btn = e.target.querySelector('button');
            btn.innerText = 'Đang xử lý...';
            btn.disabled = true;
            try {
                const res = await fetch('/encrypt', { method: 'POST', body: new FormData(e.target) });
                const data = await res.json();
                const box = document.getElementById('encResult');
                if (!res.ok) {
                    box.style.display = 'block';
                    box.style.background = '#f8d7da';
                    box.style.borderLeft = '4px solid #dc3545';
                    box.innerHTML = '<strong>Lỗi:</strong> ' + (data.error || 'Có lỗi xảy ra');
                    return;
                }
                box.style.display = 'block';
                box.style.background = '#e8f0fe';
                box.style.borderLeft = '4px solid #1a73e8';
                box.innerHTML = '<strong>Key Base64 (Lưu lại để giải mã):</strong>'
                    + '<code style="user-select:all; display:block; padding:8px; background:#fff; margin:8px 0; border:1px solid #ccd0d5; border-radius:4px; font-weight:bold;">' + data.key + '</code>'
                    + '<a href="' + data.download_url + '" download style="display:inline-block; margin-top:8px; padding:8px 14px; background:#28a745; color:#fff; text-decoration:none; border-radius:5px; font-weight:600;">⬇️ Tải file mã hóa (' + data.filename + ')</a>';
                
                document.querySelector('#decryptForm input[name="password"]').value = data.key;
            } catch (err) {
                alert('Lỗi: ' + err);
            } finally {
                btn.innerText = 'Mã hóa (Encrypt)';
                btn.disabled = false;
            }
        };

        document.getElementById('decryptForm').onsubmit = async (e) => {
            e.preventDefault();
            const btn = e.target.querySelector('button');
            btn.innerText = 'Đang xử lý...';
            btn.disabled = true;
            try {
                const res = await fetch('/decrypt', { method: 'POST', body: new FormData(e.target) });
                const data = await res.json();
                const box = document.getElementById('decResult');
                if (!res.ok) {
                    box.style.display = 'block';
                    box.style.background = '#f8d7da';
                    box.style.borderLeft = '4px solid #dc3545';
                    box.innerHTML = '<strong>❌ ' + (data.error || 'Giải mã thất bại') + '</strong>';
                    return;
                }
                box.style.display = 'block';
                box.style.background = '#d4edda';
                box.style.borderLeft = '4px solid #28a745';
                box.innerHTML = '<strong>✅ Đã giải mã thành công!</strong><br>'
                    + '<span style="font-size:12px; color:#555;">Đường dẫn lưu trên server: ' + data.output + '</span><br>'
                    + '<a href="' + data.download_url + '" download style="display:inline-block; margin-top:8px; padding:8px 14px; background:#28a745; color:#fff; text-decoration:none; border-radius:5px; font-weight:600;">⬇️ Tải file giải mã (' + data.filename + ')</a>';
            } catch (err) {
                alert('Lỗi: ' + err);
            } finally {
                btn.innerText = 'Giải mã (Decrypt)';
                btn.disabled = false;
            }
        };
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HOME_HTML)

@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(FILES_DIR, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return "File not found", 404

@app.route('/encrypt', methods=['POST'])
def encrypt():
    try:
        f = request.files['file']
        password = request.form['password']
        save_path = os.path.join(FILES_DIR, f.filename)
        f.save(save_path)
        key = aes_utils.encrypt_file_aes(save_path, password)
        enc_filename = f.filename + '.enc'
        return jsonify({
            "key": key,
            "filename": enc_filename,
            "download_url": f"/download/{enc_filename}"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/decrypt', methods=['POST'])
def decrypt():
    try:
        f = request.files['file']
        password = request.form['password']
        save_path = os.path.join(FILES_DIR, f.filename)
        f.save(save_path)
        out_path = aes_utils.decrypt_file_aes(save_path, password)
        dec_filename = os.path.basename(out_path)
        return jsonify({
            "output": out_path,
            "filename": dec_filename,
            "download_url": f"/download/{dec_filename}"
        })
    except Exception as e:
        return jsonify({"error": f"Khóa Key không khớp với file đã chọn hoặc sai mật khẩu! (Chi tiết: {str(e)})"}), 400

if __name__ == '__main__':
    app.run()
