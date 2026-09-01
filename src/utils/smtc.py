from __future__ import annotations

import ctypes
import ctypes.wintypes as wintypes
import logging
import os
import sys
from pathlib import Path
from typing import Callable

logger = logging.getLogger(__name__)

WM_APP = 0x8000
WM_SMTC_PLAY = WM_APP + 100
WM_SMTC_PAUSE = WM_APP + 101
WM_SMTC_STOP = WM_APP + 102
WM_SMTC_NEXT = WM_APP + 103
WM_SMTC_PREV = WM_APP + 104

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

MOD_CONTROL = 0x0002
MOD_ALT = 0x0001
MOD_SHIFT = 0x0004
VK_MEDIA_PLAY_PAUSE = 0xB3
VK_MEDIA_NEXT_TRACK = 0xB0
VK_MEDIA_PREV_TRACK = 0xB1
VK_MEDIA_STOP = 0xB2

HOTKEY_PLAY_PAUSE = 1
HOTKEY_NEXT = 2
HOTKEY_PREV = 3
HOTKEY_STOP = 4


class GlobalMediaHotkeys:
    def __init__(self) -> None:
        self._registered = False
        self._callbacks: dict[int, Callable] = {}
        self._hwnd = None
        self._wndproc = None

    def register(self, play_pause: Callable | None = None,
                 next_track: Callable | None = None,
                 prev_track: Callable | None = None,
                 stop: Callable | None = None) -> bool:
        if self._registered:
            return True

        if sys.platform != "win32":
            return False

        try:
            WNDCLASSEX = wintypes.WNDCLASSEX
            wc = WNDCLASSEX()
            wc.cbSize = ctypes.sizeof(WNDCLASSEX)
            wc.lpfnWndProc = ctypes.WINFUNCTYPE(
                wintypes.LPARAM,
                wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM
            )(self._wnd_proc)
            wc.hInstance = kernel32.GetModuleHandleW(None)
            wc.lpszClassName = "SanGlowMediaHotkeys"
            wc.hIcon = 0
            wc.hCursor = 0
            wc.hbrBackground = 0

            atom = user32.RegisterClassExW(ctypes.byref(wc))
            if not atom:
                logger.warning("RegisterClassEx failed: %s", kernel32.GetLastError())
                return False

            self._hwnd = user32.CreateWindowExW(
                0, wc.lpszClassName, "SanGlow Hotkeys",
                0, 0, 0, 0, 0,
                0, 0, wc.hInstance, 0
            )
            if not self._hwnd:
                logger.warning("CreateWindowEx failed: %s", kernel32.GetLastError())
                return False

            if play_pause:
                self._callbacks[HOTKEY_PLAY_PAUSE] = play_pause
            if next_track:
                self._callbacks[HOTKEY_NEXT] = next_track
            if prev_track:
                self._callbacks[HOTKEY_PREV] = prev_track
            if stop:
                self._callbacks[HOTKEY_STOP] = stop

            user32.RegisterHotKey(self._hwnd, HOTKEY_PLAY_PAUSE, 0, VK_MEDIA_PLAY_PAUSE)
            user32.RegisterHotKey(self._hwnd, HOTKEY_NEXT, 0, VK_MEDIA_NEXT_TRACK)
            user32.RegisterHotKey(self._hwnd, HOTKEY_PREV, 0, VK_MEDIA_PREV_TRACK)
            user32.RegisterHotKey(self._hwnd, HOTKEY_STOP, 0, VK_MEDIA_STOP)

            self._registered = True
            logger.info("Global media hotkeys registered")
            return True
        except Exception as e:
            logger.warning("Failed to register hotkeys: %s", e)
            return False

    def _wnd_proc(self, hwnd, msg, wparam, lparam):
        if msg == 0x0002:
            self.unregister()
            return 0
        if msg == 0x004A:
            return 0
        if msg == 0x0312:
            hotkey_id = wparam & 0xFFFF
            if hotkey_id in self._callbacks:
                try:
                    self._callbacks[hotkey_id]()
                except Exception as e:
                    logger.error("Hotkey callback error: %s", e)
            return 0
        try:
            return user32.DefWindowProcW(hwnd, msg, wparam, lparam)
        except Exception:
            return 0

    def unregister(self) -> None:
        if not self._registered:
            return
        try:
            if self._hwnd:
                user32.UnregisterHotKey(self._hwnd, HOTKEY_PLAY_PAUSE)
                user32.UnregisterHotKey(self._hwnd, HOTKEY_NEXT)
                user32.UnregisterHotKey(self._hwnd, HOTKEY_PREV)
                user32.UnregisterHotKey(self._hwnd, HOTKEY_STOP)
                user32.DestroyWindow(self._hwnd)
                self._hwnd = None
            self._registered = False
            logger.info("Global media hotkeys unregistered")
        except Exception as e:
            logger.warning("Error unregistering hotkeys: %s", e)

    def __del__(self) -> None:
        self.unregister()


_hotkeys_instance: GlobalMediaHotkeys | None = None


def get_media_hotkeys() -> GlobalMediaHotkeys:
    global _hotkeys_instance
    if _hotkeys_instance is None:
        _hotkeys_instance = GlobalMediaHotkeys()
    return _hotkeys_instance
