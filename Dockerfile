FROM python:3.10-slim

# Instalar LilyPond, TiMidity, sintetizador y fuentes de texto
RUN apt-get update && apt-get install -y \
    lilypond \
    timidity \
    fluid-soundfont-gm \
    ffmpeg \
    fonts-texgyre \
    && rm -rf /var/lib/apt/lists/*

# Configurar el soundfont por defecto para timidity
RUN echo "soundfont /usr/share/sounds/sf2/FluidR3_GM.sf2" >> /etc/timidity/timidity.cfg

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]