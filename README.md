# Hotel-reservation

Phase 1 lives in [`hotel-microservices/`](hotel-microservices/README.md).

Three FastAPI services (Hotel, Room, Booking) plus a booking website run locally with Docker Compose and in-memory data.

Azure DevOps:

- PR validation: [`azure-pipelines-pr.yml`](azure-pipelines-pr.yml)
- CI image build: [`azure-pipelines-ci.yml`](azure-pipelines-ci.yml)

```bash
cd hotel-microservices
docker compose up --build
```

Then open **http://localhost:8080** to use the Aryanstays website.
