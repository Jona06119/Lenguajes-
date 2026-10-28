Bazilio - Intérprete y Lenguaje Musical

Bazilio es un proyecto enfocado en la implementación de un lenguaje de programación capaz de interpretar estructuras musicales, manipular variables y ejecutar lógica condicional e iterativa.

Requisitos Previos

Asegúrate de contar con lo siguiente en tu sistema (probado en Archcraft / Arch Linux):

Python 3.8+

ANTLR4

Runtime de ANTLR4 para Python:

pip install antlr4-python3-runtime


Instalación y Configuración

Clonar el repositorio:

git clone https://github.com/tu-usuario/Practica_Lenguajes.git
cd Practica_Lenguajes


Compilar la gramática con ANTLR4:
Para generar el Lexer, Parser, Listener y Visitor en Python, ejecuta:

antlr4 -Dlanguage=Python3 bazilio.g4 -visitor -listener


Estructura del Código Bazilio

Un programa típico en Bazilio contiene procedimientos delimitados por |: y :|:

Principal
|:
    nota <- C4
    <w> "Reproduciendo nota:" nota
    (:) nota
:|


Sintaxis Relevante:

Bloques: |: inicio de bloque, :| fin de bloque.

Asignación: variable <- expresion

Entrada / Salida: <?> variable (lectura), <w> expresion (escritura).

Reproducción Musical: (:) nota o <:> nota

Arreglos y Listas: Agregado << y corte 8<.

Ejecución del Proyecto

Para ejecutar un archivo de prueba .bz con el intérprete principal:

python main.py programa.bz
