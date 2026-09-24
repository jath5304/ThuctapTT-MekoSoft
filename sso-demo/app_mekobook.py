import uuid
import sys
from flask import Flask, request, redirect, render_template_string, make_response
import requests

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

app = Flask(__name__)

CLIENT_ID = "mekobook"
CLIENT_SECRET = "secret_mekobook_456"
IDP_AUTH_URL = "http://localhost:5000/oauth/authorize"
IDP_TOKEN_URL = "http://localhost:5000/oauth/token"
IDP_LOGOUT_URL = "http://localhost:5000/oauth/logout"
REDIRECT_URI = "http://localhost:5002/callback"

# Quản lý phiên cục bộ của MekoBook Reader: { local_session_id: user_info }
LOCAL_SESSIONS = {}

PAGE_TEMPLATE = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>MekoBook - Thư Viện Giáo Trình Số</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #f8fafc; margin: 0; padding: 0; color: #0f172a; }
        .navbar { background: #059669; color: white; padding: 16px 32px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .navbar h2 { margin: 0; font-size: 20px; }
        .container { max-width: 900px; margin: 40px auto; background: white; padding: 32px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
        .btn-login { background: #059669; color: white; padding: 12px 24px; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; text-decoration: none; display: inline-block; }
        .btn-logout { background: #dc2626; color: white; padding: 8px 16px; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; text-decoration: none; font-size: 13px; }
        .profile-card { background: #ecfdf5; border: 1px solid #a7f3d0; border-radius: 8px; padding: 20px; margin-top: 20px; }
        .badge { background: #059669; color: white; padding: 2px 8px; border-radius: 12px; font-size: 12px; }
        .book-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-top: 20px; }
        .book-card { border: 1px solid #e2e8f0; padding: 16px; border-radius: 8px; text-align: center; background: #fff; }
        .book-card h4 { margin: 8px 0 4px; font-size: 15px; }
    </style>
</head>
<body>
<div class="navbar">
    <h2>📖 MekoBook (Thư Viện Giáo Trình Số 3D)</h2>
    <div>
        {% if user %}
            <span>Xin chào, <b>{{ user.name }}</b> ({{ user.role }})</span>
            <a href="/logout" class="btn-logout" style="margin-left: 12px;">Đăng Xuất Đồng Bộ (SLO)</a>
        {% endif %}
    </div>
</div>

<div class="container">
    {% if not user %}
        <div style="text-align: center; padding: 40px 0;">
            <div style="font-size: 60px; margin-bottom: 16px;">📚</div>
            <h3>Chào mừng bạn đến với Thư viện Giáo trình MekoBook</h3>
            <p style="color: #64748b; margin-bottom: 24px;">Bạn chưa đăng nhập. Vui lòng bấm nút bên dưới để xác thực qua MekoID.</p>
            <a href="/login" class="btn-login">🔑 Đăng Nhập Bằng MekoID (Zero-Click SSO)</a>
        </div>
    {% else %}
        <div class="profile-card">
            <h3>{{ user.avatar }} Phiên làm việc MekoBook (Cấp qua SSO)</h3>
            <p>• Người dùng: <b>{{ user.name }}</b> (Email: {{ user.email }})</p>
            <p>• Nhóm quyền: <span class="badge">{{ user.role }}</span></p>
        </div>

        <h4 style="margin-top: 32px;">📑 Giáo trình điện tử được phép đọc:</h4>
        <div class="book-grid">
            <div class="book-card">
                <div style="font-size: 36px;">📗</div>
                <h4>Giáo trình IAM & SSO 2026</h4>
                <p style="font-size: 12px; color: #64748b;">Mekosoft Publishing</p>
            </div>
            <div class="book-card">
                <div style="font-size: 36px;">📘</div>
                <h4>Lập Trình Web Phân Tán</h4>
                <p style="font-size: 12px; color: #64748b;">NXB Giáo Dục</p>
            </div>
            <div class="book-card">
                <div style="font-size: 36px;">📙</div>
                <h4>Bảo Mật API & OAuth2</h4>
                <p style="font-size: 12px; color: #64748b;">Chuyên khảo Kỹ thuật</p>
            </div>
        </div>

        <div style="margin-top: 24px; padding: 12px; background: #fef2f2; border-left: 4px solid #ef4444; font-size: 13px; color: #991b1b;">
            ⚠️ <b>Thử nghiệm SLO:</b> Nếu bạn bấm <b>"Đăng Xuất Đồng Bộ (SLO)"</b> ở góc phải trên, phiên ở cả MekoBook và tab Moodle (<a href="http://localhost:5001" target="_blank" style="color: #ea580c; font-weight: bold;">http://localhost:5001</a>) sẽ đều bị hủy cùng một lúc!
        </div>
    {% endif %}
</div>
</body>
</html>
"""

@app.route('/')
def index():
    session_id = request.cookies.get('mekobook_session')
    user = LOCAL_SESSIONS.get(session_id)
    return render_template_string(PAGE_TEMPLATE, user=user)

@app.route('/login')
def login():
    """CHUYỂN HƯỚNG SANG IDP XÁC THỰC (SP-Initiated SSO)"""
    state = str(uuid.uuid4())[:8]
    auth_redirect = f"{IDP_AUTH_URL}?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&state={state}"
    return redirect(auth_redirect)

@app.route('/callback')
def callback():
    """NHẬN CODE VÀ GỌI IDP ĐỔI TOKEN"""
    code = request.args.get('code')
    if not code:
        return "Lỗi: Không nhận được mã code từ IdP", 400

    token_resp = requests.post(IDP_TOKEN_URL, data={
        "code": code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    })

    if token_resp.status_code != 200:
        return f"Lỗi đổi token: {token_resp.text}", 400

    token_data = token_resp.json()
    user_info = token_data.get("user")

    # Tạo phiên cục bộ cho MekoBook
    local_session_id = str(uuid.uuid4())
    LOCAL_SESSIONS[local_session_id] = user_info

    resp = make_response(redirect('/'))
    resp.set_cookie('mekobook_session', local_session_id, path='/')
    print(f"[MekoBook SP2] Tạo phiên cục bộ cho '{user_info['username']}'. Hoàn tất đăng nhập!")
    return resp

@app.route('/backchannel-logout', methods=['POST'])
def backchannel_logout():
    """NHẬN LỆNH HỦY PHIÊN TỪ IDP (SLO)"""
    data = request.get_json(silent=True) or {}
    username = data.get("username")

    keys_to_delete = [sid for sid, user in LOCAL_SESSIONS.items() if user.get("username") == username]
    for sid in keys_to_delete:
        del LOCAL_SESSIONS[sid]

    print(f"[MekoBook SP2 - SLO] Nhận lệnh từ IdP: Đã hủy {len(keys_to_delete)} phiên của '{username}'!")
    return jsonify({"status": "logged_out"}), 200

@app.route('/logout')
def logout():
    """ĐĂNG XUẤT TẠI MEKOBOOK VÀ KÍCH HOẠT SLO TẠI IDP"""
    session_id = request.cookies.get('mekobook_session')
    LOCAL_SESSIONS.pop(session_id, None)

    resp = make_response(redirect(f"{IDP_LOGOUT_URL}?redirect_uri=http://localhost:5002/"))
    resp.delete_cookie('mekobook_session', path='/')
    return resp

if __name__ == '__main__':
    print("=" * 60)
    print("📖 MekoBook Reader (SP2) đang chạy tại http://localhost:5002")
    print("=" * 60)
    app.run(port=5002, debug=False)
