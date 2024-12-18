import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sympy as smp
from sympy.calculus.util import continuous_domain
from tkinter import ttk

# Variables globales para manejar los límites de los ejes
x_min_global = None
x_max_global = None
y_min_global = None
y_max_global = None
zoom_factor = 0.2  # Tamaño del paso de zoom
funcion_actual = None  # Variable global para almacenar la función cargada
funcion_simp = None
derivada = None

def is_continuous_on_interval(f, a, b):
    try:
        x = smp.symbols("x")
        # Verificar continuidad en el intervalo usando SymPy
        dominio_continuo = continuous_domain(f, x, smp.Interval(a, b))
        
        # Verificar que el intervalo [a, b] esté contenido en el dominio continuo
        if smp.Interval(a, b).is_subset(dominio_continuo):
            return True
        else:
            return False
    except Exception as e:
        print(f"Error al verificar la continuidad: {e}")
        return False


def graficar_funcion():
    global x_min_global, x_max_global, y_min_global, y_max_global, funcion_actual, funcion_simp

    funcion = entrada_funcion.get()
    try:
        f = smp.sympify(funcion, evaluate=False)
        funcion_simp=f
    except smp.SympifyError:
        print("Error al parsear la función. Asegúrese de ingresar una expresión válida.")
    try:
        # Leer los valores de a, b, iteraciones y tolerancia
        a = float(entrada_a.get())
        b = float(entrada_b.get())
        valorIteraciones=entrada_iteraciones.get()
        if (not valorIteraciones):
            iteraciones=100
        else:
            iteraciones = int(valorIteraciones)
            
        if (not entrada_tolerancia.get()): 
            tolerancia = 0.00000000001
        else:  
            tolerancia = float(entrada_tolerancia.get())
            
        if (not aproximacion.get()): 
            aproxInicial = (a+b)/2
        else:  
            aproxInicial = float(aproximacion.get())
            
        funcion_actual = funcion
        # Validaciones básicas
        if a >= b:
            messagebox.showerror("Error", "El valor de 'a' debe ser menor que 'b'.")
            return
        if aproxInicial<=a or aproxInicial>=b:
            messagebox.showerror("Error", "La aproximacion inicial debe estar en el intervalo (a,b).")
            return
        
        if (not is_continuous_on_interval(f, a, b)):
            messagebox.showerror("Error", "La función no es continua en el intervalo dado.")
            return
            
        if (signo(evaluar_funcion(a)*signo(evaluar_funcion(b)))>0):
            messagebox.showerror("Error", "La función debe tomar signos distintos en los extremos del intervalo.")
            return
        
        if iteraciones <= 0:
            messagebox.showerror("Error", "El número de iteraciones debe ser mayor que 0.")
            return
        if tolerancia <= 0:
            messagebox.showerror("Error", "La tolerancia debe ser un valor positivo.")
            return

        x_min = a
        x_max = b 
        x = np.linspace(x_min, x_max, 500)

        # Evaluar la función ingresada con el espacio de nombres de numpy
        y = eval(funcion_actual, {"__builtins__": None}, {"x": x, **np.__dict__})

        # Limpiar el gráfico anterior
        ax.clear()
        ax.plot(x, y, label=f"y = {funcion_actual}")

        # Añadir la línea del eje X (y = 0)
        ax.axhline(0, color='black', linewidth=0.8, linestyle='--')
        ax.axvline(0, color='black', linewidth=0.8, linestyle='--')

        ax.set_title(f"Gráfico de la función (Iteraciones: {iteraciones}, Tolerancia: {tolerancia})")
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.legend()

        # Ajustar los límites del eje X
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(min(y) - 5, max(y) + 5)  # Establecer límites de Y

        # Actualizar los valores globales para los límites
        x_min_global, x_max_global = x_min, x_max
        y_min_global, y_max_global = min(y) - 5, max(y) + 5
        
        canvas.draw()
        
        if metodo_seleccionado.get() == "Bisección":
            biseccion(iteraciones, tolerancia, a, b)
        elif metodo_seleccionado.get() == "Tangente":
            #metodo_tangente(iteraciones, tolerancia, (a+b)/2)
            metodo_tangente(iteraciones, tolerancia, aproxInicial)
        else:
            messagebox.showerror("Error", "Método no válido seleccionado.")
            return

    except Exception as e:
        messagebox.showerror("Error", f"La función ingresada no es válida: {e}")

