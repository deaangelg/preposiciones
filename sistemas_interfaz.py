import tkinter as tk
from tkinter import scrolledtext, messagebox
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

def print_ast(node, level=0):
    indent = "  " * level
    result = ""
    if isinstance(node, PropNode):
        result += f"{indent}PropNode: {node}\n"
    elif isinstance(node, NegNode):
        result += f"{indent}NegNode\n"
        result += print_ast(node.child, level + 1)
    elif isinstance(node, OperatorNode):
        result += f"{indent}CondNode: {node.operator}\n"
        result += print_ast(node.left, level + 1)
        result += print_ast(node.right, level + 1)
    return result

def realizar_analisis():
    proposicion = entrada_texto.get()
    if not proposicion.strip():
        messagebox.showerror("Error", "Por favor, ingrese una proposición.")
        return

    # Analizador Léxico
    tokens = analisis_lexico(proposicion)
    
    lexico_text.delete(1.0, tk.END)
    lexico_text.insert(tk.END, "Tipo\tValor\n")
    for token in tokens:
        lexico_text.insert(tk.END, f"{token.tipo}\t{token.valor}\n")

    # Analizador Sintáctico
    automata = Automata()
    resultado = automata.evaluar(tokens)

    sintactico_text.delete(1.0, tk.END)
    if resultado:
        sintactico_text.insert(tk.END, "La proposición es correcta.\n")
        sintactico_text.insert(tk.END, "\nAST generado:\n")
        sintactico_text.insert(tk.END, print_ast(resultado))
    else:
        sintactico_text.insert(tk.END, "La proposición es incorrecta.")

# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Analizador Léxico y Sintáctico")
ventana.geometry("800x600")

# Entrada de texto
entrada_label = tk.Label(ventana, text="Ingrese una proposición:")
entrada_label.pack(pady=5)
entrada_texto = tk.Entry(ventana, width=80)
entrada_texto.pack(pady=5)

# Botón para realizar análisis
boton_analizar = tk.Button(ventana, text="Analizar", command=realizar_analisis)
boton_analizar.pack(pady=10)

# Resultado del análisis léxico
lexico_label = tk.Label(ventana, text="Análisis Léxico:")
lexico_label.pack(pady=5)
lexico_text = scrolledtext.ScrolledText(ventana, width=90, height=10)
lexico_text.pack(pady=5)

# Resultado del análisis sintáctico
sintactico_label = tk.Label(ventana, text="Análisis Sintáctico:")
sintactico_label.pack(pady=5)
sintactico_text = scrolledtext.ScrolledText(ventana, width=90, height=15)
sintactico_text.pack(pady=5)

# Ejecutar la ventana principal
ventana.mainloop()
