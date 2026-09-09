import os
import sys

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(base_path, relative_path)

def run():
    print("== Running Asset Tests ==")
    passed = 0
    failed = 0

    images = ["Sleep_Button.png", "Restart_Button.png", "Shutdown_Button.png", "Cancel_Button.png", "icon.ico", "icon.png"]
    for img in images:
        path = resource_path(f"assets/{img}")
        if os.path.exists(path):
            print(f"[PASS] Found image: {img}")
            passed += 1
        else:
            print(f"[FAIL] Missing image: {img}")
            failed += 1

    sound_path = resource_path("assets/alert.wav")
    if os.path.exists(sound_path):
        print("[PASS] alert.wav exists")
        passed += 1
    else:
        print("[FAIL] alert.wav missing")
        failed += 1

    return passed, failed