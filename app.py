import os
from flask import Flask, render_template_string, request, send_from_directory

app = Flask(__name__)

# Directorio donde se guardarán los archivos temporales (audios, PDFs)
STATIC_DIR = os.path.join(os.path.dirname(__file__), 'static')
os.makedirs(STATIC_DIR, exist_ok=True)

INDEX_HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Bazilio - Intérprete DSL</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f4f4f9; color: #333; }
        .container { max-width: 800px; margin: auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        textarea { width: 100%; height: 150px; font-family: monospace; padding: 10px; border: 1px solid #ccc; border-radius: 4px; }
        input[type="submit"] { background: #007bff; color: white; border: none; padding: 10px 20px; cursor: pointer; border-radius: 4px; margin-top: 10px; }
        input[type="submit"]:hover { background: #0056b3; }
        pre { background: #eee; padding: 10px; border-radius: 4px; }
        .results { margin-top: 20px; }
        .file-links a { display: inline-block; margin-right: 15px; padding: 8px 12px; background: #28a745; color: white; text-decoration: none; border-radius: 4px; }
        .file-links a:hover { background: #218838; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Intérprete de Bazilio</h2>
        <form method="POST">
            <label>Código fuente:</label><br>
            <textarea name="codigo">{{ codigo or '' }}</textarea><br>
            <input type="submit" value="Ejecutar Código">
        </form>
        
        {% if resultado %}
            <div class="results">
                <h3>Resultado de la ejecución:</h3>
                <pre>{{ resultado }}</pre>
            </div>
        {% endif %}

        {% if audio_file or pdf_file %}
            <div class="file-links">
                <h3>Archivos Generados:</h3>
                {% if audio_file %}
                    <audio controls style="width: 100%; margin-bottom: 10px;">
                        <source src="{{ url_for('static', filename=audio_file) }}" type="audio/wav">
                        Tu navegador no soporta el elemento de audio.
                    </audio>
                    <br>
                    <a href="{{ url_for('static', filename=audio_file) }}" download>Descargar Audio (.wav)</a>
                {% endif %}
                {% if pdf_file %}
                    <a href="{{ url_for('static', filename=pdf_file) }}" target="_blank">Ver / Descargar PDF</a>
                {% endif %}
            </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    resultado = None
    codigo = None
    audio_file = None
    pdf_file = None

    if request.method == "POST":
        codigo = request.form.get("codigo")
        
        # 1. Guardar el código temporalmente para que tu parser lo lea (o pasarlo en memoria)
        temp_input_path = os.path.join(STATIC_DIR, "temp_codigo.txt")
        with open(temp_input_path, "w", encoding="utf-8") as f:
            f.write(codigo)

        try:
            # ==========================================
            # 2. AQUÍ LLAMAS A TU INTÉRPRETE DE ANTLR
            # ==========================================
            # Ejemplo (ajusta esto según cómo ejecutes tu script de ANTLR por lo general):
            # import subprocess
            # proceso = subprocess.run(['python', 'bazilio_etapa5.py', temp_input_path], capture_output=True, text=True)
            # resultado = proceso.stdout if proceso.returncode == 0 else proceso.stderr
            
            # O si importas directamente tus funciones:
            # from bazilio_etapa5 import ejecutar_interprete
            # resultado = ejecutar_interprete(codigo)

            # Por ahora, simulamos la ejecución y la detección de archivos si tu código los crea:
            resultado = f"Código procesado con éxito:\n{codigo}"
            
            # Si tu intérprete genera archivos específicos en static/, búscalos:
            if os.path.exists(os.path.join(STATIC_DIR, "hanoi_musical.wav")) or os.path.exists(os.path.join(STATIC_DIR, "hello.wav")):
                audio_file = "hanoi_musical.wav" if os.path.exists(os.path.join(STATIC_DIR, "hanoi_musical.wav")) else "hello.wav"
                
            if os.path.exists(os.path.join(STATIC_DIR, "hello.pdf")):
                pdf_file = "hello.pdf"

        except Exception as e:
            resultado = f"Error al ejecutar el intérprete: {str(e)}"

    return render_template_string(
        INDEX_HTML, 
        resultado=resultado, 
        codigo=codigo, 
        audio_file=audio_file, 
        pdf_file=pdf_file
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)