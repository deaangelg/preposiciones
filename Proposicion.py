class Proposicion:
    def __init__(self, listaTokens):
        self.listaTokens = listaTokens
        self.posicion = 0
    def ObtenerFrase(self):
        return ' '.join(token.valor for token in self.listaTokens)