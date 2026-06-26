from datetime import datetime


def form_text(form, key, default=None):
    value = form.get(key)
    if value is None:
        return default
    value = value.strip()
    return value if value else None


def form_bool(form, key):
    return key in form


def form_int(form, key):
    value = form_text(form, key)
    if value is None:
        return None
    return int(value)


def form_date(form, key):
    value = form_text(form, key)
    if not value:
        return None
    return datetime.strptime(value, "%Y-%m-%d").date()


def form_datetime(form, key):
    value = form_text(form, key)
    if not value:
        return None
    return datetime.fromisoformat(value)
