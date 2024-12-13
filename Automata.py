from TokenType import TokenType
from Token import Token
from AutomataEstado import AutomataEstado
from ASTNodes import *

class Automata:
    def __init__(self):
        self.transiciones = {
            AutomataEstado.INICIO: {TokenType.SI: AutomataEstado.COND_1, TokenType.PALABRA: AutomataEstado.PROP, TokenType.NOT: AutomataEstado.NEG},
            AutomataEstado.NEG: {TokenType.PALABRA: AutomataEstado.PROP},
            AutomataEstado.PROP: {TokenType.O: AutomataEstado.COND_2, TokenType.Y: AutomataEstado.COND_2, TokenType.PALABRA: AutomataEstado.PROP, TokenType.EOL: AutomataEstado.FIN},
            AutomataEstado.COND_1: {TokenType.NOT: AutomataEstado.NEG_PA, TokenType.PALABRA: AutomataEstado.PROP_A},
            AutomataEstado.NEG_PA: {TokenType.PALABRA: AutomataEstado.PROP_A},
            AutomataEstado.PROP_A: {TokenType.PALABRA: AutomataEstado.PROP_A, TokenType.ENTONCES: AutomataEstado.COND_2},
            AutomataEstado.COND_2: {TokenType.NOT: AutomataEstado.NEG_PB, TokenType.PALABRA: AutomataEstado.PROP_B},
            AutomataEstado.NEG_PB: {TokenType.PALABRA: AutomataEstado.PROP_B},
            AutomataEstado.PROP_B: {TokenType.PALABRA: AutomataEstado.PROP_B, TokenType.EOL: AutomataEstado.FIN}
        }
        self.estadoActual = AutomataEstado.INICIO
        self.ast = None
        self.ultimo_nodo = None

    def transition(self, input_token: Token):
        if input_token.tipo in self.transiciones[self.estadoActual]:
            self.estadoActual = self.transiciones[self.estadoActual][input_token.tipo]
            self.build_ast(input_token)
        else:
            # No hay transicion, cambiar a error
            self.estadoActual = AutomataEstado.ERROR

    def build_ast(self, input_token : Token):
        if self.estadoActual in [AutomataEstado.PROP, AutomataEstado.PROP_A, AutomataEstado.PROP_B]:
            # Si el ultimo nodo es del tipo prop agregar la palabra al contenido
            if type(self.ultimo_nodo) == PropNode:
                self.ultimo_nodo.addToken(input_token)
            elif self.ultimo_nodo == None:
                # Sino crear un nuevo propNode
                self.ultimo_nodo = PropNode(input_token)
                self.ast = self.ultimo_nodo    
                
        elif self.estadoActual == AutomataEstado.NEG:
            self.ultimo_nodo = NegNode(self.ultimo_nodo)
            self.ast = self.ultimo_nodo
            
        elif self.estadoActual in [AutomataEstado.COND_1, AutomataEstado.COND_2]:
            if input_token.tipo == TokenType.O:
                operator = OperatorType.OR
            elif input_token.tipo == TokenType.Y:
                operator = OperatorType.AND
            elif input_token.tipo == TokenType.ENTONCES:
                operator = OperatorType.IMPLICATION
            
            self.ultimo_nodo = OperatorNode(self.ast, operator, None)
            self.ast = self.ultimo_nodo

    def is_accepting(self):
        return self.estadoActual == AutomataEstado.FIN

    def evaluar(self, listaTokens):
        for token in listaTokens:
            self.transition(token)
            if self.estadoActual == AutomataEstado.ERROR:
                return None
        return self.ast if self.is_accepting() else None