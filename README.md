# 🏫 ThuctapTT - Mekosoft | Cổng Định Danh Tập Trung (MekoID)

**Đơn vị thực tập:** MekoSoft  
**Kỳ:** Đợt 3 / 2026  
**Đề tài:** Xây dựng Cổng Định Danh Tập Trung (MekoID) & SSO cho Hệ Sinh Thái Giáo Dục  

---

## 📌 Tổng quan hệ thống

Hệ thống **MekoID** là một Identity Provider (IdP) tập trung theo chuẩn **OpenID Connect Core 1.0** (dựa trên OAuth 2.0), cho phép người dùng đăng nhập một lần (Single Sign-On) và truy cập xuyên suốt các ứng dụng trong hệ sinh thái giáo dục MekoSoft:

| Ứng dụng | Port | Vai trò |
| :--- | :--- | :--- |
| **MekoID IdP** | `:5000` | Identity Provider – Cấp Token, Quản lý Phiên toàn cục |
| **Moodle LMS** (Docker) | `:8080` | Service Provider 1 – Hệ thống Quản lý Đào tạo |
| **MekoBook Reader** | `:5002` | Service Provider 2 – Thư viện Giáo trình số |

---

## 📁 Cấu trúc dự án

```
ThuctapTT-MekoSoft/
│
├── sso-demo/                              # 🔑 MekoID IdP & Ứng dụng Demo
│   ├── idp_server.py                      # Máy chủ MekoID (OIDC, JWT, SSO, SLO)
│   ├── app_moodle.py                      # SP1: Moodle LMS Demo (Port 5001)
│   ├── app_mekobook.py                    # SP2: MekoBook Reader Demo (Port 5002)
│   └── run_demo.py                        # Launcher khởi chạy toàn bộ hệ thống demo
│
├── moodle-test/                           # 🐳 Moodle LMS Thật (Docker)
│   ├── Dockerfile                         # Build Moodle 4.5 + PHP 8.2 Apache
│   ├── docker-compose.yml                 # Cụm Moodle + MariaDB 11
│   ├── HUONG_DAN_TICH_HOP_MOODLE_SSO_MEKOID.md  # 📖 Hướng dẫn & báo cáo kỹ thuật
│   └── scripts/
│       └── apply_all_patches.php          # Script vá lỗi tự động (1 lệnh duy nhất)
│
├── liferay-6.2/                           # Liferay Portal Docker Stack
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── HUONG_DAN_TICH_HOP_MOODLE_SSO_MEKOID.md   # Tài liệu kỹ thuật tích hợp SSO
└── .gitignore
```

---

## 🚀 Khởi chạy nhanh

### 1. Khởi động MekoID IdP + Ứng dụng Demo

```bash
cd sso-demo
python run_demo.py
# Hoặc chạy riêng IdP:
python idp_server.py
```

Sau khi khởi động:
- **MekoID IdP:**   http://localhost:5000
- **Moodle Demo:** http://localhost:5001
- **MekoBook:**    http://localhost:5002

### 2. Khởi động Moodle LMS Thật (Docker)

```bash
cd moodle-test
docker compose up -d
```

Sau khi container khởi động xong, áp dụng bản vá SSO:

```bash
docker cp scripts/apply_all_patches.php moodle-test-moodle-1:/var/www/html/
docker exec moodle-test-moodle-1 php /var/www/html/apply_all_patches.php
docker exec moodle-test-moodle-1 rm /var/www/html/apply_all_patches.php
```

---

## 🔑 Tài khoản kiểm thử

| Username | Mật khẩu | Vai trò |
| :--- | :--- | :--- |
| `sinhvien` | `123` | Học viên – Nguyễn Văn Sinh Viên |
| `giangvien` | `123` | Giảng viên – Trần Thị Giảng Viên |
| `admin` | `123` | Quản trị viên |

---

## 📖 Tài liệu kỹ thuật

Xem chi tiết hướng dẫn tích hợp, báo cáo sự cố và cách xử lý tại:  
👉 [`HUONG_DAN_TICH_HOP_MOODLE_SSO_MEKOID.md`](./HUONG_DAN_TICH_HOP_MOODLE_SSO_MEKOID.md)

---

## 🏗️ Kiến trúc OIDC

```
Trình duyệt
   │── Bấm "Log in using MekoID"
   │
   ▼
/auth/oauth2/login.php?id=1&sesskey=...   (Moodle tạo state có sesskey)
   │
   ▼
http://localhost:5000/oauth/authorize     (MekoID hiển thị trang đăng nhập)
   │
   ▼
http://localhost:8080/admin/oauth2callback.php?code=...&state=...
   │
   ▼ (Kênh back-channel Server-to-Server)
http://host.docker.internal:5000/oauth/token     → Moodle đổi Code lấy Access Token
http://host.docker.internal:5000/oauth/userinfo  → Moodle lấy thông tin User
   │
   ▼
Dashboard Moodle ✅
```
