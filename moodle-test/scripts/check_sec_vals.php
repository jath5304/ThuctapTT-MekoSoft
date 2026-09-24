<?php
define('CLI_SCRIPT', true);
require('/var/www/html/config.php');

echo "allowed ports: " . get_config('core', 'curlsecurityallowedport') . "\n";
echo "blocked hosts: " . get_config('core', 'curlsecurityblockedhosts') . "\n";
