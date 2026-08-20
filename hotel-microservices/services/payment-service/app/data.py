from app.models import Payment

payments: dict[int, Payment] = {}
_next_id = 1


def reset_data() -> None:
    global _next_id
    payments.clear()
    _next_id = 1


def next_id() -> int:
    global _next_id
    value = _next_id
    _next_id += 1
    return value


reset_data()
