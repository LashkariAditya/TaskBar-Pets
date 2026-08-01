"""Transparent overlay windows anchored to the taskbar with speech bubbles and interaction."""

from __future__ import annotations

import ctypes
from ctypes import wintypes
import tkinter as tk
from typing import Callable

from config import AppConfig
from src.pet import Pet
from src.taskbar import get_taskbar_info
from src.win32_helpers import (
    GWL_EXSTYLE,
    HWND_TOPMOST,
    LWA_COLORKEY,
    SWP_NOACTIVATE,
    SWP_SHOWWINDOW,
    SetLayeredWindowAttributes,
    SetWindowPos,
    WS_EX_LAYERED,
    WS_EX_NOACTIVATE,
    WS_EX_TOOLWINDOW,
    WS_EX_TRANSPARENT,
    set_window_long,
    get_window_long,
)

TRANSPARENT_COLOR = "#ff00ff"
COLORKEY_RGB = 0x00FF00FF   # BGR format for Win32: 0x00BBGGRR => magenta
TICK_MS = 16  # ~60 fps

# Minimum pixel movement before a click becomes a drag
DRAG_THRESHOLD = 5

user32 = ctypes.windll.user32


def _hwnd(window: tk.Toplevel) -> int:
    """Return the real Win32 HWND for a Tk Toplevel window."""
    try:
        return int(window.frame(), 16)
    except Exception:
        return window.winfo_id()


def _apply_layered_style(hwnd: int, click_through: bool) -> None:
    """Apply layered transparent window style, optionally with click-through."""
    style = get_window_long(hwnd, GWL_EXSTYLE)
    new_style = style | WS_EX_LAYERED | WS_EX_TOOLWINDOW | WS_EX_NOACTIVATE
    if click_through:
        new_style |= WS_EX_TRANSPARENT
    else:
        new_style &= ~WS_EX_TRANSPARENT
    set_window_long(hwnd, GWL_EXSTYLE, new_style)
    # Key out magenta pixels (BGR: 0x00FF00FF)
    SetLayeredWindowAttributes(hwnd, COLORKEY_RGB, 255, LWA_COLORKEY)


def _move_topmost(hwnd: int, x: int, y: int, w: int, h: int) -> None:
    """Move + resize + keep TOPMOST using a single SetWindowPos call."""
    user32.SetWindowPos(
        hwnd,
        HWND_TOPMOST,
        x, y, w, h,
        SWP_NOACTIVATE | SWP_SHOWWINDOW,
    )