def evaluar_funcion(x):
    global funcion_actual
    try:
        # Evaluar la función almacenada en el punto x
        y = eval(funcion_actual, {"__builtins__": None}, {"x": x, **np.__dict__})
        return float (y)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo evaluar la función en x = {x}: {e}")
        return None

def zoom(event):
    global x_min_global, x_max_global, y_min_global, y_max_global, zoom_factor

    # Detectar la dirección de la rueda del ratón para zoom in o zoom out
    if event.delta > 0 or event.num == 4:  # Zoom in
        factor = 1 - zoom_factor
    elif event.delta < 0 or event.num == 5:  # Zoom out
        factor = 1 + zoom_factor
    else:
        return

    # Calcular el centro actual del gráfico
    x_center = (x_min_global + x_max_global) / 2
    y_center = (y_min_global + y_max_global) / 2

    # Calcular los nuevos límites de los ejes
    x_width = (x_max_global - x_min_global) * factor
    y_height = (y_max_global - y_min_global) * factor

    # Limitar el zoom mínimo a un rango razonable
    if x_width < 0.1 or y_height < 0.1:  # Ajusta este valor según tus necesidades
        return

    # Actualizar los límites
    x_min_global = x_center - x_width / 2
    x_max_global = x_center + x_width / 2
    y_min_global = y_center - y_height / 2
    y_max_global = y_center + y_height / 2

    # Actualizar el gráfico
    ax.set_xlim(x_min_global, x_max_global)
    ax.set_ylim(y_min_global, y_max_global)
    canvas.draw()

def mover_izquierda(event):
    global x_min_global, x_max_global

    # Desplazar 10 unidades a la izquierda
    desplazamiento = 5
    x_min_global -= desplazamiento
    x_max_global -= desplazamiento

    # Actualizar el gráfico
    ax.set_xlim(x_min_global, x_max_global)
    canvas.draw()

def mover_derecha(event):
    global x_min_global, x_max_global

    # Desplazar 5 unidades a la derecha
    desplazamiento = 5
    x_min_global += desplazamiento
    x_max_global += desplazamiento

    # Actualizar el gráfico
    ax.set_xlim(x_min_global, x_max_global)
    canvas.draw()

def mover_arriba(event):
    global y_min_global, y_max_global

    # Desplazar 5 unidades hacia arriba
    desplazamiento = 5
    y_min_global += desplazamiento
    y_max_global += desplazamiento

    # Actualizar el gráfico
    ax.set_ylim(y_min_global, y_max_global)
    canvas.draw()

def mover_abajo(event):
    global y_min_global, y_max_global

    # Desplazar 5 unidades hacia abajo
    desplazamiento = 5
    y_min_global -= desplazamiento
    y_max_global -= desplazamiento

    # Actualizar el gráfico
    ax.set_ylim(y_min_global, y_max_global)
    canvas.draw()


def signo(a):
    if a>0:
        return 1    
    return -1


def crear_tabla():
    ventana = tk.Tk()
    ventana.title("Resultados")

    # Crear tabla
    columnas = ("Iteración", "a", "f(a)", "b", "f(b)", "c", "f(c)", "Razón de parada")
    tabla = ttk.Treeview(ventana, columns=columnas, show="headings")

    # Configurar encabezados
    for col in columnas:
        tabla.heading(col, text=col)
        tabla.column(col, anchor=tk.CENTER)

  # Estilo para filas con tag "rojo"
    style = ttk.Style()
    style.configure("Verde.Treeview", foreground="green")
    tabla.tag_configure("verde", foreground="green")
    
    tabla.pack(fill=tk.BOTH, expand=True)
    
    return tabla,ventana


