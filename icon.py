"""Programmatically drawn application icon (Pillow, no image files).

The icon is a rounded square in the Ayu Mirage palette with a crossed-out
calendar: a calendar page crossed by a red diagonal stripe.
"""
from PIL import Image, ImageDraw, ImageTk

import theme


def _s(value, scale):
    return int(round(value * scale))


def create_icon_image(size=256):
    """Draw the icon at ``size``x``size`` pixels and return a PIL Image."""
    scale = size / 256.0

    def p(v):
        return _s(v, scale)

    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Rounded-square background with an accent outline.
    draw.rounded_rectangle(
        [p(6), p(6), size - p(6), size - p(6)],
        radius=p(56),
        fill=theme.PANEL,
        outline=theme.ACCENT,
        width=max(1, p(6)),
    )

    x0, y0, x1, y1 = p(60), p(78), p(196), p(198)
    body_w = max(1, p(6))

    # Binding rings first, so the header band overlaps their bottoms.
    ring_w = max(2, p(10))
    for cx in (p(104), p(152)):
        draw.rounded_rectangle(
            [cx - ring_w // 2, p(64), cx + ring_w // 2, p(90)],
            radius=ring_w // 2,
            fill=theme.TEXT,
        )

    # Calendar body.
    draw.rounded_rectangle(
        [x0, y0, x1, y1], radius=p(12), outline=theme.TEXT, width=body_w
    )

    # Header band (blue), squared off at its bottom edge.
    draw.rounded_rectangle([x0, y0, x1, p(108)], radius=p(12), fill=theme.ACCENT2)
    draw.rectangle([x0, p(96), x1, p(108)], fill=theme.ACCENT2)

    # Day grid lines.
    grid_w = max(1, p(4))
    for yy in (p(134), p(160)):
        draw.line([p(78), yy, p(178), yy], fill=theme.MUTED, width=grid_w)
    for xx in (p(112), p(148)):
        draw.line([xx, p(120), xx, p(184)], fill=theme.MUTED, width=grid_w)

    # Red "no" stripe across the whole calendar.
    draw.line(
        [p(50), p(208), p(206), p(64)],
        fill=theme.RED,
        width=max(2, p(14)),
    )
    return img


def set_window_icon(window):
    """Set the window icon via iconphoto. Fail silently on odd platforms."""
    try:
        photo = ImageTk.PhotoImage(create_icon_image(128))
        # True: also apply to future toplevel windows of this app.
        window.iconphoto(True, photo)
        # Keep a reference so Tk does not garbage-collect the image.
        window._nnn_icon_photo = photo
    except Exception:
        pass
