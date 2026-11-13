#!/usr/bin/env python3
"""Makes dist/DissidiaChaos-<version>.zip (+ .sha256): the installer package. No game files and no pictures go in.
    package.py [version]"""
import hashlib
import os
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
version = sys.argv[1] if len(sys.argv) > 1 else open(os.path.join(HERE, "VERSION")).read().strip()
files = ["install_chaos.py", "install.sh", "install.bat", "extra_abilities.json", "README.md", "LICENSE", "VERSION",
         "tools/make_objx.py", "tools/make_hud.py", "docs/chaos.md"]
os.makedirs(os.path.join(HERE, "dist"), exist_ok=True)
name = "DissidiaChaos-%s" % version
out = os.path.join(HERE, "dist", name + ".zip")
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for f in files:
        info = zipfile.ZipInfo("%s/%s" % (name, f), date_time=(2026, 11, 13, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = (0o755 if f.endswith((".sh", ".py")) and not f.startswith("docs") else 0o644) << 16
        z.writestr(info, open(os.path.join(HERE, f), "rb").read())
digest = hashlib.sha256(open(out, "rb").read()).hexdigest()
open(out + ".sha256", "w").write("%s  %s\n" % (digest, os.path.basename(out)))
print(out, digest)
