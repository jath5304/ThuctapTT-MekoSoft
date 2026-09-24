<?php
// Test token endpoint from inside container
$token_url = 'http://host.docker.internal:5000/oauth/token';
$userinfo_url = 'http://host.docker.internal:5000/oauth/userinfo';

// We can test userinfo with a mock access token if one exists
echo "Testing connection to IdP endpoints from Moodle container...\n";

$ch = curl_init('http://host.docker.internal:5000/.well-known/openid-configuration');
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
$resp = curl_exec($ch);
$http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
curl_close($ch);

echo "Discovery Endpoint HTTP Status: $http_code\n";
if ($http_code === 200) {
    echo "Connection to host.docker.internal:5000 is EXCELLENT!\n";
} else {
    echo "Connection failed or returned $http_code\n";
}
