# ---------- Base builder (build wheels & venv) ----------
FROM python:3.13-alpine AS builder

# Toolchain only in builder (kept out of final image)
RUN apk add --no-cache \
    build-base \
    libffi-dev \
    musl-dev \
    openssl-dev \
    curl

# Isolated venv for deps
ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ---------- Dev image (hot reload) ----------
FROM python:3.13-alpine AS dev
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app

# bring venv from builder
COPY --from=builder $VIRTUAL_ENV $VIRTUAL_ENV

# app code
COPY app ./app

EXPOSE 8000
# FastAPI dev server (hot reload UI)
CMD ["fastapi", "dev", "app/main.py", "--host", "0.0.0.0", "--port", "8000"]

# ---------- Prod image (small) ----------
FROM python:3.13-alpine AS prod
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app

# bring venv from builder
COPY --from=builder $VIRTUAL_ENV $VIRTUAL_ENV

# app code
COPY app ./app

# (optional) non-root
# RUN adduser -D -H appuser && chown -R appuser:appuser /app
# USER appuser

EXPOSE 8000
ENV PORT=8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
