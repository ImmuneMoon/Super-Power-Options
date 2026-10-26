# PowerUI.py
# GUI layer: handles user interaction and visual state using customtkinter.

import os
import sys
import time
from datetime import datetime, timedelta
import customtkinter as ctk
from tkinter import messagebox, PhotoImage
from PowerApp.PowerLogic import PowerManager
from PowerApp import PowerPlatform
from PIL import Image
from CTkToolTip import CTkToolTip

try:
    from pystray import Icon, MenuItem as item, Menu
except Exception:  # No usable tray backend on this system (e.g. headless/Docker)
    Icon = None

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
        self.root.geometry("650x600")
        self.root.resizable(False, False)
        
        self.manager = PowerManager(self)
        self.load_icon()
        self.build_ui()
        self.tray_enabled = False
        self.init_tray_icon()
        self.root.protocol("WM_DELETE_WINDOW", self.hide_to_tray)
        print(f"[INFO] Running on {PowerPlatform.describe_system()} (tray: {'on' if self.tray_enabled else 'off'})")

    def init_tray_icon(self):
        if Icon is None or not PowerPlatform.tray_supported():
            return
        try:
            icon_image = Image.open(resource_path("assets/icon.ico"))
        except Exception:
            # Fallback if no icon
            icon_image = Image.new('RGB', (64, 64), color='black')
        try:
            self.tray_icon = Icon(
                "SuperPowerOptions",
                icon_image,
                title="Super Power Options",
                menu=Menu(
                    item("Show App", lambda: self.root.after(0, self.restore_window), default=True),
                    item("Cancel Timer", lambda: self.root.after(0, self.cancel_timer), visible=lambda _: getattr(self.manager, 'timer_running', False)),
                    item("Exit", lambda: self.root.after(0, self.exit_app))
                )
            )
            self.tray_icon.run_detached()
            self.tray_enabled = True
        except Exception as e:
            print(f"[WARN] Tray icon unavailable: {e}")
            if hasattr(self, 'tray_icon'):
                del self.tray_icon

    def load_icon(self):
        if PowerPlatform.detect_os() == "windows":
            app_icon_path = resource_path("assets/icon.ico")
            if os.path.exists(app_icon_path):
                try:
                    self.root.iconbitmap(app_icon_path)
                except Exception as e:
                    print(f"[WARN] Failed to load icon: {e}")
            else:
                print("[WARN] icon.ico not found at runtime")
            return
        # macOS / Linux: Tk can't use .ico files, so use the PNG
        png_path = resource_path("assets/icon.png")
        if os.path.exists(png_path):
            try:
                self._icon_photo = PhotoImage(file=png_path)  # keep a reference so it isn't garbage-collected
                self.root.iconphoto(True, self._icon_photo)
            except Exception as e:
                print(f"[WARN] Failed to load icon: {e}")

    def hide_to_tray(self):
        if self.tray_enabled:
            self.root.withdraw()  # Hide window; it lives on in the tray
        else:
            self.root.iconify()  # No tray here, so minimize instead of vanishing

    def restore_window(self):
        self.root.deiconify()
        self.root.lift()

    def exit_app(self):
        self.manager.keep_awake.stop()
        if hasattr(self, 'tray_icon'):
            self.tray_icon.stop()
        self.root.quit()

    def on_action_failed(self, message):
        self.restore_window()
        self.show_custom_message("Action Failed", message, is_error=True)

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
        self.title_label = ctk.CTkLabel(self.setup_frame, text="Set Timer", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.pack(pady=(0, 10))
        
        # Mode switch: countdown timer vs. specific date/time
        self.mode_switch = ctk.CTkSegmentedButton(self.setup_frame, values=["Timer", "Date & Time"], command=self.on_mode_change, font=ctk.CTkFont(size=14))
        self.mode_switch.set("Timer")
        self.mode_switch.pack(pady=(0, 10))
        
        # Holder keeps the swappable input/preset area in a fixed spot above the action buttons
        self.mode_holder = ctk.CTkFrame(self.setup_frame, fg_color="transparent")
        self.mode_holder.pack(fill="x")
        
        # ---- Timer mode ----
        self.timer_mode_frame = ctk.CTkFrame(self.mode_holder, fg_color="transparent")
        self.timer_mode_frame.pack()
        
        input_frame = ctk.CTkFrame(self.timer_mode_frame, fg_color="transparent")
        input_frame.pack(pady=10)
        
        self.time_entry = ctk.CTkEntry(input_frame, width=100, font=ctk.CTkFont(size=16), justify="center")
        self.time_entry.pack(side="left", padx=(0, 10))
        self.time_entry.insert(0, "15")
        
        self.unit_combobox = ctk.CTkComboBox(input_frame, width=120, values=["seconds", "minutes", "hours", "days", "weeks", "months", "years"], font=ctk.CTkFont(size=16), state="readonly")
        self.unit_combobox.set("minutes")
        self.unit_combobox.pack(side="left")
        
        presets_frame = ctk.CTkFrame(self.timer_mode_frame, fg_color="transparent")
        presets_frame.pack(pady=20)
        
        ctk.CTkButton(presets_frame, text="15 Min", width=80, command=lambda: self.set_preset(15, "minutes")).pack(side="left", padx=5)
        ctk.CTkButton(presets_frame, text="30 Min", width=80, command=lambda: self.set_preset(30, "minutes")).pack(side="left", padx=5)
        ctk.CTkButton(presets_frame, text="1 Hour", width=80, command=lambda: self.set_preset(1, "hours")).pack(side="left", padx=5)
        ctk.CTkButton(presets_frame, text="2 Hours", width=80, command=lambda: self.set_preset(2, "hours")).pack(side="left", padx=5)
        
        # ---- Date & Time mode ----
        self.date_mode_frame = ctk.CTkFrame(self.mode_holder, fg_color="transparent")
        
        dt_input = ctk.CTkFrame(self.date_mode_frame, fg_color="transparent")
        dt_input.pack(pady=10)
        
        self.date_entry = ctk.CTkEntry(dt_input, width=130, font=ctk.CTkFont(size=16), justify="center", placeholder_text="YYYY-MM-DD")
        self.date_entry.pack(side="left", padx=(0, 15))
        CTkToolTip(self.date_entry, message="Date (YYYY-MM-DD)", delay=0.2)
        
        self.hour_combobox = ctk.CTkComboBox(dt_input, width=70, values=[str(h) for h in range(1, 13)], font=ctk.CTkFont(size=16), justify="center")
        self.hour_combobox.pack(side="left")
        ctk.CTkLabel(dt_input, text=":", font=ctk.CTkFont(size=18, weight="bold")).pack(side="left", padx=4)
        self.minute_combobox = ctk.CTkComboBox(dt_input, width=70, values=[f"{m:02d}" for m in range(0, 60, 5)], font=ctk.CTkFont(size=16), justify="center")
        self.minute_combobox.pack(side="left", padx=(0, 10))
        
        self.ampm_switch = ctk.CTkSegmentedButton(dt_input, values=["AM", "PM"], font=ctk.CTkFont(size=14))
        self.ampm_switch.pack(side="left")
        
        dt_presets = ctk.CTkFrame(self.date_mode_frame, fg_color="transparent")
        dt_presets.pack(pady=(10, 0))
        
        ctk.CTkButton(dt_presets, text="Today", width=80, command=lambda: self.set_date_preset(day_offset=0)).pack(side="left", padx=5)
        ctk.CTkButton(dt_presets, text="Tomorrow", width=80, command=lambda: self.set_date_preset(day_offset=1)).pack(side="left", padx=5)
        ctk.CTkButton(dt_presets, text="11 PM", width=80, command=lambda: self.set_date_preset(hour24=23)).pack(side="left", padx=5)
        ctk.CTkButton(dt_presets, text="Midnight", width=80, command=lambda: self.set_date_preset(hour24=0)).pack(side="left", padx=5)
        
        # Live preview of how far away the chosen moment is
        self.dt_preview_label = ctk.CTkLabel(self.date_mode_frame, text="", font=ctk.CTkFont(size=13), text_color="gray70")
        self.dt_preview_label.pack(pady=(8, 0))
        
        self.reset_datetime_inputs()
        
        # Action Buttons
        actions_frame = ctk.CTkFrame(self.setup_frame, fg_color="transparent")
        actions_frame.pack(pady=20)
        
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
        self.action_label.pack(pady=(30, 4))
        
        self.target_label = ctk.CTkLabel(self.timer_frame, text="", font=ctk.CTkFont(size=14), text_color="gray70")
        self.target_label.pack(pady=(0, 6))
        
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

    # ---------- Date & Time mode helpers ----------

    def on_mode_change(self, mode):
        if mode == "Date & Time":
            self.timer_mode_frame.pack_forget()
            self.date_mode_frame.pack()
            self.title_label.configure(text="Schedule Date & Time")
            self.update_datetime_preview()
        else:
            self.date_mode_frame.pack_forget()
            self.timer_mode_frame.pack()
            self.title_label.configure(text="Set Timer")

    def _fill_datetime_inputs(self, dt):
        self.date_entry.delete(0, 'end')
        self.date_entry.insert(0, dt.strftime("%Y-%m-%d"))
        self.hour_combobox.set(str(int(dt.strftime("%I"))))
        self.minute_combobox.set(dt.strftime("%M"))
        self.ampm_switch.set(dt.strftime("%p").upper())

    def reset_datetime_inputs(self):
        # Default: one hour from now, rounded up to the next 5 minutes
        dt = datetime.now() + timedelta(hours=1)
        dt = dt.replace(second=0, microsecond=0)
        dt += timedelta(minutes=(5 - dt.minute % 5) % 5)
        self._fill_datetime_inputs(dt)

    def set_date_preset(self, day_offset=None, hour24=None):
        now = datetime.now()
        current = self.parse_target_datetime(silent=True) or now
        if day_offset is not None:
            # Keep the chosen time, change only the date
            day = (now + timedelta(days=day_offset)).date()
            current = current.replace(year=day.year, month=day.month, day=day.day)
        if hour24 is not None:
            # Next occurrence of that clock time
            current = now.replace(hour=hour24, minute=0, second=0, microsecond=0)
            if current <= now:
                current += timedelta(days=1)
        self._fill_datetime_inputs(current)
        self.update_datetime_preview()

    def parse_target_datetime(self, silent=False):
        """Returns a datetime from the date/time inputs, or None if invalid."""
        try:
            date_str = self.date_entry.get().strip()
            hour = int(self.hour_combobox.get().strip())
            minute = int(self.minute_combobox.get().strip())
            ampm = self.ampm_switch.get() or "AM"
            if not (1 <= hour <= 12 and 0 <= minute <= 59):
                raise ValueError
            return datetime.strptime(f"{date_str} {hour}:{minute:02d} {ampm}", "%Y-%m-%d %I:%M %p")
        except ValueError:
            if not silent:
                self.show_custom_message("Invalid Date/Time", "Please enter a valid date (YYYY-MM-DD) and time.", is_error=True)
            return None

    def update_datetime_preview(self):
        if self.mode_switch.get() != "Date & Time":
            return
        dt = self.parse_target_datetime(silent=True)
        if dt is None:
            self.dt_preview_label.configure(text="Enter a valid date and time", text_color="#E74C3C")
        else:
            delta = int((dt - datetime.now()).total_seconds())
            if delta <= 0:
                self.dt_preview_label.configure(text="That time is in the past", text_color="#E74C3C")
            else:
                d, rem = divmod(delta, 86400)
                h, rem = divmod(rem, 3600)
                m = rem // 60
                parts = ([f"{d}d"] if d else []) + ([f"{h}h"] if h or d else []) + [f"{m}m"]
                self.dt_preview_label.configure(text=f"{dt.strftime('%a, %b %d at %I:%M %p')}  •  in {' '.join(parts)}", text_color="gray70")
        # Keep the preview fresh while the setup screen is visible
        if not getattr(self, '_preview_job', None):
            def _refresh():
                self._preview_job = None
                self.update_datetime_preview()
            self._preview_job = self.root.after(1000, _refresh)

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
        
        message = f"Are you sure you want to {action} the system?"
        if self.mode_switch.get() == "Date & Time":
            dt = self.parse_target_datetime()
            if dt is None:
                return
            if dt <= datetime.now():
                self.show_custom_message("Invalid Date/Time", "The selected date and time is in the past.", is_error=True)
                return
            message = f"Are you sure you want to {action} the system on {dt.strftime('%a, %b %d at %I:%M %p')}?"
            
        self.show_custom_message(
            "Confirm Action",
            message,
            on_confirm=do_action
        )

    def start_timer(self):
        if self.mode_switch.get() == "Date & Time":
            dt = self.parse_target_datetime()
            if dt is None:
                return
            seconds = dt.timestamp() - time.time()
            if seconds <= 0:
                self.show_custom_message("Invalid Date/Time", "The selected date and time is in the past.", is_error=True)
                return
            self.manager.set_timer(seconds)
            self.total_seconds = int(seconds)
            self.manager.start_countdown()
            return

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
        target_dt = datetime.fromtimestamp(self.manager.target_time)
        self.target_label.configure(text=f"Scheduled for {target_dt.strftime('%a, %b %d, %Y at %I:%M:%S %p')}")
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
        self.update_datetime_preview()

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