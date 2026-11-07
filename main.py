"""NNN Countdown — desktop app entry point.

A customtkinter app that counts down (by the local system clock) to the
beginning (Nov 1, 00:00) or the end (Dec 1, 00:00) of No Nut November.
"""
import tkinter.messagebox as messagebox
import webbrowser
from datetime import datetime
from pathlib import Path

import customtkinter as ctk

import config as app_config
import i18n
import icon as app_icon
import theme
import time_logic

UNITS = ("months", "days", "hours", "minutes", "seconds")
MODE_ORDER = ("start", "end")
APP_DIR = Path(__file__).resolve().parent


class NNNCountdownApp(ctk.CTk):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.cfg, self._config_error = app_config.load_config()
        self.lang = self.cfg["language"]
        self.mode = self.cfg["mode"]

        self.configure(fg_color=theme.BG)
        self.geometry(self.cfg["geometry"] or app_config.DEFAULT_GEOMETRY)
        self.minsize(940, 560)
        self.title(self._t("window_title"))
        self.attributes("-topmost", self.cfg["always_on_top"])
        app_icon.set_window_icon(self)

        self.tz_name = time_logic.timezone_name()
        self._last_remaining = None
        self._target = None
        self._last_clock_text = ""
        self._refresh_callbacks = []   # child windows re-translate through these
        self._settings_win = None
        self._about_win = None
        self._loss_win = None
        self._mode_values = []

        self._build_toolbar()
        self._build_statusbar()
        self._build_target_row()
        self._build_cards()
        self._apply_language()
        self._bind_shortcuts()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        if self._config_error:
            # Defer so the main window exists before the dialog appears.
            self.after(400, self._show_config_error)
        self._tick()

    # ------------------------------------------------------------------ i18n

    def _t(self, key, **kwargs):
        return i18n.tr(self.lang, key, **kwargs)

    def _register_refresh(self, callback):
        self._refresh_callbacks.append(callback)

    # ------------------------------------------------------------- UI build

    def _toolbar_button(self, parent, command, width=100):
        btn = ctk.CTkButton(
            parent,
            width=width,
            height=30,
            font=ctk.CTkFont(size=13),
            fg_color=theme.BTN,
            hover_color=theme.BTN_HOVER,
            text_color=theme.TEXT,
            command=command,
        )
        btn.pack(side="left", padx=(0, 6))
        return btn

    def _build_toolbar(self):
        bar = ctk.CTkFrame(self, fg_color=theme.PANEL, corner_radius=0, height=46)
        bar.pack(fill="x", side="top")
        bar.pack_propagate(False)
        inner = ctk.CTkFrame(bar, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=8, pady=8)

        self.btn_about = self._toolbar_button(inner, self.open_about, width=90)
        self.btn_settings = self._toolbar_button(inner, self.open_settings, width=100)
        self.btn_delete = self._toolbar_button(inner, self.delete_config, width=120)
        self.btn_copy = self._toolbar_button(inner, self.copy_countdown, width=110)

        self.btn_lost = ctk.CTkButton(
            inner,
            width=130,
            height=30,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=theme.RED,
            hover_color=theme.RED_HOVER,
            text_color=theme.BG,
            command=self.open_loss,
        )
        self.btn_lost.pack(side="left", padx=(4, 0))

        self.lang_seg = ctk.CTkSegmentedButton(
            inner, values=["EN", "RU"], height=30, command=self._on_lang_seg
        )
        self.lang_seg.pack(side="right", padx=(6, 0))
        self.lang_seg.set("RU" if self.lang == "ru" else "EN")

        # Values must be unique, so initialize with real localized labels.
        self.mode_seg = ctk.CTkSegmentedButton(
            inner,
            values=[self._t("mode_start"), self._t("mode_end")],
            height=30,
            command=self._on_mode_seg,
        )
        self.mode_seg.pack(side="right", padx=(6, 0))

    def _build_cards(self):
        wrap = ctk.CTkFrame(self, fg_color="transparent")
        wrap.pack(fill="both", expand=True, padx=16, pady=(16, 8))
        wrap.grid_rowconfigure(0, weight=1)

        self.value_labels = {}
        self.caption_labels = {}
        value_colors = {
            "months": theme.ACCENT,
            "days": theme.ACCENT2,
            "hours": theme.TEXT,
            "minutes": theme.TEXT,
            "seconds": theme.TEXT,
        }
        for col, unit in enumerate(UNITS):
            wrap.grid_columnconfigure(col, weight=1, uniform="cards")
            card = ctk.CTkFrame(
                wrap,
                fg_color=theme.PANEL,
                corner_radius=12,
                border_width=1,
                border_color=theme.BORDER,
            )
            card.grid(row=0, column=col, sticky="nsew", padx=6)
            # Inner frame keeps the value+caption pair vertically centered.
            center = ctk.CTkFrame(card, fg_color="transparent")
            center.pack(expand=True)
            value = ctk.CTkLabel(
                center, text="0",
                font=ctk.CTkFont(size=48, weight="bold"),
                text_color=value_colors[unit],
            )
            value.pack()
            caption = ctk.CTkLabel(
                center, text=unit,
                font=ctk.CTkFont(size=14),
                text_color=theme.MUTED,
            )
            caption.pack()
            self.value_labels[unit] = value
            self.caption_labels[unit] = caption

    def _build_target_row(self):
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", side="bottom", padx=22, pady=(0, 4))
        self.target_label = ctk.CTkLabel(
            row, text="", font=ctk.CTkFont(size=14), text_color=theme.MUTED
        )
        self.target_label.pack(side="left")

    def _build_statusbar(self):
        bar = ctk.CTkFrame(self, fg_color=theme.PANEL, corner_radius=0, height=32)
        bar.pack(fill="x", side="bottom")
        bar.pack_propagate(False)

        self.lbl_time = ctk.CTkLabel(
            bar, text="", font=ctk.CTkFont(size=12), text_color=theme.MUTED
        )
        self.lbl_time.pack(side="left", padx=(12, 0))

        self.lbl_tz = ctk.CTkLabel(
            bar, text="", font=ctk.CTkFont(size=12), text_color=theme.MUTED
        )
        self.lbl_tz.pack(side="left", padx=(16, 0))

        self.lbl_state = ctk.CTkLabel(
            bar, text="", font=ctk.CTkFont(size=12, weight="bold"),
            text_color=theme.GREEN,
        )
        self.lbl_state.pack(side="right", padx=(0, 12))

    def _bind_shortcuts(self):
        self.bind("<Control-q>", lambda _e: self._on_close())
        self.bind("<Control-comma>", lambda _e: self.open_settings())
        self.bind("<Control-c>", lambda _e: self.copy_countdown())
        self.bind("<F1>", lambda _e: self.open_about())

    # ------------------------------------------------------------- re-render

    def _refresh_mode_seg(self):
        self._mode_values = [self._t("mode_start"), self._t("mode_end")]
        self.mode_seg.configure(values=self._mode_values)
        self.mode_seg.set(self._mode_values[MODE_ORDER.index(self.mode)])

    def _apply_language(self):
        """Push the current language into every visible widget."""
        self.title(self._t("window_title"))
        self.btn_about.configure(text=self._t("about"))
        self.btn_settings.configure(text=self._t("settings"))
        self.btn_delete.configure(text=self._t("delete_config"))
        self.btn_copy.configure(text=self._t("copy"))
        self.btn_lost.configure(text=self._t("i_lost"))
        self._refresh_mode_seg()
        for unit in UNITS:
            self.caption_labels[unit].configure(text=self._t(unit))
        # Re-render dynamic text with the new language.
        if self._target is not None and self._last_remaining is not None:
            self._render(self._last_remaining, self._target)
        self._render_clock(datetime.now(), force=True)
        for cb in list(self._refresh_callbacks):
            try:
                cb()
            except Exception:
                pass

    def _render(self, rem, target):
        months, days, hours, minutes, seconds = rem
        self.value_labels["months"].configure(text=str(months))
        self.value_labels["days"].configure(text=str(days))
        self.value_labels["hours"].configure(text=f"{hours:02d}")
        self.value_labels["minutes"].configure(text=f"{minutes:02d}")
        self.value_labels["seconds"].configure(text=f"{seconds:02d}")
        date_text = target.strftime(self._t("date_format"))
        self.target_label.configure(text=self._t("target_label", date=date_text))

    def _render_clock(self, now, force=False):
        clock_text = now.strftime("%Y-%m-%d %H:%M:%S")
        if force or clock_text != self._last_clock_text:
            self._last_clock_text = clock_text
            self.lbl_time.configure(text=f"{self._t('local_time')}: {clock_text}")
            self.lbl_tz.configure(text=f"{self._t('timezone')}: {self.tz_name}")
            if time_logic.is_challenge_active(now):
                self.lbl_state.configure(
                    text=self._t("challenge_active"), text_color=theme.GREEN
                )
            else:
                self.lbl_state.configure(
                    text=self._t("challenge_inactive"), text_color=theme.RED
                )

    # --------------------------------------------------------------- ticking

    def _tick(self):
        now = datetime.now()
        target = time_logic.next_target(now, self.mode)
        if target <= now:
            # Paranoia guard: next_target already rolls over to next year,
            # so this branch only runs on pathological clock jumps.
            target = time_logic.next_target(now.replace(year=now.year + 1), self.mode)
        rem = time_logic.remaining(now, target)
        if rem != self._last_remaining or target != self._target:
            self._last_remaining = rem
            self._target = target
            self._render(rem, target)
        self._render_clock(now)
        # Wake up as close as possible to the next wall-clock second.
        delay = max(50, 1000 - now.microsecond // 1000)
        self.after(delay, self._tick)

    # -------------------------------------------------------------- actions

    def _on_lang_seg(self, value):
        self.set_language("ru" if value == "RU" else "en")

    def _on_mode_seg(self, value):
        try:
            self.mode = MODE_ORDER[self._mode_values.index(value)]
        except (ValueError, IndexError):
            return
        self.cfg["mode"] = self.mode
        self._save_cfg_safely()
        self._render_now()

    def _render_now(self):
        now = datetime.now()
        self._target = time_logic.next_target(now, self.mode)
        self._last_remaining = time_logic.remaining(now, self._target)
        self._render(self._last_remaining, self._target)

    def set_language(self, lang):
        if lang not in ("en", "ru") or lang == self.lang:
            return
        self.lang = lang
        self.cfg["language"] = lang
        self.lang_seg.set("RU" if lang == "ru" else "EN")
        self._save_cfg_safely()
        self._apply_language()

    def _save_cfg_safely(self):
        try:
            app_config.save_config(self.cfg)
        except OSError:
            pass  # failing to persist must never crash the UI

    def _summary_text(self):
        now = datetime.now()
        target = time_logic.next_target(now, self.mode)
        months, days, hours, minutes, seconds = time_logic.remaining(now, target)
        months_text = f"{months} {i18n.unit_word(self.lang, 'month', months)}"
        days_text = f"{days} {i18n.unit_word(self.lang, 'day', days)}"
        time_text = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        suffix = self._t("until_end" if self.mode == "end" else "until_start")
        return f"{months_text}, {days_text}, {time_text} {suffix}"

    def copy_countdown(self, *_):
        try:
            self.clipboard_clear()
            self.clipboard_append(self._summary_text())
        except Exception:
            messagebox.showwarning(
                self._t("clipboard_error_title"), self._t("clipboard_error_text")
            )
            return
        # Brief "Copied!" feedback on the button itself.
        self.btn_copy.configure(text=self._t("copied"))
        self.after(1200, lambda: self.btn_copy.configure(text=self._t("copy")))

    def delete_config(self, *_):
        """Toolbar action: delete config.json and reset in-memory settings."""
        if not messagebox.askyesno(
            self._t("confirm_delete_title"), self._t("confirm_delete_text")
        ):
            return
        app_config.delete_config()
        self.cfg = dict(app_config.DEFAULTS)
        self.lang = self.cfg["language"]
        self.mode = self.cfg["mode"]
        self.lang_seg.set("RU" if self.lang == "ru" else "EN")
        self.attributes("-topmost", False)
        if self._settings_win is not None and self._settings_win.winfo_exists():
            self._settings_win.destroy()
        if self._about_win is not None and self._about_win.winfo_exists():
            self._about_win.destroy()
        self._apply_language()
        self._render_now()
        # The file stays deleted until the next save (setting change / exit).

    # ----------------------------------------------------- secondary windows

    def open_settings(self, *_):
        if self._settings_win is not None and self._settings_win.winfo_exists():
            self._settings_win.focus()
            return
        win = ctk.CTkToplevel(self)
        self._settings_win = win
        win.configure(fg_color=theme.BG)
        win.geometry("460x300")
        win.resizable(False, False)
        win.transient(self)
        app_icon.set_window_icon(win)

        heading = ctk.CTkLabel(
            win, font=ctk.CTkFont(size=18, weight="bold"), text_color=theme.ACCENT
        )
        heading.pack(padx=20, pady=(18, 10), anchor="w")

        top_var = ctk.BooleanVar(value=self.cfg["always_on_top"])
        top_switch = ctk.CTkSwitch(
            win,
            variable=top_var,
            command=lambda: self._toggle_always_on_top(top_var.get()),
            progress_color=theme.ACCENT,
            text_color=theme.TEXT,
            font=ctk.CTkFont(size=14),
        )
        top_switch.pack(padx=20, pady=6, anchor="w")

        path_caption = ctk.CTkLabel(
            win, font=ctk.CTkFont(size=13), text_color=theme.MUTED
        )
        path_caption.pack(padx=20, pady=(16, 0), anchor="w")
        path_value = ctk.CTkLabel(
            win,
            text=app_config.config_path(),
            font=ctk.CTkFont(size=12),
            text_color=theme.TEXT,
            wraplength=420,
            justify="left",
        )
        path_value.pack(padx=20, anchor="w")

        close_btn = ctk.CTkButton(
            win,
            width=120,
            fg_color=theme.BTN,
            hover_color=theme.BTN_HOVER,
            text_color=theme.TEXT,
            command=win.destroy,
        )
        close_btn.pack(pady=24)

        def refresh():
            if not win.winfo_exists():
                return
            win.title(self._t("settings_title"))
            heading.configure(text=self._t("settings_title"))
            top_switch.configure(text=self._t("always_on_top"))
            path_caption.configure(text=self._t("config_path_label"))
            close_btn.configure(text=self._t("close"))

        refresh()
        self._register_refresh(refresh)

    def _toggle_always_on_top(self, enabled):
        self.cfg["always_on_top"] = bool(enabled)
        self.attributes("-topmost", bool(enabled))
        self._save_cfg_safely()

    def open_about(self, *_):
        if self._about_win is not None and self._about_win.winfo_exists():
            self._about_win.focus()
            return
        win = ctk.CTkToplevel(self)
        self._about_win = win
        win.configure(fg_color=theme.BG)
        win.geometry("520x520")
        win.minsize(480, 480)
        win.transient(self)
        app_icon.set_window_icon(win)

        heading = ctk.CTkLabel(
            win, font=ctk.CTkFont(size=20, weight="bold"), text_color=theme.ACCENT
        )
        heading.pack(padx=20, pady=(18, 8), anchor="w")

        textbox = ctk.CTkTextbox(
            win,
            height=200,
            fg_color=theme.PANEL,
            text_color=theme.TEXT,
            font=ctk.CTkFont(size=14),
            wrap="word",
        )
        textbox.pack(fill="x", padx=20)
        textbox.insert("1.0", self._t("about_text"))
        textbox.configure(state="disabled")

        link = ctk.CTkLabel(
            win,
            font=ctk.CTkFont(size=13, underline=True),
            text_color=theme.ACCENT2,
            cursor="hand2",
        )
        link.pack(padx=20, pady=(8, 0), anchor="w")
        link.bind("<Button-1>", lambda _e: self._open_readme())

        losses_label = ctk.CTkLabel(
            win, font=ctk.CTkFont(size=14), text_color=theme.MUTED
        )
        losses_label.pack(padx=20, pady=(18, 0), anchor="w")

        danger_btn = ctk.CTkButton(
            win,
            height=32,
            fg_color=theme.RED,
            hover_color=theme.RED_HOVER,
            text_color=theme.BG,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._close_app_delete_config,
        )
        danger_btn.pack(padx=20, pady=(16, 8), anchor="w")

        close_btn = ctk.CTkButton(
            win,
            width=120,
            fg_color=theme.BTN,
            hover_color=theme.BTN_HOVER,
            text_color=theme.TEXT,
            command=win.destroy,
        )
        close_btn.pack(pady=(4, 16))

        def refresh():
            if not win.winfo_exists():
                return
            win.title(self._t("about_title"))
            heading.configure(text=self._t("about_heading"))
            textbox.configure(state="normal")
            textbox.delete("1.0", "end")
            textbox.insert("1.0", self._t("about_text"))
            textbox.configure(state="disabled")
            link.configure(text=self._t("readme_link") + " ↗")
            losses_label.configure(
                text=self._t("losses_label", n=self.cfg.get("losses", 0))
            )
            danger_btn.configure(text=self._t("close_app_delete_config"))
            close_btn.configure(text=self._t("close"))

        refresh()
        self._register_refresh(refresh)

    def _open_readme(self):
        name = "README.ru.md" if self.lang == "ru" else "README.md"
        path = APP_DIR / name
        try:
            webbrowser.open(path.as_uri())
        except Exception:
            pass

    def _close_app_delete_config(self):
        """About-window action: delete config and exit (with confirmation)."""
        if not messagebox.askyesno(
            self._t("confirm_delete_title"), self._t("confirm_delete_text")
        ):
            return
        app_config.delete_config()
        self.destroy()

    # -------------------------------------------------------- the joke button

    def open_loss(self, *_):
        if self._loss_win is not None and self._loss_win.winfo_exists():
            self._loss_win.focus()
            return
        win = ctk.CTkToplevel(self)
        self._loss_win = win
        win.configure(fg_color=theme.BG)
        win.geometry("380x220")
        win.resizable(False, False)
        win.transient(self)
        win.grab_set()  # modal
        app_icon.set_window_icon(win)

        ctk.CTkLabel(win, text="\U0001F62D", font=ctk.CTkFont(size=52)).pack(
            pady=(24, 4)
        )
        ctk.CTkLabel(
            win,
            text=self._t("lost_message"),
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=theme.TEXT,
        ).pack()
        ctk.CTkButton(
            win,
            width=140,
            fg_color=theme.ACCENT,
            hover_color=theme.ACCENT_HOVER,
            text_color=theme.BG,
            font=ctk.CTkFont(size=14, weight="bold"),
            text=self._t("continue_button"),
            command=self._finish_loss,
        ).pack(pady=20)

        win.title(self._t("lost_title"))
        # Closing the joke dialog via X counts the same as "Continue".
        win.protocol("WM_DELETE_WINDOW", self._finish_loss)

    def _finish_loss(self):
        self.cfg["losses"] = int(self.cfg.get("losses", 0)) + 1
        self._on_close()

    # -------------------------------------------------------------- shutdown

    def _show_config_error(self):
        messagebox.showwarning(
            self._t("config_error_title"),
            self._t("config_error_text", error=self._config_error),
        )

    def _on_close(self):
        try:
            self.cfg["geometry"] = self.geometry()
            self.cfg["language"] = self.lang
            self.cfg["mode"] = self.mode
            app_config.save_config(self.cfg)
        except Exception:
            pass
        self.destroy()


def main():
    theme.apply()
    app = NNNCountdownApp()
    app.mainloop()


if __name__ == "__main__":
    main()
