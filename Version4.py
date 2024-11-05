# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import networkx as nx
import tkinter as tk
from tkinter import ttk, filedialog
import string
import itertools

# Inicializa la ventana principal
root = tk.Tk()
root.title("Frases")
root.geometry("1000x500")

# Frames para organizar los elementos
frame_top = tk.Frame(root)
frame_top.pack(side=tk.TOP, padx=10, pady=10, fill=tk.X)
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
conjuncion = [" y ", " Y ", " Y,", ", Y,", ", y ", " y, ", ", y,"]
negacion_palabras = [" no ", " No ", " NO "]
frases_completas = {}
valores_asignados = {}

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

        # Manejo de negaciones
        if "no" in subfrase:
            subfrase = subfrase.replace("no", "").strip()
            negaciones.append(True)
        else:
            negaciones.append(False)
        subfrases.append(subfrase)

    if frase.strip():
        if "no" in frase:
            frase = frase.replace("no", "").strip()
            negaciones.append(True)
        else:
            negaciones.append(False)
        subfrases.append(frase.strip())

    return subfrases, tipos, negaciones

# Construye la fórmula lógica de la frase completa
def construir_formula_logica(subfrases, tipos, negaciones):
    formula = []

    for i, subfrase in enumerate(subfrases):
        variable = subfrases_guardadas.get(subfrase, "")
        subformula = f"¬{variable}" if negaciones[i] else variable
        
        if i == 0:
            formula.append(subformula)
        else:
            if tipos[i-1] == "Conjunción":
                formula.append(f"({formula.pop()} ∧ {subformula})")
            elif tipos[i-1] == "Disyunción":
                formula.append(f"({formula.pop()} ∨ {subformula})")

    return " ".join(formula)

# Función para generar la fórmula de Horn de las frases guardadas
def generar_formula_horn_guardadas():
    ventana_horn_guardadas = tk.Toplevel(root)
    ventana_horn_guardadas.title("Fórmulas de Horn de Frases Guardadas")
    ventana_horn_guardadas.geometry("600x600")

    # Crear un cuadro de texto para mostrar las fórmulas
    text_box = tk.Text(ventana_horn_guardadas, wrap=tk.WORD, width=70, height=25)
    text_box.pack(padx=10, pady=10)

    # Limpiar el cuadro de texto antes de llenarlo
    text_box.delete(1.0, tk.END)

    # Recorrer las frases guardadas
    for formula_logica, subfrases in frases_completas.items():
        texto = " ".join(subfrases)
        text_box.insert(tk.END, f"Frase Completa: {texto}\n")
        text_box.insert(tk.END, f"Fórmula de Horn: {formula_logica}\n\n")

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
                variable = subfrases_guardadas[subfrase]
                if negaciones[i]:
                    variable = f"¬{variable}"
                tabla.insert("", "end", values=(tipo, "", subfrase, variable))

# Cargar frases desde un archivo TXT
def cargar_frases_txt():
    global current_letter_index
    archivo = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    if archivo:
        with open(archivo, 'r', encoding='utf-8') as f:
            frases = f.readlines()
            for texto in frases:
                texto = texto.strip()
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

# Asigna valores de verdadero o falso a las subfrases
def asignar_valores():
    def guardar_valores():
        for subfrase in subfrases:
            valor = var_dict[subfrase].get()
            valores_asignados[subfrase] = valor
            
        mostrar_valores_asignados()
        guardar_valores_txt()
        ventana.destroy()

    def guardar_valores_txt():
        archivo = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if archivo:
            with open(archivo, 'w', encoding='utf-8') as f:
                for subfrase, valor in valores_asignados.items():
                    f.write(f"{subfrase}: {valor}\n")

    ventana = tk.Toplevel(root)
    ventana.title("Asignar Valores")
    ventana.geometry("300x200")

    subfrases = list(subfrases_guardadas.keys())
    var_dict = {}

    for subfrase in subfrases:
        var_dict[subfrase] = tk.StringVar(value='True')
        tk.Radiobutton(ventana, text=f"{subfrases_guardadas[subfrase]}: Verdadero", variable=var_dict[subfrase], value='True').pack(anchor=tk.W)
        tk.Radiobutton(ventana, text=f"{subfrases_guardadas[subfrase]}: Falso", variable=var_dict[subfrase], value='False').pack(anchor=tk.W)

    tk.Button(ventana, text="Guardar Valores", command=guardar_valores).pack(pady=10)

