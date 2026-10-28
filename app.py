import os
import sys
from flask import Flask, render_template_string, request

app = Flask(__name__)

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
            <h3>Resultado:</h3>
            <pre>{{ resultado }}</pre>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    resultado = None
    codigo = None
    if request.method == "POST":
        codigo = request.form.get("codigo")
        # Aquí puedes integrar la lógica de tu Visitor/Lexer/Parser generado por ANTLR4 para Bazilio
        resultado = f"Código recibido correctamente:\n{codigo}"
    return render_template_string(INDEX_HTML, resultado=resultado, codigo=codigo)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)