# main.py
# This file launches the tkinter GUI app. That’s it. It's the bouncer for PowerApp.
# Entry point. Instantiates and runs the GUI.

import sys
import os
import subprocess
import tempfile


def close_previous_instance():
    """Ensure only one instance of the compiled app runs at a time (any OS)."""
    if os.name == "nt":
        exe_name = os.path.basename(sys.executable)
        current_pid = os.getpid()
        subprocess.run(
            ['taskkill', '/F', '/FI', f'PID ne {current_pid}', '/IM', exe_name],
            creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0x08000000),
            stderr=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL
        )
        return
    # macOS / Linux: PID file in the temp dir
    import signal
    pid_file = os.path.join(tempfile.gettempdir(), f"super_power_options_{os.getuid()}.pid")
    try:
        with open(pid_file) as f:
            old_pid = int(f.read().strip())
        if old_pid != os.getpid():
            # Only kill it if that PID is still *this* app (PIDs get reused)
            comm = subprocess.run(["ps", "-p", str(old_pid), "-o", "comm="],
                                  capture_output=True, text=True).stdout.strip()
            if comm and os.path.basename(comm) == os.path.basename(sys.executable)[:len(os.path.basename(comm))]:
                os.kill(old_pid, signal.SIGTERM)
    except (OSError, ValueError):
        pass  # No previous instance (or it's already gone)
    try:
        with open(pid_file, "w") as f:
            f.write(str(os.getpid()))
    except OSError:
        pass


# Check if this script is being run directly (not imported as a module)
if __name__ == '__main__':
    if getattr(sys, 'frozen', False):
        close_previous_instance()

    # Import the main application class from the UI module
    from PowerApp.PowerUI import PowerApp

    # 🔧 Instantiate the PowerApp:
    # Creates the main window, sets up UI, loads images, and hooks into the logic backend
    app = PowerApp()

    # 🚀 Start the application loop:
    # Keeps the window open, listens for user input, and handles events
    app.run()
