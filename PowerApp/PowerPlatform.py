# PowerPlatform.py
# Cross-platform layer: works out which OS / desktop environment we're on and
# knows how to sleep, hibernate, restart or shut it down, keep it awake while a
# timer is running, and play the alert sound.
#
# Supported:
#   Windows  - Win32 API (SetSuspendState) and shutdown.exe
#   macOS    - pmset and System Events (AppleScript)
#   Linux    - desktop-native commands (GNOME, KDE Plasma, XFCE, Cinnamon, MATE, LXQt),
#              then systemd / elogind (systemctl, loginctl), then classic shutdown / pm-utils.

import os
import sys
import shutil
import signal
import platform
import subprocess

ACTIONS = ("sleep", "hibernate", "restart", "shutdown")


# ---------------------------------------------------------------------------
# Detection
# ---------------------------------------------------------------------------

def detect_os():
    """Returns 'windows', 'macos', 'linux' or 'other'."""
    system = platform.system()
    if system == "Windows":
        return "windows"
    if system == "Darwin":
        return "macos"
    if system == "Linux":
        return "linux"
    return "other"




def detect_desktop():
    """Returns a lowercase desktop-environment id on Linux ('gnome', 'kde', 'xfce', ...), else ''."""
    if detect_os() != "linux":
        return ""
    raw = " ".join(
        os.environ.get(var, "")
        for var in ("XDG_CURRENT_DESKTOP", "XDG_SESSION_DESKTOP", "DESKTOP_SESSION")
    ).lower()
    # Order matters: Cinnamon and Budgie both report "GNOME" as a secondary desktop.
    for key, names in (
        ("cinnamon", ("cinnamon",)),
        ("budgie", ("budgie",)),
        ("kde", ("kde", "plasma")),
        ("xfce", ("xfce",)),
        ("mate", ("mate",)),
        ("lxqt", ("lxqt",)),
        ("lxde", ("lxde",)),
        ("gnome", ("gnome", "unity", "ubuntu", "pop", "pantheon")),
    ):
        if any(n in raw for n in names):
            return key
    return ""


def describe_system():
    """Human-readable summary, e.g. 'Linux (GNOME, Docker)'."""
    os_name = {"windows": "Windows", "macos": "macOS", "linux": "Linux"}.get(detect_os(), platform.system())
    extras = []
    de = detect_desktop()
    if de:
        extras.append({"kde": "KDE Plasma", "xfce": "XFCE", "lxqt": "LXQt", "lxde": "LXDE",
                       "gnome": "GNOME", "mate": "MATE"}.get(de, de.capitalize()))
    return f"{os_name} ({', '.join(extras)})" if extras else os_name


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_CREATE_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000) if detect_os() == "windows" else 0


def _run(cmd, timeout=15):
    """Runs a command quietly. Returns True if it exited with status 0."""
    if not shutil.which(cmd[0]):
        return False
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=timeout,
            creationflags=_CREATE_NO_WINDOW,
        )
        return result.returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def _logind_dbus(method):
    """Calls org.freedesktop.login1.Manager.<method>(interactive=true) on the system bus."""
    return [
        "dbus-send", "--system", "--print-reply", "--dest=org.freedesktop.login1",
        "/org/freedesktop/login1", f"org.freedesktop.login1.Manager.{method}", "boolean:true",
    ]


# ---------------------------------------------------------------------------
# Power actions
# ---------------------------------------------------------------------------

def _windows_commands(action):
    import ctypes

    def suspend(hibernate):
        # SetSuspendState(bHibernate, bForce, bWakeupEventsDisabled)
        return lambda: bool(ctypes.windll.powrprof.SetSuspendState(hibernate, False, False))

    return {
        "sleep": [("SetSuspendState (sleep)", suspend(False))],
        "hibernate": [("SetSuspendState (hibernate)", suspend(True))],
        "restart": [("shutdown /r", ["shutdown", "/r", "/t", "0"])],
        "shutdown": [("shutdown /s", ["shutdown", "/s", "/t", "0"])],
    }[action]


