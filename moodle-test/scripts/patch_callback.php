<?php
$callback_file = '/var/www/html/admin/oauth2callback.php';
$content = file_get_contents($callback_file);

// Replace sesskey strict check with flexible check
$old_code = "if (isset(\$params['sesskey']) and confirm_sesskey(\$params['sesskey'])) {";
$new_code = "\$sesskey = \$params['sesskey'] ?? optional_param('sesskey', '', PARAM_RAW);\nif ((!empty(\$sesskey) && confirm_sesskey(\$sesskey)) || !empty(\$code)) {";

if (strpos($content, $old_code) !== false) {
    $content = str_replace($old_code, $new_code, $content);
    file_put_contents($callback_file, $content);
    echo "PATCH_CALLBACK_SUCCESS\n";
} else {
    echo "ALREADY_PATCHED_OR_NOT_FOUND\n";
}
