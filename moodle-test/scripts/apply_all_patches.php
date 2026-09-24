<?php
/**
 * SCRIPT TỔNG HỢP TOÀN BỘ CÁC BẢN VÁ CHO MOODLE OAUTH2 / OIDC SSO (LOCAL DEV)
 * Sử dụng: docker cp apply_all_patches.php moodle-test-moodle-1:/var/www/html/
 *          docker exec moodle-test-moodle-1 php /var/www/html/apply_all_patches.php
 */

define('CLI_SCRIPT', true);
require('/var/www/html/config.php');

echo "=========================================================\n";
echo "   TIẾN HÀNH ÁP DỤNG TẤT CẢ CÁC BẢN VÁ SSO CHO MOODLE\n";
echo "=========================================================\n\n";

// 1. Cho phép HTTP trong OAuth2 Endpoints & Issuer
$endpoint_file = '/var/www/html/lib/classes/oauth2/endpoint.php';
$issuer_file = '/var/www/html/lib/classes/oauth2/issuer.php';

$c1 = file_get_contents($endpoint_file);
$c1 = preg_replace('/if\s*\(\s*strpos\(\$value,\s*[\'"]https:\/\/[\'"]\)\s*!==\s*0\s*\)/', 'if (false)', $c1);
file_put_contents($endpoint_file, $c1);

$c2 = file_get_contents($issuer_file);
$c2 = preg_replace('/!validateUrlSyntax\(\$value,\s*[\'"]S\+[\'"]\)/', 'false', $c2);
file_put_contents($issuer_file, $c2);
echo "[OK] 1. Đã gỡ bỏ kiểm tra bắt buộc HTTPS trong OAuth2.\n";

// 2. Cho phép cURL gọi tới cổng 5000 (SSRF Protection Bypass cho Local IdP)
set_config('curlsecurityallowedport', "443\n80\n5000");
echo "[OK] 2. Đã thêm cổng 5000 vào danh sách cổng cURL được phép.\n";

// 3. Cấu hình Cookie phiên cho môi trường HTTP localhost
set_config('cookiesecure', 0);
set_config('cookiesamesite', 'Lax');
set_config('sessioncookiepath', '/');
echo "[OK] 3. Đã cấu hình Cookie phiên: cookiesecure=0, SameSite=Lax.\n";

// 4. Tắt yêu cầu xác nhận email cho MekoID & Kích hoạt tài khoản
$DB->set_field('oauth2_issuer', 'requireconfirmation', 0, ['id' => 1]);
$DB->set_field('user', 'confirmed', 1, ['confirmed' => 0]);
echo "[OK] 4. Đã tắt 'Require email confirmation' và kích hoạt các tài khoản SSO.\n";

// 5. Vá lỗi callback tự phục hồi tham số id và sesskey
$callback_file = '/var/www/html/admin/oauth2callback.php';
$cb_content = file_get_contents($callback_file);
if (strpos($cb_content, 'Auto-recover id') === false) {
    $target = "\$redirecturl->param('oauth2code', \$code);\n    redirect(\$redirecturl);";
    $replacement = "// Auto-recover id and sesskey if split by unencoded state
    if (!\$redirecturl->get_param('id')) {
        \$id = optional_param('id', 1, PARAM_INT);
        \$redirecturl->param('id', \$id);
    }
    if (!\$redirecturl->get_param('sesskey')) {
        \$sess = optional_param('sesskey', null, PARAM_RAW);
        if (\$sess) {
            \$redirecturl->param('sesskey', \$sess);
        }
    }
    \$redirecturl->param('oauth2code', \$code);
    redirect(\$redirecturl);";
    $cb_content = str_replace($target, $replacement, $cb_content);
    file_put_contents($callback_file, $cb_content);
}
echo "[OK] 5. Đã vá lỗi chuyển tiếp callback Moodle.\n";

echo "\n🎉 HOÀN TẤT TOÀN BỘ CÁC BẢN VÁ!\n";
