from app.models import Hotel

_INITIAL_HOTELS = [
    Hotel(id=1, name="Grand Hyderabad Hotel", city="Hyderabad", rating=4.5),
    Hotel(id=2, name="Bangalore Palace Hotel", city="Bangalore", rating=4.2),
]

hotels: dict[int, Hotel] = {}
_next_id = 1


def _sync_next_id() -> None:
    global _next_id
    _next_id = max(hotels.keys(), default=0) + 1


def reset_data() -> None:
    hotels.clear()
    for hotel in _INITIAL_HOTELS:
        hotels[hotel.id] = hotel.model_copy()
    _sync_next_id()


def next_id() -> int:
    global _next_id
    value = _next_id
    _next_id += 1
    return value


reset_data()
