# FHIR Ends

A stub FHIR backend for Patient resources using FastAPI.

## Installation

### Prerequisites (if uv not found)
Add uv to PATH permanently:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

```bash
uv sync
```

This installs dependencies from `pyproject.toml` and `uv.lock` into `.venv`.

## Running the server

```bash
uv run python -m uvicorn main:app --reload
```

Server available at http://localhost:8000

Interactive docs: http://localhost:8000/docs

## Endpoints

- `POST /fhir/Patient` - Create patient
- `GET /fhir/Patient` - List patients
- `GET /fhir/Patient/{id}` - Get patient
- `PUT /fhir/Patient/{id}` - Update patient
- `DELETE /fhir/Patient/{id}` - Delete patient

## Patient Model

See `models.py` for Pydantic schema (minimal FHIR R4 Patient stub).