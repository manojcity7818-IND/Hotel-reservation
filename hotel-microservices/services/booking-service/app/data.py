from app.models import Booking

bookings: dict[int, Booking] = {}
_next_id = 1


def reset_data() -> None:
    global _next_id
    bookings.clear()
    _next_id = 1


def next_id() -> int:
    global _next_id
    value = _next_id
    _next_id += 1
    return value


reset_data()
