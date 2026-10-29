FROM python:3.10-slim

# Instalar LilyPond, TiMidity, banco de sonido y fuentes tipográficas
RUN apt-get update && apt-get install -y \
    lilypond \
    timidity \
    fluid-soundfont-gm \
    ffmpeg \
    fonts-texgyre \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]