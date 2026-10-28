import sys

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


class Interprete(bazilioVisitor):
    def __init__(self, entrada=None, salida=None):
        self.marcos = [{}]            # pila de marcos (por ahora, uno solo)
        self._entrada = entrada if entrada is not None else sys.stdin
        self._tokens_entrada = []
        self._salida = salida if salida is not None else print

    @property
    def _vars(self):
        return self.marcos[-1]

    def ejecutar(self, arbol):
        for proc in arbol.procedimiento():
            if proc.PROC_ID().getText() == "Main":
                self.visit(proc.bloque())
                return
        raise Errorbazilio("El programa no tiene un procedimiento Main.")

    def visitBloque(self, ctx):
        for instruccion in ctx.instruccion():
            self.visit(instruccion)

    def visitAsignacion(self, ctx):
        self._vars[ctx.VAR().getText()] = self.visit(ctx.expr())

    def visitLectura(self, ctx):
        self._vars[ctx.VAR().getText()] = self._leer_entero()

    def visitEscritura(self, ctx):
        partes = []
        for hijo in list(ctx.getChildren())[1:]:               # el primero es <w>
            if hasattr(hijo, "symbol"):                        # es un TEXTO
                partes.append(hijo.getText()[1:-1])
            else:
                partes.append(self._formatear(self.visit(hijo)))
        self._salida(" ".join(partes))

    def visitEntero(self, ctx):
        return int(ctx.getText())

    def visitVariable(self, ctx):
        return self._vars.get(ctx.getText(), 0)                # sin valor todavía = 0

    def visitParentesis(self, ctx):
        return self.visit(ctx.expr())

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
    def _formatear(valor):
        if isinstance(valor, list):
            return "[" + " ".join(str(x) for x in valor) + "]"
        return str(valor)

    def _leer_entero(self):
        while not self._tokens_entrada:
            linea = self._entrada.readline()
            if linea == "":
                raise Errorbazilio(
                    "Se esperaba un entero en la entrada, pero ya no hay más datos.")
            self._tokens_entrada = linea.split()
        token = self._tokens_entrada.pop(0)
        try:
            return int(token)
        except ValueError:
            raise Errorbazilio(
                f"Se esperaba un entero en la entrada y se leyó «{token}».")


def principal(argv):
    if len(argv) < 2:
        print("Uso: python3 bazilio_etapa2.py programa.bzl")
        return 2
    try:
        arbol = parsear(FileStream(argv[1], encoding="utf-8"))
        Interprete().ejecutar(arbol)
    except Errorbazilio as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(principal(sys.argv))