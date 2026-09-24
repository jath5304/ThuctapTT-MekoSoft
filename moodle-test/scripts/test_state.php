<?php
define('CLI_SCRIPT', true);
require('/var/www/html/config.php');

$issuers = $DB->get_records('oauth2_issuer');
foreach ($issuers as $i) {
    echo "Issuer ID: {$i->id} - Name: {$i->name}\n";
}

// Test what clean_param does on typical state
$test_state = '/auth/oauth2/login.php?wantsurl=http%3A%2F%2Flocalhost%3A8080%2F&sesskey=12345&id=1';
$cleaned = clean_param($test_state, PARAM_LOCALURL);
echo "Cleaned state: $cleaned\n";

$url = new moodle_url($cleaned);
echo "Params in moodle_url: " . json_encode($url->params()) . "\n";
echo "Out URL: " . $url->out(false) . "\n";
