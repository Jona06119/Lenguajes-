#!/usr/bin/env bash
set -o errexit

echo "--- Instalando dependencias de Python ---"
pip install -r requirements.txt

echo "--- Descargando LilyPond portable para Linux ---"
# Descarga la versión estable de LilyPond para Linux (64-bits)
wget https://gitlab.com/lilypond/lilypond/-/releases/v2.24.2/downloads/lilypond-2.24.2-linux-x86_64.tar.gz

echo "--- Extrayendo LilyPond ---"
tar -xzf lilypond-2.24.2-linux-x86_64.tar.gz

# Creamos una carpeta bin local y movemos el binario o lo enlazamos
# O simplemente agregamos su ruta al PATH para que Python lo encuentre al ejecutarlo
LILYPOND_DIR=$(pwd)/lilypond-2.24.2/bin
export PATH="$LILYPOND_DIR:$PATH"

echo "--- Verificando instalación de LilyPond ---"
lilypond --version