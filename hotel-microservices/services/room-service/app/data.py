from app.models import Room


def _room(
    room_id: int,
    hotel_id: int,
    room_number: str,
    room_type: str,
    price_per_night: float,
    available: bool = True,
) -> Room:
    return Room(
        id=room_id,
        hotel_id=hotel_id,
        room_number=room_number,
        room_type=room_type,
        price_per_night=price_per_night,
        available=available,
    )


_INITIAL_ROOMS = [
    _room(101, 1, "101", "Deluxe", 5000),
    _room(102, 1, "102", "Standard", 3500),
    _room(201, 2, "201", "Deluxe", 4500),
    _room(202, 2, "202", "Standard", 3200),
    _room(301, 3, "301", "Heritage Suite", 6200),
    _room(302, 3, "302", "Deluxe", 4100),
    _room(401, 4, "401", "Boutique King", 5800),
    _room(402, 4, "402", "Deluxe", 4300),
    _room(501, 5, "501", "Business King", 3900),
    _room(502, 5, "502", "Twin", 2800),
    _room(601, 6, "601", "Sea View Suite", 8900),
    _room(602, 6, "602", "Deluxe", 6400),
    _room(701, 7, "701", "Executive", 5200),
    _room(702, 7, "702", "Standard", 3600),
    _room(801, 8, "801", "Ocean Deluxe", 7100),
    _room(802, 8, "802", "Standard", 4200),
    _room(901, 9, "901", "Club King", 5600),
    _room(902, 9, "902", "Deluxe", 4000),
    _room(1001, 10, "1001", "Garden View", 3800),
    _room(1002, 10, "1002", "Standard", 2700),
    _room(1101, 11, "1101", "Transit King", 4500),
    _room(1102, 11, "1102", "Twin", 3100),
    _room(1201, 12, "1201", "Beach Deluxe", 4800),
    _room(1202, 12, "1202", "Standard", 3300),
    _room(1301, 13, "1301", "Grand King", 5100),
    _room(1302, 13, "1302", "Deluxe", 3700),
    _room(1401, 14, "1401", "Beach Villa", 9200),
    _room(1402, 14, "1402", "Garden Deluxe", 6100),
    _room(1501, 15, "1501", "River View", 4700),
    _room(1502, 15, "1502", "Standard", 3100),
    _room(1601, 16, "1601", "Palace Suite", 9800),
    _room(1602, 16, "1602", "Heritage Deluxe", 6700),
    _room(1701, 17, "1701", "Fort View", 5400),
    _room(1702, 17, "1702", "Standard", 3400),
    _room(1801, 18, "1801", "Studio Deluxe", 4200),
    _room(1802, 18, "1802", "Standard", 2900),
    _room(1901, 19, "1901", "Heritage King", 4600),
    _room(1902, 19, "1902", "Deluxe", 3300),
    _room(2001, 20, "2001", "Harbour Suite", 6900),
    _room(2002, 20, "2002", "Deluxe", 4400),
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
