import re

endpoint_file = '/var/www/html/lib/classes/oauth2/endpoint.php'
issuer_file = '/var/www/html/lib/classes/oauth2/issuer.php'

# Patch endpoint.php
with open(endpoint_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace https check
content_patched = re.sub(
    r'if\s*\(\s*strpos\(\$value,\s*[\'"]https://[\'"]\)\s*!==\s*0\s*\)',
    'if (false)',
    content
)
with open(endpoint_file, 'w', encoding='utf-8') as f:
    f.write(content_patched)

# Patch issuer.php
with open(issuer_file, 'r', encoding='utf-8') as f:
    content2 = f.read()

content2_patched = re.sub(
    r'!validateUrlSyntax\(\$value,\s*[\'"]S\+[\'"]\)',
    'false',
    content2
)
with open(issuer_file, 'w', encoding='utf-8') as f:
    f.write(content2_patched)

print('OAUTH2_HTTPS_CHECK_REMOVED_SUCCESSFULLY')
