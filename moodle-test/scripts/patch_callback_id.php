<?php
$callback_file = '/var/www/html/admin/oauth2callback.php';
$content = file_get_contents($callback_file);

// Ensure 'id' parameter is ALWAYS present in redirecturl
$target = "\$redirecturl->param('oauth2code', \$code);\n    redirect(\$redirecturl);";
$replacement = "// Auto-recover id and sesskey if split by unencoded state
    if (!\$redirecturl->get_param('id')) {
        \$id = optional_param('id', 1, PARAM_INT);
        \$redirecturl->param('id', \$id);
    }
    if (!\$redirecturl->get_param('sesskey')) {
        \$sess = optional_param('sesskey', null, PARAM_RAW);
        if (\$sess) {
            \$redirecturl->param('sesskey', \$sess);
        }
    }
    \$redirecturl->param('oauth2code', \$code);
    redirect(\$redirecturl);";

if (strpos($content, $target) !== false) {
    $content = str_replace($target, $replacement, $content);
    file_put_contents($callback_file, $content);
    echo "PATCH_ID_SUCCESS\n";
} else {
    echo "TARGET_NOT_FOUND\n";
}
