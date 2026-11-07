"""Ayu Mirage Dark palette and widget colors for NNN Countdown.

Core palette is exactly Ayu Mirage; *_HOVER / BTN / BORDER shades are
derived darker/lighter variants used for interactive states.
"""

BG = "#1F2430"          # main background
PANEL = "#232834"       # toolbar / cards / status bar
TEXT = "#CBCCC6"        # primary text
MUTED = "#707A8C"       # secondary text
ACCENT = "#FFCC66"      # yellow accent
ACCENT2 = "#73D0FF"     # blue accent
RED = "#F28779"         # errors / "lost" / inactive state
GREEN = "#BAE67E"       # active state

BTN = "#2C3340"         # neutral button fill
BTN_HOVER = "#3A4150"   # neutral button hover
BORDER = "#3A4150"      # card borders
ACCENT_HOVER = "#E3B45C"
RED_HOVER = "#DB7266"


def apply():
    """Global customtkinter appearance settings."""
    import customtkinter as ctk

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")
