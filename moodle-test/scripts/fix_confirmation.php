<?php
define('CLI_SCRIPT', true);
require('/var/www/html/config.php');

// 1. Tắt yêu cầu xác nhận email cho MekoID
$DB->set_field('oauth2_issuer', 'requireconfirmation', 0, ['id' => 1]);
echo "Updated MekoID issuer: requireconfirmation = 0\n";

// 2. Kích hoạt tài khoản sinhvien và tất cả tài khoản OAuth2 đã tạo
$DB->set_field('user', 'confirmed', 1, ['confirmed' => 0]);
echo "Confirmed all unconfirmed users in database!\n";

// Kiểm tra lại
$user = $DB->get_record('user', ['username' => 'sinhvien']);
echo "User 'sinhvien' status: confirmed = {$user->confirmed}\n";
