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
valores_atomicos = {}  # Para almacenar valores de verdad de las subfrases

# Configuración de estilo para la tabla
style = ttk.Style()
style.configure("Treeview.Heading", font=("Arial", 10, "bold"))
style.configure("Treeview", rowheight=30, font=("Arial", 10))
style.map("Treeview", background=[("selected", "#f0f0ff")])

# Tabla en el frame derecho
tabla = ttk.Treeview(frame_right, columns=("Formula", "Frase Completa", "Subfrase", "Variable", "Valor"), show="headings")
for col, width in zip(("Formula", "Frase Completa", "Subfrase", "Variable", "Valor"), (200, 300, 200, 80, 80)):
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
    global current_letter_index, formula_logica, subfrases
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

            tabla.insert("", "end", values=(formula_logica, texto, "", "", ""))

            for i, subfrase in enumerate(subfrases):
                tipo = tipos[i] if i < len(tipos) else ""
                tabla.insert("", "end", values=(tipo, "", subfrase, subfrases_guardadas[subfrase], ""))

# Función para asignar valores a los átomos en una sola ventana
def asignar_valores_verdad():
    ventana_asignar = tk.Toplevel(root)
    ventana_asignar.title("Asignar valores a átomos")

    tk.Label(ventana_asignar, text="Asigna valores a los átomos:").pack(pady=10)

    atomos_var = {}
    for subfrase, variable in subfrases_guardadas.items():
        valor = tk.StringVar(value="1")  # Valor por defecto a "verdadero"
        atomos_var[variable] = valor

        tk.Label(ventana_asignar, text=subfrase).pack(anchor=tk.W)
        tk.Radiobutton(ventana_asignar, text="Verdadero", variable=valor, value="1").pack(anchor=tk.W)
        tk.Radiobutton(ventana_asignar, text="Falso", variable=valor, value="0").pack(anchor=tk.W)

    def guardar_valores():
        for variable, valor in atomos_var.items():
            valores_atomicos[variable] = valor.get()
        ventana_asignar.destroy()
        actualizar_tabla()

    tk.Button(ventana_asignar, text="Guardar", command=guardar_valores).pack(pady=10)
    ventana_asignar.transient(root)  # Hacer la ventana secundaria dependiente de la principal
    ventana_asignar.grab_set()  # Bloquear interacción con la ventana principal

# Función para actualizar la tabla con los valores de verdad
def actualizar_tabla():
    for subfrase, variable in subfrases_guardadas.items():
        valor = valores_atomicos.get(variable, "")
        # Actualizar la tabla para mostrar el valor asignado
        for item in tabla.get_children():
            if tabla.item(item)['values'][3] == variable:
                tabla.item(item, values=(tabla.item(item)['values'][0], 
                                          tabla.item(item)['values'][1], 
                                          tabla.item(item)['values'][2], 
                                          tabla.item(item)['values'][3], 
                                          valor))

# Botones para la interfaz
tk.Button(frame_left, text="Agregar Frase", command=agregar_frase).pack(pady=10)
tk.Button(frame_left, text="Guardar Frases", command=guardar_frases).pack(pady=10)
tk.Button(frame_left, text="Asignar Valores a Átomos", command=asignar_valores_verdad).pack(pady=10)
tk.Button(frame_left, text="Mostrar Tablas de Verdad", command=lambda: mostrar_tabla_verdad(formula_logica, subfrases)).pack(pady=10)
tk.Button(frame_left, text="Dibujar Árbol de Estados", command=lambda: dibujar_arbol_estados(formula_logica, subfrases)).pack(pady=10)

root.mainloop()