<?php
define('CLI_SCRIPT', true);
require('/var/www/html/config.php');

$endpoints = $DB->get_records('oauth2_endpoint');
foreach ($endpoints as $e) {
    echo "Endpoint: {$e->name} => {$e->url}\n";
}
