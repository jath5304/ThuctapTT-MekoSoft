<?php
define('CLI_SCRIPT', true);
require('/var/www/html/config.php');

// Simulate GET params as received from the log
$_GET['state'] = '/auth/oauth2/login.php?wantsurl=http%3A%2F%2Flocalhost%3A8080%2F&sesskey=qLzMGDoS90&id=1';
$_GET['code'] = 'cf29a16a';

$state = required_param('state', PARAM_LOCALURL);
echo "state: $state\n";

$redirecturl = new moodle_url($state);
echo "redirecturl params: " . json_encode($redirecturl->params()) . "\n";

$redirecturl->param('oauth2code', 'cf29a16a');
echo "final redirect url: " . $redirecturl->out(false) . "\n";
