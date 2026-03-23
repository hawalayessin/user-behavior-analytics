FROM python:3.11-slim

WORKDIR /app

# Dépendances système pour PostgreSQL
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
  && rm -rf /var/lib/apt/lists/*

# Installer dépendances Python à partir de requirements.txt
COPY requirements.txt .
# Certains éditeurs Windows sauvegardent en UTF-16 (caractères \x00).
# On convertit en UTF-8 au build pour que pip puisse lire le fichier.
RUN python -c "import pathlib; p=pathlib.Path('requirements.txt'); b=p.read_bytes(); \
  enc='utf-16' if b[:2] in (b'\\xff\\xfe', b'\\xfe\\xff') or b'\\x00' in b[:200] else 'utf-8'; \
  txt=b.decode(enc, errors='ignore'); pathlib.Path('requirements.utf8.txt').write_text(txt, encoding='utf-8')" \
  && pip install --no-cache-dir -r requirements.utf8.txt

# Copier le code de l'API
COPY . .

ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

