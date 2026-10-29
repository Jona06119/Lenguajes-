#!/usr/bin/env bash
# Salir inmediatamente si ocurre un error
set -o errexit

# Actualizar paquetes e instalar LilyPond en el servidor de Render
apt-get update
apt-get install -y lilypond

# Instalar las dependencias de Python de tu proyecto
pip install -r requirements.txt