# main.py
# This file launches the tkinter GUI app. That’s it. It's the bouncer for PowerApp.
# Entry point. Instantiates and runs the GUI.

import sys
import os

# Check if this script is being run directly (not imported as a module)
if __name__ == '__main__':
    # Ensure only one instance of the compiled exe runs at a time
    if getattr(sys, 'frozen', False):
        exe_name = os.path.basename(sys.executable)
        current_pid = os.getpid()
        os.system(f'taskkill /F /FI "PID ne {current_pid}" /IM "{exe_name}" 2>nul')

    # Import the main application class from the UI module
    from PowerApp.PowerUI import PowerApp

    # 🔧 Instantiate the PowerApp:
    # Creates the main window, sets up UI, loads images, and hooks into the logic backend
    app = PowerApp()

    # 🚀 Start the application loop:
    # Keeps the window open, listens for user input, and handles events
    app.run()
