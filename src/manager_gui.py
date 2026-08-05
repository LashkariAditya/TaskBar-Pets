"""Tkinter GUI Pet Manager & Settings Control Panel for Taskbar Pets."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable

from config import AppConfig
from src.autostart import is_autostart_enabled, set_autostart
from src.sprites import discover_pokemon
from src.version import APP_VERSION

# ── Pure Black Minimal Palette (Matching Screenshot Aesthetic) ───────────────
BG       = "#000000"   # Pure black
SURFACE0 = "#0a0a0a"   # Near-black surface
SURFACE1 = "#111111"   # Card background
SURFACE2 = "#1a1a1a"   # Border / hover
SURFACE3 = "#222222"   # Active hover
OVERLAY  = "#333333"   # Toggle off
TEXT     = "#ffffff"   # Pure white text
SUBTEXT  = "#888888"   # Muted grey
DIM      = "#444444"   # Very muted border
ACCENT   = "#ffffff"   # White accent
GREEN    = "#4ade80"   # Selection green
RED      = "#ff4444"   # Error red
BLUE     = "#60a5fa"   # Soft blue


def _make_toggle(parent, text: str, var: tk.BooleanVar,
                 accent: str = ACCENT, on_change: Callable[[], None] | None = None) -> tk.Frame:
    """Minimal pill toggle row."""
    row = tk.Frame(parent, bg=SURFACE1)

    inner = tk.Frame(row, bg=SURFACE1, padx=20, pady=14)
    inner.pack(fill="x")

    tk.Label(inner, text=text, font=("Segoe UI", 10),
             bg=SURFACE1, fg=TEXT, justify="left").pack(side="left")

    SWITCH_W, SWITCH_H = 44, 22
    sw_canvas = tk.Canvas(inner, width=SWITCH_W, height=SWITCH_H,
                           bg=SURFACE1, bd=0, highlightthickness=0)
    sw_canvas.pack(side="right")

    def _redraw(*_):
        sw_canvas.delete("all")
        on = var.get()
        fill = TEXT if on else OVERLAY
        sw_canvas.create_rectangle(0, 0, SWITCH_W, SWITCH_H, fill=fill, outline=DIM, width=1)
        kx = SWITCH_W - 13 if on else 13
        bg_k = BG if on else SUBTEXT
        sw_canvas.create_oval(kx - 7, 4, kx + 7, SWITCH_H - 4, fill=bg_k, outline="")

    def _toggle(_event=None):
        var.set(not var.get())
        _redraw()
        if on_change:
            on_change()

    sw_canvas.bind("<Button-1>", _toggle)
    inner.bind("<Button-1>", _toggle)
    var.trace_add("write", _redraw)
    _redraw()
    return row


def _slider_row(parent, label: str, var: tk.DoubleVar,
                from_: float, to: float,
                fmt: str = "{:.1f}", unit: str = "") -> None:
    row = tk.Frame(parent, bg=SURFACE1)
    row.pack(fill="x")

    header = tk.Frame(row, bg=SURFACE1)
    header.pack(fill="x", padx=20, pady=14)

    tk.Label(header, text=label, font=("Segoe UI", 10),
             bg=SURFACE1, fg=TEXT).pack(side="left")

    val_lbl = tk.Label(header, text=fmt.format(var.get()) + unit,
                       font=("Segoe UI", 10, "bold"),
                       bg=SURFACE1, fg=SUBTEXT)
    val_lbl.pack(side="right")

    style = ttk.Style()
    style.configure("Mono.Horizontal.TScale", troughcolor=SURFACE3,
                    background=SURFACE1, sliderlength=14)

    slider = ttk.Scale(row, from_=from_, to=to, variable=var, orient="horizontal",
                       style="Mono.Horizontal.TScale")
    slider.pack(fill="x", padx=20, pady=14)

    def _update(*_):
        val_lbl.configure(text=fmt.format(var.get()) + unit)

    var.trace_add("write", _update)


def _divider(parent):
    tk.Frame(parent, bg=SURFACE2, height=1).pack(fill="x")


class PetManagerWindow:
    def __init__(
        self,
        config: AppConfig,
        on_save_callback: Callable[[AppConfig], None] | None = None,
        on_check_updates_callback: Callable[[], None] | None = None,
    ):
        self.config = config
        self.on_save_callback = on_save_callback
        self.on_check_updates_callback = on_check_updates_callback

        self.root = tk.Toplevel()
        self.root.title("Taskbar Pets")
        self.root.geometry("600x720")
        self.root.minsize(520, 600)
        self.root.configure(bg=BG)
        self.root.attributes("-topmost", True)

        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure(".", background=BG, foreground=TEXT, font=("Segoe UI", 10))
        style.configure("TLabel", background=BG, foreground=TEXT)
        style.configure("TFrame", background=BG)
        style.configure("TNotebook", background=BG, borderwidth=0, tabmargins=0)
        style.configure("TNotebook.Tab",
                        background=BG, foreground=SUBTEXT,
                        padding=[22, 10], font=("Segoe UI", 10),
                        borderwidth=0)
        style.map("TNotebook.Tab",
                  background=[("selected", BG), ("active", SURFACE1)],
                  foreground=[("selected", TEXT), ("active", TEXT)])
        style.configure("Vertical.TScrollbar",
                        background=SURFACE2, troughcolor=BG,
                        borderwidth=0, arrowsize=0, relief="flat", width=4)
        style.map("Vertical.TScrollbar",
                  background=[("active", SURFACE3)])

        self.selected_pets: dict[str, tk.BooleanVar] = {}
        self._build_ui()

    def _build_ui(self) -> None:
        # ── Top header bar ────────────────────────────────────────────────
        header = tk.Frame(self.root, bg=BG, padx=28, pady=22)
        header.pack(fill="x")

        title_col = tk.Frame(header, bg=BG)
        title_col.pack(side="left", fill="x", expand=True)

        tk.Label(title_col, text="TASKBAR PETS",
                 font=("Segoe UI", 20, "bold"),
                 bg=BG, fg=TEXT).pack(anchor="w")
        tk.Label(title_col, text="Desktop Companion Manager",
                 font=("Segoe UI", 10),
                 bg=BG, fg=SUBTEXT).pack(anchor="w", pady=2)

        # Version badge
        tk.Label(header, text=f"v{APP_VERSION}",
                 font=("Segoe UI", 9),
                 bg=SURFACE2, fg=SUBTEXT,
                 padx=8, pady=4).pack(side="right", anchor="n")

        _divider(self.root)

        # ── Bottom save bar (packed before content so it stays pinned) ────
        bar = tk.Frame(self.root, bg=BG, padx=28, pady=18)
        bar.pack(fill="x", side="bottom")

        _divider(self.root)

        update_btn = tk.Label(
            bar,
            text="Check for Updates",
            font=("Segoe UI", 10),
            bg=BG,
            fg=TEXT,
            cursor="hand2",
            padx=16,
            pady=8,
        )
        update_btn.pack(side="left")
        if self.on_check_updates_callback:
            update_btn.bind("<Button-1>", lambda _: self.on_check_updates_callback())
            update_btn.bind("<Enter>", lambda _: update_btn.configure(fg=SUBTEXT))
            update_btn.bind("<Leave>", lambda _: update_btn.configure(fg=TEXT))
        else:
            update_btn.configure(fg=SUBTEXT, cursor="arrow")

        cancel_btn = tk.Label(bar, text="Cancel",
                              font=("Segoe UI", 10), bg=BG, fg=SUBTEXT,
                              cursor="hand2", padx=16, pady=8)
        cancel_btn.pack(side="right", padx=12)
        cancel_btn.bind("<Button-1>", lambda _: self.root.destroy())
        cancel_btn.bind("<Enter>", lambda _: cancel_btn.configure(fg=TEXT))
        cancel_btn.bind("<Leave>", lambda _: cancel_btn.configure(fg=SUBTEXT))

        save_btn = tk.Label(
            bar,
            text="  Save & Apply  ",
            font=("Segoe UI", 10, "bold"),
            bg=TEXT, fg=BG,
            padx=20, pady=8,
            cursor="hand2",
        )
        save_btn.pack(side="right")
        save_btn.bind("<Button-1>", lambda _: self._save_and_apply())
        save_btn.bind("<Enter>", lambda _: save_btn.configure(bg=SUBTEXT))
        save_btn.bind("<Leave>", lambda _: save_btn.configure(bg=TEXT))

        # ── Tab navigation ────────────────────────────────────────────────
        nb = ttk.Notebook(self.root)
        nb.pack(fill="both", expand=True, padx=0, pady=0)

        roster_tab = tk.Frame(nb, bg=BG)
        nb.add(roster_tab, text="  Roster  ")

        settings_tab = tk.Frame(nb, bg=BG)
        nb.add(settings_tab, text="  Settings  ")

        self._build_roster_tab(roster_tab)
        self._build_settings_tab(settings_tab)

    # ─────────────────────────────────────────────────────────────────────────
    # Roster Tab
    # ─────────────────────────────────────────────────────────────────────────

    def _build_roster_tab(self, parent: tk.Frame) -> None:
        from src.sprites import discover_pokemon_by_gen, discover_pokemon, GEN_KEYS, SPECIAL_KEYS, GEN_LABELS

        self._roster_parent = parent
        self._roster_discover = discover_pokemon
        self._roster_discover_by_gen = discover_pokemon_by_gen

        # ── Search Bar ────────────────────────────────────────────────────
        search_outer = tk.Frame(parent, bg=BG, padx=24, pady=14)
        search_outer.pack(fill="x")

        search_box = tk.Frame(search_outer, bg=SURFACE1,
                              highlightbackground=SURFACE2, highlightthickness=1)
        search_box.pack(fill="x")

        tk.Label(search_box, text="🔍", bg=SURFACE1, fg=SUBTEXT,
                 font=("Segoe UI", 10), padx=12, pady=10).pack(side="left")

        search_var = tk.StringVar()
        search_entry = tk.Entry(search_box, textvariable=search_var,
                                bg=SURFACE1, fg=TEXT, insertbackground=TEXT,
                                bd=0, highlightthickness=0,
                                font=("Segoe UI", 11), width=30)
        search_entry.pack(side="left", fill="x", expand=True, pady=10)

        clear_btn = tk.Label(search_box, text="✕", bg=SURFACE1, fg=SUBTEXT,
                             font=("Segoe UI", 10), padx=12, pady=10,
                             cursor="hand2")
        clear_btn.pack(side="right")
        clear_btn.bind("<Button-1>", lambda _: search_var.set(""))

        # Placeholder
        def _on_focus_in(_):
            if search_entry.get() == "Search Pokémon...":
                search_entry.delete(0, "end")
                search_entry.configure(fg=TEXT)

        def _on_focus_out(_):
            if not search_entry.get():
                search_entry.insert(0, "Search Pokémon...")
                search_entry.configure(fg=SUBTEXT)

        search_entry.insert(0, "Search Pokémon...")
        search_entry.configure(fg=SUBTEXT)
        search_entry.bind("<FocusIn>", _on_focus_in)
        search_entry.bind("<FocusOut>", _on_focus_out)

        # ── Gen Filter Tabs ───────────────────────────────────────────────
        gen_bar = tk.Frame(parent, bg=BG, padx=24, pady=8)
        gen_bar.pack(fill="x")

        self.current_gen = tk.StringVar(value="all")
        self._gen_btn_widgets: dict[str, tk.Label] = {}

        all_gen_options = [("All", "all")]
        for gen_key in GEN_KEYS + SPECIAL_KEYS:
            all_gen_options.append((GEN_LABELS.get(gen_key, gen_key), gen_key))

        for label_text, gen_code in all_gen_options:
            is_active = (gen_code == "all")
            btn = tk.Label(
                gen_bar,
                text=label_text,
                font=("Segoe UI", 9),
                bg=TEXT if is_active else BG,
                fg=BG if is_active else SUBTEXT,
                padx=12, pady=5, cursor="hand2"
            )
            btn.pack(side="left", padx=4)
            self._gen_btn_widgets[gen_code] = btn

        # ── Selection Counter + Quick Actions ──────────────────────────────
        action_row = tk.Frame(parent, bg=BG, padx=24, pady=8)
        action_row.pack(fill="x")

        max_init = getattr(self.config, "max_active_pets", 5)
        count_lbl = tk.Label(action_row, text=f"0/{max_init} selected",
                             font=("Segoe UI", 9),
                             bg=BG, fg=SUBTEXT)
        count_lbl.pack(side="left")

        for (label, cmd, clr) in [
            ("Clear", self._clear_all, SUBTEXT),
            ("Default", self._select_default, SUBTEXT),
        ]:
            b = tk.Label(action_row, text=label,
                         font=("Segoe UI", 9),
                         bg=BG, fg=clr, cursor="hand2", padx=8)
            b.pack(side="right")
            b.bind("<Button-1>", lambda _, c=cmd: c())
            b.bind("<Enter>", lambda _, w=b: w.configure(fg=TEXT))
            b.bind("<Leave>", lambda _, w=b, c=clr: w.configure(fg=c))

        _divider(parent)

        # ── Card Grid Container ──────────────────────────────────────────
        container = tk.Frame(parent, bg=BG)
        container.pack(fill="both", expand=True)

        canvas = tk.Canvas(container, bg=BG, bd=0,
                           highlightthickness=0, yscrollincrement=1)
        scrollbar = ttk.Scrollbar(container, orient="vertical",
                                  command=canvas.yview,
                                  style="Vertical.TScrollbar")

        scroll_frame = tk.Frame(canvas, bg=BG)
        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        win_id = canvas.create_window((0, 0), window=scroll_frame, anchor="nw")

        def _on_canvas_resize(e):
            canvas.itemconfig(win_id, width=e.width)
        canvas.bind("<Configure>", _on_canvas_resize)

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def _on_wheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)) * 40, "units")

        def _bind_wheel(widget):
            widget.bind("<MouseWheel>", _on_wheel)
            for child in widget.winfo_children():
                _bind_wheel(child)

        canvas.bind("<MouseWheel>", _on_wheel)
        canvas.bind("<Enter>", lambda _: canvas.focus_set())

        def _update_count():
            n = sum(v.get() for v in self.selected_pets.values())
            max_allowed = getattr(self.config, "max_active_pets", 5)
            if n >= max_allowed:
                count_lbl.configure(text=f"✓ {n}/{max_allowed} selected  (max reached)", fg=GREEN)
            else:
                count_lbl.configure(text=f"{n}/{max_allowed} selected", fg=SUBTEXT)

        self._update_count = _update_count

        def _sync_selection_vars(all_pokemon: list[str]) -> None:
            for p_name in all_pokemon:
                if p_name not in self.selected_pets:
                    self.selected_pets[p_name] = tk.BooleanVar(
                        value=(p_name in self.config.active_pets))

        def _render_grid(*_):
            by_gen = self._roster_discover_by_gen()
            all_pokemon = self._roster_discover()
            _sync_selection_vars(all_pokemon)

            for w in scroll_frame.winfo_children():
                w.destroy()

            selected_gen = self.current_gen.get()
            raw_query = search_var.get().strip()
            query = raw_query.lower() if raw_query != "Search Pokémon..." else ""

            if selected_gen == "all":
                pool = all_pokemon
            else:
                pool = by_gen.get(selected_gen, [])

            if query:
                pool = [p for p in pool if query in p.lower()]

            if not pool:
                tk.Label(scroll_frame, text="No Pokémon found",
                         font=("Segoe UI", 11), bg=BG, fg=SUBTEXT,
                         pady=40).pack()
                canvas.configure(scrollregion=canvas.bbox("all"))
                _bind_wheel(scroll_frame)
                _update_count()
                return

            COLS = 3
            for c in range(COLS):
                scroll_frame.columnconfigure(c, weight=1, uniform="col")

            for idx, p_name in enumerate(pool):
                row_idx = idx // COLS
                col_idx = idx % COLS
                var = self.selected_pets.get(p_name)
                if not var:
                    var = tk.BooleanVar(value=(p_name in self.config.active_pets))
                    self.selected_pets[p_name] = var

                display_name = p_name.replace("_", " ").capitalize()

                card = tk.Frame(scroll_frame, bg=SURFACE1,
                                highlightthickness=1,
                                highlightbackground=SURFACE2)
                card.grid(row=row_idx, column=col_idx, padx=5, pady=4, sticky="nsew")

                inner = tk.Frame(card, bg=SURFACE1, padx=10, pady=10)
                inner.pack(fill="both")

                # Name label
                name_lbl = tk.Label(inner, text=display_name,
                                    font=("Segoe UI", 9, "bold"),
                                    bg=SURFACE1, fg=TEXT, anchor="w")
                name_lbl.pack(side="left", fill="x", expand=True)

                # Checkbox dot
                dot = tk.Canvas(inner, width=16, height=16,
                                bg=SURFACE1, bd=0, highlightthickness=0)
                dot.pack(side="right")

                def _draw_dot(c=dot, v=var):
                    c.delete("all")
                    if v.get():
                        c.create_oval(1, 1, 15, 15, fill=TEXT, outline="")
                    else:
                        c.create_oval(1, 1, 15, 15, fill="", outline=DIM, width=1)

                def _toggle_card(event=None, v=var, d=_draw_dot,
                                 crd=card, ic=inner, n_lbl=name_lbl, dt=dot):
                    current_count = sum(
                        var_item.get() for var_item in self.selected_pets.values()
                    )
                    max_allowed = getattr(self.config, "max_active_pets", 5)
                    if not v.get() and current_count >= max_allowed:
                        count_lbl.configure(
                            text=f"⚠  Max {max_allowed} pets — deselect one first", fg=RED
                        )
                        return
                    v.set(not v.get())
                    d()
                    if v.get():
                        crd.configure(highlightbackground=TEXT)
                        ic.configure(bg=SURFACE2)
                        n_lbl.configure(bg=SURFACE2)
                        dt.configure(bg=SURFACE2)
                    else:
                        crd.configure(highlightbackground=SURFACE2)
                        ic.configure(bg=SURFACE1)
                        n_lbl.configure(bg=SURFACE1)
                        dt.configure(bg=SURFACE1)
                    _update_count()

                var.trace_add("write", lambda *_, d=_draw_dot: d())
                _draw_dot()

                # Set initial selected style
                if var.get():
                    card.configure(highlightbackground=TEXT)
                    inner.configure(bg=SURFACE2)
                    name_lbl.configure(bg=SURFACE2)
                    dot.configure(bg=SURFACE2)

                for w in [card, inner, name_lbl, dot]:
                    w.bind("<Button-1>", _toggle_card)
                    w.bind("<MouseWheel>", _on_wheel)

                    def _on_enter(e, c=card, ic=inner, v=var):
                        if not v.get():
                            c.configure(highlightbackground=SURFACE3)
                    def _on_leave(e, c=card, ic=inner, v=var):
                        if not v.get():
                            c.configure(highlightbackground=SURFACE2)
                    card.bind("<Enter>", _on_enter)
                    card.bind("<Leave>", _on_leave)

            canvas.yview_moveto(0)
            canvas.configure(scrollregion=canvas.bbox("all"))
            _bind_wheel(scroll_frame)
            _update_count()

        # Build gen button click handlers
        def _select_gen(g):
            self.current_gen.set(g)
            for code, widget in self._gen_btn_widgets.items():
                if code == g:
                    widget.configure(bg=TEXT, fg=BG)
                else:
                    widget.configure(bg=BG, fg=SUBTEXT)
            _render_grid()

        for _, gen_code in all_gen_options:
            btn = self._gen_btn_widgets[gen_code]
            btn.bind("<Button-1>", lambda _, g=gen_code: _select_gen(g))

        search_var.trace_add("write", lambda *_: _render_grid())
        self._render_roster_grid = _render_grid
        _render_grid()

    def refresh_roster(self) -> None:
        """Re-scan asset folders and rebuild the roster grid."""
        if hasattr(self, "_render_roster_grid"):
            self._render_roster_grid()

    # ─────────────────────────────────────────────────────────────────────────
    # Settings Tab
    # ─────────────────────────────────────────────────────────────────────────

    def _build_settings_tab(self, parent: tk.Frame) -> None:
        canvas = tk.Canvas(parent, bg=BG, bd=0, highlightthickness=0, yscrollincrement=1)
        scrollbar = ttk.Scrollbar(parent, orient="vertical",
                                  command=canvas.yview,
                                  style="Vertical.TScrollbar")

        s_frame = tk.Frame(canvas, bg=BG)
        s_frame.bind("<Configure>",
                     lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        win_id = canvas.create_window((0, 0), window=s_frame, anchor="nw")

        def _on_resize(e):
            canvas.itemconfig(win_id, width=e.width)
        canvas.bind("<Configure>", _on_resize)
        canvas.configure(yscrollcommand=scrollbar.set)

        def _on_wheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)) * 40, "units")

        def _bind_wheel(widget):
            widget.bind("<MouseWheel>", _on_wheel)
            for child in widget.winfo_children():
                _bind_wheel(child)

        canvas.bind("<MouseWheel>", _on_wheel)
        canvas.bind("<Enter>", lambda _: canvas.focus_set())

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def section(title: str) -> tk.Frame:
            tk.Frame(s_frame, bg=BG, height=20).pack(fill="x")
            hdr = tk.Frame(s_frame, bg=BG, padx=24)
            hdr.pack(fill="x")
            tk.Label(hdr, text=title.upper(),
                     font=("Segoe UI", 8, "bold"),
                     bg=BG, fg=SUBTEXT).pack(anchor="w")
            tk.Frame(s_frame, bg=SURFACE2, height=1).pack(fill="x", padx=24, pady=6)
            card = tk.Frame(s_frame, bg=SURFACE1)
            card.pack(fill="x", padx=24, pady=0)
            card.bind("<MouseWheel>", _on_wheel)
            return card

        # ── Startup ───────────────────────────────────────────────────────
        boot_card = section("Startup")

        self.autostart_var = tk.BooleanVar(value=is_autostart_enabled())
        t = _make_toggle(boot_card, "Start with Windows", self.autostart_var)
        t.pack(fill="x", padx=0)

        _divider(boot_card)

        status_frame = tk.Frame(boot_card, bg=SURFACE1, padx=20, pady=10)
        status_frame.pack(fill="x")
        self.boot_status_lbl = tk.Label(
            status_frame,
            text="Enabled — runs silently on boot" if is_autostart_enabled() else "Disabled",
            font=("Segoe UI", 9),
            bg=SURFACE1,
            fg=GREEN if is_autostart_enabled() else SUBTEXT,
        )
        self.boot_status_lbl.pack(anchor="w")

        def _update_boot_status():
            en = self.autostart_var.get()
            self.boot_status_lbl.configure(
                text="Enabled — runs silently on boot" if en else "Disabled",
                fg=GREEN if en else SUBTEXT
            )
        self.autostart_var.trace_add("write", lambda *_: _update_boot_status())

        # ── Appearance ────────────────────────────────────────────────────
        app_card = section("Appearance")

        self.scale_var = tk.DoubleVar(value=self.config.pet_scale)
        _slider_row(app_card, "Pet Size", self.scale_var, 1.0, 4.0, "{:.2f}", "×")
        _divider(app_card)

        self.speed_var = tk.DoubleVar(value=self.config.pet_speed)
        _slider_row(app_card, "Walk Speed", self.speed_var, 0.2, 4.0, "{:.1f}", "×")
        _divider(app_card)

        self.offset_var = tk.DoubleVar(
            value=float(getattr(self.config, "taskbar_offset", 0)))
        _slider_row(app_card, "Taskbar Offset", self.offset_var, -25.0, 25.0, "{:+.0f}", "px")

        # ── Interaction ───────────────────────────────────────────────────
        int_card = section("Interaction")
        self.interactive_var = tk.BooleanVar(value=self.config.interactive_mode)
        t = _make_toggle(int_card, "Interactive Mode  (click / drag / right-click)",
                         self.interactive_var)
        t.pack(fill="x")

        # ── Effects ───────────────────────────────────────────────────────
        fx_card = section("Effects")
        self.speech_var = tk.BooleanVar(value=self.config.speech_enabled)
        t = _make_toggle(fx_card, "Speech Bubbles", self.speech_var)
        t.pack(fill="x")
        _divider(fx_card)

        self.particles_var = tk.BooleanVar(value=self.config.particles_enabled)
        t = _make_toggle(fx_card, "Heart & Sleep Particles", self.particles_var)
        t.pack(fill="x")

        # ── Movement ──────────────────────────────────────────────────────
        mv_card = section("Movement")
        self.freeze_var = tk.BooleanVar(value=self.config.freeze_pets)
        t = _make_toggle(mv_card, "Freeze Pets  (animations still play)", self.freeze_var)
        t.pack(fill="x")

        # ── Tips ──────────────────────────────────────────────────────────
        tip_card = section("Tips")
        tip = tk.Frame(tip_card, bg=SURFACE1, padx=20, pady=14)
        tip.pack(fill="x")
        tk.Label(
            tip,
            text=(
                "Enable Interactive Mode, then drag any Pokémon\n"
                "to place it anywhere on your screen.\n\n"
                "Right-click a pet → Pin Here to lock position.\n"
                "Right-click again → Unpin to resume walking."
            ),
            font=("Segoe UI", 9), bg=SURFACE1, fg=SUBTEXT, justify="left",
        ).pack(anchor="w")
        tk.Frame(s_frame, bg=BG, height=30).pack(fill="x")

        # Bind scroll to all settings widgets so mouse wheel works everywhere
        s_frame.update_idletasks()
        _bind_wheel(s_frame)

    # ─────────────────────────────────────────────────────────────────────────
    # Actions
    # ─────────────────────────────────────────────────────────────────────────

    def _select_all(self) -> None:
        max_allowed = getattr(self.config, "max_active_pets", 5)
        count = 0
        for var in self.selected_pets.values():
            if count < max_allowed:
                var.set(True)
                count += 1
            else:
                var.set(False)
        if hasattr(self, "_update_count"):
            self._update_count()

    def _select_default(self) -> None:
        from config import DEFAULT_ROSTER
        max_allowed = getattr(self.config, "max_active_pets", 5)
        selected = 0
        for p_name, var in self.selected_pets.items():
            if selected < max_allowed and p_name in DEFAULT_ROSTER:
                var.set(True)
                selected += 1
            else:
                var.set(False)
        if hasattr(self, "_update_count"):
            self._update_count()

    def _clear_all(self) -> None:
        for var in self.selected_pets.values():
            var.set(False)
        if hasattr(self, "_update_count"):
            self._update_count()

    def _save_and_apply(self) -> None:
        active = [p for p, var in self.selected_pets.items() if var.get()]
        if not active:
            active = ["pikachu"]

        max_allowed = getattr(self.config, "max_active_pets", 5)
        active = active[:max_allowed]

        self.config.active_pets       = active
        self.config.pet_scale         = round(self.scale_var.get(), 2)
        self.config.pet_speed         = round(self.speed_var.get(), 2)
        self.config.interactive_mode  = self.interactive_var.get()
        self.config.speech_enabled    = self.speech_var.get()
        self.config.particles_enabled = self.particles_var.get()
        self.config.freeze_pets       = self.freeze_var.get()
        self.config.auto_start        = self.autostart_var.get()
        self.config.taskbar_offset    = int(self.offset_var.get())

        set_autostart(self.config.auto_start)
        self.config.save()

        if self.on_save_callback:
            self.on_save_callback(self.config)

        self.root.destroy()
