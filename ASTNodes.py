from enum import Enum
from Token import Token

class OperatorType(Enum):
    OR = 0
    AND = 1
    IMPLICATION = 2

class ASTNode:
    pass

class PropNode(ASTNode):
    def __init__(self, token : Token):
        self.tokens: list[Token] = []
        self.addToken(token)
        
    def addToken(self,token : Token):
        self.tokens.append(token)
        
    def __str__(self):
        return ' '.join([token.valor for token in self.tokens])
        

class NegNode(ASTNode):
    def __init__(self, child : ASTNode):
        self.child = child

class OperatorNode(ASTNode):
    def __init__(self, left : ASTNode, operator : OperatorType, right : ASTNode):
        self.left = left
        self.operator = operator
        self.right = right