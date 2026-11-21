FROM node:22-bookworm-slim AS frontend
WORKDIR /ui
COPY frontend/package*.json ./
RUN --mount=type=secret,id=build_ca if [ -s /run/secrets/build_ca ]; then export NODE_EXTRA_CA_CERTS=/run/secrets/build_ca; fi; npm ci
COPY frontend/ ./
RUN npm run build
FROM python:3.12-slim
WORKDIR /app
COPY requirements.lock .
RUN --mount=type=secret,id=build_ca if [ -s /run/secrets/build_ca ]; then export PIP_CERT=/run/secrets/build_ca; fi; pip install --timeout 120 --retries 5 --no-cache-dir -r requirements.lock
COPY . .
COPY --from=frontend /ui/dist /app/frontend/dist
RUN useradd --create-home appuser && chown -R appuser /app
USER appuser
EXPOSE 8000
CMD ["sh","-c","alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
