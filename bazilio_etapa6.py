import os
import re
import shutil
import subprocess
import sys
import threading

from antlr4 import CommonTokenStream, FileStream
from antlr4.error.ErrorListener import ErrorListener

from bazilioLexer import bazilioLexer
from bazilioParser import bazilioParser
from bazilioVisitor import bazilioVisitor


class Errorbazilio(Exception):
    """Error de sintaxis o de ejecución de un programa Bazilio."""


class _ListenerErrores(ErrorListener):
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        raise Errorbazilio(
            f"Error de sintaxis en la línea {line}, columna {column}: {msg}")


def parsear(flujo):
    lexer = bazilioLexer(flujo)
    lexer.removeErrorListeners()
    lexer.addErrorListener(_ListenerErrores())
    parser = bazilioParser(CommonTokenStream(lexer))
    parser.removeErrorListeners()
    parser.addErrorListener(_ListenerErrores())
    return parser.programa()


def _div_c(a, b):
    """División entera con truncamiento hacia cero, como en C."""
    q = abs(a) // abs(b)
    return q if (a < 0) == (b < 0) else -q


# Las teclas blancas del piano: A0 = 0, B0 = 1, C1 = 2 ... C8 = 51
NOTA_MIN, NOTA_MAX = 0, 51
_POSICION = {"C": 0, "D": 1, "E": 2, "F": 3, "G": 4, "A": 5, "B": 6}


def valor_nota(texto):
    """'C4' -> 23, 'C' -> 23 (Do central), 'A0' -> 0, 'C8' -> 51."""
    letra = texto[0]
    octava = int(texto[1]) if len(texto) == 2 else 4
    if octava == 0:
        if letra not in "AB":
            raise Errorbazilio(f"La nota {texto} no existe en el piano (la octava 0 solo tiene A0 y B0).")
        return 0 if letra == "A" else 1
    valor = 2 + 7 * (octava - 1) + _POSICION[letra]
    if valor > NOTA_MAX:
        raise Errorbazilio(f"La nota {texto} no existe en el piano (la última es C8).")
    return valor


class Interprete(bazilioVisitor):
    def __init__(self, entrada=None, salida=None):
        self.procedimientos = {}      # nombre -> (parámetros, bloque)
        self.marcos = []              # pila de variables: un diccionario por llamada
        self.partitura = []           # valores de las notas tocadas, en orden
        self._entrada = entrada if entrada is not None else sys.stdin
        self._tokens_entrada = []
        self._salida = salida if salida is not None else print

    @property
    def _vars(self):
        return self.marcos[-1]

    def cargar(self, arbol):
        for proc in arbol.procedimiento():
            nombre = proc.PROC_ID().getText()
            params = [v.getText() for v in proc.VAR()]
            if nombre in self.procedimientos:
                raise Errorbazilio(f"El procedimiento {nombre} está definido más de una vez.")
            if len(set(params)) != len(params):
                raise Errorbazilio(f"El procedimiento {nombre} repite nombres de parámetros formales.")
            self.procedimientos[nombre] = (params, proc.bloque())

    def ejecutar(self, inicio="Main"):
        self._llamar(inicio, [])

    def _llamar(self, nombre, valores):
        if nombre not in self.procedimientos:
            raise Errorbazilio(f"Se llamó al procedimiento {nombre}, que no está definido.")
        params, bloque = self.procedimientos[nombre]
        if len(params) != len(valores):
            raise Errorbazilio(f"{nombre} espera {len(params)} parámetro(s) y recibió {len(valores)}.")
        self.marcos.append(dict(zip(params, valores)))
        try:
            self.visit(bloque)
        finally:
            self.marcos.pop()
import sys
import os
import subprocess
from antlr4 import *
from BazilioLexer import BazilioLexer
from BazilioParser import BazilioParser
from BazilioVisitor import BazilioVisitor

