# Hotel Booking Microservices — Phase 1

Local hotel booking application made of four independent Python microservices plus a website. All data is in-memory. Services talk to each other over REST and run together with Docker Compose.

This phase does **not** use a database, Redis, Azure, Kubernetes, Terraform, Kafka, RabbitMQ, authentication, or a service mesh.

Open the website at **http://localhost:8080** after `docker compose up`. The main screen uses `/images/hero-background.png` as the homepage background.

---

## 1. Architecture

```
                         Host machine
              http://localhost:8080  (Aryanstays website)
                           |
                           v
                    +--------------+
                    | Web (nginx)  |
                    | static UI    |
                    | API proxy    |
                    +------+-------+
                           |
         +-----------------+------------------+
         |                 |                  |
         v                 v                  v
 /api/v1/hotels     /api/v1/rooms      /api/v1/bookings
         |                 |                  |
 +--------------+   +--------------+   +-----------------+
 | Hotel        |   | Room         |   | Booking         |
 | Service      |   | Service      |   | Service         |
 | :8000        |   | :8000        |   | :8000           |
 +--------------+   +--------------+   +--------+--------+
                            ^                   |
                            |   HTTP REST       |
                            +-------------------+
                            ROOM_SERVICE_URL
                            http://room-service:8000

 Also reachable directly:
   Hotel    http://localhost:8000
   Room     http://localhost:8002
   Booking  http://localhost:8003
   Payment  http://localhost:8004

 Booking flow:

 Client
   |
   | POST /api/v1/bookings
   v
 Booking Service
   |
   | GET  /api/v1/rooms/{id}/availability
   | POST /api/v1/rooms/{id}/reserve
   v
 Room Service  (in-memory availability)
   |
   +-- unavailable --> HTTP 409
   +-- available   --> reserve, then Booking Service stores the booking
```

---

## 2. Microservices

### Hotel Service

Owns hotel records (id, name, city, rating). Sample data includes 25 hotels in each of 10 cities plus 10 hotels each in Mysore and Udaipur (270 hotels total): Hyderabad, Bangalore, Mumbai, New Delhi, Chennai, Goa, Jaipur, Pune, Kolkata, Kochi, Mysore, and Udaipur.

`GET /api/v1/hotels?q=Mumbai` filters by city or hotel name.

- Base URL on the host: `http://localhost:8000`
- Does not call other services

### Room Service

Owns rooms and availability. Each hotel has sample rooms (for example 101/102 for Grand Hyderabad Hotel and 201/202 for Bangalore Palace Hotel).

- Base URL on the host: `http://localhost:8002`
- `POST /reserve` sets `available` to `false`
- `POST /release` sets `available` to `true`

### Booking Service

Creates, lists, and cancels bookings. It **never** reads Room Service or Payment Service memory. It calls those services over REST.

- Base URL on the host: `http://localhost:8003`
- `ROOM_SERVICE_URL=http://room-service:8000`
- `PAYMENT_SERVICE_URL=http://payment-service:8000`

A new booking starts as `PENDING_PAYMENT`. After Payment Service reports success, Booking Service sets the status to `CONFIRMED`.

### Payment Service

Takes payment for a booking. Supported methods: **UPI**, **Credit/Debit card**, **Net banking**, and **Wallet**.

- Base URL on the host: `http://localhost:8004`
- `POST /api/v1/payments` creates a payment
- `GET /api/v1/payments/methods` lists payment options
- Demo failures: UPI IDs ending in `@fail`, or card numbers starting with `0000`

### Website (Aryanstays)

The hotel booking UI at `http://localhost:8080`. It is an Agoda-style full-page experience: top promo strip, product navigation, large MEGA SALE hero, destination search with dates and guests, top destinations, deal banners, and property result cards. The browser calls:

- `/api/v1/hotels` → Hotel Service
- `/api/v1/rooms` → Room Service
- `/api/v1/bookings` → Booking Service
- `/api/v1/payments` → Payment Service

You can browse hotels, see rooms and availability, create a booking, and cancel a booking. The website does not store data itself.

---

## 3. Why each service is independent

