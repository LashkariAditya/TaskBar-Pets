"""Win32 helpers for layered, click-through overlay windows."""

import ctypes
from ctypes import wintypes

user32 = ctypes.windll.user32

GWL_EXSTYLE = -20
WS_EX_LAYERED = 0x00080000
WS_EX_TRANSPARENT = 0x00000020
WS_EX_TOOLWINDOW = 0x00000080
WS_EX_NOACTIVATE = 0x08000000

SWP_NOMOVE = 0x0002
SWP_NOSIZE = 0x0001
SWP_NOACTIVATE = 0x0010
SWP_SHOWWINDOW = 0x0040
HWND_TOPMOST = wintypes.HWND(-1)
LWA_COLORKEY = 0x00000001

GetWindowLongPtr = user32.GetWindowLongPtrW
SetWindowLongPtr = user32.SetWindowLongPtrW
SetWindowPos = user32.SetWindowPos
SetLayeredWindowAttributes = user32.SetLayeredWindowAttributes
GetWindow = user32.GetWindow
GetAncestor = user32.GetAncestor
GW_OWNER = 4
GA_ROOT = 2

LONG_PTR = wintypes.LPARAM

GetWindowLongPtr.argtypes = [wintypes.HWND, ctypes.c_int]
GetWindowLongPtr.restype = LONG_PTR
SetWindowLongPtr.argtypes = [wintypes.HWND, ctypes.c_int, LONG_PTR]
SetWindowLongPtr.restype = LONG_PTR
SetWindowPos.argtypes = [
    wintypes.HWND,
    wintypes.HWND,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    wintypes.UINT,
]
SetWindowPos.restype = wintypes.BOOL
SetLayeredWindowAttributes.argtypes = [
    wintypes.HWND,
    wintypes.COLORREF,
    wintypes.BYTE,
    wintypes.DWORD,
]
SetLayeredWindowAttributes.restype = wintypes.BOOL
GetWindow.argtypes = [wintypes.HWND, wintypes.UINT]
GetWindow.restype = wintypes.HWND
GetAncestor.argtypes = [wintypes.HWND, wintypes.UINT]
GetAncestor.restype = wintypes.HWND


def get_root_window(hwnd: int) -> int:
    root = GetAncestor(hwnd, GA_ROOT)
    return root or hwnd


def get_window_long(hwnd: int, index: int) -> int:
    return GetWindowLongPtr(hwnd, index)


def set_window_long(hwnd: int, index: int, value: int) -> int:
    return SetWindowLongPtr(hwnd, index, value)


def make_click_through(hwnd: int) -> None:
    """Make the pet window layered/topmost and hide it from alt-tab."""
    set_click_through(hwnd, True)


def set_click_through(hwnd: int, click_through: bool = True) -> None:
    """Toggle WS_EX_TRANSPARENT on a window handle."""
    style = get_window_long(hwnd, GWL_EXSTYLE)
    base_style = style | WS_EX_LAYERED | WS_EX_TOOLWINDOW | WS_EX_NOACTIVATE
    if click_through:
        new_style = base_style | WS_EX_TRANSPARENT
    else:
        new_style = base_style & ~WS_EX_TRANSPARENT

    set_window_long(hwnd, GWL_EXSTYLE, new_style)
    SetLayeredWindowAttributes(hwnd, 0x00FF00FF, 255, LWA_COLORKEY)



def ensure_topmost(hwnd: int) -> None:
    SetWindowPos(
        hwnd,
        HWND_TOPMOST,
        0,
        0,
        0,
        0,
        SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE | SWP_SHOWWINDOW,
    )
    owner = GetWindow(hwnd, GW_OWNER)
    if owner:
        SetWindowPos(
            owner,
            HWND_TOPMOST,
            0,
            0,
            0,
            0,
            SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE,
        )
