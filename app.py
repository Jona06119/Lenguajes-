import os
from flask import Flask, render_template_string, request, url_for

app = Flask(__name__)

# Directorio de archivos estáticos
STATIC_DIR = os.path.join(os.path.dirname(__file__), 'static')
os.makedirs(STATIC_DIR, exist_ok=True)

INDEX_HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>ANTLR y LilyPond</title>
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; 
            background: #121212; 
            color: #ffffff; 
            display: flex; 
            justify-content: center; 
            align-items: center; 
            min-height: 100vh; 
            margin: 0; 
        }
        .container { 
            width: 100%; 
            max-width: 480px; 
            background: #1e1e1e; 
            padding: 30px; 
            border-radius: 12px; 
            box-shadow: 0 8px 24px rgba(0,0,0,0.5); 
        }
        h1 { font-size: 24px; margin-bottom: 25px; font-weight: 700; text-align: center; }
        label { display: block; font-size: 14px; margin-bottom: 8px; color: #ccc; }
        input[type="text"], textarea { 
            width: 100%; 
            background: #2a2a2a; 
            border: 1px solid #3a3a3a; 
            border-radius: 8px; 
            color: white; 
            padding: 12px; 
            font-size: 14px; 
            box-sizing: border-box; 
            margin-bottom: 20px; 
        }
        textarea { height: 120px; font-family: monospace; resize: vertical; }
        input[type="text"]:focus, textarea:focus { border-color: #007bff; outline: none; }
        .btn { 
            background: #222; 
            color: white; 
            border: 1px solid #444; 
            padding: 12px 20px; 
            cursor: pointer; 
            border-radius: 8px; 
            font-size: 14px; 
            width: 100%; 
            font-weight: 600;
            transition: background 0.2s;
        }
        .btn:hover { background: #333; }
        .success-box { 
            background: #1b3b2b; 
            border: 1px solid #2d6a4f; 
            color: #52b788; 
            padding: 12px; 
            border-radius: 8px; 
            margin-top: 20px; 
            font-size: 14px; 
            text-align: center;
        }
        audio { width: 100%; margin-top: 20px; border-radius: 8px; }
        .download-btn { 
            display: block; 
            text-align: center; 
            background: transparent; 
            color: white; 
            border: 1px solid #444; 
            padding: 12px; 
            border-radius: 8px; 
            text-decoration: none; 
            margin-top: 15px; 
            font-size: 14px; 
            font-weight: 600;
        }
        .download-btn:hover { background: #2a2a2a; }
    </style>
</head>
<body>
    <div class="container">
        <h1>ANTLR y LilyPond</h1>
        <form method="POST">
            <label>Nombre de la cancion:</label>
            <input type="text" name="nombre_cancion" value="{{ nombre_cancion or 'mi_melodia' }}" required>
            
            <label>Escribe tus notas (ej: c4, d4, e4, do#):</label>
            <textarea name="codigo" placeholder="g4&#10;g4&#10;f4&#10;f4" required>{{ codigo or '' }}</textarea>
            
            <button type="submit" class="btn">Convertir y Generar</button>
        </form>

        {% if mensaje_exito %}
            <div class="success-box">
                {{ mensaje_exito }}
            </div>
        {% endif %}

        {% if audio_file %}
            <!-- Reproductor integrado para escuchar ahí mismo -->
            <audio controls autoplay>
                <source src="{{ url_for('static', filename=audio_file) }}?t={{ timestamp }}" type="audio/wav">
                Tu navegador no soporta el elemento de audio.
            </audio>
        {% endif %}

        {% if pdf_file %}
            <!-- Botón para abrir o descargar el PDF generado al momento -->
            <a href="{{ url_for('static', filename=pdf_file) }}?t={{ timestamp }}" class="download-btn" target="_blank">Descargar Partitura PDF</a>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    nombre_cancion = "mi_melodia"
    codigo = ""
    mensaje_exito = None
    audio_file = None
    pdf_file = None
    import time
    timestamp = int(time.time())

    if request.method == "POST":
        nombre_cancion = request.form.get("nombre_cancion", "mi_melodia")
        codigo = request.form.get("codigo")
        
        # =========================================================================
        # AQUÍ INTEGRAS LA LLAMADA A TU INTÉRPRETE ANTLR / LILYPOND:
        # 1. Guardas el texto ingresado en un archivo temporal o se lo pasas a tu parser.
        # 2. Ejecutas la lógica que genera tu archivo .wav y tu archivo .pdf.
        # 3. Asegúrate de guardar esos archivos resultantes directamente en 'static/'
        #    con nombres fijos o basados en la canción (ej: static/audio.wav y static/partitura.pdf).
        # =========================================================================

        # Ejemplo de simulación de nombres de archivos generados en la carpeta static:
        audio_nombre = "hanoi_musical.wav"  # O el nombre que genere tu app
        pdf_nombre = "hello.pdf"            # O el nombre que genere tu app

        # Verificamos que realmente se hayan creado en la carpeta static
        audio_path = os.path.join(STATIC_DIR, audio_nombre)
        pdf_path = os.path.join(STATIC_DIR, pdf_nombre)

        # (Opcional para pruebas: si no existen físicamente aún, puedes crear archivos vacíos o de prueba)
        if not os.path.exists(audio_path):
            with open(audio_path, "wb") as f:
                f.write(b"") # Reemplaza esto con la ejecución real de tu intérprete
        if not os.path.exists(pdf_path):
            with open(pdf_path, "wb") as f:
                f.write(b"") # Reemplaza esto con la generación real de tu PDF

        # Activamos las variables para que aparezcan en la vista web
        mensaje_exito = f"Archivos generados correctamente para '{nombre_cancion}'"
        audio_file = audio_nombre
        pdf_file = pdf_nombre

    return render_template_string(
        INDEX_HTML,
        nombre_cancion=nombre_cancion,
        codigo=codigo,
        mensaje_exito=mensaje_exito,
        audio_file=audio_file,
        pdf_file=pdf_file,
        timestamp=timestamp
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)