Each service has its own process, Docker image, in-memory store, and HTTP API. Hotel data, room data, and booking data are not shared through imports or a common database. You can start, stop, rebuild, and test one service without the others (Booking Service needs Room Service only when creating or cancelling a booking).

---

## 4. REST communication between services

The only service-to-service call in Phase 1 is Booking Service → Room Service.

| Booking action | Room Service call | Result |
| --- | --- | --- |
| Create booking | `GET /api/v1/rooms/{room_id}/availability` | If `available` is false, return **409** |
| Create booking | `POST /api/v1/rooms/{room_id}/reserve` | Marks the room unavailable |
| Cancel booking | `POST /api/v1/rooms/{room_id}/release` | Marks the room available again |

Calls use the Compose **service name**, not `localhost`:

```
http://room-service:8000
```

`localhost` inside a container is that container itself, so Booking Service would fail if it used `localhost:8002`.

If Room Service is down, Booking Service returns **503** instead of crashing.

---

## 5. Docker architecture

- Each service image is `python:3.12-slim`, runs as a non-root user, and starts Uvicorn on port **8000**.
- Compose maps host ports: Hotel `8000`, Room `8002`, Booking `8003`.
- All three containers join the `hotel-network` bridge network.
- Health checks call each container's `GET /health` on `127.0.0.1:8000`.
- Restart policy: `unless-stopped`.
- Booking Service waits until Room Service is healthy.

---

## 6. Project structure

```
hotel-microservices/
├── services/
│   ├── hotel-service/
│   ├── room-service/
│   ├── booking-service/
│   └── payment-service/
├── web/
│   ├── public/
│   ├── tests/
│   ├── nginx.conf
│   └── Dockerfile
├── scripts/
│   └── run-tests.sh
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

Each backend service contains `app/` (FastAPI), `tests/`, `requirements.txt`, `Dockerfile`, and `.dockerignore`. The website lives in `web/`.

---

## 7. Prerequisites

- Docker Engine with Docker Compose v2
- Ports 8000, 8002, and 8003 free on the host
- Optional for unit tests only: Python 3.12

---

## 8. How to build

From `hotel-microservices/`:

```bash
docker compose build
```

Build and start in one step:

```bash
docker compose up --build
```

Rebuild a single service:

```bash
docker compose build hotel-service
docker compose up -d hotel-service
```

```bash
docker compose up -d --build room-service
```

---

## 9. How to run

```bash
docker compose up -d
```

Open the Aryanstays website:

[http://localhost:8080](http://localhost:8080)

Check containers:

```bash
docker compose ps
```

Health checks from the host:

```bash
curl http://localhost:8000/health
curl http://localhost:8002/health
curl http://localhost:8003/health
```

Expected:

```json
{"status":"healthy","service":"hotel-service"}
```

Readiness:

```bash
curl http://localhost:8000/ready
curl http://localhost:8002/ready
curl http://localhost:8003/ready
```

---

## 10. How to stop

```bash
docker compose down
```

Because data is in-memory, stopping containers clears hotels/rooms/bookings back to the sample seed on the next start.

---

## 11. How to view logs

All services:

```bash
docker compose logs -f
```

One service:

```bash
docker compose logs -f booking-service
```

---

## 12. How to test APIs

Interactive docs (Swagger):

- Hotel: http://localhost:8000/docs
- Room: http://localhost:8002/docs
- Booking: http://localhost:8003/docs

Unit tests (from `hotel-microservices/`, with Python 3.12):

```bash
./scripts/run-tests.sh
```

Or per service:

```bash
cd services/hotel-service && pytest
cd services/room-service && pytest
cd services/booking-service && pytest
cd web && pytest
```

---

## 13. Example curl commands

### Get hotels

```bash
curl http://localhost:8000/api/v1/hotels
```

### Get rooms

```bash
curl http://localhost:8002/api/v1/rooms
```

### Check room availability

```bash
curl http://localhost:8002/api/v1/rooms/101/availability
```

### Create booking

```bash
curl -X POST http://localhost:8003/api/v1/bookings \
  -H "Content-Type: application/json" \
  -d '{
    "hotel_id": 1,
    "room_id": 101,
    "customer_name": "John Doe",
    "customer_email": "john@example.com",
    "check_in": "2026-09-01",
    "check_out": "2026-09-03"
  }'