class BazilioInterpreter(BazilioVisitor):
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
        return left + right if ctx.op.type == BazilioParser.PLUS else left - right

    def visitExprOpMul(self, ctx):
        left = self.visit(ctx.left)
        right = self.visit(ctx.right)
        op = ctx.op.type
        if op == BazilioParser.MULT: 
            return left * right
        elif op == BazilioParser.DIV: 
            return left // right if right != 0 else 0
        elif op == BazilioParser.MOD: 
            return left % right if right != 0 else 0
        return 0

    def visitExprOpRel(self, ctx):
        left = self.visit(ctx.left)
        right = self.visit(ctx.right)
        op = ctx.op.type
        if op == BazilioParser.LTE: return 1 if left <= right else 0
        if op == BazilioParser.GTE: return 1 if left >= right else 0
        if op == BazilioParser.LT:  return 1 if left < right else 0
        if op == BazilioParser.GT:  return 1 if left > right else 0
        if op == BazilioParser.EQ:  return 1 if left == right else 0
        if op == BazilioParser.NEQ: return 1 if left != right else 0
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
    lexer = BazilioLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = BazilioParser(stream)
    tree = parser.program()
    
    interpreter = BazilioInterpreter()
    interpreter.visit(tree)
    
    if interpreter.notas_tocadas:
        generar_archivos(base_name, interpreter.notas_tocadas)
    def visitBloque(self, ctx):
        for instruccion in ctx.instruccion():
            self.visit(instruccion)

    def visitAsignacion(self, ctx):
        valor = self.visit(ctx.expr())
        if isinstance(valor, list):
            valor = list(valor)
        self._vars[ctx.VAR().getText()] = valor

    def visitLectura(self, ctx):
        self._vars[ctx.VAR().getText()] = self._leer_entero()

    def visitEscritura(self, ctx):
        partes = []
        for hijo in list(ctx.getChildren())[1:]:
            if hasattr(hijo, "symbol"):
                partes.append(hijo.getText()[1:-1])
            else:
                partes.append(self._formatear(self.visit(hijo)))
        self._salida(" ".join(partes))

    def visitReproduccion(self, ctx):
        valor = self.visit(ctx.expr())
        for nota in (valor if isinstance(valor, list) else [valor]):
            nota_a_lilypond(nota)         # valida que esté en el rango del piano
            self.partitura.append(nota)

    def visitInvocacion(self, ctx):
        valores = [self.visit(e) for e in ctx.expr()]
        self._llamar(ctx.PROC_ID().getText(), valores)

    def visitCondicional(self, ctx):
        bloques = ctx.bloque()
        if self._verdadero(self.visit(ctx.expr())):
            self.visit(bloques[0])
        elif len(bloques) > 1:
            self.visit(bloques[1])

    def visitIteracion(self, ctx):
        while self._verdadero(self.visit(ctx.expr())):
            self.visit(ctx.bloque())

    def visitAgregado(self, ctx):
        nombre = ctx.VAR().getText()
        lista = self._vars.get(nombre, 0)
        if not isinstance(lista, list):
            raise Errorbazilio(f"{nombre} no es una lista: no se puede usar << con ella.")
        valor = self.visit(ctx.expr())
        if isinstance(valor, list):
            raise Errorbazilio("Las listas solo pueden contener enteros o notas.")
        lista.append(valor)

    def visitCorte(self, ctx):
        nombre = ctx.VAR().getText()
        lista = self._vars.get(nombre, 0)
        if not isinstance(lista, list):
            raise Errorbazilio(f"{nombre} no es una lista: no se puede usar 8< con ella.")
        i = self._entero(self.visit(ctx.expr()))
        self._comprobar_indice(nombre, lista, i)
        del lista[i - 1]

    def visitIndice(self, ctx):
        base = self.visit(ctx.expr(0))
        if not isinstance(base, list):
            raise Errorbazilio("Solo se puede consultar un índice en una lista.")
        i = self._entero(self.visit(ctx.expr(1)))
        self._comprobar_indice(ctx.expr(0).getText(), base, i)
        return base[i - 1]

    def visitLongitud(self, ctx):
        valor = self.visit(ctx.expr())
        if not isinstance(valor, list):
            raise Errorbazilio("El operador # solo se puede aplicar a una lista.")
        return len(valor)

    def visitMulDiv(self, ctx):
        a, b = self._operandos(ctx)
        op = ctx.op.text
        if op == "*":
            return a * b
        if b == 0:
            raise Errorbazilio("División por cero.")
        q = _div_c(a, b)
        return q if op == "/" else a - b * q

    def visitSumaResta(self, ctx):
        a, b = self._operandos(ctx)
        return a + b if ctx.op.text == "+" else a - b

    def visitRelacional(self, ctx):
        a, b = self._operandos(ctx)
        return int({"<": a < b, ">": a > b, "<=": a <= b, ">=": a >= b}[ctx.op.text])

    def visitIgualdad(self, ctx):
        a, b = self.visit(ctx.expr(0)), self.visit(ctx.expr(1))
        return int((a == b) if ctx.op.text == "=" else (a != b))

    def visitParentesis(self, ctx):
        return self.visit(ctx.expr())

    def visitLista(self, ctx):
        elementos = [self.visit(e) for e in ctx.expr()]
        if any(isinstance(e, list) for e in elementos):
            raise Errorbazilio("Las listas solo pueden contener enteros o notas.")
        return elementos

    def visitEntero(self, ctx):
        return int(ctx.getText())

    def visitNota(self, ctx):
        return valor_nota(ctx.getText())

    def visitVariable(self, ctx):
        return self._vars.get(ctx.getText(), 0)

    @staticmethod
    def _entero(valor):
        if isinstance(valor, list):
            raise Errorbazilio("Se esperaba un entero y se encontró una lista.")
        return valor

    def _operandos(self, ctx):
        izquierda = self._entero(self.visit(ctx.expr(0)))
        derecha = self._entero(self.visit(ctx.expr(1)))
        return izquierda, derecha

    @staticmethod
    def _verdadero(valor):
        if isinstance(valor, list):
            raise Errorbazilio("Una condición debe ser un entero (0 es falso, otro valor es verdadero).")
        return valor != 0

    @staticmethod
    def _formatear(valor):
        if isinstance(valor, list):
            return "[" + " ".join(str(x) for x in valor) + "]"
        return str(valor)

    @staticmethod
    def _comprobar_indice(nombre, lista, i):
        n = len(lista)
        if not 1 <= i <= n:
            raise Errorbazilio(f"Índice {i} inexistente en {nombre} (la lista tiene {n} elemento(s); los índices van de 1 a {n}).")

    def _leer_entero(self):
        while not self._tokens_entrada:
            linea = self._entrada.readline()
            if linea == "":
                raise Errorbazilio("Se esperaba un entero en la entrada, pero ya no hay más datos.")
            self._tokens_entrada = linea.split()
        token = self._tokens_entrada.pop(0)
        try:
            return int(token)
        except ValueError:
            raise Errorbazilio(f"Se esperaba un entero en la entrada y se leyó «{token}».")