def _macos_commands(action):
    # macOS has no separate user-level hibernate. With the default hibernatemode on
    # laptops, sleep already writes memory to disk ("safe sleep"), so hibernate maps to sleep.
    if action in ("sleep", "hibernate"):
        return [
            ("pmset sleepnow", ["pmset", "sleepnow"]),
            ("System Events sleep", ["osascript", "-e", 'tell application "System Events" to sleep']),
        ]
    if action == "restart":
        return [
            ("System Events restart", ["osascript", "-e", 'tell application "System Events" to restart']),
            ("shutdown -r", ["shutdown", "-r", "now"]),
        ]
    return [
        ("System Events shut down", ["osascript", "-e", 'tell application "System Events" to shut down']),
        ("shutdown -h", ["shutdown", "-h", "now"]),
    ]


def _linux_desktop_commands(action, desktop):
    """Desktop-native commands. These close the session gracefully, so they're tried first."""
    qdbus = shutil.which("qdbus6") or shutil.which("qdbus") or "qdbus"
    table = {
        "gnome": {
            "restart": ["gnome-session-quit", "--reboot", "--no-prompt"],
            "shutdown": ["gnome-session-quit", "--power-off", "--no-prompt"],
        },
        "budgie": {
            "restart": ["gnome-session-quit", "--reboot", "--no-prompt"],
            "shutdown": ["gnome-session-quit", "--power-off", "--no-prompt"],
        },
        "cinnamon": {
            "restart": ["cinnamon-session-quit", "--reboot", "--no-prompt"],
            "shutdown": ["cinnamon-session-quit", "--power-off", "--no-prompt"],
        },
        "kde": {
            "restart": [qdbus, "org.kde.Shutdown", "/Shutdown", "logoutAndReboot"],
            "shutdown": [qdbus, "org.kde.Shutdown", "/Shutdown", "logoutAndShutdown"],
        },
        "xfce": {
            "sleep": ["xfce4-session-logout", "--suspend"],
            "hibernate": ["xfce4-session-logout", "--hibernate"],
            "restart": ["xfce4-session-logout", "--reboot", "--fast"],
            "shutdown": ["xfce4-session-logout", "--halt", "--fast"],
        },
        "lxqt": {
            "sleep": ["lxqt-leave", "--suspend"],
            "hibernate": ["lxqt-leave", "--hibernate"],
            "restart": ["lxqt-leave", "--reboot"],
            "shutdown": ["lxqt-leave", "--shutdown"],
        },
    }
    cmd = table.get(desktop, {}).get(action)
    return [(f"{desktop} session ({cmd[0]})", cmd)] if cmd else []


def _linux_commands(action):
    systemd_verb = {"sleep": "suspend", "hibernate": "hibernate", "restart": "reboot", "shutdown": "poweroff"}[action]
    logind_method = {"sleep": "Suspend", "hibernate": "Hibernate", "restart": "Reboot", "shutdown": "PowerOff"}[action]

    candidates = list(_linux_desktop_commands(action, detect_desktop()))
    candidates += [
        (f"systemctl {systemd_verb}", ["systemctl", systemd_verb]),
        (f"loginctl {systemd_verb}", ["loginctl", systemd_verb]),  # elogind (non-systemd distros)
        ("logind via D-Bus", _logind_dbus(logind_method)),
    ]

    # Last resorts (usually need root)
    candidates += {
        "sleep": [("pm-suspend", ["pm-suspend"])],
        "hibernate": [("pm-hibernate", ["pm-hibernate"])],
        "restart": [("shutdown -r", ["shutdown", "-r", "now"])],
        "shutdown": [("shutdown -h", ["shutdown", "-h", "now"])],
    }[action]
    return candidates


def get_candidates(action):
    """Ordered list of (label, command-or-callable) to try for an action on this system."""
    if action not in ACTIONS:
        raise ValueError(f"Unknown action: {action}")
    os_id = detect_os()
    if os_id == "windows":
        return _windows_commands(action)
    if os_id == "macos":
        return _macos_commands(action)
    return _linux_commands(action)


