<?php
define('CLI_SCRIPT', true);
require('/var/www/html/config.php');

$issuer = new \core\oauth2\issuer(1);
$client = \core\oauth2\api::get_user_oauth_client($issuer, new moodle_url('/'));

// Use reflection to read protected property/method
$ref = new ReflectionClass($client);
$method = $ref->getMethod('token_url');
$method->setAccessible(true);
$token_url = $method->invoke($client);

echo "Token URL: " . $token_url . "\n";
