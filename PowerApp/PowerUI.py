# PowerUI.py
# GUI layer: handles user interaction and visual state using customtkinter.

import os
import sys
import customtkinter as ctk
from tkinter import messagebox
from PowerApp.PowerLogic import PowerManager
from pystray import Icon, MenuItem as item, Menu
from PIL import Image

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(base_path, relative_path)

class PowerApp:
    def __init__(self):
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        
        self.root = ctk.CTk() # Main application window
        self.root.title("⚡ Super Power Options ⚡")
        self.root.geometry("650x550")
        self.root.resizable(False, False)
        
        self.manager = PowerManager(self)
        self.load_icon()
        self.build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.hide_to_tray)

    def load_icon(self):
        app_icon_path = resource_path("assets/icon.ico")
        if os.path.exists(app_icon_path):
            try:
                self.root.iconbitmap(app_icon_path)
            except Exception as e:
                print(f"[WARN] Failed to load icon: {e}")
        else:
            print("[WARN] icon.ico not found at runtime")

    def hide_to_tray(self):
        self.root.withdraw()  # Hide window
        icon_image = Image.open(resource_path("assets/icon.ico"))
        self.tray_icon = Icon(
            "SuperPowerOptions",
            icon_image,
            menu=Menu(
                item("Restore", lambda: self.restore_window()),
                item("Exit", lambda: self.exit_app())
            )
        )
        self.tray_icon.run_detached()

    def restore_window(self):
        self.root.deiconify()
        if hasattr(self, 'tray_icon'):
            self.tray_icon.stop()

    def exit_app(self):
        if hasattr(self, 'tray_icon'):
            self.tray_icon.stop()
        self.root.quit()

    def build_ui(self):
        # Main container
        self.main_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Setup view (visible when timer is NOT running)
        self.setup_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.setup_frame.pack(fill="both", expand=True)
        
        # Title
        ctk.CTkLabel(self.setup_frame, text="Set Timer", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(0, 20))
        
        # Custom time input
        input_frame = ctk.CTkFrame(self.setup_frame, fg_color="transparent")
        input_frame.pack(pady=10)
        
        self.time_entry = ctk.CTkEntry(input_frame, width=100, font=ctk.CTkFont(size=16), justify="center")
        self.time_entry.pack(side="left", padx=(0, 10))
        self.time_entry.insert(0, "15")
        
        self.unit_combobox = ctk.CTkComboBox(input_frame, width=120, values=["seconds", "minutes", "hours"], font=ctk.CTkFont(size=16))
        self.unit_combobox.set("minutes")
        self.unit_combobox.pack(side="left")
        
        # Presets
        presets_frame = ctk.CTkFrame(self.setup_frame, fg_color="transparent")
        presets_frame.pack(pady=20)
        
        ctk.CTkButton(presets_frame, text="15 Min", width=80, command=lambda: self.set_preset(15, "minutes")).pack(side="left", padx=5)
        ctk.CTkButton(presets_frame, text="30 Min", width=80, command=lambda: self.set_preset(30, "minutes")).pack(side="left", padx=5)
        ctk.CTkButton(presets_frame, text="1 Hour", width=80, command=lambda: self.set_preset(1, "hours")).pack(side="left", padx=5)
        ctk.CTkButton(presets_frame, text="2 Hours", width=80, command=lambda: self.set_preset(2, "hours")).pack(side="left", padx=5)
        
        # Action Buttons
        actions_frame = ctk.CTkFrame(self.setup_frame, fg_color="transparent")
        actions_frame.pack(pady=30)
        
        sleep_btn = ctk.CTkButton(actions_frame, text="🌙 Sleep", width=120, height=40, command=lambda: self.confirm_and_start('sleep'))
        sleep_btn.grid(row=0, column=0, padx=10, pady=10)
        
        hibernate_btn = ctk.CTkButton(actions_frame, text="❄️ Hibernate", width=120, height=40, command=lambda: self.confirm_and_start('hibernate'))
        hibernate_btn.grid(row=0, column=1, padx=10, pady=10)
        
        restart_btn = ctk.CTkButton(actions_frame, text="🔄 Restart", width=120, height=40, fg_color="#F39C12", hover_color="#D68910", command=lambda: self.confirm_and_start('restart'))
        restart_btn.grid(row=1, column=0, padx=10, pady=10)
        
        shutdown_btn = ctk.CTkButton(actions_frame, text="🔌 Shutdown", width=120, height=40, fg_color="#E74C3C", hover_color="#C0392B", command=lambda: self.confirm_and_start('shutdown'))
        shutdown_btn.grid(row=1, column=1, padx=10, pady=10)
        
        # Timer view (visible when timer IS running)
        self.timer_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        
        self.action_label = ctk.CTkLabel(self.timer_frame, text="", font=ctk.CTkFont(size=20))
        self.action_label.pack(pady=(30, 10))
        
        self.timer_label = ctk.CTkLabel(self.timer_frame, text="00:00:00", font=ctk.CTkFont(family="Courier New", size=64, weight="bold"))
        self.timer_label.pack(pady=20)
        
        self.progress_bar = ctk.CTkProgressBar(self.timer_frame, width=400, height=15)
        self.progress_bar.set(1.0)
        self.progress_bar.pack(pady=20)
        
        cancel_btn = ctk.CTkButton(self.timer_frame, text="❌ Cancel", width=150, height=45, fg_color="#E74C3C", hover_color="#C0392B", command=self.cancel_timer)
        cancel_btn.pack(pady=40)

    def set_preset(self, value, unit):
        self.time_entry.delete(0, 'end')
        self.time_entry.insert(0, str(value))
        self.unit_combobox.set(unit)

    def confirm_and_start(self, action):
        if messagebox.askokcancel("Confirm", f"Really {action} the system?"):
            self.manager.set_action(action)
            self.start_timer()

    def start_timer(self):
        try:
            value = int(self.time_entry.get())
            if value == 1337:
                self.timer_label.configure(text="DEV MODE")
            unit = self.unit_combobox.get()
            sec = 1
            multiplier = {
                "seconds": sec,
                "minutes": sec * 60,
                "hours": sec * 3600,
            }.get(unit, 1)
            seconds = value * multiplier
            if seconds <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number.")
            return

        self.manager.set_timer(seconds)
        self.total_seconds = seconds
        self.manager.start_countdown()

    def on_timer_started(self):
        action_texts = {
            'sleep': '🌙 Sleeping in...',
            'hibernate': '❄️ Hibernating in...',
            'restart': '🔄 Restarting in...',
            'shutdown': '🔌 Shutting down in...'
        }
        self.action_label.configure(text=action_texts.get(self.manager.action, 'Action pending...'))
        self.setup_frame.pack_forget()
        self.timer_frame.pack(fill="both", expand=True)
        self.update_timer_loop()

    def update_timer_display(self, remaining):
        if isinstance(remaining, int):
            # Format HH:MM:SS
            hours = remaining // 3600
            minutes = (remaining % 3600) // 60
            secs = remaining % 60
            self.timer_label.configure(text=f"{hours:02d}:{minutes:02d}:{secs:02d}")
            
            # Update progress bar
            progress = remaining / max(1, self.total_seconds)
            self.progress_bar.set(progress)
        else:
            self.timer_label.configure(text=str(remaining))

    def on_timer_ended(self):
        self.timer_frame.pack_forget()
        self.setup_frame.pack(fill="both", expand=True)

    def cancel_timer(self):
        self.manager.cancel()

    def update_timer_loop(self):
        self.manager.tick()
        if self.manager.timer_running:
            self.root.after(100, self.update_timer_loop)

    def run(self):
        self.root.mainloop()