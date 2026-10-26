# build_and_deploy.py
# Native cross-platform build helper.
#   python build_and_deploy.py            -> native build for THIS OS (PyInstaller) into dist/
#   python build_and_deploy.py --check    -> print what the app detects about this system

import sys
import platform
import subprocess
from pathlib import Path

ROOT = Path(__file__).parent.resolve()


def run(cmd):
    print(f"[>] {' '.join(cmd)}")
    subprocess.run(cmd, check=True, cwd=ROOT)


def native_build():
    run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "pyinstaller"])
    run([sys.executable, "-m", "PyInstaller", "--noconfirm", "Super_Power_Options.spec"])
    out = {"Windows": "dist/Super Power Options.exe", "Darwin": "dist/Super Power Options.app"}.get(
        platform.system(), "dist/Super Power Options")
    print(f"[OK] Built {out}")


if __name__ == "__main__":
    args = set(sys.argv[1:])
    if "--check" in args:
        run([sys.executable, "-m", "PowerApp.PowerPlatform"])
    else:
        native_build()