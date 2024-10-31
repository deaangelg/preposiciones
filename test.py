# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import networkx as nx
import tkinter as tk 
from tkinter import ttk
import string
import itertools

# Inicializa la ventana principal
root = tk.Tk()
root.title("Frases")
root.geometry("1000x500")

# Frames para organizar los elementos
frame_left = tk.Frame(root)
frame_left.pack(side=tk.LEFT, padx=10, pady=10)
frame_right = tk.Frame(root)
frame_right.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH, expand=True)

# Variables de control
text_entries = []
alphabet = list(string.ascii_uppercase)
current_letter_index = 0
subfrases_guardadas = {}
disyuncion = [" o ", " ó ", " Ó ", " O ", " o,", ", o,"]
conjuncion = [" y ", " Y ", " Y,", ", Y,", ", y ", " y, ", ", y, "]
negacion_palabras = [" no ", " No ", " NO "]
frases_completas = {}

# Configuración de estilo para la tabla
style = ttk.Style()
style.configure("Treeview.Heading", font=("Arial", 10, "bold"))
style.configure("Treeview", rowheight=30, font=("Arial", 10))
style.map("Treeview", background=[("selected", "#f0f0ff")])

# Tabla en el frame derecho
tabla = ttk.Treeview(frame_right, columns=("Formula", "Frase Completa", "Subfrase", "Variable"), show="headings")
for col, width in zip(("Formula", "Frase Completa", "Subfrase", "Variable"), (200, 300, 200, 80)):
    tabla.heading(col, text=col)
    tabla.column(col, anchor="w", width=width)
tabla.pack(fill=tk.BOTH, expand=True)

# Función para agregar una nueva caja de texto
def agregar_frase():
    nueva_caja = tk.Entry(frame_left, width=50)
    nueva_caja.pack(pady=5)
    text_entries.append(nueva_caja)

# Función para dividir la frase en subfrases
def dividir_frase_multiple(frase):
    subfrases, tipos, negaciones = [], [], []
    while any(con in frase for con in disyuncion + conjuncion):
        es_negacion = any(neg in frase for neg in negacion_palabras)
        index_disyuncion = min((frase.find(con) for con in disyuncion if con in frase), default=len(frase))
        index_conjuncion = min((frase.find(con) for con in conjuncion if con in frase), default=len(frase))

        if index_disyuncion < index_conjuncion:
            conector = next(con for con in disyuncion if frase.find(con) == index_disyuncion)
            subfrase, frase = map(str.strip, frase.split(conector, 1))
            tipos.append("Disyunción")
        else:
            conector = next(con for con in conjuncion if frase.find(con) == index_conjuncion)
            subfrase, frase = map(str.strip, frase.split(conector, 1))
            tipos.append("Conjunción")

        if es_negacion:
            subfrase = subfrase.replace(" no", "").strip()  # Eliminamos la negación de la subfrase
            negaciones.append(True)
        else:
            negaciones.append(False)
        subfrases.append(subfrase)

    # Añade la última parte como subfrase
    if frase.strip():
        es_negacion = any(neg in frase for neg in negacion_palabras)
        if es_negacion:
            frase = frase.replace(" no", "").strip()
            negaciones.append(True)
        else:
            negaciones.append(False)
        subfrases.append(frase.strip())

    return subfrases, tipos, negaciones

# Construye la fórmula lógica de la frase completa
def construir_formula_logica(subfrases, tipos, negaciones):
    stack = []
    formula = []

    for i, subfrase in enumerate(subfrases):
        variable = subfrases_guardadas.get(subfrase, "")
        subformula = f"¬{variable}" if negaciones[i] else variable
        
        if i == 0:
            formula.append(subformula)
        else:
            # Añade paréntesis a las operaciones anteriores
            if tipos[i-1] == "Conjunción":
                formula.append(f"({formula.pop()} ∧ {subformula})")
            elif tipos[i-1] == "Disyunción":
                formula.append(f"({formula.pop()} ∨ {subformula})")

    # Formar la expresión final
    return " ".join(formula)

