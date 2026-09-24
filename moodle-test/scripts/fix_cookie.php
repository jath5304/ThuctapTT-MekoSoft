<?php
define('CLI_SCRIPT', true);
require('/var/www/html/config.php');

// Fix 1: Tắt cookiesecure (đang là http://localhost, không cần SSL)
set_config('cookiesecure', 0);

// Fix 2: Đặt SameSite=Lax để cookie được gửi khi redirect từ IdP về Moodle
set_config('cookiesamesite', 'Lax');

// Fix 3: Đảm bảo session path đúng
set_config('sessioncookiepath', '/');

echo 'cookiesecure set to: ' . get_config('core', 'cookiesecure') . PHP_EOL;
echo 'cookiesamesite set to: ' . get_config('core', 'cookiesamesite') . PHP_EOL;
echo 'sessioncookiepath set to: ' . get_config('core', 'sessioncookiepath') . PHP_EOL;
echo 'DONE' . PHP_EOL;