def nota_a_lilypond(valor):
    """Valor 0..51 -> LilyPond absoluto, duración de negra (p. ej. c'4)."""
    if not NOTA_MIN <= valor <= NOTA_MAX:
        raise Errorbazilio(f"Se intentó tocar el valor {valor}, fuera del rango del piano (0 a 51).")
    if valor < 2:
        letra, octava = ("a", "b")[valor], 0
    else:
        k = valor - 2
        octava, letra = 1 + k // 7, "cdefgab"[k % 7]
    marcas = "'" * (octava - 3) if octava > 3 else "," * (3 - octava)
    return f"{letra}{marcas}4"


def version_lilypond():
    try:
        salida = subprocess.run(["lilypond", "--version"], capture_output=True, text=True).stdout
        return re.search(r"(\d+\.\d+\.\d+)", salida).group(1)
    except (OSError, AttributeError):
        return "2.20.0"


def texto_lilypond(partitura, tempo=120):
    notas = [nota_a_lilypond(v) for v in partitura]
    renglones = [" ".join(notas[i:i + 8]) for i in range(0, len(notas), 8)]
    cuerpo = "\n".join("      " + r for r in renglones)
    return (f'\\version "{version_lilypond()}"\n'
            "\\score {\n"
            "  \\absolute {\n"
            f"    \\tempo 4 = {tempo}\n"
            f"{cuerpo}\n"
            "  }\n"
            "  \\layout { }\n"
            "  \\midi { }\n"
            "}\n")


def generar_salida(partitura, base, solo_ly=False, aviso=print):
    """Escribe base.ly y convierte con las herramientas externas que haya instaladas."""
    ruta_ly = base + ".ly"
    with open(ruta_ly, "w", encoding="utf-8") as f:
        f.write(texto_lilypond(partitura))
    generados = [ruta_ly]
    if solo_ly:
        return generados

    def correr(cmd, descripcion):
        if shutil.which(cmd[0]) is None:
            aviso(f"Aviso: no se encontró «{cmd[0]}», no se generó {descripcion}.")
            return False
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            detalle = r.stderr.strip()[-400:]
            aviso(f"Aviso: falló {cmd[0]} al generar {descripcion}:\n{detalle}")
            return False
        return True

    pasos = [
        (["lilypond", "-o", base, ruta_ly], "el PDF y el MIDI", [".pdf", ".midi"]),
        (["timidity", "-Ow", "-o", base + ".wav", base + ".midi"], "el WAV", [".wav"]),
        (["ffmpeg", "-y", "-loglevel", "error", "-i", base + ".wav",
          "-codec:a", "libmp3lame", "-qscale:a", "2", base + ".mp3"], "el MP3", [".mp3"]),
    ]
    for cmd, descripcion, extensiones in pasos:
        if not correr(cmd, descripcion):
            break
        generados += [base + e for e in extensiones]
    return generados


def principal(argv):
    solo_ly = "--solo-ly" in argv
    args = [a for a in argv[1:] if not a.startswith("--")]
    if not args:
        print("Uso: python3 bazilio_etapa6.py programa.bzl [Procedimiento] [--solo-ly]")
        return 2
    ruta = args[0]
    inicio = args[1] if len(args) > 1 else "Main"
    try:
        arbol = parsear(FileStream(ruta, encoding="utf-8"))
        interprete = Interprete()
        interprete.cargar(arbol)
        interprete.ejecutar(inicio)
        if interprete.partitura:
            base = os.path.splitext(ruta)[0]
            archivos = generar_salida(interprete.partitura, base, solo_ly=solo_ly)
            nombres = ", ".join(os.path.basename(a) for a in archivos)
            print("Archivos generados: " + nombres, file=sys.stderr)
    except Errorbazilio as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except BrokenPipeError:
        return 0
    return 0


if __name__ == "__main__":
    sys.setrecursionlimit(200000)
    threading.stack_size(512 * 1024 * 1024)            # para recursividad profunda
    resultado = []
    hilo = threading.Thread(target=lambda: resultado.append(principal(sys.argv)))
    hilo.start()
    hilo.join()
    sys.exit(resultado[0] if resultado else 1)