<?php
// Simulate raw query string:
// code=cf29a16a&state=/auth/oauth2/login.php?wantsurl=http%3A%2F%2Flocalhost%3A8080%2F&sesskey=qLzMGDoS90&id=1
$query = "code=cf29a16a&state=/auth/oauth2/login.php?wantsurl=http%3A%2F%2Flocalhost%3A8080%2F&sesskey=qLzMGDoS90&id=1";
parse_str($query, $get);
echo "state: " . $get['state'] . "\n";
echo "sesskey: " . ($get['sesskey'] ?? 'none') . "\n";
echo "id: " . ($get['id'] ?? 'none') . "\n";
