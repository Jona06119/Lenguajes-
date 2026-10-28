import os
import sys
from flask import Flask, render_template_string, request, url_for
from antlr4 import InputStream, CommonTokenStream

# Importación correcta respetando las mayúsculas de Bazilio
from bazilio import BazilioLexer, BazilioParser, BazilioInterpreter, generar_archivos

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
            max-width: 520px; 
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
        /* Estilo horizontal para el reproductor y el PDF */
        .results-row {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-top: 20px;
        }
        audio { 
            flex: 1; 
            height: 40px;
            border-radius: 8px; 
        }
        .download-btn { 
            display: flex;
            align-items: center;
            justify-content: center;
            background: #2a2a2a; 
            color: white; 
            border: 1px solid #444; 
            padding: 0 16px; 
            height: 40px;
            border-radius: 8px; 
            text-decoration: none; 
            font-size: 14px; 
            font-weight: 600;
            white-space: nowrap;
            box-sizing: border-box;
        }
        .download-btn:hover { background: #333; }
        .error-box {
            background: #3b1b1b;
            border: 1px solid #6a2d2d;
            color: #ff8888;
            padding: 12px;
            border-radius: 8px;
            margin-top: 20px;
            font-size: 14px;
            white-space: pre-wrap;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>ANTLR y LilyPond</h1>
        <form method="POST">
            <label>Nombre de la cancion:</label>
            <input type="text" name="nombre_cancion" value="{{ nombre_cancion or 'mi_melodia' }}" required>
            
            <label>Escribe tus notas (ej: C4, D4, E4):</label>
            <textarea name="codigo" placeholder="C4&#10;D4&#10;E4&#10;F4" required>{{ codigo or '' }}</textarea>
            
            <button type="submit" class="btn">Convertir y Generar</button>
        </form>

        {% if mensaje_exito %}
            <div class="success-box">
                {{ mensaje_exito }}
            </div>
        {% endif %}

        {% if error %}
            <div class="error-box">
                {{ error }}
            </div>
        {% endif %}

        {% if audio_file or pdf_file %}
            <div class="results-row">
                {% if audio_file %}
                    <audio controls autoplay>
                        <source src="{{ url_for('static', filename=audio_file) }}?t={{ timestamp }}" type="audio/wav">
                        Tu navegador no soporta el elemento de audio.
                    </audio>
                {% endif %}

                {% if pdf_file %}
                    <a href="{{ url_for('static', filename=pdf_file) }}?t={{ timestamp }}" class="download-btn" target="_blank">PDF</a>
                {% endif %}
            </div>
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
    error = None
    audio_file = None
    pdf_file = None
    import time
    timestamp = int(time.time())

    if request.method == "POST":
        nombre_cancion = request.form.get("nombre_cancion", "mi_melodia").strip()
        codigo = request.form.get("codigo", "").strip()
        
        # --- ENVUELVE AUTOMÁTICAMENTE LAS NOTAS SI EL USUARIO NO PUSO LA ESTRUCTURA ---
        if codigo and not codigo.upper().startswith("PROC"):
            lineas = [l.strip() for l in codigo.splitlines() if l.strip()]
            instrucciones = []
            for l in lineas:
                if not l.upper().startswith("TOCA"):
                    instrucciones.append(f"    TOCA {l}")
                else:
                    instrucciones.append(f"    {l}")
            codigo = "PROC Main\nINICIO\n" + "\n".join(instrucciones) + "\nFIN"
        # --------------------------------------------------------------------------

        # Rutas de salida directas en la carpeta static/
        base_path = os.path.join(STATIC_DIR, nombre_cancion)
        
        try:
            # Procesamos el código con ANTLR utilizando tu analizador
            input_stream = InputStream(codigo)
            lexer = BazilioLexer(input_stream)
            stream = CommonTokenStream(lexer)
            parser = BazilioParser(stream)
            tree = parser.programa()  # Regla principal en minúscula como en tu gramática g4
            
            interpreter = BazilioInterpreter()
            interpreter.visit(tree)
            
            if interpreter.notas_tocadas:
                # Generamos los archivos físicos (PDF y WAV)
                generar_archivos(base_path, interpreter.notas_tocadas)
                
                # Verificamos que se hayan creado en la carpeta static
                if os.path.exists(f"{base_path}.wav"):
                    audio_file = f"{nombre_cancion}.wav"
                if os.path.exists(f"{base_path}.pdf"):
                    pdf_file = f"{nombre_cancion}.pdf"
                
                mensaje_exito = f"Archivos generados correctamente para '{nombre_cancion}'"
            else:
                error = "El código se ejecutó, pero no se detectaron notas musicales con la instrucción TOCA."

        except Exception as e:
            error = f"Error al interpretar o compilar:\n{str(e)}"

    return render_template_string(
        INDEX_HTML,
        nombre_cancion=nombre_cancion,
        codigo=codigo,
        mensaje_exito=mensaje_exito,
        error=error,
        audio_file=audio_file,
        pdf_file=pdf_file,
        timestamp=timestamp
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)