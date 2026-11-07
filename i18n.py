"""UI translations (English / Russian) for NNN Countdown."""

STRINGS = {
    "en": {
        "window_title": "NNN Countdown",
        # toolbar
        "about": "About",
        "settings": "Settings",
        "delete_config": "Delete config",
        "i_lost": "I lost \U0001F62D",
        "copy": "Copy",
        "copied": "Copied!",
        "mode_start": "Until start",
        "mode_end": "Until end",
        # countdown cards
        "months": "months",
        "days": "days",
        "hours": "hours",
        "minutes": "minutes",
        "seconds": "seconds",
        "target_label": "Target: {date}",
        "date_format": "%Y-%m-%d %H:%M",
        # status bar
        "local_time": "Local time",
        "timezone": "Timezone",
        "challenge_active": "\u25CF challenge is active",
        "challenge_inactive": "\u25CB challenge is not active",
        # settings window
        "settings_title": "Settings",
        "always_on_top": "Always on top",
        "config_path_label": "Config file:",
        "close": "Close",
        # about window
        "about_title": "About the event",
        "about_heading": "No Nut November (NNN)",
        "about_text": (
            "No Nut November (NNN) is an annual internet challenge: "
            "participants try to make it through the whole month of "
            "November without slipping.\n\n"
            "This app is a joke countdown: it shows the time until the "
            "next beginning (November 1, 00:00) or until the end of the "
            "challenge (December 1, 00:00) using your local system clock. "
            "Months are counted calendar-wise, and your settings are stored "
            "in a config.json inside your OS user-config directory."
        ),
        "readme_link": "Open README",
        "losses_label": "Losses: {n}",
        "close_app_delete_config": "Close app and delete config",
        # dialogs
        "confirm_delete_title": "Delete config?",
        "confirm_delete_text": (
            "The configuration file will be deleted and all settings "
            "will be reset to defaults (no restart needed)."
        ),
        "clipboard_error_title": "Clipboard unavailable",
        "clipboard_error_text": "Could not copy the text to the clipboard.",
        "config_error_title": "Config reset",
        "config_error_text": (
            "The configuration file was corrupted, so the default values "
            "were restored.\n\nDetails: {error}"
        ),
        # loss joke dialog
        "lost_title": "I lost \U0001F62D",
        "lost_message": "unlucky \U0001F62D\U0001F622",
        "continue_button": "Continue",
        # copy summary suffixes
        "until_start": "until No Nut November",
        "until_end": "until the end of No Nut November",
    },
    "ru": {
        "window_title": "Обратный отсчёт Недрочабря",
        # toolbar
        "about": "О событии",
        "settings": "Настройки",
        "delete_config": "Удалить конфиг",
        "i_lost": "Я проиграл \U0001F62D",
        "copy": "Скопировать",
        "copied": "Скопировано!",
        "mode_start": "До начала",
        "mode_end": "До конца",
        # countdown cards
        "months": "месяцы",
        "days": "дни",
        "hours": "часы",
        "minutes": "минуты",
        "seconds": "секунды",
        "target_label": "Цель: {date}",
        "date_format": "%d.%m.%Y %H:%M",
        # status bar
        "local_time": "Локальное время",
        "timezone": "Часовой пояс",
        "challenge_active": "\u25CF челлендж активен",
        "challenge_inactive": "\u25CB челлендж не активен",
        # settings window
        "settings_title": "Настройки",
        "always_on_top": "Поверх всех окон",
        "config_path_label": "Файл конфигурации:",
        "close": "Закрыть",
        # about window
        "about_title": "О событии",
        "about_heading": "Недрочабрь (No Nut November)",
        "about_text": (
            "«Недрочабрь» (No Nut November, NNN) — ежегодный "
            "интернет-челлендж: участники стараются продержаться весь "
            "ноябрь.\n\n"
            "Это приложение — шуточный обратный отсчёт: оно показывает, "
            "сколько осталось до ближайшего начала (1 ноября, 00:00) или "
            "до конца челленджа (1 декабря, 00:00) по локальному системному "
            "времени. Месяцы считаются календарно, а настройки хранятся "
            "в config.json в системной директории пользователя."
        ),
        "readme_link": "Открыть README",
        "losses_label": "Проигрышей: {n}",
        "close_app_delete_config": "Закрыть приложение и удалить конфиг",
        # dialogs
        "confirm_delete_title": "Удалить конфиг?",
        "confirm_delete_text": (
            "Файл конфигурации будет удалён, а все настройки сброшены "
            "к значениям по умолчанию (перезапуск не нужен)."
        ),
        "clipboard_error_title": "Буфер обмена недоступен",
        "clipboard_error_text": "Не удалось скопировать текст в буфер обмена.",
        "config_error_title": "Конфиг сброшен",
        "config_error_text": (
            "Файл конфигурации был повреждён, поэтому восстановлены "
            "значения по умолчанию.\n\nПодробности: {error}"
        ),
        # loss joke dialog
        "lost_title": "Я проиграл \U0001F62D",
        "lost_message": "анлак \U0001F62D\U0001F622",
        "continue_button": "Продолжить",
        # copy summary suffixes
        "until_start": "до Недрочабря",
        "until_end": "до конца Недрочабря",
    },
}

DEFAULT_LANGUAGE = "en"

# Plural forms: English has two, Russian has three (1 / 2-4 / 0,5-20...).
_PLURALS = {
    "en": {
        "month": ("month", "months"),
        "day": ("day", "days"),
    },
    "ru": {
        "month": ("месяц", "месяца", "месяцев"),
        "day": ("день", "дня", "дней"),
    },
}


def tr(lang, key, **kwargs):
    """Translate ``key`` for ``lang`` with optional {placeholders}.

    Falls back to English, then to the raw key — never raises KeyError.
    """
    table = STRINGS.get(lang, STRINGS[DEFAULT_LANGUAGE])
    text = table.get(key, STRINGS[DEFAULT_LANGUAGE].get(key, key))
    return text.format(**kwargs) if kwargs else text


def unit_word(lang, unit, n):
    """Correctly pluralized unit word for a number (month/day)."""
    forms = _PLURALS.get(lang, _PLURALS[DEFAULT_LANGUAGE])[unit]
    if lang == "ru":
        n_abs = abs(n) % 100
        n1 = n_abs % 10
        if 10 < n_abs < 20:
            return forms[2]
        if 1 < n1 < 5:
            return forms[1]
        if n1 == 1:
            return forms[0]
        return forms[2]
    return forms[0] if n == 1 else forms[1]
