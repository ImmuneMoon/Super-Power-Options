# PowerUI.py
# GUI layer: handles user interaction and visual state using customtkinter.

import os
import sys
import customtkinter as ctk
from tkinter import messagebox
from PowerApp.PowerLogic import PowerManager
from pystray import Icon, MenuItem as item, Menu
from PIL import Image
from CTkToolTip import CTkToolTip

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
        self.init_tray_icon()
        self.root.protocol("WM_DELETE_WINDOW", self.hide_to_tray)

    def init_tray_icon(self):
        try:
            icon_image = Image.open(resource_path("assets/icon.ico"))
        except Exception:
            # Fallback if no icon
            icon_image = Image.new('RGB', (64, 64), color='black')
        self.tray_icon = Icon(
            "SuperPowerOptions",
            icon_image,
            title="Super Power Options",
            menu=Menu(
                item("Show App", lambda: self.restore_window(), default=True),
                item("Cancel Timer", lambda: self.cancel_timer(), visible=lambda _: getattr(self.manager, 'timer_running', False)),
                item("Exit", lambda: self.exit_app())
            )
        )
        self.tray_icon.run_detached()

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

    def restore_window(self):
        self.root.deiconify()

    def exit_app(self):
        if hasattr(self, 'tray_icon'):
            self.tray_icon.stop()
        self.root.quit()

    def build_ui(self):
        # Load button images
        img_size = (64, 64)
        try:
            self.sleep_img = ctk.CTkImage(light_image=Image.open(resource_path("assets/Sleep_Button.png")), size=img_size)
            self.hibernate_img = ctk.CTkImage(light_image=Image.open(resource_path("assets/Hibernate_Button.png")), size=img_size)
            self.restart_img = ctk.CTkImage(light_image=Image.open(resource_path("assets/Restart_Button.png")), size=img_size)
            self.shutdown_img = ctk.CTkImage(light_image=Image.open(resource_path("assets/Shutdown_Button.png")), size=img_size)
            self.cancel_img = ctk.CTkImage(light_image=Image.open(resource_path("assets/Cancel_Button.png")), size=img_size)
        except Exception as e:
            print(f"[WARN] Could not load button images: {e}")
            self.sleep_img = self.hibernate_img = self.restart_img = self.shutdown_img = self.cancel_img = None

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
        
        self.unit_combobox = ctk.CTkComboBox(input_frame, width=120, values=["seconds", "minutes", "hours", "days", "weeks", "months", "years"], font=ctk.CTkFont(size=16))
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
        
        sleep_btn = ctk.CTkButton(actions_frame, text="", image=self.sleep_img, width=80, height=80, fg_color="transparent", hover_color="gray25", command=lambda: self.confirm_and_start('sleep'))
        sleep_btn.grid(row=0, column=0, padx=15, pady=15)
        CTkToolTip(sleep_btn, message="Sleep System", delay=0.2)
        
        hibernate_btn = ctk.CTkButton(actions_frame, text="", image=self.hibernate_img, width=80, height=80, fg_color="transparent", hover_color="gray25", command=lambda: self.confirm_and_start('hibernate'))
        hibernate_btn.grid(row=0, column=1, padx=15, pady=15)
        CTkToolTip(hibernate_btn, message="Hibernate System", delay=0.2)
        
        restart_btn = ctk.CTkButton(actions_frame, text="", image=self.restart_img, width=80, height=80, fg_color="transparent", hover_color="gray25", command=lambda: self.confirm_and_start('restart'))
        restart_btn.grid(row=1, column=0, padx=15, pady=15)
        CTkToolTip(restart_btn, message="Restart System", delay=0.2)
        
        shutdown_btn = ctk.CTkButton(actions_frame, text="", image=self.shutdown_img, width=80, height=80, fg_color="transparent", hover_color="gray25", command=lambda: self.confirm_and_start('shutdown'))
        shutdown_btn.grid(row=1, column=1, padx=15, pady=15)
        CTkToolTip(shutdown_btn, message="Shutdown System", delay=0.2)
        
        # Timer view (visible when timer IS running)
        self.timer_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        
        self.action_label = ctk.CTkLabel(self.timer_frame, text="", font=ctk.CTkFont(size=20))
        self.action_label.pack(pady=(30, 10))
        
        self.timer_label = ctk.CTkLabel(self.timer_frame, text="00:00:00", font=ctk.CTkFont(family="Courier New", size=64, weight="bold"))
        self.timer_label.pack(pady=20)
        
        self.progress_bar = ctk.CTkProgressBar(self.timer_frame, width=400, height=15)
        self.progress_bar.set(1.0)
        self.progress_bar.pack(pady=20)
        
        cancel_btn = ctk.CTkButton(self.timer_frame, text="", image=self.cancel_img, width=80, height=80, fg_color="transparent", hover_color="gray25", command=self.cancel_timer)
        cancel_btn.pack(pady=40)
        CTkToolTip(cancel_btn, message="Cancel Timer", delay=0.2)

    def set_preset(self, value, unit):
        self.time_entry.delete(0, 'end')
        self.time_entry.insert(0, str(value))
        self.unit_combobox.set(unit)

    def show_custom_message(self, title, text, on_confirm=None, is_error=False):
        dialog = ctk.CTkToplevel(self.root)
        dialog.title(title)
        dialog.geometry("350x180")
        dialog.resizable(False, False)
        dialog.attributes("-topmost", True)
        
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 175
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 90
        dialog.geometry(f"+{x}+{y}")
        dialog.grab_set()

        lbl_color = "#E74C3C" if is_error else "white"
        ctk.CTkLabel(dialog, text=text, text_color=lbl_color, font=ctk.CTkFont(size=16, weight="bold"), wraplength=300).pack(pady=(30, 20))
        
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20)
        
        if on_confirm:
            def yes_action():
                dialog.destroy()
                on_confirm()
            btn_yes = ctk.CTkButton(btn_frame, text="Yes", width=100, fg_color="#E74C3C", hover_color="#C0392B", command=yes_action)
            btn_yes.pack(side="left", padx=10)
            
            btn_no = ctk.CTkButton(btn_frame, text="Cancel", width=100, command=dialog.destroy)
            btn_no.pack(side="right", padx=10)
        else:
            btn_ok = ctk.CTkButton(btn_frame, text="OK", width=100, command=dialog.destroy)
            btn_ok.pack(pady=10)

    def confirm_and_start(self, action):
        def do_action():
            self.manager.set_action(action)
            self.start_timer()
            
        self.show_custom_message(
            "Confirm Action",
            f"Are you sure you want to {action} the system?",
            on_confirm=do_action
        )

    def start_timer(self):
        try:
            val_str = self.time_entry.get().strip()
            if val_str == "1337":
                self.timer_label.configure(text="DEV MODE")
            value = float(val_str)
            unit = self.unit_combobox.get()
            sec = 1
            multiplier = {
                "seconds": sec,
                "minutes": sec * 60,
                "hours": sec * 3600,
                "days": sec * 86400,
                "weeks": sec * 604800,
                "months": sec * 2592000, # 30 days
                "years": sec * 31536000 # 365 days
            }.get(unit, 1)
            seconds = int(value * multiplier)
            if seconds <= 0:
                raise ValueError
        except ValueError:
            self.show_custom_message("Invalid Input", "Please enter a valid number (e.g. 1.5).", is_error=True)
            return

        self.manager.set_timer(seconds)
        self.total_seconds = seconds
        self.manager.start_countdown()

    def on_timer_started(self):
        action_texts = {
            'sleep': 'Sleeping in...',
            'hibernate': 'Hibernating in...',
            'restart': 'Restarting in...',
            'shutdown': 'Shutting down in...'
        }
        self.action_label.configure(text=action_texts.get(self.manager.action, 'Action pending...'))
        self.setup_frame.pack_forget()
        self.timer_frame.pack(fill="both", expand=True)
        self.update_timer_loop()

    def update_timer_display(self, remaining):
        if isinstance(remaining, int):
            years = remaining // 31536000
            rem = remaining % 31536000
            days = rem // 86400
            rem = rem % 86400
            hours = rem // 3600
            minutes = (rem % 3600) // 60
            secs = rem % 60
            
            parts = []
            if years > 0:
                parts.append(f"{years}y")
            if days > 0:
                parts.append(f"{days}d")
            
            parts.append(f"{hours:02d}:{minutes:02d}:{secs:02d}")
            timer_str = " ".join(parts)
            
            # Reduce font size dynamically if the string is very long
            font_size = 64 if len(timer_str) <= 8 else (48 if len(timer_str) <= 12 else 36)
            self.timer_label.configure(text=timer_str, font=ctk.CTkFont(family="Courier New", size=font_size, weight="bold"))
            
            # Update progress bar
            progress = remaining / max(1, self.total_seconds)
            self.progress_bar.set(progress)

            # Update tray icon tooltip
            if hasattr(self, 'tray_icon'):
                action_str = self.manager.action.capitalize() if self.manager.action else "Action"
                self.tray_icon.title = f"{action_str} in {timer_str}"
        else:
            self.timer_label.configure(text=str(remaining))

    def on_timer_ended(self):
        if hasattr(self, 'tray_icon'):
            self.tray_icon.title = "Super Power Options"
        self.timer_frame.pack_forget()
        self.setup_frame.pack(fill="both", expand=True)

    def cancel_timer(self):
        if hasattr(self, 'tray_icon'):
            self.tray_icon.title = "Super Power Options"
        self.manager.cancel()

    def update_timer_loop(self):
        self.manager.tick()
        if self.manager.timer_running:
            self.root.after(100, self.update_timer_loop)

    def run(self):
        self.root.mainloop()