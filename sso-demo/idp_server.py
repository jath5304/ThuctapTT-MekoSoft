import uuid
import sys
import time
import base64
import json
import hmac
import hashlib
from flask import Flask, request, redirect, render_template_string, jsonify, make_response
import requests

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

app = Flask(__name__)

# ============================================================
# HELPER: TẠO JSON WEB TOKEN (JWT) CHUẨN OIDC (HS256)
# ============================================================
def create_jwt(payload, secret="mekoid_secret_2026"):
    header = {"typ": "JWT", "alg": "HS256"}
    h_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip('=')
    p_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip('=')
    sig = hmac.new(secret.encode(), f"{h_b64}.{p_b64}".encode(), hashlib.sha256).digest()
    s_b64 = base64.urlsafe_b64encode(sig).decode().rstrip('=')
    return f"{h_b64}.{p_b64}.{s_b64}"

# ============================================================
# 1. DATABASE NGƯỜI DÙNG GIẢ LẬP (User Repository / SSoT)
# ============================================================
USERS_DB = {
    "sinhvien": {
        "password": "123",
        "name": "Nguyễn Văn Sinh Viên",
        "given_name": "Sinh Viên",
        "family_name": "Nguyễn Văn",
        "email": "sinhvien@meko.edu.vn",
        "role": "Học viên",
        "avatar": "🎓"
    },
    "giangvien": {
        "password": "123",
        "name": "ThS. Trần Thị Giảng Viên",
        "given_name": "Giảng Viên",
        "family_name": "Trần Thị",
        "email": "giangvien@meko.edu.vn",
        "role": "Giảng viên",
        "avatar": "👨‍🏫"
    },
    "admin": {
        "password": "123",
        "name": "Quản Trị Viên Hệ Thống",
        "given_name": "Quản Trị Viên",
        "family_name": "Hệ Thống",
        "email": "admin@meko.edu.vn",
        "role": "Admin",
        "avatar": "🛡️"
    }
}

# ============================================================
# 2. CLIENTS ĐÃ ĐĂNG KÝ (Hỗ trợ cả Demo & Moodle, Liferay thật)
# ============================================================
REGISTERED_CLIENTS = {
    "moodle": {
        "name": "Moodle LMS",
        "secret": "secret_moodle_123",
        "redirect_uris": [
            "http://localhost:5001/callback",
            "http://localhost:8080/admin/oauth2callback.php",
            "http://localhost:8081/admin/oauth2callback.php",
            "http://127.0.0.1:8080/admin/oauth2callback.php"
        ],
        "logout_uri": "http://localhost:5001/backchannel-logout"
    },
    "mekobook": {
        "name": "MekoBook (Thư viện Sách số)",
        "secret": "secret_mekobook_456",
        "redirect_uris": ["http://localhost:5002/callback"],
        "logout_uri": "http://localhost:5002/backchannel-logout"
    },
    "liferay": {
        "name": "Liferay Portal",
        "secret": "secret_liferay_123",
        "redirect_uris": [
            "http://localhost:8082/c/portal/login/openidconnect",
            "http://localhost:8080/c/portal/login/openidconnect"
        ],
        "logout_uri": ""
    }
}

# ============================================================
# 3. QUẢN LÝ PHIÊN TOÀN CỤC & TOKENS
# ============================================================
GLOBAL_SESSIONS = {}   # { session_id: { "username": ..., "clients": {...} } }
AUTH_CODES = {}        # { code: { "username": ..., "client_id": ..., "redirect_uri": ... } }
ACCESS_TOKENS = {}     # { token: { "username": ..., "client_id": ..., "expires": ... } }

