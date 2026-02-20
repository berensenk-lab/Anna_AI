#!/usr/bin/env python3
"""Generate requirements.txt from pyproject.toml"""

import re
from pathlib import Path

# Read pyproject.toml
pyproject_path = Path(__file__).parent / "pyproject.toml"
with open(pyproject_path, 'r') as f:
    content = f.read()

# Extract main dependencies section
match = re.search(r'dependencies = \[(.*?)\]', content, re.DOTALL)
if match:
    deps_str = match.group(1)
    deps = re.findall(r'"([^"]+)"', deps_str)
    
    # Write to requirements.txt
    req_path = Path(__file__).parent / "requirements.txt"
    with open(req_path, 'w') as f:
        for dep in sorted(deps):
            f.write(dep + '\n')
    
    print(f'[OK] Generated requirements.txt with {len(deps)} dependencies')
    print(f'[OK] Saved to {req_path}')
else:
    print('[ERROR] Could not parse dependencies from pyproject.toml')
