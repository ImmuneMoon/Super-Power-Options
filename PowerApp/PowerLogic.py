# PowerLogic.py
# Handles all the backend timer logic, system power commands, and triggering the doom (aka sleep/restart/shutdown)
# Manages timer execution, threading, and system-level power actions.

import os
import time
import platform
import subprocess
import ctypes

class PowerManager:
    def __init__(self, app):
        self.app = app  # Reference to the UI for callback updates, so we can update the display from here
        self.timer_seconds = 0
        self.target_time = 0
        self.cancel_flag = False  # Used to bail out of countdown if user cancels
        self.action = None  # What are we doing? Action to perform: 'sleep', 'hibernate', 'restart', or 'shutdown'
        self.timer_running = False

    def set_action(self, action):
        self.action = action  # Store the desired action

    def set_timer(self, seconds):
        self.timer_seconds = seconds
        self.cancel_flag = False  # Reset cancel flag for a fresh countdown

    def start_countdown(self):
        if self.timer_running:
            return
        self.timer_running = True
        self.cancel_flag = False
        self.target_time = time.time() + self.timer_seconds
        
        # Prevent sleep while timer is running
        if platform.system() == "Windows":
            ES_CONTINUOUS = 0x80000000
            ES_SYSTEM_REQUIRED = 0x00000001
            ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED)
        
        self.app.on_timer_started() # Notify UI that timer started

    def tick(self):
        if not self.timer_running:
            return

        if self.cancel_flag:
            self.timer_running = False
            self.app.update_timer_display("Cancelled")
            self._restore_sleep()
            self.app.on_timer_ended()
            return
            
        remaining = int(self.target_time - time.time())
        if remaining > 0:
            self.app.update_timer_display(remaining)
        else:
            self.timer_running = False
            self.app.update_timer_display(0)
            self._restore_sleep()
            self.app.on_timer_ended()
            self._play_sound()  # Ding dong, time’s up
            self.execute_action()  # Trigger the system-level event

    def _restore_sleep(self):
        if platform.system() == "Windows":
            ES_CONTINUOUS = 0x80000000
            ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS)

    def cancel(self):
        self.cancel_flag = True  # Abort countdown execution. User said "Wait I played games instead of doing my homework, I've actually gotta be up all night now"

    def execute_action(self):
        # System calls for each power state. Windows-only.
        if self.action == 'sleep':
            # SetSuspendState(bHibernate, bForce, bWakeupEventsDisabled)
            ctypes.windll.powrprof.SetSuspendState(False, False, False)
        elif self.action == 'hibernate':
            ctypes.windll.powrprof.SetSuspendState(True, False, False)
        elif self.action == 'restart':
            os.system("shutdown /r /t 0")
        elif self.action == 'shutdown':
            os.system("shutdown /s /t 0")

    def _play_sound(self):
        # Attempts to play an alert sound cross-platform
        sound_path = os.path.join(os.path.dirname(__file__), "..", "assets", "alert.wav")
        if platform.system() == "Windows":
            import winsound
            if os.path.exists(sound_path):
                winsound.PlaySound(sound_path, winsound.SND_FILENAME)
        else:
            if os.path.exists(sound_path):
                subprocess.call(["aplay", sound_path])
