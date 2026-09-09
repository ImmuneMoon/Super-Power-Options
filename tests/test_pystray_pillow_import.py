import os
import sys
from PIL import Image

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(base_path, relative_path)

def run():
    print("== Running Pillow Image Test ==")
    passed = 0
    failed = 0

    try:
        print(f"[INFO] Pillow version: {Image.__version__}")
        passed += 1
    except Exception as e:
        print(f"[FAIL] Could not detect Pillow version: {e}")
        failed += 1

    test_icon = resource_path("assets/icon.ico")

    try:
        img = Image.open(test_icon)
        img.verify()  # Validate it's not corrupt
        print("[PASS] icon.ico successfully loaded and verified")
        passed += 1
    except Exception as e:
        print(f"[FAIL] Failed to open/verify icon.ico: {e}")
        failed += 1

    return passed, failed
