# Generated from bazilio.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .bazilioParser import bazilioParser
else:
    from bazilioParser import bazilioParser

# This class defines a complete listener for a parse tree produced by bazilioParser.
class bazilioListener(ParseTreeListener):

    # Enter a parse tree produced by bazilioParser#programa.
    def enterPrograma(self, ctx:bazilioParser.ProgramaContext):
        pass

    # Exit a parse tree produced by bazilioParser#programa.
    def exitPrograma(self, ctx:bazilioParser.ProgramaContext):
        pass


    # Enter a parse tree produced by bazilioParser#procedimiento.
    def enterProcedimiento(self, ctx:bazilioParser.ProcedimientoContext):
        pass

    # Exit a parse tree produced by bazilioParser#procedimiento.
    def exitProcedimiento(self, ctx:bazilioParser.ProcedimientoContext):
        pass


    # Enter a parse tree produced by bazilioParser#bloque.
    def enterBloque(self, ctx:bazilioParser.BloqueContext):
        pass

    # Exit a parse tree produced by bazilioParser#bloque.
    def exitBloque(self, ctx:bazilioParser.BloqueContext):
        pass


    # Enter a parse tree produced by bazilioParser#Asignacion.
    def enterAsignacion(self, ctx:bazilioParser.AsignacionContext):
        pass

    # Exit a parse tree produced by bazilioParser#Asignacion.
    def exitAsignacion(self, ctx:bazilioParser.AsignacionContext):
        pass


    # Enter a parse tree produced by bazilioParser#Lectura.
    def enterLectura(self, ctx:bazilioParser.LecturaContext):
        pass

    # Exit a parse tree produced by bazilioParser#Lectura.
    def exitLectura(self, ctx:bazilioParser.LecturaContext):
        pass


    # Enter a parse tree produced by bazilioParser#Escritura.
    def enterEscritura(self, ctx:bazilioParser.EscrituraContext):
        pass

    # Exit a parse tree produced by bazilioParser#Escritura.
    def exitEscritura(self, ctx:bazilioParser.EscrituraContext):
        pass


    # Enter a parse tree produced by bazilioParser#Reproduccion.
    def enterReproduccion(self, ctx:bazilioParser.ReproduccionContext):
        pass

    # Exit a parse tree produced by bazilioParser#Reproduccion.
    def exitReproduccion(self, ctx:bazilioParser.ReproduccionContext):
        pass


    # Enter a parse tree produced by bazilioParser#Invocacion.
    def enterInvocacion(self, ctx:bazilioParser.InvocacionContext):
        pass

    # Exit a parse tree produced by bazilioParser#Invocacion.
    def exitInvocacion(self, ctx:bazilioParser.InvocacionContext):
        pass


    # Enter a parse tree produced by bazilioParser#Condicional.
    def enterCondicional(self, ctx:bazilioParser.CondicionalContext):
        pass

    # Exit a parse tree produced by bazilioParser#Condicional.
    def exitCondicional(self, ctx:bazilioParser.CondicionalContext):
        pass


    # Enter a parse tree produced by bazilioParser#Iteracion.
    def enterIteracion(self, ctx:bazilioParser.IteracionContext):
        pass

    # Exit a parse tree produced by bazilioParser#Iteracion.
    def exitIteracion(self, ctx:bazilioParser.IteracionContext):
        pass


    # Enter a parse tree produced by bazilioParser#Agregado.
    def enterAgregado(self, ctx:bazilioParser.AgregadoContext):
        pass

    # Exit a parse tree produced by bazilioParser#Agregado.
    def exitAgregado(self, ctx:bazilioParser.AgregadoContext):
        pass


    # Enter a parse tree produced by bazilioParser#Corte.
    def enterCorte(self, ctx:bazilioParser.CorteContext):
        pass

    # Exit a parse tree produced by bazilioParser#Corte.
    def exitCorte(self, ctx:bazilioParser.CorteContext):
        pass


    # Enter a parse tree produced by bazilioParser#Indice.
    def enterIndice(self, ctx:bazilioParser.IndiceContext):
        pass

    # Exit a parse tree produced by bazilioParser#Indice.
    def exitIndice(self, ctx:bazilioParser.IndiceContext):
        pass


    # Enter a parse tree produced by bazilioParser#Lista.
    def enterLista(self, ctx:bazilioParser.ListaContext):
        pass

    # Exit a parse tree produced by bazilioParser#Lista.
    def exitLista(self, ctx:bazilioParser.ListaContext):
        pass


    # Enter a parse tree produced by bazilioParser#Variable.
    def enterVariable(self, ctx:bazilioParser.VariableContext):
        pass

    # Exit a parse tree produced by bazilioParser#Variable.
    def exitVariable(self, ctx:bazilioParser.VariableContext):
        pass


    # Enter a parse tree produced by bazilioParser#Relacional.
    def enterRelacional(self, ctx:bazilioParser.RelacionalContext):
        pass

    # Exit a parse tree produced by bazilioParser#Relacional.
    def exitRelacional(self, ctx:bazilioParser.RelacionalContext):
        pass


    # Enter a parse tree produced by bazilioParser#Entero.
    def enterEntero(self, ctx:bazilioParser.EnteroContext):
        pass

    # Exit a parse tree produced by bazilioParser#Entero.
    def exitEntero(self, ctx:bazilioParser.EnteroContext):
        pass


    # Enter a parse tree produced by bazilioParser#MulDiv.
    def enterMulDiv(self, ctx:bazilioParser.MulDivContext):
        pass

    # Exit a parse tree produced by bazilioParser#MulDiv.
    def exitMulDiv(self, ctx:bazilioParser.MulDivContext):
        pass


    # Enter a parse tree produced by bazilioParser#Parentesis.
    def enterParentesis(self, ctx:bazilioParser.ParentesisContext):
        pass

    # Exit a parse tree produced by bazilioParser#Parentesis.
    def exitParentesis(self, ctx:bazilioParser.ParentesisContext):
        pass


    # Enter a parse tree produced by bazilioParser#Longitud.
    def enterLongitud(self, ctx:bazilioParser.LongitudContext):
        pass

    # Exit a parse tree produced by bazilioParser#Longitud.
    def exitLongitud(self, ctx:bazilioParser.LongitudContext):
        pass


    # Enter a parse tree produced by bazilioParser#Nota.
    def enterNota(self, ctx:bazilioParser.NotaContext):
        pass

    # Exit a parse tree produced by bazilioParser#Nota.
    def exitNota(self, ctx:bazilioParser.NotaContext):
        pass


    # Enter a parse tree produced by bazilioParser#Igualdad.
    def enterIgualdad(self, ctx:bazilioParser.IgualdadContext):
        pass

    # Exit a parse tree produced by bazilioParser#Igualdad.
    def exitIgualdad(self, ctx:bazilioParser.IgualdadContext):
        pass


    # Enter a parse tree produced by bazilioParser#SumaResta.
    def enterSumaResta(self, ctx:bazilioParser.SumaRestaContext):
        pass

    # Exit a parse tree produced by bazilioParser#SumaResta.
    def exitSumaResta(self, ctx:bazilioParser.SumaRestaContext):
        pass



del bazilioParser