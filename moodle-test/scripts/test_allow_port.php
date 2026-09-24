<?php
define('CLI_SCRIPT', true);
require('/var/www/html/config.php');

// Add port 5000 to allowed ports
set_config('curlsecurityallowedport', "443\n80\n5000");

$helper = new \core\files\curl_security_helper();
$test_url = 'http://host.docker.internal:5000/oauth/token';

$res = $helper->url_is_blocked($test_url);
echo "With port 5000 added: Is '$test_url' blocked? " . ($res ? "YES, STILL BLOCKED!" : "NO, ALLOWED!") . "\n";
if ($res) {
    echo "Block reason: " . $helper->get_blocked_url_string() . "\n";
}
