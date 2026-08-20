from pydantic import BaseModel, Field


class RoomCreate(BaseModel):
    hotel_id: int
    room_number: str = Field(..., min_length=1)
    room_type: str = Field(..., min_length=1)
    price_per_night: float = Field(..., gt=0)
    available: bool = True


class RoomUpdate(BaseModel):
    hotel_id: int
    room_number: str = Field(..., min_length=1)
    room_type: str = Field(..., min_length=1)
    price_per_night: float = Field(..., gt=0)
    available: bool


class RoomResponse(BaseModel):
    id: int
    hotel_id: int
    room_number: str
    room_type: str
    price_per_night: float
    available: bool


class AvailabilityResponse(BaseModel):
    room_id: int
    available: bool
