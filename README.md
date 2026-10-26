# ⚡ Super Power Options

Because some of us want style, and others want a server to shut down *on schedule, quietly, and without sass.*

---

## 💣 What is This?
A stylish Python desktop app that lets you schedule your **Windows, macOS or Linux** machine to:
- 🌙 **Sleep**
- ❄️ **Hibernate**
- 🔄 **Restart**
- 🔌 **Shutdown**

Set a countdown (**seconds to years**) or pick an exact **date & time**. Built with a sleek dark-mode UI, quick preset buttons and a visual progress bar. It detects your OS and desktop environment and uses the right power commands for it.

## 🚀 Features

- **Modern Dark Mode UI**: Powered by `customtkinter` with rounded buttons and fluid state changes.
- **Timer or Date & Time**: Count down from a duration, or schedule an exact moment.
- **Precision Timing**: Avoids drift by calculating deltas against real UNIX timestamps.
- **Cross-Platform Power Control**: Detects the OS and desktop and tries the best method first, falling back automatically (see table below).
- **Single-Instance Enforcement**: Launching a new instance closes any previously running one.
- **Keeps the Machine Awake**: Prevents idle sleep while the countdown runs (`SetThreadExecutionState` / `caffeinate` / `systemd-inhibit`).
- **Tray Icon** where the desktop supports one; otherwise closing the window just minimizes it.
- **Silent Execution**: Background commands run without console flashes.

### How each OS is handled

| System | Sleep / Hibernate | Restart / Shutdown |
|---|---|---|
| Windows | `SetSuspendState` (Win32 API) | `shutdown /r` / `shutdown /s` |
| macOS | `pmset sleepnow` (hibernate = sleep; macOS has no separate user hibernate) | System Events (AppleScript), then `shutdown` |
| Linux – GNOME, Cinnamon, Budgie, KDE, XFCE, LXQt | desktop command where one exists, then `systemctl` | session command (closes apps gracefully), then `systemctl` |
| Linux – other / non-systemd | `systemctl` → `loginctl` (elogind) → logind over D-Bus → `pm-utils` | `systemctl` → `loginctl` → D-Bus → `shutdown` |

Run `python build_and_deploy.py --check` to see exactly what will be used on your machine.

## 🎮 How to Use It
1. Run the app for your OS (see *Downloads* below), or `python main.py` from source.
2. Choose **Timer** (number + unit, or a preset) or **Date & Time** (date, hour, minute, AM/PM).
3. Click the icon for what you want to happen.
4. Watch the progress bar count down.
5. Cancel at any time if you change your mind!

## 📁 Project Structure
```text
Super Power Options/
├── main.py                  # Launch point and single-instance enforcer
├── PowerApp/
│   ├── PowerUI.py           # CustomTkinter GUI layer
│   ├── PowerLogic.py        # Timer / countdown logic
│   └── PowerPlatform.py     # OS + desktop detection, power commands, keep-awake, sound
├── assets/                  # Icons, button PNGs and the alert .wav
├── Super_Power_Options.spec # PyInstaller config (Windows / macOS / Linux)
├── .github/workflows/build.yml  # CI: builds all three OSes
└── README.md
```

## 🔧 Requirements (running from source)
- Python 3.10+ with tkinter
  - Linux: install `python3-tk` from your package manager if it's missing
- `pip install -r requirements.txt` (`pywin32` is installed on Windows only)
- Linux tray icon on GNOME needs the *AppIndicator* extension; without it the window minimizes instead.

## 📦 Downloads / Builds

**GitHub Actions** builds every push on Windows, macOS and Linux runners (see the *Actions* tab → artifacts). Pushing a tag like `v1.2.0` attaches all three to a GitHub Release.

**Build locally** (PyInstaller can only build for the OS it's running on):
```bash
python build_and_deploy.py
```
Output: `dist/Super Power Options.exe` (Windows), `dist/Super Power Options.app` (macOS), `dist/Super Power Options` (Linux).

> **macOS:** the app isn't code-signed, so the first launch needs right-click → *Open*. Restart/Shutdown will ask for permission to control *System Events*.


## 📜 License
MIT License
