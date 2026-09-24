<?php
define('CLI_SCRIPT', true);
require('/var/www/html/config.php');

$issuer = new \core\oauth2\issuer(1);
$client = \core\oauth2\api::get_user_oauth_client($issuer, new moodle_url('/'));

echo "Token URL from client: " . $client->token_url() . "\n";

// Test cURL to token_url
$ch = curl_init($client->token_url());
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, http_build_query([
    'code' => 'test_code',
    'client_id' => 'moodle',
    'client_secret' => 'secret_moodle_123',
    'grant_type' => 'authorization_code'
]));
$response = curl_exec($ch);
$http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
$error = curl_error($ch);
curl_close($ch);

echo "HTTP Code: $http_code\n";
echo "cURL Error: $error\n";
echo "Response: $response\n";
