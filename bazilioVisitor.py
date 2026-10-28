# Generated from bazilio.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .bazilioParser import bazilioParser
else:
    from bazilioParser import bazilioParser

# This class defines a complete generic visitor for a parse tree produced by bazilioParser.

class bazilioVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by bazilioParser#programa.
    def visitPrograma(self, ctx:bazilioParser.ProgramaContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by bazilioParser#procedimiento.
    def visitProcedimiento(self, ctx:bazilioParser.ProcedimientoContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by bazilioParser#bloque.
    def visitBloque(self, ctx:bazilioParser.BloqueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by bazilioParser#Asignacion.
    def visitAsignacion(self, ctx:bazilioParser.AsignacionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by bazilioParser#Lectura.
    def visitLectura(self, ctx:bazilioParser.LecturaContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by bazilioParser#Escritura.
    def visitEscritura(self, ctx:bazilioParser.EscrituraContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by bazilioParser#Reproduccion.
    def visitReproduccion(self, ctx:bazilioParser.ReproduccionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by bazilioParser#Invocacion.
    def visitInvocacion(self, ctx:bazilioParser.InvocacionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by bazilioParser#Condicional.
    def visitCondicional(self, ctx:bazilioParser.CondicionalContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by bazilioParser#Iteracion.
    def visitIteracion(self, ctx:bazilioParser.IteracionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by bazilioParser#Agregado.
    def visitAgregado(self, ctx:bazilioParser.AgregadoContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by bazilioParser#Corte.
    def visitCorte(self, ctx:bazilioParser.CorteContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by bazilioParser#Indice.
    def visitIndice(self, ctx:bazilioParser.IndiceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by bazilioParser#Lista.
    def visitLista(self, ctx:bazilioParser.ListaContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by bazilioParser#Variable.
    def visitVariable(self, ctx:bazilioParser.VariableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by bazilioParser#Relacional.
    def visitRelacional(self, ctx:bazilioParser.RelacionalContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by bazilioParser#Entero.
    def visitEntero(self, ctx:bazilioParser.EnteroContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by bazilioParser#MulDiv.
    def visitMulDiv(self, ctx:bazilioParser.MulDivContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by bazilioParser#Parentesis.
    def visitParentesis(self, ctx:bazilioParser.ParentesisContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by bazilioParser#Longitud.
    def visitLongitud(self, ctx:bazilioParser.LongitudContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by bazilioParser#Nota.
    def visitNota(self, ctx:bazilioParser.NotaContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by bazilioParser#Igualdad.
    def visitIgualdad(self, ctx:bazilioParser.IgualdadContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by bazilioParser#SumaResta.
    def visitSumaResta(self, ctx:bazilioParser.SumaRestaContext):
        return self.visitChildren(ctx)



del bazilioParser