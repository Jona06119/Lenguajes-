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
        self.call_stack = [{}]  # Pila de entornos de variables locales por ámbito
        self.notas_tocadas = []

    # Mapeo oficial de notas musicales base (Octava 4)[cite: 1, 2]
    NOTE_MAP = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5, 'G': 6}

    def get_var(self, name):
        return self.call_stack[-1].get(name, 0)

    def set_var(self, name, val):
        self.call_stack[-1][name] = val

    def visitProgram(self, ctx):
        for proc in ctx.procDef():
            proc_name = proc.PROC_ID().getText()
            self.procs[proc_name] = proc
        
        if 'Main' not in self.procs:
            print("Error: No se definió el procedimiento 'Main'")
            sys.exit(1)
            
        return self.visit(self.procs['Main'])

    def visitStmtAsigna(self, ctx):
        var_name = ctx.VAR().getText()
        val = self.visit(ctx.expr())
        self.set_var(var_name, val)

    def visitStmtEscribe(self, ctx):
        vals = [str(self.visit(e)) for e in ctx.exprList().expr()]
        print(" ".join(vals))

    def visitStmtLee(self, ctx):
        var_name = ctx.VAR().getText()
        val = input(f"<?> {var_name}: ")
        # Conversión automática a entero si es numérico, de lo contrario texto
        try:
            val_conv = int(val)
        except ValueError:
            try:
                val_conv = float(val)
            except ValueError:
                val_conv = val
        self.set_var(var_name, val_conv)

    def visitStmtToca(self, ctx):
        val = self.visit(ctx.expr())
        self.notas_tocadas.append(val)

    def visitStmtMientras(self, ctx):
        while self.visit(ctx.expr()):
            for stmt in ctx.stmt():
                self.visit(stmt)

    def visitStmtAgrega(self, ctx):
        var_name = ctx.VAR().getText()
        val = self.visit(ctx.expr())
        lst = self.get_var(var_name)
        if isinstance(lst, list):
            lst.append(val)
        else:
            self.set_var(var_name, [val])

    def visitExprOpAdd(self, ctx):
        left = self.visit(ctx.left)
        right = self.visit(ctx.right)
        return left + right if ctx.op.type == bazilioParser.PLUS else left - right

    def visitExprOpMul(self, ctx):
        left = self.visit(ctx.left)
        right = self.visit(ctx.right)
        op = ctx.op.type
        if op == bazilioParser.MULT: 
            return left * right
        elif op == bazilioParser.DIV: 
            return left // right if right != 0 else 0
        elif op == bazilioParser.MOD: 
            return left % right if right != 0 else 0
        return 0

    def visitExprOpRel(self, ctx):
        left = self.visit(ctx.left)
        right = self.visit(ctx.right)
        op = ctx.op.type
        if op == bazilioParser.LTE: return 1 if left <= right else 0
        if op == bazilioParser.GTE: return 1 if left >= right else 0
        if op == bazilioParser.LT:  return 1 if left < right else 0
        if op == bazilioParser.GT:  return 1 if left > right else 0
        if op == bazilioParser.EQ:  return 1 if left == right else 0
        if op == bazilioParser.NEQ: return 1 if left != right else 0
        return 0

    def visitExprEntero(self, ctx):
        return int(ctx.ENTERO().getText())

    def visitExprTexto(self, ctx):
        return ctx.TEXTO().getText().strip('"“”')

    def visitExprVar(self, ctx):
        return self.get_var(ctx.VAR().getText())

    def visitExprNota(self, ctx):
        text = ctx.NOTA().getText()
        base = text[0]
        octava = int(text[1]) if len(text) > 1 else 4
        return (octava * 7) + self.NOTE_MAP[base] - 5

    def visitExprLista(self, ctx):
        return [self.visit(e) for e in ctx.expr()]

    def visitExprLong(self, ctx):
        lst = self.get_var(ctx.VAR().getText())
        return len(lst) if isinstance(lst, list) else 0

    def visitExprIndex(self, ctx):
        lst = self.get_var(ctx.VAR().getText())
        idx = self.visit(ctx.expr())
        # Las listas en Bazilio manejan índices basados en 1[cite: 1, 2]
        if isinstance(lst, list) and 1 <= idx <= len(lst):
            return lst[idx - 1]
        else:
            print(f"Error: Índice {idx} inexistente en l (la lista tiene {len(lst) if isinstance(lst, list) else 0} elemento(s); los índices van de 1 a {len(lst) if isinstance(lst, list) else 0}).")
            sys.exit(1)

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
    
    print(f"Generado archivo fuente: {ly_filename}")
    
    # Invocación de LilyPond para compilar y generar la partitura en PDF y el archivo MIDI[cite: 1, 2]
    print("Compilando partitura PDF con LilyPond...")
    res_lily = subprocess.run(["lilypond", ly_filename], capture_output=True, text=True)
    
    pdf_filename = f"{base_name}.pdf"
    midi_filename = f"{base_name}.midi"
    
    if os.path.exists(pdf_filename):
        print(f"¡Partitura guardada con éxito en PDF!: {pdf_filename}")
    else:
        print("Aviso de compilación LilyPond:", res_lily.stderr)
        
    wav_filename = f"{base_name}.wav"
    mp3_filename = f"{base_name}.mp3"
    
    # Generación opcional de WAV con TiMidity++ y MP3 con ffmpeg[cite: 1, 2]
    if os.path.exists(midi_filename):
        res_timidity = subprocess.run(["timidity", midi_filename, "-Ow", "-o", wav_filename], capture_output=True)
        if res_timidity.returncode == 0:
            subprocess.run(["ffmpeg", "-y", "-i", wav_filename, mp3_filename], capture_output=True)
            print(f"Audio generado y convertido a MP3: {mp3_filename}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 bazilio.py <archivo.bzl>")
        sys.exit(1)
        
    bzl_file = sys.argv[1]
    base_name = os.path.splitext(bzl_file)[0]
    
    input_stream = FileStream(bzl_file, encoding='utf-8')
    lexer = bazilioLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = bazilioParser(stream)
    tree = parser.programa()
    
    interpreter = bazilioInterpreter()
    interpreter.visit(tree)
    
    if interpreter.notas_tocadas:
        generar_archivos(base_name, interpreter.notas_tocadas)