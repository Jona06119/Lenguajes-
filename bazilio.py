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

    def visitPrograma(self, ctx):
        procs = ctx.procedimiento()
        if procs:
            if not isinstance(procs, list):
                procs = [procs]
            for proc in procs:
                proc_name = proc.PROC_ID().getText()
                self.procs[proc_name] = proc
        
        if 'Main' not in self.procs:
            # Si no encontró Main por nombre, toma el primero por defecto
            if self.procs:
                main_proc = list(self.procs.values())[0]
                return self.visit(main_proc)
            return
            
        return self.visit(self.procs['Main'])

    def visitProcedimiento(self, ctx):
        bloque = ctx.bloque() if hasattr(ctx, 'bloque') else ctx
        if bloque is not None:
            instrucciones = bloque.instruccion() if hasattr(bloque, 'instruccion') else []
            if instrucciones:
                if not isinstance(instrucciones, list):
                    instrucciones = [instrucciones]
                for stmt in instrucciones:
                    self.visit(stmt)

    def visitAsignacion(self, ctx):
        var_name = ctx.VAR().getText()
        val = self.visit(ctx.expr())
        self.set_var(var_name, val)

    def visitEscritura(self, ctx):
        exprs = ctx.expr() if hasattr(ctx, 'expr') else []
        if exprs:
            if not isinstance(exprs, list):
                exprs = [exprs]
            vals = [str(self.visit(e)) for e in exprs]
            print(" ".join(vals))

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

    def visitReproduccion(self, ctx):
        val = self.visit(ctx.expr())
        if val is not None:
            self.notas_tocadas.append(val)

    def visitIteracion(self, ctx):
        while self.visit(ctx.expr()):
            bloque = ctx.bloque() if hasattr(ctx, 'bloque') else ctx
            if bloque is not None:
                instrucciones = bloque.instruccion() if hasattr(bloque, 'instruccion') else []
                if instrucciones:
                    if not isinstance(instrucciones, list):
                        instrucciones = [instrucciones]
                    for stmt in instrucciones:
                        self.visit(stmt)

    def visitAgregado(self, ctx):
        var_name = ctx.VAR().getText()
        val = self.visit(ctx.expr())
        lst = self.get_var(var_name)
        if isinstance(lst, list):
            lst.append(val)
        else:
            self.set_var(var_name, [val])

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

    def visitEntero(self, ctx):
        return int(ctx.ENTERO().getText())

    def visitNota(self, ctx):
        text = ctx.NOTA().getText()
        base = text[0].upper()
        octava = int(text[1]) if len(text) > 1 else 4
        return (octava * 7) + self.NOTE_MAP.get(base, 0) - 5

    def visitVariable(self, ctx):
        return self.get_var(ctx.VAR().getText())

    def visitLista(self, ctx):
        exprs = ctx.expr() if hasattr(ctx, 'expr') else []
        if exprs:
            if not isinstance(exprs, list):
                exprs = [exprs]
            return [self.visit(e) for e in exprs]
        return []

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
    
    subprocess.run(["lilypond", ly_filename], capture_output=True, text=True)
    
    pdf_filename = f"{base_name}.pdf"
    midi_filename = f"{base_name}.midi"
    wav_filename = f"{base_name}.wav"
    mp3_filename = f"{base_name}.mp3"
    
    if os.path.exists(midi_filename):
        res_timidity = subprocess.run(["timidity", midi_filename, "-Ow", "-o", wav_filename], capture_output=True)
        if res_timidity.returncode == 0:
            subprocess.run(["ffmpeg", "-y", "-i", wav_filename, mp3_filename], capture_output=True)