# Procesa y muestra cada frase en la tabla
def guardar_frases():
    global current_letter_index
    for entrada in text_entries:
        texto = entrada.get()
        if texto:
            subfrases, tipos, negaciones = dividir_frase_multiple(texto)
            for subfrase in subfrases:
                if subfrase not in subfrases_guardadas:
                    if current_letter_index < len(alphabet):
                        subfrases_guardadas[subfrase] = alphabet[current_letter_index]
                        current_letter_index += 1

            formula_logica = construir_formula_logica(subfrases, tipos, negaciones)
            frases_completas[formula_logica] = subfrases

            tabla.insert("", "end", values=(formula_logica, texto, "", ""))

            for i, subfrase in enumerate(subfrases):
                tipo = tipos[i] if i < len(tipos) else ""
                tabla.insert("", "end", values=(tipo, "", subfrase, subfrases_guardadas[subfrase]))

# Genera y muestra la tabla de verdad para una fórmula específica
def mostrar_tabla_verdad(formula, subfrases):
    ventana_tabla = tk.Toplevel(root)
    ventana_tabla.title("Tabla de Verdad")
    ventana_tabla.geometry("400x400")

    tabla_verdad = ttk.Treeview(ventana_tabla, columns=("Variables", "Resultado"), show="headings")
    tabla_verdad.heading("Variables", text="Variables")
    tabla_verdad.heading("Resultado", text="Resultado")
    tabla_verdad.pack(fill=tk.BOTH, expand=True)

    variables = [subfrases_guardadas[subfrase] for subfrase in subfrases]
    combinaciones = list(itertools.product([0, 1], repeat=len(variables)))

    for combinacion in combinaciones:
        valores = dict(zip(variables, combinacion))
        resultado = evaluar_formula(formula, valores)
        tabla_verdad.insert("", "end", values=(valores, resultado))

# Evalúa la fórmula lógica
def evaluar_formula(formula, valores):
    for var, val in valores.items():
        formula = formula.replace(var, str(val))
    formula = formula.replace("¬", " not ").replace("∧", " and ").replace("∨", " or ")
    try:
        return int(eval(formula))
    except:
        return "Error"

# Dibuja el árbol de estados
def dibujar_arbol_estados(formula):
    G = nx.DiGraph()
    
    # Agregar el nodo raíz
    G.add_node(formula)

    # Dividir la fórmula en subfórmulas y conectarlas
    subfórmulas = formula.replace("(", "").replace(")", "").split("∧") if "∧" in formula else formula.replace("(", "").replace(")", "").split("∨")
    
    for subfórmula in subfórmulas:
        subfórmula = subfórmula.strip()
        G.add_node(subfórmula)
        G.add_edge(formula, subfórmula)

    # Crear la visualización
    pos = nx.spring_layout(G)  # Layout para los nodos
    plt.figure(figsize=(8, 6))
    nx.draw(G, pos, with_labels=True, arrows=True, node_size=2000, node_color='lightblue', font_size=10)
    plt.title("Árbol de Estados de la Fórmula")
    plt.show()

# Botones de la interfaz gráfica
for text, command in [("Agregar frase", agregar_frase), ("Guardar", guardar_frases), 
                      ("Borrar todo", lambda: tabla.delete(*tabla.get_children()))]:
    tk.Button(frame_left, text=text, command=command).pack(pady=10)

# Agregar botón de tabla de verdad por fórmula
def generar_botones_tabla_verdad():
    for formula, subfrases in frases_completas.items():
        tk.Button(frame_left, text=f"Tabla de Verdad para {formula}",
                  command=lambda f=formula, s=subfrases: mostrar_tabla_verdad(f, s)).pack(pady=5)

tk.Button(frame_left, text="Generar Tablas de Verdad", command=generar_botones_tabla_verdad).pack(pady=10)

# Agregar botón para mostrar el árbol de estados
def generar_botones_arbol_estados():
    for formula in frases_completas.keys():
        tk.Button(frame_left, text=f"Árbol de Estados para {formula}",
                  command=lambda f=formula: dibujar_arbol_estados(f)).pack(pady=5)

tk.Button(frame_left, text="Generar Árboles de Estados", command=generar_botones_arbol_estados).pack(pady=10)

root.mainloop()
