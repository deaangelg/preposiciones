from Automata import *
from Proposicion import *
from Token import *
from TokenType import *

def analisis_lexico(proposicion):
    # Cambiar frase a minusculas y separar por espacios
    tokens = proposicion.lower().split(' ')
    
    # Tokenizar palabras
    listaTokens = []
    for token in tokens:
        if token == 'y':
            listaTokens.append(Token(TokenType.Y, token))
        elif token == 'o':
            listaTokens.append(Token(TokenType.O, token))
        elif token == 'si':
            listaTokens.append(Token(TokenType.SI, token))
        elif token == 'entonces':
            listaTokens.append(Token(TokenType.ENTONCES, token))
        elif token == 'no':
            listaTokens.append(Token(TokenType.NOT, token))
        else:
            listaTokens.append(Token(TokenType.PALABRA, token))
    listaTokens.append(Token(TokenType.EOL, ''))
    return listaTokens  

# Analizador Sintactico
def print_ast(node, level=0):
    indent = "  " * level
    if isinstance(node, PropNode):
        print(f"{indent}PropNode: {node}")
    elif isinstance(node, NegNode):
        print(f"{indent}NegNode")
        print_ast(node.child, level + 1)
    elif isinstance(node, OperatorNode):
        print(f"{indent}CondNode: {node.operator}")
        print_ast(node.left, level + 1)
        print_ast(node.right, level + 1)

def main():
    # Solicta al que ingrese una proposicion
    print("Ingrese una proposicion: ")
    tokens = analisis_lexico(input())

    print("\nAnalisis Lexico:")
    print("Tipo\tValor")
    for token in tokens:
        print(token.tipo, token.valor)
        
    print("\nAnalisis Sintactico:")
    automata = Automata()
    resultado = automata.evaluar(tokens)
    if resultado:
        print("La proposición es correcta.")       
    else:
        print("La proposición es incorrecta.") 
        
    print("Analisis Semantico")
    if resultado:
        print("\nAST generado:")
        print_ast(resultado)  # Asumiendo que tienes una función para imprimir el AST

 
    
if __name__ == "__main__":
    main()