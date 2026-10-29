import sys
import os
import subprocess
import re
from antlr4 import *
from bazilioLexer import bazilioLexer
from bazilioParser import bazilioParser
from bazilioVisitor import bazilioVisitor

class bazilioInterpreter(bazilioVisitor):
    def __init__(self):
        self.notas_tocadas = []
        self.NOTE_MAP = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5, 'G': 6}

    def visit(self, tree):
        if tree is None:
            return
        
        # Recorrido recursivo universal por todo el árbol sintáctico
        if hasattr(tree, 'children') and tree.children:
            for child in tree.children:
                self.visit(child)
        
        # Extraer texto del nodo actual
        text = tree.getText() if hasattr(tree, 'getText') else ""
        
        # Detectar automáticamente cualquier nota musical (ej: C4, d4, f#4, etc.)
        if re.match(r'^[a-gA-G][#b]?[0-9]$', text):
            base = text[0].upper()
            # Buscar el dígito de la octava
            match_oct = re.search(r'[0-9]+', text)
            octava = int(match_oct.group()) if match_oct else 4
            
            val = (octava * 7) + self.NOTE_MAP.get(base, 0) - 5
            self.notas_tocadas.append(val)
            
        return super().visit(tree) if hasattr(super(), 'visit') else None

def num_a_lilypond(num):
    octava = (num + 5) // 7
    nota_idx = (num + 5) % 7
    nombres = ['c', 'd', 'e', 'f', 'g', 'a', 'b']
    nombre = nombres[nota_idx]
    
    if octava == 4:
        return nombre + "4"
    elif octava > 4:
        return nombre + ("'" * (octava - 4)) + "4"
    else:
        return nombre + ("," * (4 - octava)) + "4"

def generar_archivos(base_name, notas):
    ly_filename = f"{base_name}.ly"
    ly_code = "\\version \"2.24.3\"\n\\score {\n  \\relative c' {\n    \\tempo 4 = 120\n    "
    ly_code += " ".join([num_a_lilypond(n) for n in notas])
    ly_code += "\n  }\n  \\layout { }\n  \\midi { }\n}\n"
    
    with open(ly_filename, "w", encoding="utf-8") as f:
        f.write(ly_code)
    
    # 1. Generar PDF y MIDI con LilyPond
    subprocess.run(["lilypond", ly_filename], capture_output=True, text=True)
    
    pdf_filename = f"{base_name}.pdf"
    midi_filename = f"{base_name}.midi"
    wav_filename = f"{base_name}.wav"
    mp3_filename = f"{base_name}.mp3"
    
    # 2. Convertir MIDI a WAV usando TiMidity
    if os.path.exists(midi_filename):
        subprocess.run(["timidity", midi_filename, "-Ow", "-o", wav_filename], capture_output=True)
        
        # 3. Convertir WAV a MP3 con FFmpeg para asegurar compatibilidad total en el navegador
        if os.path.exists(wav_filename):
            subprocess.run(["ffmpeg", "-y", "-i", wav_filename, mp3_filename], capture_output=True)