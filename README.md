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

Then open **http://localhost:8080** to use the Aryanstays website. The homepage uses a full-bleed chef-hat photo on a black background, and the catalog has 270 in-memory hotels across 12 Indian cities.
