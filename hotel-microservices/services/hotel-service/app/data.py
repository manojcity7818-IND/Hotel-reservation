from app.models import Hotel

_INITIAL_HOTELS = [
    Hotel(id=1, name="Grand Hyderabad Hotel", city="Hyderabad", rating=4.5),
    Hotel(id=2, name="Bangalore Palace Hotel", city="Bangalore", rating=4.2),
    Hotel(id=3, name="Charminar Heritage Stay", city="Hyderabad", rating=4.3),
    Hotel(id=4, name="MG Road Boutique Hotel", city="Bangalore", rating=4.6),
    Hotel(id=5, name="Whitefield Business Inn", city="Bangalore", rating=4.1),
    Hotel(id=6, name="Marine Drive Suites", city="Mumbai", rating=4.7),
    Hotel(id=7, name="Gateway Mumbai Hotel", city="Mumbai", rating=4.4),
    Hotel(id=8, name="Bandra Sea View Stay", city="Mumbai", rating=4.3),
    Hotel(id=9, name="Connaught Place Inn", city="New Delhi", rating=4.5),
    Hotel(id=10, name="Lotus Temple View Hotel", city="New Delhi", rating=4.1),
    Hotel(id=11, name="Aerocity Transit Hotel", city="New Delhi", rating=4.4),
    Hotel(id=12, name="Marina Beach Residency", city="Chennai", rating=4.3),
    Hotel(id=13, name="Nungambakkam Grand", city="Chennai", rating=4.4),
    Hotel(id=14, name="Calangute Beach Resort", city="Goa", rating=4.6),
    Hotel(id=15, name="Panaji Riverside Hotel", city="Goa", rating=4.2),
    Hotel(id=16, name="Pink City Palace Hotel", city="Jaipur", rating=4.7),
    Hotel(id=17, name="Amber Fort View Stay", city="Jaipur", rating=4.4),
    Hotel(id=18, name="Koregaon Park Stay", city="Pune", rating=4.3),
    Hotel(id=19, name="Park Street Heritage", city="Kolkata", rating=4.4),
    Hotel(id=20, name="Fort Kochi Harbour Inn", city="Kochi", rating=4.5),
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
