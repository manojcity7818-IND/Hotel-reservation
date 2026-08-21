from app.models import Notification

notifications: dict[int, Notification] = {}
_next_id = 1


def reset_data() -> None:
    global _next_id
    notifications.clear()
    _next_id = 1


def next_id() -> int:
    global _next_id
    value = _next_id
    _next_id += 1
    return value


reset_data()
