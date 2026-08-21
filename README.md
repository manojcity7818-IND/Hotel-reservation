# Hotel-reservation

Phase 1 lives in [`hotel-microservices/`](hotel-microservices/README.md).

Five FastAPI services (hotel, room, booking, payment, notification) plus the Aryanstays website.

Azure DevOps:

- PR validation: [`azure-pipelines-pr.yml`](azure-pipelines-pr.yml)
- CI image build: [`azure-pipelines-ci.yml`](azure-pipelines-ci.yml)

```bash
cd hotel-microservices
docker compose up --build
```

Then open **http://localhost:8080** to use the Aryanstays website. After you book, open **http://localhost:8025** to read the booking emails in Mailpit.
