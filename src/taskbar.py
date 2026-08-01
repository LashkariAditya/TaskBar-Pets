"""Detect Windows taskbar position and size with robust multi-method fallback."""

import ctypes
from ctypes import wintypes
from dataclasses import dataclass
from enum import IntEnum
import winreg


# ── Win32 globals ──────────────────────────────────────────────────────────────
shell32 = ctypes.windll.shell32
user32 = ctypes.windll.user32


class TaskbarEdge(IntEnum):
    LEFT = 0
    TOP = 1
    RIGHT = 2
    BOTTOM = 3


class RECT(ctypes.Structure):
    _fields_ = [
        ("left", wintypes.LONG),
        ("top", wintypes.LONG),
        ("right", wintypes.LONG),
        ("bottom", wintypes.LONG),
    ]


class APPBARDATA(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("hWnd", wintypes.HWND),
        ("uCallbackMessage", wintypes.UINT),
        ("uEdge", wintypes.UINT),
        ("rc", RECT),
        ("lParam", wintypes.LPARAM),
    ]


ABM_GETTASKBARPOS = 0x00000005
ABM_GETSTATE = 0x00000004
ABS_AUTOHIDE = 0x00000001


def is_autohide_enabled_in_registry() -> bool:
    """Return True if Auto-Hide Taskbar is enabled in Windows Registry settings."""
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Explorer\StuckRects3",
        )
        val, _ = winreg.QueryValueEx(key, "Settings")
        winreg.CloseKey(key)
        return bool(val[8] & 1)
    except Exception:
        return False


def _get_taskbar_hwnd_rect() -> RECT | None:
    """Get the current actual rect of the taskbar window directly via FindWindow."""
    for cls in ("Shell_TrayWnd", "Shell_SecondaryTrayWnd"):
        try:
            hwnd = user32.FindWindowW(cls, None)
            if hwnd:
                r = RECT()
                user32.GetWindowRect(hwnd, ctypes.byref(r))
                if r.right > r.left and r.bottom > r.top:
                    return r
        except Exception:
            pass
    return None


def get_live_taskbar_height() -> int:
    """Return the actual current height of the taskbar (collapses to ~2px when auto-hidden)."""
    # Method 1: Shell window rect
    r = _get_taskbar_hwnd_rect()
    if r is not None:
        screen_h = user32.GetSystemMetrics(1)
        h = r.bottom - r.top
        # only trust if it's near the bottom of screen
        if r.bottom >= screen_h - 10:
            return h

    # Method 2: Work area gap
    try:
        SPI_GETWORKAREA = 48
        work = RECT()
        user32.SystemParametersInfoW(SPI_GETWORKAREA, 0, ctypes.byref(work), 0)
        screen_h = user32.GetSystemMetrics(1)
        gap = screen_h - work.bottom
        if gap >= 5:
            return gap
    except Exception:
        pass

    # Method 3: ABM_GETTASKBARPOS
    try:
        data = APPBARDATA()
        data.cbSize = ctypes.sizeof(APPBARDATA)
        ret = shell32.SHAppBarMessage(ABM_GETTASKBARPOS, ctypes.byref(data))
        if ret and data.rc.bottom > data.rc.top:
            return data.rc.bottom - data.rc.top
    except Exception:
        pass

    return 48  # fallback assume standard height


@dataclass(frozen=True)
class TaskbarInfo:
    left: int
    top: int
    right: int
    bottom: int
    edge: TaskbarEdge

    @property
    def width(self) -> int:
        return self.right - self.left

    @property
    def height(self) -> int:
        return self.bottom - self.top

    def walk_rect(self, max_pet_height: int) -> tuple[int, int, int, int]:
        """Return (x, y, width, height) for the pet overlay."""
        if self.edge == TaskbarEdge.BOTTOM:
            y = self.top - max_pet_height
            return (self.left, y, self.width, max_pet_height)
        if self.edge == TaskbarEdge.TOP:
            y = self.bottom
            return (self.left, y, self.width, max_pet_height)
        if self.edge == TaskbarEdge.LEFT:
            return (self.right, self.top, max_pet_height, self.height)
        # RIGHT edge
        return (self.left - max_pet_height, self.top, max_pet_height, self.height)

    def ground_offset(self, max_pet_height: int) -> int:
        return max_pet_height

    def surface_overlap(self, max_pet_height: int) -> int:
        return 0  # no overlap needed; walk_rect already places pets cleanly above

    def walk_axis_length(self) -> int:
        if self.edge in (TaskbarEdge.BOTTOM, TaskbarEdge.TOP):
            return self.width
        return self.height

    def is_horizontal(self) -> bool:
        return self.edge in (TaskbarEdge.BOTTOM, TaskbarEdge.TOP)

    def is_valid(self) -> bool:
        return self.width > 0 and self.height > 0

    @property
    def is_hidden(self) -> bool:
        """Return True if the auto-hide taskbar is currently collapsed (not visible).

        Strategy: read the LIVE taskbar height right now. When auto-hide taskbar
        is fully collapsed it becomes a ~2px strip. When it's visible it's 40-60px.
        We call get_live_taskbar_height() to get the fresh value each tick.
        """
        live_h = get_live_taskbar_height()
        return live_h <= 12  # collapsed = 2px; visible = 48px


