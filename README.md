# ⚡ Super Power Options

[![Release](https://img.shields.io/github/v/release/ImmuneMoon/Super-Power-Options?color=blue&logo=github)](https://github.com/ImmuneMoon/Super-Power-Options/releases/latest)
[![Build Status](https://img.shields.io/github/actions/workflow/status/ImmuneMoon/Super-Power-Options/build.yml?branch=main&label=Build%20%28CI%29)](https://github.com/ImmuneMoon/Super-Power-Options/actions)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-brightgreen)](https://github.com/ImmuneMoon/Super-Power-Options/releases/latest)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Because some of us want style, and others want a machine to shut down *on schedule, quietly, and without sass.*

---

## 💣 What is This?

**Super Power Options** is a sleek, dark-mode desktop app that lets you schedule your **Windows, macOS, or Linux** computer to:
- 🌙 **Sleep**
- ❄️ **Hibernate**
- 🔄 **Restart**
- 🔌 **Shutdown**

Choose between a duration countdown (**seconds to years**) or schedule an exact **Date & Time**. Designed with rounded iconography, hover tooltips, smooth state transitions, audio alerts, and automated OS power management.

---

## 🚀 Key Features

* **Dual Scheduling Modes:**
  * **Timer Mode:** Count down from any duration (seconds, minutes, hours, days, weeks, months, years) with quick presets (`15 Min`, `30 Min`, `1 Hour`, `2 Hours`) and decimal support (`1.5 hours`).
  * **Date & Time Mode:** Pick an exact calendar date and clock time with 5-minute precision steps, 12-hour AM/PM formatting, and quick jump buttons (`Today`, `Tomorrow`, `11 PM`, `Midnight`).
* **Live Dynamic Preview:** Shows the target moment and live relative time remaining before you even click an action button.
* **Native Cross-Platform Power Control:** Intelligently identifies your operating system and desktop environment to invoke the most graceful method first:
  * **Windows:** Win32 API (`SetSuspendState`) for sleep/hibernate; silent `shutdown.exe`.
  * **macOS:** Native `pmset` (safe sleep) and AppleScript / System Events for graceful restart/shutdown.
  * **Linux (GNOME, KDE Plasma, XFCE, Cinnamon, Budgie, MATE, LXQt):** Desktop session quit commands ensure user applications close cleanly, with automated fallbacks to `systemctl`, `loginctl` (elogind), and D-Bus `login1.Manager`.
* **Sleep Prevention While Timing:** Actively prevents your OS from entering idle sleep while a countdown is running (`SetThreadExecutionState` on Windows, `caffeinate` on macOS, `systemd-inhibit` on Linux).
* **System Tray Integration:** Persistent tray icon displays live countdown progress; falls back to window minimization if the desktop lacks AppIndicator support.
* **Single-Instance Protection:** Prevents duplicate running instances from conflicting.
* **Custom Alert Sounds:** Plays an audio alert when the countdown completes (customize by replacing `assets/alert.wav`).
* **Developer Easter Egg:** Type `1337` in Timer mode to activate Dev Mode.

---

## 🖥️ Operating System Integration Matrix

| Operating System | Sleep / Hibernate | Restart / Shutdown |
|---|---|---|
| **Windows** | `SetSuspendState` (Win32 API) | `shutdown /r` / `shutdown /s` |
| **macOS** | `pmset sleepnow` (Safe Sleep) | System Events (AppleScript) → `shutdown` |
| **Linux (GNOME, Cinnamon, Budgie)** | `systemctl suspend` / `hibernate` | `gnome-session-quit` / `cinnamon-session-quit` → `systemctl` |
| **Linux (KDE Plasma)** | `systemctl suspend` / `hibernate` | `qdbus org.kde.Shutdown` → `systemctl` |
| **Linux (XFCE, LXQt)** | `xfce4-session-logout` / `lxqt-leave` | `xfce4-session-logout` / `lxqt-leave` → `systemctl` |
| **Linux (Generic / Non-systemd)** | `systemctl` → `loginctl` (elogind) → D-Bus | `systemctl` → `loginctl` → D-Bus → `shutdown` |

> Run `python build_and_deploy.py --check` in your terminal to see the exact command chain detected for your current machine.

---

## 📦 Downloads & Installation

Pre-built binaries for all platforms are available on the **[Latest GitHub Release](https://github.com/ImmuneMoon/Super-Power-Options/releases/latest)**:

| Platform | Download | Description |
|---|---|---|
| **Windows** | `SuperPowerOptions-Windows.zip` or `.exe` | Standalone executable (no Python required) |
| **macOS** | `SuperPowerOptions-macOS.zip` | Standalone `.app` bundle |
| **Linux** | `SuperPowerOptions-Linux.tar.gz` | Portable binary executable |

> **macOS Note:** Because the application is not signed with an Apple Developer certificate, on first launch right-click `Super Power Options.app` and choose **Open**.

---

## 🛠️ Running from Source

### Prerequisites
* Python 3.10+ with `tkinter`
  * *Linux (Ubuntu/Debian):* `sudo apt install python3-tk`
  * *Linux (Fedora):* `sudo dnf install python3-tkinter`
  * *Linux (Arch):* `sudo pacman -S tk`

### Setup
```bash
# Clone the repository
git clone https://github.com/ImmuneMoon/Super-Power-Options.git
cd Super-Power-Options

# Set up virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the app
python main.py
```

On Windows, you can also double-click `SuperPowerOptions.bat` to launch immediately.

---

## 🔨 Building Locally

To package a standalone executable for your current operating system using PyInstaller:

```bash
python build_and_deploy.py
```

The output lands in `dist/`:
* Windows: `dist/Super Power Options.exe`
* macOS: `dist/Super Power Options.app`
* Linux: `dist/Super Power Options`

Automated multi-platform builds run on every push and tag via [GitHub Actions](.github/workflows/build.yml).

---

## 📁 Project Structure

```text
Super Power Options/
├── main.py                  # Entry point and single-instance enforcer
├── PowerApp/
│   ├── PowerUI.py           # CustomTkinter GUI & modal dialogs
│   ├── PowerLogic.py        # Countdown timer and threading management
│   └── PowerPlatform.py     # OS/desktop detection, power commands & keep-awake
├── assets/                  # App icon, 64x64 PNG button assets & alert.wav
├── tests/                   # Verification and platform test suite
├── .github/workflows/       # GitHub Actions CI build matrix (Win / Mac / Linux)
├── Super_Power_Options.spec # Unified cross-platform PyInstaller specification
├── SuperPowerOptions.bat    # Windows batch launcher
├── build_and_deploy.py      # Local build script
├── version.txt              # Windows PE executable version properties
├── requirements.txt         # Python dependencies
└── README.md
```

---

## 📜 License

Distributed under the [MIT License](LICENSE).

---

## ☕ Support the Project

If you find this project helpful and want to support further development by Fulllion Creative Works, consider leaving a tip!

* [Donate via PayPal](https://www.paypal.com/donate/?hosted_button_id=LCDZX75HR4CLC)
* [Support on Ko-fi](https://ko-fi.com/fulllion)

---
© 2026 Fulllion Creative Works. All rights reserved.