```

### Get booking

```bash
curl http://localhost:8003/api/v1/bookings/1
```

Replace `1` with the `booking_id` from the create response.

### Cancel booking

```bash
curl -X DELETE http://localhost:8003/api/v1/bookings/1
```

Other useful calls:

```bash
curl http://localhost:8000/api/v1/hotels/1
curl http://localhost:8002/api/v1/rooms/hotel/1
curl -X POST http://localhost:8002/api/v1/rooms/102/reserve
curl -X POST http://localhost:8002/api/v1/rooms/102/release
```

---

## 14. Example booking flow

1. List hotels: `GET http://localhost:8000/api/v1/hotels`
2. List rooms for hotel 1: `GET http://localhost:8002/api/v1/rooms/hotel/1`
3. Confirm room 101 is available: `GET http://localhost:8002/api/v1/rooms/101/availability`
4. Create a booking for room 101 via Booking Service (see curl above).
5. Room 101 is now reserved (`available: false`).
6. Creating a second booking for room 101 returns **HTTP 409**.
7. Cancel the booking: `DELETE http://localhost:8003/api/v1/bookings/{booking_id}`.
8. Room 101 is released (`available: true`) and the booking status is `CANCELLED`.

---

## 15. Troubleshooting

| Problem | What to check |
| --- | --- |
| Port already in use | Stop whatever is bound to 8000/8002/8003, or change the left-hand ports in `docker-compose.yml`. |
| Booking create returns 503 | Room Service is not healthy. Run `docker compose ps` and `docker compose logs room-service`. |
| Booking create returns 409 | The room is already reserved. Release it or cancel the existing booking. |
| Cannot reach a service from another container | Use `http://room-service:8000`, not `localhost`. |
| Healthcheck stays unhealthy | Wait for the start period, then inspect logs. Health URLs inside the container are `http://127.0.0.1:8000/health`. |
| Data disappeared after restart | Expected. Phase 1 stores everything in memory. |
| Rebuild did not pick up code | `docker compose build --no-cache <service>` then `docker compose up -d <service>`. |

---

## 16. Azure DevOps pipelines

Two pipelines live at the repository root:

| File | When it runs | What it does |
| --- | --- | --- |
| `azure-pipelines-pr.yml` | Pull requests to `main` | Install Python 3.12, compile services, run unit tests with coverage, SonarCloud analysis, and Docker **build** validation (no push) |
| `azure-pipelines-ci.yml` | Pushes to `main` | Run unit tests, publish the `hotel-microservices` artifact, then **build, Trivy-scan, and push** images for hotel-service, room-service, booking-service, and hotel-web |

### Create the pipelines

1. In Azure DevOps, create a pipeline from `azure-pipelines-pr.yml` (PR validation).
2. Create a second pipeline from `azure-pipelines-ci.yml` (CI / image build).
3. Create variable group **KV-VariableGroup** (same name as in the YAML).
4. Create SonarCloud service connection **SonarCloud-ServiceConnection**.
5. Update `sonarOrganization` and `sonarProjectKey` in `azure-pipelines-pr.yml` if your SonarCloud project uses different values.
6. Create a Docker Registry service connection named **hotelreservationacr** pointing at your Azure Container Registry.
7. Grant the CI pipeline permission to use that ACR connection.

Images pushed by CI:

- `hotel-service:$(Build.BuildId)` and `:latest`
- `room-service:$(Build.BuildId)` and `:latest`
- `booking-service:$(Build.BuildId)` and `:latest`
- `hotel-web:$(Build.BuildId)` and `:latest`

---

## Ports

HTTP errors used by the APIs:

| Status | Meaning |
| --- | --- |
| 400 | Invalid request |
| 404 | Hotel / room / booking not found |
| 409 | Room already reserved, or booking cannot be created because the room is unavailable |
| 500 | Unexpected internal error |
| 503 | Room Service is unavailable (Booking Service only) |

---

## Ports

| Service | Container port | Host port |
| --- | --- | --- |
| hotel-service | 8000 | 8000 |
| room-service | 8000 | 8002 |
| booking-service | 8000 | 8003 |
| payment-service | 8000 | 8004 |
| web | 8080 | 8080 |