# ============================================================
# GIAO DIỆN HTML LOGIN (MekoID Central Login Page)
# ============================================================
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>MekoID - Cổng Định Danh Tập Trung</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0f172a; margin: 0; display: flex; justify-content: center; align-items: center; min-height: 100vh; color: #f8fafc; }
        .card { background: #1e293b; border-radius: 16px; padding: 40px; width: 420px; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.5); border: 1px solid #334155; }
        .logo { text-align: center; margin-bottom: 24px; }
        .logo h1 { margin: 0; font-size: 28px; color: #38bdf8; letter-spacing: 1px; }
        .logo p { margin: 6px 0 0; font-size: 13px; color: #94a3b8; }
        .badge { display: inline-block; background: #0284c7; color: white; padding: 5px 12px; border-radius: 20px; font-size: 12px; margin-top: 10px; font-weight: bold; }
        .input-group { margin-bottom: 18px; text-align: left; }
        .input-group label { display: block; font-size: 13px; color: #cbd5e1; margin-bottom: 6px; font-weight: 500; }
        .input-group input { width: 100%; padding: 12px; border-radius: 8px; border: 1px solid #475569; background: #0f172a; color: white; box-sizing: border-box; font-size: 14px; }
        .input-group input:focus { border-color: #38bdf8; outline: none; }
        .btn { width: 100%; padding: 12px; background: #0284c7; color: white; border: none; border-radius: 8px; font-size: 15px; font-weight: 600; cursor: pointer; transition: 0.2s; }
        .btn:hover { background: #0369a1; }
        .error { background: #ef444420; border: 1px solid #ef4444; color: #fca5a5; padding: 10px; border-radius: 8px; font-size: 13px; margin-bottom: 16px; }
        .demo-accounts { margin-top: 24px; padding-top: 16px; border-top: 1px dashed #334155; font-size: 12px; color: #94a3b8; }
        .demo-pill { display: inline-block; background: #334155; padding: 3px 8px; border-radius: 4px; color: #38bdf8; cursor: pointer; margin: 2px; }
    </style>
</head>
<body>
<div class="card">
    <div class="logo">
        <h1>🔐 MekoID</h1>
        <p>Cổng Định Danh Tập Trung (Identity Provider)</p>
        <div class="badge">Đang xác thực cho: {{ client_name }}</div>
    </div>

    {% if error %}
    <div class="error">⚠️ {{ error }}</div>
    {% endif %}

    <form method="POST" action="/oauth/login">
        <input type="hidden" name="client_id" value="{{ client_id }}">
        <input type="hidden" name="redirect_uri" value="{{ redirect_uri }}">
        <input type="hidden" name="state" value="{{ state }}">
        <input type="hidden" name="scope" value="{{ scope }}">
        
        <div class="input-group">
            <label>Tên đăng nhập / Mã định danh</label>
            <input type="text" name="username" id="username" placeholder="sinhvien / giangvien / admin" required>
        </div>
        <div class="input-group">
            <label>Mật khẩu</label>
            <input type="password" name="password" id="password" placeholder="123" required>
        </div>
        <button type="submit" class="btn">Đăng Nhập Ngay</button>
    </form>

    <div class="demo-accounts">
        💡 <b>Tài khoản thử nghiệm (Mật khẩu: 123):</b><br>
        • Học viên: <span class="demo-pill" onclick="fill('sinhvien')">sinhvien</span><br>
        • Giảng viên: <span class="demo-pill" onclick="fill('giangvien')">giangvien</span><br>
        • Quản trị: <span class="demo-pill" onclick="fill('admin')">admin</span>
    </div>
</div>
<script>
    function fill(user) {
        document.getElementById('username').value = user;
        document.getElementById('password').value = '123';
    }
</script>
</body>
</html>
"""

# ============================================================
# CÁC ENDPOINT CHUẨN OPENID CONNECT & OAUTH 2.0
# ============================================================

@app.route('/.well-known/openid-configuration')
def openid_configuration():
    """
    OIDC DISCOVERY ENDPOINT (RFC 8414)
    Moodle và Liferay gọi vào đây để tự động nhận diện toàn bộ endpoint của IdP.
    """
    base_url = request.host_url.rstrip('/')
    config = {
        "issuer": base_url,
        "authorization_endpoint": f"{base_url}/oauth/authorize",
        "token_endpoint": f"{base_url}/oauth/token",
        "userinfo_endpoint": f"{base_url}/oauth/userinfo",
        "end_session_endpoint": f"{base_url}/oauth/logout",
        "jwks_uri": f"{base_url}/oauth/jwks",
        "response_types_supported": ["code", "token", "id_token", "code id_token"],
        "subject_types_supported": ["public"],
        "id_token_signing_alg_values_supported": ["HS256", "RS256"],
        "scopes_supported": ["openid", "profile", "email"],
        "token_endpoint_auth_methods_supported": ["client_secret_post", "client_secret_basic"],
        "claims_supported": [
            "sub", "iss", "name", "preferred_username",
            "given_name", "family_name", "email", "email_verified", "picture", "role"
        ]
    }
    resp = jsonify(config)
    resp.headers["Access-Control-Allow-Origin"] = "*"
    return resp

@app.route('/oauth/jwks')
def jwks():
    """JWKS Public Keys Stub"""
    return jsonify({"keys": []})

@app.route('/oauth/authorize')
def authorize():
    """
    ENDPOINT TIẾP NHẬN YÊU CẦU SSO TỪ CLIENT (Moodle, Liferay, MekoBook)
    """
    client_id = request.args.get('client_id', 'unknown')
    redirect_uri = request.args.get('redirect_uri', '')
    state = request.args.get('state', '')
    scope = request.args.get('scope', 'openid')

    # Lấy tên client hiển thị
    client_info = REGISTERED_CLIENTS.get(client_id, {"name": client_id})
    client_name = client_info.get("name", client_id)

    # 1. KIỂM TRA COOKIE PHIÊN TOÀN CỤC (GLOBAL SSO SESSION)
    sso_cookie = request.cookies.get('mekoid_sso_session')
    
    if sso_cookie and sso_cookie in GLOBAL_SESSIONS:
        # => ĐÃ CÓ PHIÊN TOÀN CỤC TẠI IDP => THỰC HIỆN ZERO-CLICK SSO!
        user_session = GLOBAL_SESSIONS[sso_cookie]
        username = user_session["username"]
        user_session["clients"].add(client_id)

        # Cấp mã Authorization Code
        code = str(uuid.uuid4())[:12]
        AUTH_CODES[code] = {
            "username": username,
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "scope": scope,
            "expires": time.time() + 300
        }
        
        print(f"[IdP - SSO HIT] '{username}' đã đăng nhập trước đó! Tự động chuyển hướng về '{client_name}'.")
        import urllib.parse
        q_params = {"code": code}
        if state:
            q_params["state"] = state
        delim = "&" if "?" in redirect_uri else "?"
        return redirect(f"{redirect_uri}{delim}{urllib.parse.urlencode(q_params)}")

    # 2. CHƯA CÓ PHIÊN => HIỂN THỊ GIAO DIỆN ĐĂNG NHẬP
    return render_template_string(
        LOGIN_TEMPLATE,
        client_name=client_name,
        client_id=client_id,
        redirect_uri=redirect_uri,
        state=state,
        scope=scope,
        error=None
    )

@app.route('/oauth/login', methods=['POST'])
def process_login():
    """XỬ LÝ FORM ĐĂNG NHẬP KHI NGƯỜI DÙNG SUBMIT"""
    username = request.form.get('username')
    password = request.form.get('password')
    client_id = request.form.get('client_id')
    redirect_uri = request.form.get('redirect_uri')
    state = request.form.get('state', '')
    scope = request.form.get('scope', 'openid')

    user = USERS_DB.get(username)
    if not user or user["password"] != password:
        client_info = REGISTERED_CLIENTS.get(client_id, {"name": client_id})
        return render_template_string(
            LOGIN_TEMPLATE,
            client_name=client_info.get("name", client_id),
            client_id=client_id,
            redirect_uri=redirect_uri,
            state=state,
            scope=scope,
            error="Tên đăng nhập hoặc mật khẩu không chính xác!"
        ), 401

    # 1. TẠO PHIÊN TOÀN CỤC (GLOBAL SSO SESSION)
    sso_session_id = str(uuid.uuid4())
    GLOBAL_SESSIONS[sso_session_id] = {
        "username": username,
        "clients": {client_id}
    }

    # 2. CẤP AUTHORIZATION CODE
    code = str(uuid.uuid4())[:12]
    AUTH_CODES[code] = {
        "username": username,
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": scope,
        "expires": time.time() + 300
    }
    print(f"[IdP - NEW LOGIN] '{username}' đăng nhập thành công. Tạo Global Session={sso_session_id[:8]}... Cấp Code={code}")

    # 3. SET COOKIE SSO VÀ CHUYỂN HƯỚNG VỀ CLIENT
    import urllib.parse
    q_params = {"code": code}
    if state:
        q_params["state"] = state
    delim = "&" if "?" in redirect_uri else "?"
    resp = make_response(redirect(f"{redirect_uri}{delim}{urllib.parse.urlencode(q_params)}"))
    resp.set_cookie('mekoid_sso_session', sso_session_id, path='/', httponly=True)
    return resp

@app.route('/oauth/token', methods=['POST'])
def token_endpoint():
    """
    TOKEN ENDPOINT (Hỗ trợ chuẩn OAuth 2.0 & OIDC)
    Client gửi mã code lên đổi lấy Access Token và ID Token (JWT).
    """
    code = request.form.get('code')
    client_id = request.form.get('client_id')
    
    # Hỗ trợ cả xác thực client qua Basic Auth Header
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Basic '):
        try:
            raw_creds = base64.b64decode(auth_header[6:]).decode()
            if ':' in raw_creds:
                client_id = raw_creds.split(':')[0]
        except Exception:
            pass

    auth_data = AUTH_CODES.pop(code, None)
    if not auth_data:
        return jsonify({"error": "invalid_grant", "error_description": "Authorization code không hợp lệ hoặc đã dùng!"}), 400

    username = auth_data["username"]
    user_info = USERS_DB[username]
    base_url = request.host_url.rstrip('/')

    # 1. Sinh Access Token
    access_token = f"meko_at_{uuid.uuid4().hex}"
    ACCESS_TOKENS[access_token] = {
        "username": username,
        "client_id": client_id,
        "expires": time.time() + 3600
    }

    # 2. Sinh ID Token (Chuẩn JWT OIDC)
    now = int(time.time())
    id_token_payload = {
        "iss": base_url,
        "sub": username,
        "aud": client_id,
        "exp": now + 3600,
        "iat": now,
        "auth_time": now,
        "name": user_info["name"],
        "given_name": user_info["given_name"],
        "family_name": user_info["family_name"],
        "preferred_username": username,
        "email": user_info["email"],
        "email_verified": True,
        "role": user_info["role"]
    }
    id_token = create_jwt(id_token_payload)

    response_data = {
        "access_token": access_token,
        "token_type": "Bearer",
        "expires_in": 3600,
        "id_token": id_token,
        "scope": "openid profile email",
        # Trả kèm user info trong body cho các client tùy chỉnh
        "user": {
            "id": username,
            "username": username,
            "name": user_info["name"],
            "email": user_info["email"],
            "role": user_info["role"],
            "avatar": user_info["avatar"]
        }
    }
    
    resp = jsonify(response_data)
    resp.headers["Access-Control-Allow-Origin"] = "*"
    return resp

@app.route('/oauth/userinfo', methods=['GET', 'POST'])
def userinfo_endpoint():
    """
    OIDC USERINFO ENDPOINT (RFC 6749 & OpenID Connect Core 1.0)
    Moodle và Liferay gọi vào đây bằng Bearer Token để lấy thông tin tài khoản.
    """
    # 1. Lấy Bearer Token từ Header hoặc Query Param
    auth_header = request.headers.get('Authorization', '')
    token = None
    if auth_header.startswith('Bearer '):
        token = auth_header[7:].strip()
    else:
        token = request.args.get('access_token') or request.form.get('access_token')

    if not token or token not in ACCESS_TOKENS:
        return jsonify({"error": "invalid_token", "error_description": "Access Token không hợp lệ hoặc đã hết hạn"}), 401

    token_data = ACCESS_TOKENS[token]
    username = token_data["username"]
    user_info = USERS_DB[username]
    base_url = request.host_url.rstrip('/')

    # Trả về các trường chuẩn OIDC (khớp 100% với User Field Mapping của Moodle & Liferay)
    profile = {
        "sub": username,
        "id": username,
        "preferred_username": username,
        "username": username,
        "name": user_info["name"],
        "given_name": user_info["given_name"],
        "family_name": user_info["family_name"],
        "firstname": user_info["given_name"],
        "lastname": user_info["family_name"],
        "email": user_info["email"],
        "email_verified": True,
        "picture": f"{base_url}/static/avatar.png",
        "role": user_info["role"]
    }

    print(f"[IdP - UserInfo] Đã cung cấp Profile của '{username}' cho Client: {token_data.get('client_id')}")
    resp = jsonify(profile)
    resp.headers["Access-Control-Allow-Origin"] = "*"
    return resp

@app.route('/oauth/logout')
def logout():
    """
    ENDPOINT ĐĂNG XUẤT ĐỒNG BỘ (SINGLE LOGOUT - SLO)
    """
    sso_cookie = request.cookies.get('mekoid_sso_session')
    redirect_uri = request.args.get('redirect_uri', 'http://localhost:5001/')

    if sso_cookie and sso_cookie in GLOBAL_SESSIONS:
        session_data = GLOBAL_SESSIONS.pop(sso_cookie)
        username = session_data["username"]
        logged_clients = session_data["clients"]

        print(f"[IdP - SLO] Kích hoạt Đăng xuất đồng bộ cho '{username}' trên: {list(logged_clients)}")

        for cid in logged_clients:
            client_conf = REGISTERED_CLIENTS.get(cid)
            if client_conf and client_conf.get("logout_uri"):
                try:
                    requests.post(client_conf["logout_uri"], json={"username": username}, timeout=2)
                    print(f"[IdP - SLO] Đã gửi lệnh hủy phiên tới: {client_conf['name']}")
                except Exception as e:
                    print(f"[IdP - SLO Warning] Không thể kết nối tới {cid}: {e}")

    resp = make_response(redirect(redirect_uri))
    resp.delete_cookie('mekoid_sso_session', path='/')
    return resp

@app.route('/')
def home():
    """Trang chủ IdP hiển thị trạng thái"""
    return jsonify({
        "service": "MekoID Central Identity Provider",
        "status": "UP",
        "version": "2.0-OIDC",
        "supported_protocols": ["OpenID Connect Core 1.0", "OAuth 2.0 Authorization Code Flow"],
        "active_global_sessions": len(GLOBAL_SESSIONS),
        "oidc_discovery_url": f"{request.host_url.rstrip('/')}/.well-known/openid-configuration"
    })

if __name__ == '__main__':
    print("=" * 65)
    print("🚀 MekoID OIDC Identity Provider v2.0 đang chạy tại http://localhost:5000")
    print("📋 OIDC Discovery: http://localhost:5000/.well-known/openid-configuration")
    print("=" * 65)
    app.run(host='0.0.0.0', port=5000, debug=False)
