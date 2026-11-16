"""Reproducible full temple rebuild; fails if a builder or final GLB export fails."""
import subprocess
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BLENDER = Path(r'C:\Program Files\Blender Foundation\Blender 5.3\blender.exe')
OUT = ROOT / 'output' / 'review' / 'rebuild'
OUT.mkdir(parents=True, exist_ok=True)
results = []
for script in sorted((ROOT / 'blender').glob('build_*_temple.py')):
    result = subprocess.run([str(BLENDER), '--background', '--python',
        str(ROOT / 'blender' / 'rebuild_temple.py'), '--', str(script)],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace')
    (OUT / (script.stem + '.log')).write_text(result.stdout, encoding='utf-8')
    passed = result.returncode == 0 and 'REBUILT ' in result.stdout and 'Traceback' not in result.stdout
    results.append({'builder': script.name, 'passed': passed, 'exit_code': result.returncode})
    print(('PASS ' if passed else 'FAIL ') + script.name, flush=True)
    (OUT / 'results.json').write_text(json.dumps(results, indent=2), encoding='utf-8')
sys.exit(0 if all(row['passed'] for row in results) else 1)
