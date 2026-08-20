# Hotel-reservation

Phase 1 lives in [`hotel-microservices/`](hotel-microservices/README.md).

Three FastAPI services (Hotel, Room, Booking) plus a booking website run locally with Docker Compose and in-memory data.

```bash
cd hotel-microservices
docker compose up --build
```

Then open **http://localhost:8080** to use the hotel website.