def perform(action):
    """
    Tries each method for the action until one succeeds.
    Returns (success, method_label_or_error_message).
    """
    tried = []
    for label, cmd in get_candidates(action):
        ok = cmd() if callable(cmd) else _run(cmd)
        if ok:
            return True, label
        tried.append(label)
    hint = ""
    if action == "hibernate" and detect_os() == "linux":
        hint = " Hibernate may be disabled on this system (it needs a swap partition/file large enough for RAM)."
    return False, f"Couldn't {action} on {describe_system()}. Tried: {', '.join(tried) or 'nothing available'}.{hint}"


# ---------------------------------------------------------------------------
# Keep-awake while the timer runs
# ---------------------------------------------------------------------------

class KeepAwake:
    """Stops the machine from idling into sleep while a countdown is active."""

    def __init__(self):
        self._proc = None

    def start(self):
        self.stop()
        os_id = detect_os()
        if os_id == "windows":
            import ctypes
            ES_CONTINUOUS, ES_SYSTEM_REQUIRED = 0x80000000, 0x00000001
            ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED)
            return
        cmd = None
        if os_id == "macos" and shutil.which("caffeinate"):
            # -i: prevent idle sleep; -w: exit automatically if this app dies
            cmd = ["caffeinate", "-i", "-w", str(os.getpid())]
        elif os_id == "linux" and shutil.which("systemd-inhibit"):
            cmd = ["systemd-inhibit", "--what=idle:sleep", "--who=Super Power Options",
                   "--why=Power timer running", "--mode=block", "sleep", "infinity"]
        if cmd:
            try:
                self._proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                              start_new_session=True)
            except OSError:
                self._proc = None

    def stop(self):
        if detect_os() == "windows":
            import ctypes
            ctypes.windll.kernel32.SetThreadExecutionState(0x80000000)  # ES_CONTINUOUS only
            return
        if self._proc and self._proc.poll() is None:
            try:
                # Kill the whole group so the inner `sleep infinity` goes too
                os.killpg(self._proc.pid, signal.SIGTERM)
            except (OSError, AttributeError):
                self._proc.terminate()
            try:
                # Must be fully gone before we suspend, or our own inhibitor would block it
                self._proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self._proc.kill()
        self._proc = None


# ---------------------------------------------------------------------------
# Alert sound
# ---------------------------------------------------------------------------

def play_sound(path):
    """Plays a .wav file (blocking, short). Silently does nothing if no player is available."""
    if not os.path.exists(path):
        return
    os_id = detect_os()
    if os_id == "windows":
        import winsound
        winsound.PlaySound(path, winsound.SND_FILENAME)
        return
    players = [["afplay", path]] if os_id == "macos" else [
        ["paplay", path], ["pw-play", path], ["aplay", "-q", path],
    ]
    for cmd in players:
        if _run(cmd, timeout=10):
            return


# ---------------------------------------------------------------------------
# Tray support
# ---------------------------------------------------------------------------

def tray_supported():
    """
    Whether a system-tray icon will actually be visible/usable.
    - macOS: pystray needs the main thread, which tkinter owns -> no tray.
    - Docker: no session bus / tray host -> no tray.
    - GNOME: only shows tray icons through the AppIndicator extension.
    """
    os_id = detect_os()
    if os_id == "windows":
        return True
    if os_id == "macos":
        return False
    if os_id == "linux":
        if not (os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")):
            return False
        if detect_desktop() == "gnome":
            try:
                import pystray
                return "appindicator" in pystray.Icon.__module__
            except Exception:
                return False
        return True
    return False


if __name__ == "__main__":
    # Quick diagnostic: python -m PowerApp.PowerPlatform
    print(f"System:   {describe_system()}")
    print(f"Tray:     {'yes' if tray_supported() else 'no'}")
    for a in ACTIONS:
        labels = [label for label, _ in get_candidates(a)]
        print(f"{a:<9} -> {' | '.join(labels)}")
    sys.exit(0)
