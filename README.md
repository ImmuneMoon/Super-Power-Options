# ⚡ Super Power Options

Because some of us want style, and others want a server to shut down *on schedule, quietly, and without sass.*

---

## 💣 What is This?
A stylish Python desktop app that lets you schedule your Windows PC to:
- 🌙 **Sleep**
- ❄️ **Hibernate**
- 🔄 **Restart**
- 🔌 **Shutdown**

And it lets you do it in **seconds, minutes, or hours**. Built with a sleek dark-mode UI, quick preset buttons, a visual progress bar, and precise Windows API integration.

## 🚀 Features

- **Modern Dark Mode UI**: Powered by `customtkinter` with rounded buttons and fluid state changes.
- **Precision Timing**: Avoids drift by calculating deltas against real UNIX timestamps.
- **Accurate Power States**: Uses direct Windows API calls (`ctypes.windll.powrprof.SetSuspendState`) to cleanly differentiate between Sleep and Hibernate.
- **Single-Instance Enforcement**: Launching a new instance will automatically cleanly close any previously running instance in the background.
- **Keeps Windows Awake**: Actively prevents Windows from unexpectedly entering idle sleep while your countdown is ticking.
- **Silent Execution**: Background commands execute completely invisibly (no command-prompt flashes).

## 🎮 How to Use It
1. Run `dist/Super Power Options.exe` (or `python main.py` if running from source).
2. Type a number and pick a time unit, or use one of the quick presets (15m, 30m, 1h, 2h).
3. Click the icon for what you want to happen.
4. Watch the progress bar count down.
5. Cancel at any time if you change your mind!

---
© 2026 Fulllion Creative Works. All rights reserved.

## 📁 Project Structure
```text
Super Power Options/
├── main.py               # Launch point and single-instance enforcer
├── PowerApp/
│   ├── PowerUI.py        # CustomTkinter GUI layer
│   └── PowerLogic.py     # Timer, threading, and system-level execution logic
├── assets/               # Vector SVGs, raw PNGs, and optional .wav alerts
├── Super_Power_Options.spec # PyInstaller configuration
└── README.md
```

## 🔧 Requirements
- Python 3.8+
- Windows OS (Requires Windows APIs)
- `customtkinter`, `pillow`, `pystray`, `pywin32`

Install dependencies using:
```bash
pip install -r requirements.txt
```

## 🛠️ Build Instructions
To build your own standalone executable without needing a Python environment:
```bash
python -m PyInstaller Super_Power_Options.spec
```
The output `.exe` will appear in the `/dist` directory with all required assets embedded.

## 📜 License
MIT License


## ☕ Support the Project

If you find this extension helpful and want to support further development by Fulllion Creative Works, consider leaving a tip!

* [Donate via PayPal](https://www.paypal.com/donate/?hosted_button_id=LCDZX75HR4CLC)
* [Support on Ko-fi](https://ko-fi.com/fulllion)