def biseccion(iteraciones, tolerancia, a, b):
    # Crear ventana
    tabla, ventana=crear_tabla()
    def agregar_fila(iteracion, a, fa, b, fb, c, fc, razon, es_ultima):
        tag = "verde" if es_ultima else ""
        tabla.insert("", "end", values=(iteracion, a, fa, b, fb, c, fc, razon), tags=(tag))

   
    # Lógica del método de bisección
    i = 0
    c = a + ((b - a) / 2)
    if evaluar_funcion(c) == 0:
        agregar_fila(i, a, evaluar_funcion(a), b, evaluar_funcion(b), c, evaluar_funcion(c), "Raíz exacta", True)
        ventana.mainloop()
        return c

    while i < iteraciones:
        c = a + ((b - a) / 2)
        i += 1

        if (signo(evaluar_funcion(c)) * signo(evaluar_funcion(a))) > 0:
            anterior = a
            a = c
        else:
            anterior = b
            b = c
        
        if evaluar_funcion(c) == 0:
            agregar_fila(i, a, evaluar_funcion(a), b, evaluar_funcion(b), c, evaluar_funcion(c), "Raíz exacta", True)
            #tabla.insert("Raiz encontrada en: ", c, evaluar_funcion(c), "", "", "","", "", tags=("verde"))
            ventana.mainloop()
            return c
        

        if abs(c - anterior) < tolerancia:
            agregar_fila(i, a, evaluar_funcion(a), b, evaluar_funcion(b), c, evaluar_funcion(c), "Tolerancia alcanzada", True)
            ventana.mainloop()
            return c
        agregar_fila(i, a, evaluar_funcion(a), b, evaluar_funcion(b), c, evaluar_funcion(c), abs(c-anterior), False)


    if i == iteraciones:
        agregar_fila(i, a, evaluar_funcion(a), b, evaluar_funcion(b), c, evaluar_funcion(c), "Máximo de iteraciones", True)

    ventana.mainloop()
    return c



def evaluar_derivada(x):
    global funcion_simp
    variable = smp.symbols("x")
    derivada= smp.diff(funcion_simp)
    return float (derivada.evalf(subs={variable: x}))

def crear_tabla_tangente():
    ventana = tk.Tk()
    ventana.title("Resultados")

    # Crear tabla
    columnas = ("Iteración", "pAnterior", "Derivada", "nuevoP", "f(nuevoP)", "Razón de parada")
    tabla = ttk.Treeview(ventana, columns=columnas, show="headings")

    # Configurar encabezados
    for col in columnas:
        tabla.heading(col, text=col)
        tabla.column(col, anchor=tk.CENTER)

    #Estilo para filas con tag "rojo"
    style = ttk.Style()
    style.configure("Verde.Treeview", foreground="green")
    tabla.tag_configure("verde", foreground="green")
    
    tabla.pack(fill=tk.BOTH, expand=True)
    
    return tabla,ventana


def metodo_tangente(iteraciones, tolerancia, pInicial):
    # Crear ventana y tabla
    tabla, ventana = crear_tabla_tangente()
    def agregar_fila(iteracion, pAnterior, derivada, nuevoP, fNuevoP, razon, es_ultima):
        tag = "verde" if es_ultima else ""
        tabla.insert("", "end", values=(iteracion, pAnterior, derivada, nuevoP, fNuevoP, razon), tags=(tag))


    # Lógica del método de la tangente
    nuevoP = pInicial
    i = 0

    # Verificar si ya se tiene la raíz exacta
    if evaluar_funcion(nuevoP) == 0:
        agregar_fila(i, nuevoP, "-", nuevoP, evaluar_funcion(nuevoP), "Raíz exacta", True)
        ventana.mainloop()
        return nuevoP

    while i < iteraciones:
        pAnterior = nuevoP
        i += 1
        derivada = evaluar_derivada(pAnterior)

        # Verificar si la derivada es cero o no es válida
        if derivada == 0 or derivada is None or not smp.sympify(derivada).is_real:
            agregar_fila(i, pAnterior, derivada, "-", "-", "La derivada es 0, no se puede seguir", False)
            ventana.mainloop()
            return

        nuevoP = pAnterior - (evaluar_funcion(pAnterior) / derivada)
        
        # Verificar si el valor de la función en el nuevo punto es válido
        if evaluar_funcion(nuevoP) is None or not smp.sympify(evaluar_funcion(nuevoP)).is_real:
            agregar_fila(i, pAnterior, derivada, nuevoP, "-", "Función no válida en p", False)
            ventana.mainloop()
            return

        # Verificar si se alcanzó la raíz exacta
        if evaluar_funcion(nuevoP) == 0:
            agregar_fila(i, pAnterior, derivada, nuevoP, evaluar_funcion(nuevoP), "Raíz exacta", True)
            ventana.mainloop()
            return nuevoP

        # Verificar si se cumple la condición de tolerancia
        if abs(nuevoP - pAnterior) < tolerancia:
            agregar_fila(i, pAnterior, derivada, nuevoP, evaluar_funcion(nuevoP), "Tolerancia alcanzada", True)
            ventana.mainloop()
            return nuevoP
        
        agregar_fila(i, pAnterior, derivada, nuevoP, evaluar_funcion(nuevoP), abs(nuevoP - pAnterior), False)


    # Si se alcanza el máximo de iteraciones
    if i == iteraciones:
        agregar_fila(i, pAnterior, derivada, nuevoP, evaluar_funcion(nuevoP), "Máximo de iteraciones", True)

    ventana.mainloop()
    return nuevoP

# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Graficador de Funciones")
ventana.geometry("800x700")

# Etiqueta y entrada para la función
etiqueta_funcion = tk.Label(ventana, text="Introduce una función de x (ejemplo: x**2, sin(x)): ")
etiqueta_funcion.pack(pady=10)
entrada_funcion = tk.Entry(ventana, width=50)
entrada_funcion.pack(pady=5)

# Etiquetas y entradas para a y b
etiqueta_a = tk.Label(ventana, text="Valor inicial del intervalo (a):", )
etiqueta_a.pack(pady=5)
entrada_a = tk.Entry(ventana, width=20)
entrada_a.pack(pady=5)

etiqueta_b = tk.Label(ventana, text="Valor final del intervalo (b):")
etiqueta_b.pack(pady=5)
entrada_b = tk.Entry(ventana, width=20)
entrada_b.pack(pady=5)

etiqueta_aprox = tk.Label(ventana, text="Aproximacion inicial (para el metodo de Newton, (a+b)/2 por default):")
etiqueta_aprox.pack(pady=5)

aproximacion = tk.Entry(ventana, width=20)
aproximacion.pack(pady=5)

# Etiquetas y entradas para iteraciones y tolerancia
etiqueta_iteraciones = tk.Label(ventana, text="Número de iteraciones (100 por default):")
etiqueta_iteraciones.pack(pady=5)
entrada_iteraciones = tk.Entry(ventana, width=20)
entrada_iteraciones.pack(pady=5)

etiqueta_tolerancia = tk.Label(ventana, text="Tolerancia (10^-10 por default):")
etiqueta_tolerancia.pack(pady=5)
entrada_tolerancia = tk.Entry(ventana, width=20)
entrada_tolerancia.pack(pady=5)

etiqueta_metodo = tk.Label(ventana, text="Seleccione el método:")
etiqueta_metodo.pack()
metodo_seleccionado = tk.StringVar(value="Bisección")  # Valor por defecto: Bisección
style = ttk.Style()
style.theme_use("clam")
style.configure("TCombobox", fieldbackground="white", background="lightgray")

metodos = ["Bisección", "Tangente"]
menu_metodo = ttk.Combobox(ventana, textvariable=metodo_seleccionado, values=metodos, state="readonly")
menu_metodo.pack(pady=5)
# Botón para graficar
boton_graficar = tk.Button(ventana, text="Calcular raiz y graficar", command=graficar_funcion)
boton_graficar.pack(pady=10)

# Área para el gráfico
fig, ax = plt.subplots(figsize=(9, 9))
canvas = FigureCanvasTkAgg(fig, master=ventana)
canvas.get_tk_widget().pack()

# Vincular las teclas de dirección y la rueda del ratón para mover el gráfico y hacer zoom
ventana.bind("<Left>", mover_izquierda)
ventana.bind("<Right>", mover_derecha)
ventana.bind("<Up>", mover_arriba)
ventana.bind("<Down>", mover_abajo)
ventana.bind("<Button-4>", zoom)  
ventana.bind("<Button-5>", zoom)   

ventana.mainloop()