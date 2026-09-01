from __future__ import annotations

import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

APP_NAME = "SanGlow"
REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"


def _get_exe_path() -> str | None:
    if getattr(sys, "frozen", False):
        return sys.executable
    return None


def is_autostart_enabled() -> bool:
    if sys.platform != "win32":
        return False
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_READ)
        try:
            winreg.QueryValueEx(key, APP_NAME)
            return True
        except FileNotFoundError:
            return False
        finally:
            winreg.CloseKey(key)
    except Exception as e:
        logger.debug("autostart check failed: %s", e)
        return False


def enable_autostart() -> bool:
    if sys.platform != "win32":
        return False

    exe_path = _get_exe_path()
    if not exe_path:
        logger.warning("Cannot enable autostart: not a frozen app")
        return False

    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, f'"{exe_path}" --minimized')
        winreg.CloseKey(key)
        logger.info("Autostart enabled: %s", exe_path)
        return True
    except Exception as e:
        logger.error("Failed to enable autostart: %s", e)
        return False


def disable_autostart() -> bool:
    if sys.platform != "win32":
        return False

    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_SET_VALUE)
        try:
            winreg.DeleteValue(key, APP_NAME)
        except FileNotFoundError:
            pass
        winreg.CloseKey(key)
        logger.info("Autostart disabled")
        return True
    except Exception as e:
        logger.error("Failed to disable autostart: %s", e)
        return False
