FROM python:3.11-slim

WORKDIR /app

# Dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    pkg-config \
    libcairo2 \
    libcairo2-dev \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    shared-mime-info \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copier requirements
COPY requirements.txt .

# Conversion UTF16 -> UTF8
RUN python -c "import pathlib; p=pathlib.Path('requirements.txt'); b=p.read_bytes(); \
enc='utf-16' if b[:2] in (b'\xff\xfe', b'\xfe\xff') or b'\x00' in b[:200] else 'utf-8'; \
txt=b.decode(enc, errors='ignore'); pathlib.Path('requirements.utf8.txt').write_text(txt, encoding='utf-8')" \
&& pip install --no-cache-dir -r requirements.utf8.txt

# Copier le code
COPY . .

ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]