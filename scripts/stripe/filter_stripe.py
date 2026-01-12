#!/usr/bin/env python3
import sys
import os
import re

file_path = 'nsc_admin/settings.py'
if os.path.exists(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content
    # Replace hardcoded Stripe keys with empty strings
    content = re.sub(r'sk_live_[^",\s]+', '""', content)
    content = re.sub(r'pk_live_[^",\s]+', '""', content)

    if content != original:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

