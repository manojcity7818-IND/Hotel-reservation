from pydantic import BaseModel


class Room(BaseModel):
    id: int
    hotel_id: int
    room_number: str
    room_type: str
    price_per_night: float
    available: bool
