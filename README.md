# FHIR Ends

A full-stack FHIR demo featuring a FastAPI backend and a React + TypeScript frontend.

## Features

- **FHIR Backend**: FastAPI-based server supporting Patient and Practitioner resources.
- **Modern Frontend**: React, TypeScript, Tailwind CSS, and Lucide icons.
- **Interoperability**: Returns FHIR `Bundle` and `CapabilityStatement` resources.
- **Standard Search**: Supports FHIR-native search parameters (`name`, `family`, `given`, `gender`).
- **Containerized**: Fully orchestrated using Docker Compose.

## Getting Started

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/)
- (Optional for local development) [uv](https://github.com/astral-sh/uv)

### Running the Full Stack

The easiest way to run the entire application (Backend, Frontend, and Database) is using Docker Compose:

```bash
docker-compose up --build
```

For a better development experience with automatic hot-reloading when you change code, use Docker Compose Watch:

```bash
docker-compose watch
```

- **Frontend**: [http://localhost:3000](http://localhost:3000)
- **Backend API**: [http://localhost:8000](http://localhost:8000)
- **Interactive API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

### Local Development (Backend Only)

1. **Install dependencies**:
   ```bash
   uv sync
   ```

2. **Seed the database**:
   ```bash
   # Ensure Postgres is running via docker-compose up -d db
   uv run python seed.py
   ```

3. **Run the server**:
   ```bash
   uv run python -m uvicorn main:app --reload
   ```

## Frontend Features

- **Login Portal**: Mock authentication to demonstrate secure routing.
- **Patient Dashboard**: View, search, and manage patient records in a clean, modern interface.
- **Real-time Search**: Instant filtering using FHIR search parameters.

## API Endpoints

- `GET /fhir/metadata` - CapabilityStatement
- `GET /fhir/Patient` - Search/List patients (returns Bundle)
- `POST /fhir/Patient` - Create patient
- `GET /fhir/Patient/{id}` - Read patient
- `PUT /fhir/Patient/{id}` - Update patient
- `DELETE /fhir/Patient/{id}` - Delete patient

## Project Structure

- `/`: FastAPI backend code and configuration.
- `/frontend`: React + TypeScript frontend application.
- `models.py`: FHIR-compliant Pydantic models.
- `seed.py`: Database seeder script.