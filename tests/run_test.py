import os
import importlib.util

def load_test_modules():
    tests_dir = os.path.dirname(__file__)
    test_modules = []

    for file in os.listdir(tests_dir):
        if file.startswith("test_") and file.endswith(".py") and file != "run_tests.py":
            path = os.path.join(tests_dir, file)
            name = file[:-3]  # Strip .py extension

            spec = importlib.util.spec_from_file_location(name, path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            test_modules.append(module)

    return test_modules

def run_all():
    print("==== Super Power Options Test Suite ====")
    total_passed = 0
    total_failed = 0

    for mod in load_test_modules():
        if hasattr(mod, "run"):
            passed, failed = mod.run()
            total_passed += passed
            total_failed += failed
        else:
            print(f"[SKIP] {mod.__name__} has no run()")

    print(f"\n==== TEST RESULTS: {total_passed} Passed, {total_failed} Failed ====")

if __name__ == "__main__":
    run_all()
