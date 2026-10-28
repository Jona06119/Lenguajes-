import sys
import os
import subprocess
from antlr4 import *
from bazilioLexer import bazilioLexer
from bazilioParser import bazilioParser
from bazilioVisitor import bazilioVisitor

class bazilioInterpreter(bazilioVisitor):
    def __init__(self):
        self.procs = {}
        self.call_stack = [{}]
        self.notas_tocadas = []

    NOTE_MAP = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5, 'G': 6}

    def get_var(self, name):
        return self.call_stack[-1].get(name, 0)

    def set_var(self, name, val):
        self.call_stack[-1][name] = val

    # Método generado por la regla principal 'programa'
    def visitPrograma(self, ctx):
        for proc in ctx.procedimiento():
            proc_name = proc.PROC_ID().getText()
            self.procs[proc_name] = proc
        
        if 'Main' not in self.procs:
            print("Error: No se definió el procedimiento 'Main'")
            sys.exit(1)
            
        return self.visit(self.procs['Main'])

    def visitProcedimiento(self, ctx):
        for stmt in ctx.bloque().instruccion():
            self.visit(stmt)

    # Coincide con la etiqueta # Asignacion en bazilio.g4
    def visitAsignacion(self, ctx):
        var_name = ctx.VAR().getText()
        val = self.visit(ctx.expr())
        self.set_var(var_name, val)

    # Coincide con la etiqueta # Escritura en bazilio.g4
    def visitEscritura(self, ctx):
        vals = [str(self.visit(e)) for e in ctx.expr()]
        print(" ".join(vals))

    # Coincide con la etiqueta # Lectura en bazilio.g4
    def visitLectura(self, ctx):
        var_name = ctx.VAR().getText()
        val = input(f"<?> {var_name}: ")
        try:
            val_conv = int(val)
        except ValueError:
            try:
                val_conv = float(val)
            except ValueError:
                val_conv = val
        self.set_var(var_name, val_conv)

    # Coincide con la etiqueta # Reproduccion (TOCA expr) en bazilio.g4
    def visitReproduccion(self, ctx):
        val = self.visit(ctx.expr())
        if val is not None:
            self.notas_tocadas.append(val)

    # Coincide con la etiqueta # Iteracion en bazilio.g4
    def visitIteracion(self, ctx):
        while self.visit(ctx.exor()):
            for stmt in ctx.bloque().instruccion():
                self.visit(stmt)

    # Coincide con la etiqueta # Agregado en bazilio.g4
    def visitAgregado(self, ctx):
        var_name = ctx.VAR().getText()
        val = self.visit(ctx.expr())
        lst = self.get_var(var_name)
        if isinstance(lst, list):
            lst.append(val)
        else:
            self.set_var(var_name, [val])

    # Coincide con la etiqueta # SunaResta / MulDiv en bazilio.g4
    def visitSunaResta(self, ctx):
        left = self.visit(ctx.left)
        right = self.visit(ctx.right)
        return left + right if ctx.op.type == bazilioParser.MAS else left - right

    def visitMulDiv(self, ctx):
        left = self.visit(ctx.left)
        right = self.visit(ctx.right)
        op = ctx.op.type
        if op == bazilioParser.POR: return left * right
        elif op == bazilioParser.ENTRE: return left // right if right != 0 else 0
        elif op == bazilioParser.MODULO: return left % right if right != 0 else 0
        return 0

    def visitRelacional(self, ctx):
        left = self.visit(ctx.left)
        right = self.visit(ctx.right)
        op = ctx.op.type
        if op == bazilioParser.MENDRIGUAL: return 1 if left <= right else 0
        if op == bazilioParser.MAYDRIGUAL: return 1 if left >= right else 0
        if op == bazilioParser.MENDR:  return 1 if left < right else 0
        if op == bazilioParser.MAYDR:  return 1 if left > right else 0
        if op == bazilioParser.IGUAL:  return 1 if left == right else 0
        if op == bazilioParser.DISTINTO: return 1 if left != right else 0
        return 0

    # Coincide con la etiqueta # Entero en bazilio.g4
    def visitEntero(self, ctx):
        return int(ctx.ENTERO().getText())

    # Coincide con la etiqueta # Nota en bazilio.g4
    def visitNota(self, ctx):
        text = ctx.NOTA().getText()
        base = text[0].upper()
        octava = int(text[1]) if len(text) > 1 else 4
        return (octava * 7) + self.NOTE_MAP.get(base, 0) - 5

    # Coincide con la etiqueta # Variable en bazilio.g4
    def visitVariable(self, ctx):
        return self.get_var(ctx.VAR().getText())

    # Coincide con la etiqueta # Lista en bazilio.g4
    def visitLista(self, ctx):
        return [self.visit(e) for e in ctx.expr()]

    def visitLongitud(self, ctx):
        lst = self.get_var(ctx.VAR().getText())
        return len(lst) if isinstance(lst, list) else 0

    def visitIndice(self, ctx):
        lst = self.get_var(ctx.VAR().getText())
        idx = self.visit(ctx.expr())
        if isinstance(lst, list) and 1 <= idx <= len(lst):
            return lst[idx - 1]
        else:
            return 0

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
    
    res_lily = subprocess.run(["lilypond", ly_filename], capture_output=True, text=True)
    
    pdf_filename = f"{base_name}.pdf"
    midi_filename = f"{base_name}.midi"
    wav_filename = f"{base_name}.wav"
    mp3_filename = f"{base_name}.mp3"
    
    if os.path.exists(midi_filename):
        res_timidity = subprocess.run(["timidity", midi_filename, "-Ow", "-o", wav_filename], capture_output=True)
        if res_timidity.returncode == 0:
            subprocess.run(["ffmpeg", "-y", "-i", wav_filename, mp3_filename], capture_output=True)