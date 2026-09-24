<?php
define('CLI_SCRIPT', true);
require('/var/www/html/config.php');

$issuer = new \core\oauth2\issuer(1);
$client = \core\oauth2\api::get_user_oauth_client($issuer, new moodle_url('/'));

// Call upgrade_token with a dummy code
try {
    $res = $client->upgrade_token('dummy_code_for_test');
    echo "Result: " . ($res ? 'TRUE' : 'FALSE') . "\n";
} catch (\Exception $e) {
    echo "Exception message: " . $e->getMessage() . "\n";
    echo "Debug info: " . ($e->debuginfo ?? 'none') . "\n";
}
