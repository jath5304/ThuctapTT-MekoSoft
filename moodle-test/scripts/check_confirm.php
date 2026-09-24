<?php
define('CLI_SCRIPT', true);
require('/var/www/html/config.php');

$issuers = $DB->get_records('oauth2_issuer');
foreach ($issuers as $i) {
    echo "Issuer: {$i->name} - requireconfirmation: {$i->requireconfirmation}\n";
}

// Check unconfirmed users created by oauth2
$users = $DB->get_records('user', ['confirmed' => 0]);
echo "Unconfirmed users count: " . count($users) . "\n";
foreach ($users as $u) {
    echo "User: {$u->username} ({$u->email}) - confirmed: {$u->confirmed}\n";
}
