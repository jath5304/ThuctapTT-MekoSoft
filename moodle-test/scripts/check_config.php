<?php
define('CLI_SCRIPT', true);
require('/var/www/html/config.php');
echo 'wwwroot: ' . $CFG->wwwroot . PHP_EOL;
echo 'cookiesecure: ' . ($CFG->cookiesecure ?? 'not set') . PHP_EOL;
echo 'cookiesamesite: ' . ($CFG->cookiesamesite ?? 'not set') . PHP_EOL;
echo 'sessioncookiepath: ' . ($CFG->sessioncookiepath ?? '/') . PHP_EOL;
echo 'dbtype: ' . $CFG->dbtype . PHP_EOL;
