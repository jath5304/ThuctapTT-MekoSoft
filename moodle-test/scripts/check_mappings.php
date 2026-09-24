<?php
define('CLI_SCRIPT', true);
require('/var/www/html/config.php');

$mappings = $DB->get_records('oauth2_user_field_mapping');
echo "Count mappings: " . count($mappings) . "\n";
foreach ($mappings as $m) {
    echo "Mapping: {$m->externalfield} => {$m->internalfield}\n";
}
