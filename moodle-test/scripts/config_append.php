<?php
define('MOODLE_INTERNAL', true);
// Đặt vào cuối config.php
// Fix session và cookie cho môi trường HTTP localhost
$CFG->cookiesecure = false;           // Tắt yêu cầu HTTPS cho cookie
$CFG->cookiesamesite = 'Lax';         // Cho phép gửi cookie khi redirect từ bên ngoài (IdP)
$CFG->sessioncookiepath = '/';        // Cookie áp dụng toàn bộ site
$CFG->sslproxy = false;               // Không dùng SSL proxy