class OverlayWindow:
    def __init__(
        self,
        pets: list[Pet],
        config: AppConfig,
        on_close: Callable[[], None] | None = None,
        on_pet_dismiss: Callable[[Pet], None] | None = None,
    ):
        self.pets = pets
        self.config = config
        self.on_close = on_close
        self.on_pet_dismiss = on_pet_dismiss

        self._taskbar = get_taskbar_info()

        # ── Auto-hide taskbar tracking ─────────────────────────────────
        # We detect visibility by cursor position (works because overlay has a real HWND).
        # is_autohide: set once from registry at startup.
        import winreg as _winreg
        try:
            _k = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Explorer\StuckRects3")
            _v, _ = _winreg.QueryValueEx(_k, "Settings")
            _winreg.CloseKey(_k)
            self._is_autohide = bool(_v[8] & 1)
        except Exception:
            self._is_autohide = False

        # True  = taskbar is currently slid up / visible
        # False = taskbar has slid away (hidden)
        self._taskbar_visible: bool = True
        # Seconds since cursor left the bottom zone — after 1.5s we treat as hidden
        self._cursor_away_secs: float = 0.0
        # Seconds since cursor entered the bottom zone — after 0.3s we treat as visible
        self._cursor_near_secs: float = 0.0

        # Per-pet data
        self._pet_photo_lists: dict[int, dict] = {}   # full lists, prevent GC
        self._pet_windows: dict[int, tk.Toplevel] = {}
        self._pet_labels: dict[int, tk.Label] = {}
        self._pet_hwnds: dict[int, int] = {}

        # Effects (speech/particles) per pet
        self._fx_windows: dict[int, tk.Toplevel] = {}
        self._fx_canvases: dict[int, tk.Canvas] = {}
        self._fx_hwnds: dict[int, int] = {}

        # --- Drag state ---
        self._drag_start_mouse: dict[int, tuple[int, int]] = {}  # pet_idx -> (mx, my) at press
        self._drag_start_win: dict[int, tuple[int, int]] = {}    # pet_idx -> (wx, wy) at press
        self._is_dragging: dict[int, bool] = {}                  # pet_idx -> True if drag confirmed

        # Create hidden root first (required before any PhotoImage)
        self.root = tk.Tk()
        self.root.withdraw()
        self.root.protocol("WM_DELETE_WINDOW", self._handle_close)

        self._rebuild_windows()
        self.root.after(TICK_MS, self._tick)

    # ------------------------------------------------------------------
    # Window creation
    # ------------------------------------------------------------------

    def _rebuild_windows(self) -> None:
        for w in list(self._pet_windows.values()) + list(self._fx_windows.values()):
            try:
                w.destroy()
            except Exception:
                pass

        self._pet_windows.clear()
        self._pet_labels.clear()
        self._pet_hwnds.clear()
        self._fx_windows.clear()
        self._fx_canvases.clear()
        self._fx_hwnds.clear()
        self._pet_photo_lists.clear()
        self._drag_start_mouse.clear()
        self._drag_start_win.clear()
        self._is_dragging.clear()

        for i, pet in enumerate(self.pets):
            sx, sy = self._screen_pos(pet, i)

            # ---- Sprite window ----
            sw = tk.Toplevel(self.root)
            sw.overrideredirect(True)
            sw.configure(bg=TRANSPARENT_COLOR)
            sw.attributes("-transparentcolor", TRANSPARENT_COLOR)
            sw.attributes("-topmost", True)

            lbl = tk.Label(sw, bg=TRANSPARENT_COLOR, bd=0, highlightthickness=0)
            lbl.pack()

            # Bind drag events (drag takes priority; click fires only if no drag)
            lbl.bind("<Button-1>",        lambda e, idx=i: self._on_press(e, idx))
            lbl.bind("<B1-Motion>",       lambda e, idx=i: self._on_drag(e, idx))
            lbl.bind("<ButtonRelease-1>", lambda e, idx=i: self._on_release(e, idx))
            lbl.bind("<Double-Button-1>", lambda e, p=pet: p.feed())
            lbl.bind("<Button-3>",        lambda e, p=pet: self._show_menu(e, p))

            # Position at correct spot immediately
            sw.geometry(f"{pet.width}x{pet.height}+{sx}+{sy}")
            sw.update_idletasks()

            self._pet_windows[i] = sw
            self._pet_labels[i] = lbl

            # ---- Effects window (speech bubble) ----
            fx_w = max(pet.width + 120, 200)
            fx_h = 50

            fw = tk.Toplevel(self.root)
            fw.overrideredirect(True)
            fw.configure(bg=TRANSPARENT_COLOR)
            fw.attributes("-transparentcolor", TRANSPARENT_COLOR)
            fw.attributes("-topmost", True)

            fc = tk.Canvas(
                fw, width=fx_w, height=fx_h,
                bg=TRANSPARENT_COLOR, bd=0, highlightthickness=0,
            )
            fc.pack()

            fw.geometry(f"{fx_w}x{fx_h}+{sx - (fx_w - pet.width)//2}+{sy - fx_h}")
            fw.update_idletasks()

            self._fx_windows[i] = fw
            self._fx_canvases[i] = fc

            # Load PhotoImages NOW (tk.Tk() already exists)
            self._pet_photo_lists[i] = pet.sprites.to_tk_frames()

        # Wait for Tk to fully realize windows, then apply Win32 styles
        self.root.update()
        self._apply_styles()

        # Set initial frame on every label
        for i, pet in enumerate(self.pets):
            frames = self._pet_photo_lists.get(i, {}).get("walk", [])
            if frames:
                lbl = self._pet_labels[i]
                lbl.configure(image=frames[0])
                lbl.image = frames[0]

        self.root.update()

    def _apply_styles(self) -> None:
        click_through = not self.config.interactive_mode
        for i in list(self._pet_windows.keys()):
            sw = self._pet_windows[i]
            fw = self._fx_windows[i]

            shwnd = _hwnd(sw)
            fhwnd = _hwnd(fw)

            _apply_layered_style(shwnd, click_through)
            _apply_layered_style(fhwnd, True)  # effects window is always click-through

            self._pet_hwnds[i] = shwnd
            self._fx_hwnds[i] = fhwnd

    # ------------------------------------------------------------------
    # Drag-to-place logic
    # ------------------------------------------------------------------

    def _on_press(self, event: tk.Event, idx: int) -> None:
        """Record the start position for a potential drag."""
        pet = self.pets[idx] if idx < len(self.pets) else None
        if pet is None:
            return
        sx, sy = self._screen_pos(pet, idx)
        self._drag_start_mouse[idx] = (event.x_root, event.y_root)
        self._drag_start_win[idx] = (sx, sy)
        self._is_dragging[idx] = False

    def _on_drag(self, event: tk.Event, idx: int) -> None:
        """Move the pet window while the mouse button is held."""
        if idx not in self._drag_start_mouse:
            return
        mx0, my0 = self._drag_start_mouse[idx]
        dx = event.x_root - mx0
        dy = event.y_root - my0

        # Confirm drag once threshold is exceeded
        if not self._is_dragging[idx]:
            if abs(dx) < DRAG_THRESHOLD and abs(dy) < DRAG_THRESHOLD:
                return
            self._is_dragging[idx] = True

        pet = self.pets[idx] if idx < len(self.pets) else None
        if pet is None:
            return

        wx0, wy0 = self._drag_start_win[idx]
        new_x = wx0 + dx
        new_y = wy0 + dy

        # Move window immediately via SetWindowPos for smooth dragging
        shwnd = self._pet_hwnds.get(idx)
        if shwnd:
            _move_topmost(shwnd, new_x, new_y, pet.width, pet.height)

        # Also move the effects window
        fhwnd = self._fx_hwnds.get(idx)
        if fhwnd:
            fx_w = max(pet.width + 120, 200)
            fx_h = 50
            _move_topmost(fhwnd, new_x - (fx_w - pet.width) // 2, new_y - fx_h, fx_w, fx_h)

    def _on_release(self, event: tk.Event, idx: int) -> None:
        """On release: save custom X+Y for session walking; click = affection."""
        pet = self.pets[idx] if idx < len(self.pets) else None
        if pet is None:
            return

        if self._is_dragging.get(idx, False):
            mx0, my0 = self._drag_start_mouse[idx]
            wx0, wy0 = self._drag_start_win[idx]
            new_x = wx0 + (event.x_root - mx0)
            new_y = wy0 + (event.y_root - my0)

            # Clamp X so pet stays within screen width, use screen width walk range
            screen_w = self.root.winfo_screenwidth()
            safe_x = max(0, min(new_x, screen_w - pet.width))

            # Save session-only custom position (cleared on restart automatically)
            pet.custom_y = new_y
            pet.custom_x_start = safe_x
            # Reset horizontal walk counter to new origin
            pet.x = 0.0
            pet.say("📍 Moved!")
        else:
            # Plain click — trigger affection
            pet.pet()

        # Clean up drag state
        self._drag_start_mouse.pop(idx, None)
        self._drag_start_win.pop(idx, None)
        self._is_dragging[idx] = False

    def _reset_pet_pos(self, pet: Pet) -> None:
        """Reset pet back to default taskbar position (clears session-only position)."""
        pet.custom_y = None
        pet.custom_x_start = None
        pet.x = 0.0
        pet.say("🚶 Back to Taskbar!")

    # ------------------------------------------------------------------
    # Interaction
    # ------------------------------------------------------------------

    def update_interactivity(self, interactive_mode: bool) -> None:
        self.config.interactive_mode = interactive_mode
        self._apply_styles()

    def update_pets(self, new_pets: list[Pet]) -> None:
        self.pets = new_pets
        self._rebuild_windows()

    def _on_click(self, pet: Pet) -> None:
        pet.pet()

    def _show_menu(self, event: tk.Event, pet: Pet) -> None:
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label=f"  {pet.name.capitalize()}", state="disabled")
        menu.add_separator()
        menu.add_command(label="  Give Affection", command=pet.pet)
        menu.add_command(label="  Feed Berry", command=pet.feed)
        menu.add_command(label="  Sleep / Wake", command=pet.toggle_sleep)
        menu.add_command(label="  Say Something", command=pet.say_random)
        menu.add_separator()
        if pet.custom_y is not None or pet.custom_x_start is not None:
            menu.add_command(label="  ↩️ Reset to Taskbar Position", command=lambda: self._reset_pet_pos(pet))
        else:
            menu.add_command(label="  🖱️ Drag to move (resets on restart)", state="disabled")
        menu.add_separator()
        if self.on_pet_dismiss:
            menu.add_command(
                label="  Dismiss Pet", command=lambda: self.on_pet_dismiss(pet)
            )
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def _pin_pet_here(self, pet: Pet) -> None:
        """Pin a pet at its current position via the right-click menu."""
        # Use the pet's current computed screen position
        sx, sy = self._screen_pos(pet)
        pet.free_roam = True
        pet.free_x = sx
        pet.free_y = sy
        pet.say("📌 Pinned here!")

    def _handle_close(self) -> None:
        if self.on_close:
            self.on_close()
        self.root.destroy()

    # ------------------------------------------------------------------
    # Main tick / render loop
    # ------------------------------------------------------------------

    def _check_real_taskbar_hidden(self) -> bool:
        """Check if the Windows Taskbar window (Shell_TrayWnd) is currently collapsed/hidden.

        Strictly queries real Win32 taskbar window bounds — NOT mouse position!
        """
        screen_h = user32.GetSystemMetrics(1)
        for cls in ("Shell_TrayWnd", "Shell_SecondaryTrayWnd"):
            try:
                hwnd = user32.FindWindowW(cls, None)
                if hwnd:
                    class RECT(ctypes.Structure):
                        _fields_ = [("left", wintypes.LONG), ("top", wintypes.LONG), ("right", wintypes.LONG), ("bottom", wintypes.LONG)]
                    r = RECT()
                    user32.GetWindowRect(hwnd, ctypes.byref(r))
                    h = r.bottom - r.top
                    # When taskbar collapses in Windows auto-hide, top slides down off-screen
                    if r.top >= screen_h - 10 or h <= 10:
                        return True
                    else:
                        return False
            except Exception:
                pass

        # Fallback: check work area gap & registry flag
        try:
            class RECT(ctypes.Structure):
                _fields_ = [("left", wintypes.LONG), ("top", wintypes.LONG), ("right", wintypes.LONG), ("bottom", wintypes.LONG)]
            work = RECT()
            user32.SystemParametersInfoW(48, 0, ctypes.byref(work), 0)
            gap = screen_h - work.bottom
            if gap < 5:
                import winreg
                try:
                    k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\StuckRects3")
                    v, _ = winreg.QueryValueEx(k, "Settings")
                    winreg.CloseKey(k)
                    return bool(v[8] & 1)
                except Exception:
                    pass
        except Exception:
            pass

        return False

    def _tick(self) -> None:
        if not self.root.winfo_exists():
            return

        dt = TICK_MS / 1000.0

        new_tb = get_taskbar_info()
        if (
            new_tb.left != self._taskbar.left
            or new_tb.top != self._taskbar.top
            or new_tb.width != self._taskbar.width
            or new_tb.height != self._taskbar.height
        ):
            self._taskbar = new_tb
            self._apply_styles()

        walk_length = self._taskbar.walk_axis_length()
        freeze = self.config.freeze_pets

        for i, pet in enumerate(self.pets):
            if i not in self._pet_windows:
                continue

            # Skip update for this pet while it's being actively dragged
            if self._is_dragging.get(i, False):
                continue

            lbl = self._pet_labels[i]
            fc = self._fx_canvases.get(i)

            if pet.custom_x_start is not None:
                # Walk freely across the full screen width from origin
                screen_w = self.root.winfo_screenwidth()
                max_walk = max(0, screen_w - pet.custom_x_start - pet.width)
                min_x, max_x = 0.0, float(max_walk)
            else:
                min_x, max_x = 0.0, float(max(0, walk_length - pet.width))
            pet.update(dt, min_x, max_x, speed_mult=self.config.pet_speed,
                       freeze=freeze)

            # -- Select and apply frame (Walk animation vs Front-Facing Idle Model) --
            photos = self._pet_photo_lists.get(i, {})
            from src.pet import PetState
            if pet.state in (PetState.IDLE, PetState.HAPPY, PetState.SLEEP) or freeze:
                key = "idle_flip" if pet.direction < 0 else "idle"
            else:
                key = "walk_flip" if pet.direction < 0 else "walk"

            frames = photos.get(key, photos.get("walk", []))
            if frames:
                frame = frames[pet.frame_index % len(frames)]
                lbl.configure(image=frame)
                lbl.image = frame   # strong ref

            # -- Compute screen position --
            sx, sy = self._screen_pos(pet, i, dt)

            # Use SetWindowPos to move + keep topmost atomically
            shwnd = self._pet_hwnds.get(i)
            if shwnd:
                _move_topmost(shwnd, sx, sy, pet.width, pet.height)

            # -- Effects window --
            if fc is not None:
                fx_w = max(pet.width + 120, 200)
                fx_h = 50
                fx_x = sx - (fx_w - pet.width) // 2
                fx_y = sy - fx_h
                fhwnd = self._fx_hwnds.get(i)
                if fhwnd:
                    _move_topmost(fhwnd, fx_x, fx_y, fx_w, fx_h)

                fc.delete("all")

                # Custom height indicator badge
                if pet.custom_y is not None:
                    fc.create_text(
                        fx_w // 2, 10,
                        text="📍", font=("Segoe UI", 9),
                        fill="#f9e2af",
                    )

                # Speech bubble
                if self.config.speech_enabled and pet.speech_text:
                    cx, cy = fx_w // 2, fx_h // 2
                    t = pet.speech_text
                    tw = len(t) * 7 + 18
                    th = 22
                    fc.create_rectangle(
                        cx - tw // 2, cy - th // 2,
                        cx + tw // 2, cy + th // 2,
                        fill="#1e1e2e", outline="#cdd6f4", width=1,
                    )
                    fc.create_text(cx, cy, text=t, fill="#cdd6f4",
                                   font=("Segoe UI", 9, "bold"))

                # Particles
                if self.config.particles_enabled:
                    for p in pet.particles:
                        age_frac = p.age / max(p.lifetime, 0.001)
                        px = fx_w // 2 + int(p.x - (pet.x + pet.width / 2))
                        py = int(fx_h * (1.0 - age_frac))
                        glyph = {"heart": "♥", "zzz": "z", "sparkle": "*"}.get(p.kind, "+")
                        color = {"heart": "#ff4d6d", "zzz": "#9d4edd", "sparkle": "#ffb703"}.get(p.kind, "#fff")
                        fc.create_text(px, py, text=glyph, fill=color,
                                       font=("Segoe UI", 12, "bold"))

        self.root.after(TICK_MS, self._tick)

    def _screen_pos(self, pet: Pet, pet_index: int = 0, dt: float = 0.016) -> tuple[int, int]:
        """Calculate screen (x, y) for pet.

        • Freeze (Stop Walking OFF): pets sit fixed above system tray clock. When taskbar
          auto-hides they fall to the bottom; when it reappears they rise back.
        • Walking ON: pets walk along the taskbar; fall when taskbar hides.
        """
        tb = self._taskbar
        offset = getattr(self.config, 'taskbar_offset', 0)
        screen_h = user32.GetSystemMetrics(1)
        screen_w = user32.GetSystemMetrics(0)

        # Taskbar top edge (physical px) — where pet feet should rest
        taskbar_top = tb.top  # e.g. 1032 on 1080p with 48px taskbar

        # Is the auto-hide taskbar currently collapsed? (Strictly Win32 taskbar rect — NO mouse tracking)
        taskbar_is_hidden = self._check_real_taskbar_hidden()

        # ── Stopped / Freeze Mode (Fixed Position above Clock) ─────────────
        if self.config.freeze_pets and pet.custom_y is None and pet.custom_x_start is None:
            # Horizontally fixed side-by-side above clock (no walking left/right)
            right_margin = 20
            target_x = screen_w - right_margin
            for j in range(pet_index + 1):
                if j < len(self.pets):
                    target_x -= (self.pets[j].width + 8)
            sx = max(0, target_x)

            # Target Y floor: falls to screen bottom when taskbar hides, rises when visible
            if taskbar_is_hidden:
                target_y = float(screen_h - pet.height + offset)
            else:
                target_y = float(taskbar_top - pet.height + offset)

            sy = int(pet.update_vertical(dt, target_y))
            return sx, sy

        # ── Walking Mode ─────────────────────────────────────────────────
        if pet.custom_y is not None:
            target_y = float(pet.custom_y)
        elif taskbar_is_hidden:
            # Taskbar auto-hidden → fall to very bottom of screen
            target_y = float(screen_h - pet.height + offset)
        elif tb.edge.name == "BOTTOM":
            # Taskbar visible → feet on top of taskbar
            target_y = float(taskbar_top - pet.height + offset)
        elif tb.edge.name == "TOP":
            target_y = float(tb.bottom + offset)
        elif tb.edge.name == "LEFT":
            target_y = float(tb.top + int(pet.x))
        else:  # RIGHT
            target_y = float(tb.top + int(pet.x))

        # Gravity physics animation
        sy = int(pet.update_vertical(dt, target_y))

        # ── X position ───────────────────────────────────────────────────
        if pet.custom_x_start is not None:
            sx = pet.custom_x_start + int(pet.x)
        elif tb.edge.name in ("BOTTOM", "TOP"):
            sx = tb.left + int(pet.x)
        elif tb.edge.name == "LEFT":
            sx = tb.right + offset
        else:  # RIGHT
            sx = tb.left - pet.width + offset

        return sx, sy

    def run(self) -> None:
        self.root.mainloop()
