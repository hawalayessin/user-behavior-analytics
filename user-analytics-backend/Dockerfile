FROM python:3.11-slim

WORKDIR /app

# Dépendances système minimales
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Installer les dépendances Python (sans utiliser requirements.txt, qui a un encodage Windows)
RUN pip install --no-cache-dir \
    alembic==1.18.4 \
    annotated-doc==0.0.4 \
    annotated-types==0.7.0 \
    anyio==4.12.1 \
    click==8.3.1 \
    colorama==0.4.6 \
    fastapi \
    greenlet==3.3.1 \
    h11==0.16.0 \
    idna==3.11 \
    Mako==1.3.10 \
    MarkupSafe==3.0.3 \
    psycopg2-binary \
    "pydantic[email]" \
    pydantic_core==2.41.5 \
    pydantic-settings \
    python-dotenv==1.2.1 \
    SQLAlchemy==2.0.46 \
    sqlalchemy \
    starlette==0.52.1 \
    typing-inspection==0.4.2 \
    typing_extensions==4.15.0 \
    "uvicorn[standard]" \
    "passlib[bcrypt]" \
    "python-jose[cryptography]" \
    python-multipart

# Copier le code source
COPY . .

EXPOSE 8000

# ⚠️ PAS de --reload en Docker
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]