<?php
define('CLI_SCRIPT', true);
require('/var/www/html/config.php');

// Đọc config.php hiện tại
$config_file = '/var/www/html/config.php';
$content = file_get_contents($config_file);

// Kiểm tra đã patch chưa
if (strpos($content, 'cookiesecure = false') !== false) {
    echo "ALREADY_PATCHED" . PHP_EOL;
    exit(0);
}

// Thêm các dòng config trước require_once 'lib/setup.php'
$append = "\n// === LOCAL SSO PATCH: Cho phep HTTP trong localhost ===\n";
$append .= "\$CFG->cookiesecure   = false;      // Tat bat buoc HTTPS cho cookie\n";
$append .= "\$CFG->cookiesamesite = 'Lax';      // Cho phep gui cookie khi redirect tu IdP\n";
$append .= "\$CFG->sessioncookiepath = '/';     // Cookie ap dung toan bo site\n";
$append .= "// === END PATCH ===\n";

$content = str_replace(
    "require_once(__DIR__ . '/lib/setup.php');",
    $append . "require_once(__DIR__ . '/lib/setup.php');",
    $content
);

file_put_contents($config_file, $content);
echo "PATCH_CONFIG_SUCCESS" . PHP_EOL;