# ── Detection methods ─────────────────────────────────────────────────────────

def _try_appbar() -> TaskbarInfo | None:
    """Try SHAppBarMessage ABM_GETTASKBARPOS (classic method)."""
    try:
        data = APPBARDATA()
        data.cbSize = ctypes.sizeof(APPBARDATA)
        ret = shell32.SHAppBarMessage(ABM_GETTASKBARPOS, ctypes.byref(data))
        if ret and (data.rc.right > 0 or data.rc.bottom > 0):
            h = data.rc.bottom - data.rc.top
            w = data.rc.right - data.rc.left
            if h < 5 or w < 5:
                return None  # collapsed strip, not a real position
            return TaskbarInfo(
                left=data.rc.left,
                top=data.rc.top,
                right=data.rc.right,
                bottom=data.rc.bottom,
                edge=TaskbarEdge(data.uEdge),
            )
    except Exception:
        pass
    return None


def _try_find_tray_window() -> TaskbarInfo | None:
    """Try finding Shell_TrayWnd or Windows 11 taskbar window classes."""
    for cls in ("Shell_TrayWnd", "Shell_SecondaryTrayWnd"):
        try:
            hwnd = user32.FindWindowW(cls, None)
            if hwnd:
                rect = RECT()
                user32.GetWindowRect(hwnd, ctypes.byref(rect))
                if rect.right > rect.left and rect.bottom > rect.top:
                    w = rect.right - rect.left
                    h = rect.bottom - rect.top
                    if h < 5 or w < 5:
                        continue  # collapsed strip
                    screen_h = user32.GetSystemMetrics(1)
                    screen_w = user32.GetSystemMetrics(0)
                    if rect.bottom >= screen_h - 5 and w > h:
                        edge = TaskbarEdge.BOTTOM
                    elif rect.top <= 5 and w > h:
                        edge = TaskbarEdge.TOP
                    elif rect.left <= 5 and h > w:
                        edge = TaskbarEdge.LEFT
                    else:
                        edge = TaskbarEdge.RIGHT
                    return TaskbarInfo(
                        left=rect.left,
                        top=rect.top,
                        right=rect.right,
                        bottom=rect.bottom,
                        edge=edge,
                    )
        except Exception:
            pass
    return None


def _try_work_area() -> TaskbarInfo | None:
    """Infer taskbar from the difference between screen and work area."""
    try:
        SPI_GETWORKAREA = 48
        work = RECT()
        user32.SystemParametersInfoW(SPI_GETWORKAREA, 0, ctypes.byref(work), 0)
        screen_w = user32.GetSystemMetrics(0)
        screen_h = user32.GetSystemMetrics(1)

        if work.right <= 0 or work.bottom <= 0:
            return None

        bottom_gap = screen_h - work.bottom
        top_gap = work.top
        left_gap = work.left
        right_gap = screen_w - work.right

        gaps = {
            TaskbarEdge.BOTTOM: bottom_gap,
            TaskbarEdge.TOP: top_gap,
            TaskbarEdge.LEFT: left_gap,
            TaskbarEdge.RIGHT: right_gap,
        }
        edge, gap_size = max(gaps.items(), key=lambda kv: kv[1])

        # Auto-hidden taskbar: work area = full screen, so gap is 0.
        # Fall back to default 48px bottom taskbar position.
        if gap_size < 5:
            gap_size = 48
            edge = TaskbarEdge.BOTTOM

        if edge == TaskbarEdge.BOTTOM:
            return TaskbarInfo(
                left=0, top=screen_h - gap_size,
                right=screen_w, bottom=screen_h,
                edge=edge,
            )
        elif edge == TaskbarEdge.TOP:
            return TaskbarInfo(
                left=0, top=0,
                right=screen_w, bottom=gap_size,
                edge=edge,
            )
        elif edge == TaskbarEdge.LEFT:
            return TaskbarInfo(
                left=0, top=0,
                right=gap_size, bottom=screen_h,
                edge=edge,
            )
        else:  # RIGHT
            return TaskbarInfo(
                left=screen_w - gap_size, top=0,
                right=screen_w, bottom=screen_h,
                edge=edge,
            )
    except Exception:
        pass
    return None


def _default_taskbar() -> TaskbarInfo:
    """Last-resort fallback: assume bottom taskbar on current screen."""
    screen_w = user32.GetSystemMetrics(0) or 1920
    screen_h = user32.GetSystemMetrics(1) or 1080
    taskbar_h = 48
    return TaskbarInfo(
        left=0,
        top=screen_h - taskbar_h,
        right=screen_w,
        bottom=screen_h,
        edge=TaskbarEdge.BOTTOM,
    )


def get_taskbar_info() -> TaskbarInfo:
    """Return the taskbar STATIC position (edge + bounds) using best detection.

    NOTE: This returns the RESTING position of the taskbar (its full-size position).
    Use TaskbarInfo.is_hidden to check whether an auto-hide taskbar is currently collapsed.
    """
    for method in (_try_appbar, _try_find_tray_window, _try_work_area):
        result = method()
        if result and result.is_valid():
            return result
    return _default_taskbar()
