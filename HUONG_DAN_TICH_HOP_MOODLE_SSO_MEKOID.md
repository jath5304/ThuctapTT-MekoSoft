# HƯỚNG DẪN TÍCH HỢP SSO / OIDC GIỮA MEKOID VÀ MOODLE LMS
**Dự án:** Cổng Định Danh Tập Trung (MekoID) & Hệ Sinh Thái Giáo Dục MekoSoft  
**Môi trường:** Docker (Moodle 4.5 + MariaDB 11) & Python Flask OIDC IdP Server  
**Ngày cập nhật:** 24/09/2026  

---

## 1. TỔNG QUAN KIẾN TRÚC & MÔ HÌNH KẾT NỐI

```
  ┌─────────────────────────────────────────────────────────────┐
  │                 TRÌNH DUYỆT (BROWSER)                       │
  │  - Truy cập: http://localhost:8080 (Moodle LMS)            │
  │  - Chuyển hướng xác thực: http://localhost:5000 (MekoID)   │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
     ┌───────────────────────────┴───────────────────────────┐
     │                                                       │
     ▼                                                       ▼
┌───────────────────────────────┐               ┌───────────────────────────────┐
│     MOODLE LMS CONTAINER      │               │       MEKOID IDP SERVER       │
│  (Docker Port :8080)          │               │      (Host Port :5000)        │
│                               │               │                               │
│  • Plugin: auth_oauth2        │               │  • OpenID Connect v2.0        │
│  • Client ID: moodle          │               │  • Global Session Manager     │
│  • Quản lý phiên học tập      │               │  • Cấp Auth Code & JWT Token  │
└───────────────┬───────────────┘               └───────────────▲───────────────┘
                │                                               │
                │ Trao đổi Token & UserInfo (Server-to-Server)   │
                │ Gọi qua: http://host.docker.internal:5000/... │
                └───────────────────────────────────────────────┘
```

* **MekoID IdP (Port 5000):** Chạy trên máy Host (Windows), đóng vai trò Máy chủ Định danh Trung tâm chuẩn OpenID Connect Core 1.0.
* **Moodle LMS (Port 8080):** Chạy bên trong Docker Container, sử dụng module `auth_oauth2` đóng vai trò Service Provider (Relying Party).
* **Kênh liên lạc Back-Channel:** Do Moodle nằm trong container, khi Moodle gọi Server-to-Server sang MekoID để đổi Token và lấy UserInfo, Moodle sử dụng địa chỉ mạng đặc biệt: `http://host.docker.internal:5000`.

---

## 2. CẤU TRÚC THƯ MỤC DỰ ÁN (`moodle-test/`)

Sau khi dọn dẹp và chuẩn hóa, toàn bộ thư mục được tổ chức khoa học:

```
moodle-test/
├── Dockerfile                              # Build Moodle 4.5 trên nền PHP 8.2 Apache
├── docker-compose.yml                      # Cấu hình cụm Moodle + MariaDB 11
├── HUONG_DAN_TICH_HOP_MOODLE_SSO_MEKOID.md # Tài liệu kỹ thuật này
└── scripts/                                # Thư mục công cụ & bản vá
    ├── apply_all_patches.php               # ⭐ SCRIPT TỔNG HỢP TOÀN BỘ BẢN VÁ (Chạy 1 lệnh duy nhất)
    ├── fix_cookie.php                      # Cấu hình cookie phiên HTTP
    ├── fix_confirmation.php                # Tắt bắt buộc xác nhận email & kích hoạt user
    ├── patch_https.php                     # Gỡ bỏ ép buộc HTTPS trong OAuth2
    ├── patch_callback_id.php               # Vá lỗi phục hồi tham số id và sesskey
    └── test_*.php / check_*.php            # Bộ công cụ chẩn đoán và kiểm thử
```

---

## 3. CÁC BƯỚC CẤU HÌNH TRÊN GIAO DIỆN QUẢN TRỊ MOODLE

### Bước 1: Kích hoạt Phương thức Xác thực OAuth 2
1. Đăng nhập tài khoản Admin vào Moodle: `http://localhost:8080`.
2. Vào: **Site administration** $\rightarrow$ **Plugins** $\rightarrow$ **Authentication** $\rightarrow$ **Manage authentication**.
3. Tìm dòng **OAuth 2** và bấm vào biểu tượng con mắt để chuyển sang trạng thái **Enabled**.

