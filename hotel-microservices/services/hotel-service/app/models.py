from pydantic import BaseModel


class Hotel(BaseModel):
    id: int
    name: str
    city: str
    rating: float