def mostrar_valores_asignados():
    ventana_valores = tk.Toplevel(root)
    ventana_valores.title("Valores Asignados")
    ventana_valores.geometry("400x300")

    tabla_valores = ttk.Treeview(ventana_valores, columns=("Variable", "Valor"), show="headings")
    for col, width in zip(("Variable", "Valor"), (200, 150)):
        tabla_valores.heading(col, text=col)
        tabla_valores.column(col, anchor="w", width=width)
    tabla_valores.pack(fill=tk.BOTH, expand=True)

    for subfrase, variable in subfrases_guardadas.items():
        valor = valores_asignados.get(subfrase, "No asignado")
        tabla_valores.insert("", "end", values=(variable, valor))

# Evalúa la fórmula lógica
def evaluar_formula(formula, valores):
    for var, val in valores.items():
        formula = formula.replace(var, str(val))
    formula = formula.replace("¬", " not ").replace("∧", " and ").replace("∨", " or ")
    try:
        return int(eval(formula))
    except:
        return "Error"

# Dibuja el árbol de estados en forma de pirámide
def dibujar_arbol_estados(formula):
    G = nx.DiGraph()

    def agregar_nodos(nodo_padre, variables, nivel):
        if not variables:
            return
        
        var_actual = variables[0]
        operacion = f"{formula} (Nivel {nivel})"
        if nivel == 0:
            G.add_node(operacion)
            G.add_edge(nodo_padre, operacion)
            nodo_padre = operacion
        
        for estado in [0, 1]:
            estado_str = f"{var_actual} = {'True' if estado else 'False'}"
            G.add_node(estado_str)
            G.add_edge(nodo_padre, estado_str)
            
            agregar_nodos(estado_str, variables[1:], nivel + 1)

    variables = list(subfrases_guardadas.keys())
    agregar_nodos("", variables, 0)

    pos = nx.spring_layout(G)
    labels = {nodo: nodo for nodo in G.nodes}
    plt.figure(figsize=(12, 8))
    nx.draw(G, pos, with_labels=True, labels=labels, arrows=True, node_size=2000, node_color='lightblue', font_size=10, font_weight='bold', edge_color='gray')
    plt.title("Árbol de Estados de la Fórmula")
    plt.show()

# Generar botones para los árboles de estados
def generar_botones_arbol_estados():
    for formula in frases_completas.keys():
        tk.Button(frame_left, text=f"Árbol de Estados para {formula}",
                  command=lambda f=formula: dibujar_arbol_estados(f)).pack(pady=5)

# Generar tablas de verdad
def generar_tabla_verdad():
    for formula, subfrases in frases_completas.items():
        tk.Button(frame_left, text=f"Tabla de Verdad para {formula}",
                  command=lambda f=formula, s=subfrases: mostrar_tabla_verdad(f, s)).pack(pady=5)

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

# Botones de la interfaz gráfica en la parte superior
boton_textos = [
    ("Agregar frase", agregar_frase), 
    ("Cargar TXT", cargar_frases_txt), 
    ("Guardar", guardar_frases),
    ("Borrar todo", lambda: tabla.delete(*tabla.get_children())),
    ("Asignar Valores", asignar_valores),
    ("Generar Fórmulas de Horn", generar_formula_horn_guardadas),
    ("Generar Árboles de Estados", generar_botones_arbol_estados),
    ("Generar Tablas de Verdad", generar_tabla_verdad)
]

for text, command in boton_textos:
    btn = tk.Button(frame_top, text=text, command=command)
    btn.pack(side=tk.LEFT, padx=5)

root.mainloop()
