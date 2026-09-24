<?php
define('CLI_SCRIPT', true);
require('/var/www/html/config.php');

$helper = new \core\files\curl_security_helper();
$test_url = 'http://host.docker.internal:5000/oauth/token';

$res = $helper->url_is_blocked($test_url);
echo "Is '$test_url' blocked by Moodle cURL security? " . ($res ? "YES, BLOCKED!" : "NO, ALLOWED!") . "\n";
if ($res) {
    echo "Block reason: " . $helper->get_blocked_url_string() . "\n";
}
