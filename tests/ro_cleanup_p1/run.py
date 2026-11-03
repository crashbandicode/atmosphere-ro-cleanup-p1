# SPDX-License-Identifier: GPL-2.0-only
"""Exercise the production map/parse block and real result guards with OS calls stubbed."""
import subprocess
import tempfile
from pathlib import Path

root = Path(__file__).resolve().parents[2]
path = "stratosphere/ro/source/impl/ro_service_impl.cpp"
baseline = "6b0c077b4c608a3a2ee712b8dc35fee87ceb62e8"
template = Path(__file__).with_name("harness.cpp.in").read_text()
flags = "-std=gnu++23 -O2 -Wall -Wextra -Werror -DATMOSPHERE_OS_LINUX"
flags += " -DATMOSPHERE_ARCH_X64 -DATMOSPHERE_BOARD_GENERIC_LINUX -DATMOSPHERE_IS_STRATOSPHERE"
with tempfile.TemporaryDirectory(prefix="ro-p1-") as directory:
    cpp, exe = Path(directory) / "test.cpp", Path(directory) / "test"
    for revision in ("patched", baseline):
        source = (root / path).read_text() if revision == "patched" else subprocess.check_output(
            ["git", "-C", str(root), "show", revision + ":" + path], text=True, timeout=15)
        body = source.split("Result MapManualLoadModuleMemory(", 1)[1]
        body = body.split("/* Map the NRO. */", 1)[1].split("/* Set NRO perms. */", 1)[0]
        cpp.write_text(template.replace("@@BODY@@", body))
        subprocess.run(["/usr/bin/c++", *flags.split(), "-I" + str(root / "libraries/libvapours/include"),
                        str(cpp), "-o", str(exe)], check=True, timeout=60)
        result = subprocess.run([str(exe)], timeout=5)
        assert result.returncode == (0 if revision == "patched" else 42), revision
        print(f"{revision}: exit {result.returncode} (map failure, parse failure, success)")
