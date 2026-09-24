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

CLIENT_ID = "moodle"
CLIENT_SECRET = "secret_moodle_123"
IDP_AUTH_URL = "http://localhost:5000/oauth/authorize"
IDP_TOKEN_URL = "http://localhost:5000/oauth/token"
IDP_LOGOUT_URL = "http://localhost:5000/oauth/logout"
REDIRECT_URI = "http://localhost:5001/callback"

# Quản lý phiên cục bộ của Moodle LMS: { local_session_id: user_info }
LOCAL_SESSIONS = {}

PAGE_TEMPLATE = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Moodle LMS - Hệ Thống Đào Tạo Trực Tuyến</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #f1f5f9; margin: 0; padding: 0; color: #1e293b; }
        .navbar { background: #ea580c; color: white; padding: 16px 32px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .navbar h2 { margin: 0; font-size: 20px; }
        .container { max-width: 900px; margin: 40px auto; background: white; padding: 32px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
        .btn-login { background: #0284c7; color: white; padding: 12px 24px; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; text-decoration: none; display: inline-block; }
        .btn-logout { background: #ef4444; color: white; padding: 8px 16px; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; text-decoration: none; font-size: 13px; }
        .profile-card { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; margin-top: 20px; }
        .badge { background: #ea580c; color: white; padding: 2px 8px; border-radius: 12px; font-size: 12px; }
        .course-list { list-style: none; padding: 0; }
        .course-list li { background: #fff; border: 1px solid #cbd5e1; margin-bottom: 8px; padding: 12px; border-radius: 6px; display: flex; justify-content: space-between; }
    </style>
</head>
<body>
<div class="navbar">
    <h2>🎓 Moodle LMS (Cổng Học Trực Tuyến)</h2>
    <div>
        {% if user %}
            <span>Xin chào, <b>{{ user.name }}</b> ({{ user.role }})</span>
            <a href="/logout" class="btn-logout" style="margin-left: 12px;">Đăng Xuất (SLO)</a>
        {% endif %}
    </div>
</div>

<div class="container">
    {% if not user %}
        <div style="text-align: center; padding: 40px 0;">
            <div style="font-size: 60px; margin-bottom: 16px;">📚</div>
            <h3>Chào mừng bạn đến với Hệ thống Đào tạo Moodle LMS</h3>
            <p style="color: #64748b; margin-bottom: 24px;">Bạn chưa đăng nhập. Vui lòng xác thực tài khoản qua Cổng Định Danh Tập Trung.</p>
            <a href="/login" class="btn-login">🔑 Đăng Nhập Bằng MekoID (SSO)</a>
        </div>
    {% else %}
        <div class="profile-card">
            <h3>{{ user.avatar }} Thông tin tài khoản (Được cấp từ MekoID Token)</h3>
            <p>• Họ và tên: <b>{{ user.name }}</b></p>
            <p>• Email: <b>{{ user.email }}</b></p>
            <p>• Vai trò: <span class="badge">{{ user.role }}</span></p>
        </div>

        <h4 style="margin-top: 32px;">📖 Khóa học của bạn trong học kỳ:</h4>
        <ul class="course-list">
            <li><span>Kiến trúc Hệ thống & SSO / IAM</span> <span style="color: #16a34a; font-weight: bold;">Đang diễn ra</span></li>
            <li><span>Lập trình Ứng dụng Phân tán</span> <span style="color: #16a34a; font-weight: bold;">Đang diễn ra</span></li>
            <li><span>An toàn & Bảo mật Thông tin</span> <span style="color: #64748b;">Chưa mở</span></li>
        </ul>
        
        <div style="margin-top: 24px; padding: 12px; background: #e0f2fe; border-left: 4px solid #0284c7; font-size: 13px; color: #0369a1;">
            💡 <b>Thử nghiệm SSO:</b> Bạn đã đăng nhập vào Moodle. Bây giờ hãy mở tab mới và truy cập ứng dụng thứ hai: <a href="http://localhost:5002" target="_blank" style="font-weight: bold; color: #0284c7;">http://localhost:5002 (MekoBook)</a> để thấy cơ chế Zero-Click SSO!
        </div>
    {% endif %}
</div>
</body>
</html>
"""

@app.route('/')
def index():
    session_id = request.cookies.get('moodle_session')
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
    """NHẬN MÃ CODE TỪ IDP VÀ GỌI BACK-CHANNEL ĐỔI TOKEN"""
    code = request.args.get('code')
    if not code:
        return "Lỗi: Không nhận được mã code từ IdP", 400

    # Gọi Backend sang IdP để đổi Code lấy Token & UserInfo
    token_resp = requests.post(IDP_TOKEN_URL, data={
        "code": code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    })

    if token_resp.status_code != 200:
        return f"Lỗi đổi token: {token_resp.text}", 400

    token_data = token_resp.json()
    user_info = token_data.get("user")

    # Tạo phiên cục bộ cho Moodle
    local_session_id = str(uuid.uuid4())
    LOCAL_SESSIONS[local_session_id] = user_info

    resp = make_response(redirect('/'))
    resp.set_cookie('moodle_session', local_session_id, path='/')
    print(f"[Moodle SP1] Tạo phiên cục bộ cho '{user_info['username']}'. Hoàn tất đăng nhập!")
    return resp

@app.route('/backchannel-logout', methods=['POST'])
def backchannel_logout():
    """NHẬN LỆNH HỦY PHIÊN TỪ IDP (SLO)"""
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    
    # Hủy toàn bộ phiên trong bộ nhớ của user này
    keys_to_delete = [sid for sid, user in LOCAL_SESSIONS.items() if user.get("username") == username]
    for sid in keys_to_delete:
        del LOCAL_SESSIONS[sid]

    print(f"[Moodle SP1 - SLO] Nhận lệnh từ IdP: Đã hủy {len(keys_to_delete)} phiên của '{username}'!")
    return jsonify({"status": "logged_out"}), 200

@app.route('/logout')
def logout():
    """ĐĂNG XUẤT CỤC BỘ VÀ CHUYỂN HƯỚNG TỚI IDP ĐỂ SLO"""
    session_id = request.cookies.get('moodle_session')
    LOCAL_SESSIONS.pop(session_id, None)

    resp = make_response(redirect(f"{IDP_LOGOUT_URL}?redirect_uri=http://localhost:5001/"))
    resp.delete_cookie('moodle_session', path='/')
    return resp

if __name__ == '__main__':
    print("=" * 60)
    print("🎓 Moodle LMS (SP1) đang chạy tại http://localhost:5001")
    print("=" * 60)
    app.run(port=5001, debug=False)
