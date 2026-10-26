import sys
import os

def run():
    print("== Running Platform Tests ==")
    passed = 0
    failed = 0

    try:
        from PowerApp import PowerPlatform
        os_id = PowerPlatform.detect_os()
        print(f"[PASS] Detected OS: {os_id} ({PowerPlatform.describe_system()})")
        passed += 1

        for action in PowerPlatform.ACTIONS:
            candidates = PowerPlatform.get_candidates(action)
            if candidates:
                print(f"[PASS] Action '{action}' has {len(candidates)} candidate(s): {[c[0] for c in candidates]}")
                passed += 1
            else:
                print(f"[FAIL] Action '{action}' has no candidate")
                failed += 1

        tray = PowerPlatform.tray_supported()
        print(f"[PASS] Tray supported: {tray}")
        passed += 1

    except Exception as e:
        print(f"[FAIL] Platform test error: {e}")
        failed += 1

    return passed, failed
