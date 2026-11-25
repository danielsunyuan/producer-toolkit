"""Write declared licence metadata for the current installed environment."""
import importlib.metadata
import json
from pathlib import Path
import sys

records = []
for distribution in sorted(importlib.metadata.distributions(), key=lambda d: d.metadata.get('Name', '').lower()):
    data = distribution.metadata
    text = (data.get('License') or '').strip()
    records.append({
        'name': data.get('Name'), 'version': distribution.version,
        'license_expression': data.get('License-Expression'),
        'license_summary': text.splitlines()[0] if text else None,
        'source_urls': data.get_all('Project-URL', []) + ([data['Home-page']] if data.get('Home-page') else []),
        'license_files': [str(p) for p in distribution.files or []
                          if 'license' in str(p).lower() or 'copying' in str(p).lower()],
    })
output = Path(sys.argv[1] if len(sys.argv) > 1 else 'license-inventory.json')
output.write_text(json.dumps(records, indent=2) + '\n', encoding='utf-8')
print(f'Recorded declared licence metadata for {len(records)} distributions.')