### Bước 2: Tạo Dịch vụ Định danh MekoID
1. Vào: **Site administration** $\rightarrow$ **Server** $\rightarrow$ **OAuth 2 services**.
2. Bấm nút **Create new custom service** và điền:
   * **Name:** `MekoID`
   * **Client ID:** `moodle`
   * **Client secret:** `secret_moodle_123`
   * **Service base URL:** `http://host.docker.internal:5000`
   * Tích chọn: **Show on login page**
   * Bỏ tích chọn: **Require email confirmation** (rất quan trọng)
   * $\rightarrow$ Bấm **Save changes**.

### Bước 3: Cấu hình Endpoints
Bấm vào biểu tượng **Configure endpoints** (cột Actions của dòng MekoID), thêm lần lượt 3 endpoints:

| Tên Endpoint (Name) | Đường dẫn (URL) | Ghi chú |
| :--- | :--- | :--- |
| **`authorization_endpoint`** | `http://localhost:5000/oauth/authorize` | Trình duyệt người dùng gọi |
| **`token_endpoint`** | `http://host.docker.internal:5000/oauth/token` | Container Moodle gọi sang IdP |
| **`userinfo_endpoint`** | `http://host.docker.internal:5000/oauth/userinfo` | Container Moodle gọi sang IdP |
| **`end_session_endpoint`** | `http://localhost:5000/oauth/logout` | Đăng xuất đồng bộ (SLO) |

### Bước 4: Cấu hình Ánh xạ thông tin người dùng (User Field Mappings)
Bấm vào biểu tượng **Configure user field mappings** cạnh MekoID và thêm 4 trường:
* `email` $\rightarrow$ `email`
* `given_name` $\rightarrow$ `firstname`
* `family_name` $\rightarrow$ `lastname`
* `sub` $\rightarrow$ `username`

---

## 4. BÁO CÁO SỰ CỐ & CÁC BẢN VÁ KỸ THUẬT (TROUBLESHOOTING)

Trong quá trình tích hợp thực tế, hệ thống đã gặp 6 vấn đề bảo mật/kỹ thuật kinh điển của Moodle và đã được xử lý triệt để:

### Sự cố 1: `PHP setting max_input_vars must be at least 5000`
* **Nguyên nhân:** Moodle 4.5 yêu cầu số lượng biến input form tối thiểu 5000 để chạy bộ cài đặt và phân quyền, mặc định của PHP là 1000.
* **Giải pháp:** Bổ sung cấu hình `max_input_vars = 5000` vào `/usr/local/etc/php/conf.d/moodle.ini` và reload Apache.

### Sự cố 2: Lỗi bắt buộc HTTPS (`sslonlyaccess`) khi thêm Endpoint
* **Nguyên nhân:** Moodle mặc định kiểm tra cứng `strpos($value, 'https://') !== 0` trong `lib/classes/oauth2/endpoint.php` và `issuer.php` để ngăn chặn rò rỉ token trên production.
* **Giải pháp:** Gỡ bỏ điều kiện kiểm tra bắt buộc HTTPS trong mã nguồn nội bộ để cho phép chạy thử nghiệm trên `http://localhost` và `http://host.docker.internal`.

### Sự cố 3: Lỗi mất phiên `Your session has most likely timed out` (`invalidsesskey`)
* **Nguyên nhân:**
  1. Cookie phiên `MoodleSession` ban đầu bị gắn cờ `Secure = true`, khiến trình duyệt từ chối gửi cookie khi chuyển hướng qua giao thức HTTP.
  2. MekoID ban đầu không mã hóa URL (URL-encode) cho tham số `state`, dẫn đến chuỗi bị cắt cụt tại ký tự `&sesskey=...`.
* **Giải pháp:**
  * Cấu hình `$CFG->cookiesecure = false;` và `$CFG->cookiesamesite = 'Lax';` trong `config.php`.
  * Cập nhật `idp_server.py` sử dụng `urllib.parse.urlencode()` cho toàn bộ redirect URLs.

