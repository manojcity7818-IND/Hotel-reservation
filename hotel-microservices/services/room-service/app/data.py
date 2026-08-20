from app.models import Room

_INITIAL_ROOMS = [
    Room(
        id=101,
        hotel_id=1,
        room_number="101",
        room_type="Deluxe",
        price_per_night=5000,
        available=True,
    ),
    Room(
        id=102,
        hotel_id=1,
        room_number="102",
        room_type="Standard",
        price_per_night=3500,
        available=True,
    ),
    Room(
        id=201,
        hotel_id=2,
        room_number="201",
        room_type="Deluxe",
        price_per_night=4500,
        available=True,
    ),
]

rooms: dict[int, Room] = {}
_next_id = 1


def _sync_next_id() -> None:
    global _next_id
    _next_id = max(rooms.keys(), default=0) + 1


def reset_data() -> None:
    rooms.clear()
    for room in _INITIAL_ROOMS:
        rooms[room.id] = room.model_copy()
    _sync_next_id()


def next_id() -> int:
    global _next_id
    value = _next_id
    _next_id += 1
    return value


reset_data()
