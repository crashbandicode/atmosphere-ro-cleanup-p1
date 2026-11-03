#!/usr/bin/env python3
"""Run actual RO function/result guards with injected OS boundaries; prove old code fails."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile

root = Path(__file__).resolve().parents[2]
test = Path(__file__).resolve().parent
ro_path = 'stratosphere/ro/source/impl/ro_service_impl.cpp'
version_path = 'stratosphere/ams_mitm/source/set_mitm/setsys_mitm_service.cpp'

def function(text):
    start = text.index('    Result MapManualLoadModuleMemory(')
    opening = text.index('{', start)
    depth = 1
    for end in range(opening + 1, len(text)):
        depth += (text[end] == '{') - (text[end] == '}')
        if depth == 0:
            return text[start:end + 1]
    raise ValueError('Unbalanced production function')

current = (root / ro_path).read_text()
baseline = subprocess.check_output(['git', '-C', str(root), 'show', '1.12.1:' + ro_path], text=True)
format_expression = re.search(r'(util::SNPrintf\(display_version, sizeof\(display_version\), .*?\));',
                              (root / version_path).read_text())[1]
template = (test / 'harness.cpp.in').read_text()
records = []
with tempfile.TemporaryDirectory(prefix='atmosphere-ro-p1-') as folder:
    temporary = Path(folder)
    for label, source in [('patched', current), ('baseline', baseline)]:
        cpp = temporary / f'{label}.cpp'
        exe = temporary / label
        cpp.write_text(template.replace('@@PRODUCTION_FUNCTION@@', function(source))
                       .replace('@@PRODUCTION_FORMAT@@', format_expression))
        compile_result = subprocess.run([
            '/usr/bin/c++', '-std=gnu++23', '-O2', '-Wall', '-Wextra', '-Werror',
            '-DATMOSPHERE_OS_LINUX', '-DATMOSPHERE_ARCH_X64', '-DATMOSPHERE_BOARD_GENERIC_LINUX',
            '-DATMOSPHERE_IS_STRATOSPHERE', '-DATMOSPHERE_GIT_BRANCH="ro-cleanup-p1"',
            '-DATMOSPHERE_GIT_REVISION="ro-cleanup-p1-host-test"', '-DATMOSPHERE_GIT_HASH=0',
            '-I' + str(root / 'libraries/libvapours/include'), str(cpp), '-o', str(exe)],
            capture_output=True, text=True, timeout=60)
        if compile_result.returncode:
            print(compile_result.stdout + compile_result.stderr)
            raise SystemExit(compile_result.returncode)
        result = subprocess.run([str(exe)], capture_output=True, text=True, timeout=10)
        records.append(dict(label=label, function_sha256=hashlib.sha256(function(source).encode()).hexdigest(),
                            returncode=result.returncode, stdout=result.stdout, stderr=result.stderr))
        if label == 'patched':
            assert result.returncode == 0, records[-1]
        else:
            assert result.returncode == 42 and 'parse failure cleanup missing or repeated' in result.stderr, records[-1]
print(json.dumps(dict(production_result_macros=True, cases=records,
                     limits='OS/context boundaries are injected; this is not a hardware page-lifecycle test.'), indent=2))
