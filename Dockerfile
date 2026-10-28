FROM python:3.10-slim

# Instalar LilyPond, TiMidity y FFmpeg directamente en el sistema Linux
RUN apt-get update && apt-get install -y \
    lilypond \
    timidity \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar e instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . .

EXPOSE 5000

# Comando para iniciar la aplicación con gunicorn
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]