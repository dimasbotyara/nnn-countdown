# NNN Countdown

**[🇷🇺 Русская версия: README.ru.md](README.ru.md)**

A small desktop joke app built with **Python + customtkinter**: it shows a
live countdown — based on your local system clock — to the beginning
(November 1, 00:00) or to the end (December 1, 00:00) of **No Nut November**.
Bilingual UI (English / Russian), dark Ayu Mirage theme, settings persisted
in a `config.json` inside your OS user-config directory.

## Features

- Two countdown modes: **until start** (nearest future Nov 1) and
  **until end** (nearest future Dec 1), with automatic next-year rollover.
- Calendar-accurate month counting (not naive 30-day months).
- Five always-visible cards: months, days, hours, minutes, seconds,
  refreshed every second from `datetime.now()`.
- Status bar with local time, timezone name and a "challenge active"
  indicator (November 1–30).
- Language switch (EN/RU), "always on top", "copy countdown text" button,
  keyboard shortcuts.
- Joke **"I lost 😭"** button with a persistent losses counter.
- Debug-proof config: corrupted files are reset to safe defaults instead of
  crashing.

## Installation

You need Python 3.9+ with **tkinter** (on Debian/Ubuntu:
`sudo apt install python3-tk`; on macOS/Windows it ships with python.org
installers).

```bash
python -m pip install -r requirements.txt
```

Dependencies: `customtkinter` and `Pillow` only.

## Run

```bash
python main.py
```

## Tests

```bash
python -m unittest discover -s tests -v
```

## Modes, languages, settings

- **Mode** — toggled in the toolbar (*Until start / Until end*). The target
  is the nearest future Nov 1 00:00 or Dec 1 00:00 **local time**; if this
  year's target has already passed, the app counts to next year's.
- **Language** — EN/RU toggle in the toolbar; every string (including window
  title, dialogs and plurals) switches immediately.
- **Settings window** (Ctrl+,) — "Always on top" switch and the exact path
  of the config file.
- **Delete config** — removes `config.json` after a confirmation and resets
  the running app to defaults, no restart required. The file is recreated
  the next time something gets saved (e.g. on exit, which stores the window
  geometry).
- **Copy** (Ctrl+C) — copies a textual summary like
  `3 months, 12 days, 05:04:03 until No Nut November` to the clipboard.

Keyboard shortcuts: `Ctrl+Q` quit, `Ctrl+,` settings, `Ctrl+C` copy,
`F1` about.

## Where config.json lives

| OS      | Path                                                        |
|---------|-------------------------------------------------------------|
| Linux   | `$XDG_CONFIG_HOME/nnn-countdown/config.json` or `~/.config/nnn-countdown/config.json` |
| macOS   | `~/Library/Application Support/nnn-countdown/config.json`   |
| Windows | `%APPDATA%\nnn-countdown\config.json`                       |

Stored values: `language`, `mode`, `geometry`, `always_on_top`, `losses`.
The path resolution is done manually in `config.py` (no `platformdirs`
dependency). If the file is missing it is created with defaults; if it is
corrupted you'll see a friendly warning and safe defaults are used.

## How the time is computed

Everything is based on **local system time** (`datetime.now()`, naive local
datetimes) — no UTC conversion, no hard-coded timezone, so DST changes are
handled by the OS itself.

The remainder is computed in two steps (see `time_logic.py`):

1. Count how many **full calendar months** fit between now and the target
   (`add_months` clamps the day, e.g. Jan 31 + 1 month → Feb 28/29).
2. The leftover is a plain `timedelta` split into days / hours / minutes /
   seconds.

Example: Aug 20 10:00 → Nov 1 00:00 = **2 months** (to Oct 20 10:00),
**11 days**, **14 hours**.

## The "I lost 😭" button

Pure joke, deliberately wired exactly as specified: pressing it opens a
modal window saying **`unlucky 😭😢`** / **`анлак 😭😢`** (lowercase, no
period). Its single button — **Continue / Продолжить** — closes the whole
app. Just before closing, the `losses` counter in the config is incremented;
the counter is shown in the *About* window. Closing the dialog via its
window X counts the same as pressing Continue. There is no other logic
behind the button.

The *About* window (F1) also contains the losses counter, a README link and
a **"Close app and delete config"** button.

## Project layout

```
nnn-countdown/
├── main.py         # application & UI
├── time_logic.py   # target/remaining math, calendar months, timezone name
├── config.py       # per-OS config path, safe load/save/delete
├── i18n.py         # EN/RU strings + pluralization
├── theme.py        # Ayu Mirage Dark palette
├── icon.py         # Pillow-drawn window icon (crossed-out calendar)
├── tests/          # unittest suite for time logic and config
├── requirements.txt
├── README.md / README.ru.md
└── .gitignore
```

## Decisions on ambiguous points

- At exactly **Nov 1 00:00:00** the start countdown targets *next* year's
  Nov 1 (the current one has "happened"); same rule for Dec 1.
- Language switching while a secondary window is open re-renders it in
  place (no restart).
- The hover/border colors (`#2C3340`, `#3A4150`, …) are derived shades of
  the given Ayu palette, used only for interactive states.
- Date formats follow the UI language (`%Y-%m-%d` for EN, `%d.%m.%Y` for RU).

## Limitations

- The window icon is applied via `iconphoto`; on some platforms/WMs (or when
  Pillow is missing at runtime) the icon may simply not appear — the app
  keeps working.
- The timezone label is best-effort: an IANA name (e.g. `Europe/Moscow`) is
  shown on most Linux systems; elsewhere you may see an abbreviation such as
  `MSK` or `UTC+3`.
- After "Delete config" the file may reappear on exit (window geometry is
  saved). Use the About-window button if you want it gone permanently.
