import sys
import os
import subprocess
from antlr4 import *
from bazilioLexer import bazilioLexer
from bazilioParser import bazilioParser
from bazilioVisitor import bazilioVisitor

class BazilioInterpreter(bazilioVisitor):
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
                proc_name = proc.PROC_ID().getText() if hasattr(proc, 'PROC_ID') and proc.PROC_ID() else "Main"
                self.procs[proc_name] = proc
        
        if 'Main' not in self.procs and self.procs:
            main_proc = list(self.procs.values())[0]
            return self.visit(main_proc)
        elif 'Main' in self.procs:
            return self.visit(self.procs['Main'])
        return None

    def visitProcedimiento(self, ctx):
        bloque = ctx.bloque() if hasattr(ctx, 'bloque') else ctx
        if bloque is not None:
            instrucciones = bloque.instruccion() if hasattr(bloque, 'instruccion') else []
            if instrucciones:
                if not isinstance(instrucciones, list):
                    instrucciones = [instrucciones]
                for stmt in instrucciones:
                    self.visit(stmt)

    # Método genérico para instrucciones (captura TOCA sin depender de etiquetas)
    def visitInstruccion(self, ctx):
        texto_instruccion = ctx.getText().upper()
        
        # Si la instrucción es de reproducción (contiene TOCA)
        if "TOCA" in texto_instruccion or (hasattr(ctx, 'TOCA') and ctx.TOCA() is not None):
            exprs = ctx.expr() if hasattr(ctx, 'expr') else None
            if exprs:
                if isinstance(exprs, list):
                    for e in exprs:
                        val = self.visit(e)
                        if val is not None:
                            self.notas_tocadas.append(val)
                else:
                    val = self.visit(exprs)
                    if val is not None:
                        self.notas_tocadas.append(val)
            return
        
        # Si es asignación
        elif hasattr(ctx, 'VAR') and ctx.VAR() is not None and hasattr(ctx, 'ASIGN'):
            var_name = ctx.VAR().getText()
            val = self.visit(ctx.expr())
            self.set_var(var_name, val)
            return

        return self.visitChildren(ctx)

    # Método genérico para expresiones (captura notas, enteros y variables)
    def visitExpr(self, ctx):
        # Si es una nota musical
        if hasattr(ctx, 'NOTA') and ctx.NOTA() is not None:
            text = ctx.NOTA().getText()
            base = text[0].upper()
            octava = int(text[1]) if len(text) > 1 else 4
            return (octava * 7) + self.NOTE_MAP.get(base, 0) - 5
        
        # Si es un número entero
        elif hasattr(ctx, 'ENTERO') and ctx.ENTERO() is not None:
            return int(ctx.ENTERO().getText())
        
        # Si es una variable
        elif hasattr(ctx, 'VAR') and ctx.VAR() is not None:
            return self.get_var(ctx.VAR().getText())
        
        # Operaciones matemáticas básicas
        elif hasattr(ctx, 'op') and ctx.op is not None:
            left = self.visit(ctx.left) if hasattr(ctx, 'left') else 0
            right = self.visit(ctx.right) if hasattr(ctx, 'right') else 0
            op_type = ctx.op.type
            if hasattr(bazilioParser, 'MAS') and op_type == bazilioParser.MAS: return left + right
            if hasattr(bazilioParser, 'MENOS') and op_type == bazilioParser.MENOS: return left - right
            if hasattr(bazilioParser, 'POR') and op_type == bazilioParser.POR: return left * right
            if hasattr(bazilioParser, 'ENTRE') and op_type == bazilioParser.ENTRE: return left // right if right != 0 else 0
            return left + right

        return self.visitChildren(ctx)

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