import os
import sys
import tkinter as tk

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(base_path, relative_path)

def run():
    print("== Running Icon Tests ==")
    passed = 0
    failed = 0
    path = os.path
    icon_path = resource_path("assets/icon.ico")
    exists = os.path.exists(icon_path)
    print(f"[RESULT] Icon file exists: {'[OK]' if exists else '[MISSING]'}")
    if exists:
        passed += 1
    else:
        failed += 1

    png_path = resource_path("assets/icon.png")
    png_exists = os.path.exists(png_path)
    print(f"[RESULT] PNG icon exists: {'[OK]' if png_exists else '[MISSING]'}")
    if png_exists:
        passed += 1
    else:
        failed += 1

    if sys.platform == "win32" and exists:
        try:
            root = tk.Tk()
            root.iconbitmap(icon_path)
            root.withdraw()
            root.destroy()
            print("[RESULT] iconbitmap loaded successfully [OK]")
            passed += 1
        except Exception as e:
            print(f"[ERROR] iconbitmap failed [FAIL] -> {e}")
            failed += 1

    return passed, failed