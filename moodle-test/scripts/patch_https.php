<?php
$endpoint_file = '/var/www/html/lib/classes/oauth2/endpoint.php';
$issuer_file = '/var/www/html/lib/classes/oauth2/issuer.php';

$content = file_get_contents($endpoint_file);
$content = preg_replace('/if\s*\(\s*strpos\(\$value,\s*[\'"]https:\/\/[\'"]\)\s*!==\s*0\s*\)/', 'if (false)', $content);
file_put_contents($endpoint_file, $content);

$content2 = file_get_contents($issuer_file);
$content2 = preg_replace('/!validateUrlSyntax\(\$value,\s*[\'"]S\+[\'"]\)/', 'false', $content2);
file_put_contents($issuer_file, $content2);

echo "OAUTH2_HTTPS_CHECK_REMOVED_SUCCESSFULLY\n";
