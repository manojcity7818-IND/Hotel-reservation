from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.requests import Request

from app import data
from app.models import Hotel
from app.schemas import HotelCreate, HotelResponse, HotelUpdate

app = FastAPI(title="Hotel Service", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": "Invalid request."})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    if isinstance(exc, HTTPException):
        raise exc
    return JSONResponse(
        status_code=500, content={"detail": "Unexpected internal error."}
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy", "service": "hotel-service"}


@app.get("/ready")
def ready() -> dict[str, str]:
    return {"status": "ready", "service": "hotel-service"}


@app.get("/api/v1/hotels", response_model=list[HotelResponse])
def get_hotels(city: Optional[str] = None, q: Optional[str] = None) -> list[Hotel]:
    results = list(data.hotels.values())
    needle = (city or q or "").strip().lower()
    if needle:
        results = [
            hotel
            for hotel in results
            if needle in hotel.city.lower() or needle in hotel.name.lower()
        ]
    return results


@app.get("/api/v1/hotels/{hotel_id}", response_model=HotelResponse)
def get_hotel(hotel_id: int) -> Hotel:
    hotel = data.hotels.get(hotel_id)
    if hotel is None:
        raise HTTPException(status_code=404, detail="Hotel not found.")
    return hotel


@app.post("/api/v1/hotels", response_model=HotelResponse, status_code=201)
def create_hotel(payload: HotelCreate) -> Hotel:
    hotel = Hotel(id=data.next_id(), **payload.model_dump())
    data.hotels[hotel.id] = hotel
    return hotel


@app.put("/api/v1/hotels/{hotel_id}", response_model=HotelResponse)
def update_hotel(hotel_id: int, payload: HotelUpdate) -> Hotel:
    if hotel_id not in data.hotels:
        raise HTTPException(status_code=404, detail="Hotel not found.")
    hotel = Hotel(id=hotel_id, **payload.model_dump())
    data.hotels[hotel_id] = hotel
    return hotel


@app.delete("/api/v1/hotels/{hotel_id}", status_code=204)
def delete_hotel(hotel_id: int) -> None:
    if hotel_id not in data.hotels:
        raise HTTPException(status_code=404, detail="Hotel not found.")
    del data.hotels[hotel_id]
