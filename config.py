"""Per-OS config location plus safe load/save/delete for NNN Countdown.

Config file lives in the user's system config directory:
  Linux:   $XDG_CONFIG_HOME/nnn-countdown/config.json
           (or ~/.config/nnn-countdown/config.json)
  macOS:   ~/Library/Application Support/nnn-countdown/config.json
  Windows: %APPDATA%\\nnn-countdown\\config.json

The path resolution is done manually (no platformdirs dependency).
"""
import json
import os
import re
import sys

APP_DIR_NAME = "nnn-countdown"
CONFIG_FILENAME = "config.json"
DEFAULT_GEOMETRY = "1000x640"

DEFAULTS = {
    "language": "en",          # "en" | "ru"
    "mode": "start",           # "start" | "end"
    "geometry": DEFAULT_GEOMETRY,
    "always_on_top": False,
    "losses": 0,
}

# e.g. "900x600", "1024x768+100+50"
_GEOMETRY_RE = re.compile(r"^\d{2,5}x\d{2,5}([+-]\d{1,5}){0,2}$")


def config_dir():
    """Directory that holds config.json on the current OS."""
    if sys.platform.startswith("win"):
        base = os.environ.get("APPDATA") or os.path.join(
            os.path.expanduser("~"), "AppData", "Roaming"
        )
    elif sys.platform == "darwin":
        base = os.path.join(
            os.path.expanduser("~"), "Library", "Application Support"
        )
    else:  # linux and other unixes
        base = os.environ.get("XDG_CONFIG_HOME") or os.path.join(
            os.path.expanduser("~"), ".config"
        )
    return os.path.join(base, APP_DIR_NAME)


def config_path():
    return os.path.join(config_dir(), CONFIG_FILENAME)


def load_config():
    """Return ``(config_dict, error)``.

    Never raises. Missing file -> defaults are written. Corrupted file or
    invalid values -> safe defaults, and ``error`` describes the problem
    so the UI can show a friendly message.
    """
    path = config_path()
    try:
        with open(path, "r", encoding="utf-8") as fh:
            raw = json.load(fh)
        if not isinstance(raw, dict):
            raise ValueError("top-level value is not an object")
        cfg = dict(DEFAULTS)
        cfg.update(_sanitize(raw))
        return cfg, None
    except FileNotFoundError:
        cfg = dict(DEFAULTS)
        try:
            save_config(cfg)
        except OSError:
            pass  # read-only config dir is unfortunate but not fatal
        return cfg, None
    except (OSError, ValueError) as exc:  # ValueError covers JSONDecodeError
        cfg = dict(DEFAULTS)
        try:
            save_config(cfg)  # rewrite with safe defaults
        except OSError:
            pass
        return cfg, str(exc)


def _sanitize(raw):
    """Keep only known keys with valid value types; drop the rest."""
    clean = {}
    if raw.get("language") in ("en", "ru"):
        clean["language"] = raw["language"]
    if raw.get("mode") in ("start", "end"):
        clean["mode"] = raw["mode"]
    geometry = raw.get("geometry")
    if isinstance(geometry, str) and _GEOMETRY_RE.match(geometry):
        clean["geometry"] = geometry
    if isinstance(raw.get("always_on_top"), bool):
        clean["always_on_top"] = raw["always_on_top"]
    losses = raw.get("losses")
    # bool is a subclass of int in Python — exclude it explicitly.
    if isinstance(losses, int) and not isinstance(losses, bool) and losses >= 0:
        clean["losses"] = losses
    return clean


def save_config(cfg):
    """Write config atomically (temp file + rename). Creates the dir."""
    data = dict(DEFAULTS)
    data.update({k: v for k, v in cfg.items() if k in DEFAULTS})
    os.makedirs(config_dir(), exist_ok=True)
    tmp_path = config_path() + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    os.replace(tmp_path, config_path())


def delete_config():
    """Delete config.json. Returns True if the file is gone afterwards."""
    try:
        os.remove(config_path())
        return True
    except FileNotFoundError:
        return True
    except OSError:
        return False
