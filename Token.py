from TokenType import TokenType

class Token:
    def __init__(self, tipo : TokenType, valor : str):
        self.tipo = tipo
        self.valor = valor
    
    def __str__(self):
        return self.valor