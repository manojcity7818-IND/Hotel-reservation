from pydantic import BaseModel, Field


class HotelCreate(BaseModel):
    name: str = Field(..., min_length=1)
    city: str = Field(..., min_length=1)
    rating: float = Field(..., ge=0, le=5)


class HotelUpdate(BaseModel):
    name: str = Field(..., min_length=1)
    city: str = Field(..., min_length=1)
    rating: float = Field(..., ge=0, le=5)


class HotelResponse(BaseModel):
    id: int
    name: str
    city: str
    rating: float