### Sự cố 4: Lỗi thiếu tham số `A required parameter (id) was missing`
* **Nguyên nhân:** Moodle yêu cầu tham số `id` (Issuer ID) khi xử lý callback `/auth/oauth2/login.php?id=1`. Do tham số `state` bị cắt rời, `id` bị rớt thành query param tự do thay vì nằm trong URL chuyển tiếp.
* **Giải pháp:** Vá file `admin/oauth2callback.php` cơ chế **tự động phục hồi `id` và `sesskey`**: nếu thiếu `id` trên đường dẫn chuyển tiếp, Moodle sẽ tự động bắt lại từ request hoặc gán mặc định `id = 1` của MekoID.

### Sự cố 5: Lỗi `Could not upgrade OAuth 2 token. HTTP status for remote endpoint: {$a}`
* **Nguyên nhân cốt lõi (SSRF Protection):** Moodle có cơ chế bảo mật mạng nội bộ `curl_security_helper`. Mặc định Moodle **chỉ cho phép cURL ra cổng 80 và 443**. Vì MekoID chạy trên cổng **`5000`**, Moodle chủ động chặn kết nối cURL trước khi gửi gói tin, khiến mã HTTP trả về là `0`.
* **Giải pháp:** Bổ sung cổng `5000` vào danh sách cho phép của Moodle:  
  `set_config('curlsecurityallowedport', "443\n80\n5000");`

### Sự cố 6: Lỗi `This account is pending email confirmation`
* **Nguyên nhân:** Tùy chọn `Require email confirmation` của dịch vụ OAuth 2 trong Moodle bị bật, khiến tài khoản sinh viên mới tạo bị gán `confirmed = 0`.
* **Giải pháp:** Cập nhật cơ sở dữ liệu `mdl_oauth2_issuer`: gán `requireconfirmation = 0` và kích hoạt tài khoản `confirmed = 1`.

---

## 5. TRIỂN KHAI NHANH QUA SCRIPT TỰ ĐỘNG (`apply_all_patches.php`)

Nếu cần triển khai lại từ đầu trên một máy mới, sau khi khởi động container Moodle và tạo Issuer MekoID, bạn chỉ cần chạy **đúng 1 lệnh** để áp dụng toàn bộ 5 bản vá trên:

```powershell
# Chạy từ thư mục moodle-test trên máy tính:
docker cp scripts/apply_all_patches.php moodle-test-moodle-1:/var/www/html/
docker exec moodle-test-moodle-1 php /var/www/html/apply_all_patches.php
docker exec moodle-test-moodle-1 rm /var/www/html/apply_all_patches.php
```

---

## 6. KỊCH BẢN KIỂM THỬ NGHIỆM THU (TEST CASE)

| Kịch bản | Thao tác | Hiện tượng quan sát được | Kết luận |
| :--- | :--- | :--- | :--- |
| **1. Đăng nhập Moodle lần đầu** | Vào `http://localhost:8080/login/index.php`, bấm nút **"Log in using MekoID"**, nhập tài khoản `sinhvien / 123`. | Trình duyệt chuyển sang MekoID $\rightarrow$ xác thực thành công $\rightarrow$ Moodle tự tạo tài khoản và chuyển thẳng vào **Dashboard** của học viên *Nguyễn Văn Sinh Viên*. | **PASS** (SSO Thành công) |
| **2. Zero-Click SSO sang MekoBook** | Giữ nguyên tab Moodle, mở tab mới vào `http://localhost:5002` (MekoBook Reader), bấm **"Đăng Nhập Bằng MekoID"**. | Trình duyệt tự nhận diện phiên MekoID $\rightarrow$ **Vào thẳng trang đọc sách mà không cần gõ mật khẩu**. | **PASS** (Zero-Click SSO) |
| **3. Đăng xuất đồng bộ (SLO)** | Tại tab MekoBook (`:5002`), bấm nút **"Đăng Xuất Đồng Bộ (SLO)"**. Quay lại tab Moodle (`:8080`) bấm **F5**. | Phiên tại MekoBook bị hủy $\rightarrow$ Tab Moodle bấm F5 cũng lập tức bị văng ra màn hình đăng nhập. | **PASS** (SLO Hoàn tất) |
