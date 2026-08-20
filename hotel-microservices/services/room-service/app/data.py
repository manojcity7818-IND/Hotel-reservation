from app.models import Room

CITY_HOTEL_COUNTS = {
    "Hyderabad": 25,
    "Bangalore": 25,
    "Mumbai": 25,
    "New Delhi": 25,
    "Chennai": 25,
    "Goa": 25,
    "Jaipur": 25,
    "Pune": 25,
    "Kolkata": 25,
    "Kochi": 25,
    "Mysore": 10,
    "Udaipur": 10,
}

_ROOM_TYPES = [
    ("Deluxe", 1.0),
    ("Standard", 0.72),
    ("Suite", 1.45),
]

_CITY_BASE_PRICE = {
    "Hyderabad": 4200,
    "Bangalore": 4800,
    "Mumbai": 6200,
    "New Delhi": 5400,
    "Chennai": 4000,
    "Goa": 7000,
    "Jaipur": 4500,
    "Pune": 3900,
    "Kolkata": 3700,
    "Kochi": 4300,
    "Mysore": 3600,
    "Udaipur": 5200,
}


def _build_rooms() -> list[Room]:
    rooms: list[Room] = []
    hotel_id = 1
    for city, count in CITY_HOTEL_COUNTS.items():
        base = _CITY_BASE_PRICE[city]
        for _ in range(count):
            for index, (room_type, multiplier) in enumerate(_ROOM_TYPES[:2], start=1):
                room_id = hotel_id * 100 + index
                rooms.append(
                    Room(
                        id=room_id,
                        hotel_id=hotel_id,
                        room_number=str(room_id),
                        room_type=room_type,
                        price_per_night=round(base * multiplier + (hotel_id % 7) * 50),
                        available=True,
                    )
                )
            hotel_id += 1
    return rooms


_INITIAL_ROOMS = _build_rooms()

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
