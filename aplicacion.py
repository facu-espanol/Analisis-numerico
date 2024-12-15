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
            tolerancia = 0.000001
        else:  
            tolerancia = float(entrada_tolerancia.get())
        funcion_actual = funcion
        # Validaciones básicas
        if a >= b:
            messagebox.showerror("Error", "El valor de 'a' debe ser menor que 'b'.")
            return
        
        if (not is_continuous_on_interval(f, a, b)):
            messagebox.showerror("Error", "La funcion no es continua en el intervalo dado.")
            return
            
        if ((evaluar_funcion(a)>0 and evaluar_funcion(b) > 0) or  (evaluar_funcion(a)<0 and evaluar_funcion(b) < 0)):
            messagebox.showerror("Error", "La funcion debe tomar signos distintos en los extremos del intervalo.")
            return
        
        if iteraciones <= 0:
            messagebox.showerror("Error", "El número de iteraciones debe ser mayor que 0.")
            return
        if tolerancia <= 0:
            messagebox.showerror("Error", "La tolerancia debe ser un valor positivo.")
            return

        # Almacenar la función ingresada

        # Crear un rango de valores para x con un margen de ±5
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
        
        
        if metodo_seleccionado.get() == "Bisección":
            resultado = biseccion(iteraciones, tolerancia, a, b)
        elif metodo_seleccionado.get() == "Tangente":
            resultado = metodo_tangente(iteraciones, tolerancia, (a+b)/2)
        else:
            messagebox.showerror("Error", "Método no válido seleccionado.")
            return
        
        
        #biseccion(iteraciones, tolerancia, a, b)
        #metodo_tangente(iteraciones, tolerancia, (a+b)/2)
        #hola=evaluar_derivada(f,3)
        #print("Derivada en 3 ", hola)
        # Actualizar el lienzo
        canvas.draw()
    except Exception as e:
        messagebox.showerror("Error", f"La función ingresada no es válida: {e}")

def evaluar_funcion(x):
    global funcion_actual
    try:
        # Evaluar la función almacenada en el punto x
        y = eval(funcion_actual, {"__builtins__": None}, {"x": x, **np.__dict__})
        return y
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

#Tolerancia es la exactitud del 0
def biseccion(iteraciones, tolerancia, a, b):
    i=0
    c=a+((b-a)/2)
    print("Hola mundo")
    if (evaluar_funcion(c)==0):
        print("Valor exacto de la raiz: ", c)
        return c
    
    while(i<iteraciones and abs(evaluar_funcion(c))>tolerancia):
        c=a+((b-a)/2)
        if (evaluar_funcion(c)==0):
            print("Valor exacto de la raiz: ", c)
            return c

        i+=1
        print ("Iteración: ", i)
        print("Valor de a: ", a)
        print("Valor de b: ", b)
        print("Valor aproximado de la raiz: ", c)
        
        #smp.sign(evaluar_funcion(c))
        if ((signo(evaluar_funcion(c))*signo(evaluar_funcion(a)))>0):
            a=c
        else:
            b=c
        #ver por que entra aca y despues sigue ejecutando
        if(abs(evaluar_funcion(c))<tolerancia):
            print("Procedimiento terminado por llegar al límite de tolerancia.")
            return
        print("\n")
        
    return c


def evaluar_derivada(x):
    global funcion_simp
    variable = smp.symbols("x")
    derivada= smp.diff(funcion_simp)
    return float (derivada.evalf(subs={variable: x}))



def metodo_tangente(iteraciones, tolerancia, pInicial):
    nuevoP=pInicial
    if (evaluar_funcion(nuevoP)==0):
        print("Valor exacto de la raiz: ", nuevoP)
        return nuevoP   
    #if (evaluar_derivada(nuevoP)==0):
    #    nuevoP=nuevoP+0.1
    i=0
    while(i<iteraciones and abs(evaluar_funcion(nuevoP))>tolerancia):
        pAnterior=nuevoP
        if (evaluar_derivada(pAnterior)==0):
            print("La derivada es 0. No se puede seguir con el metodo")
            return
        nuevoP=(pAnterior-(evaluar_funcion(pAnterior)/evaluar_derivada(pAnterior)))
        if (evaluar_funcion(nuevoP)==0):
            print("Valor exacto de la raiz: ", nuevoP)
            return nuevoP   
        i+=1
        print ("Iteración: ", i)
        print("Valor aproximado de la raiz: ", nuevoP)
    
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


# Etiquetas y entradas para iteraciones y tolerancia
etiqueta_iteraciones = tk.Label(ventana, text="Número de iteraciones:")
etiqueta_iteraciones.pack(pady=5)
entrada_iteraciones = tk.Entry(ventana, width=20)
entrada_iteraciones.pack(pady=5)

etiqueta_tolerancia = tk.Label(ventana, text="Tolerancia:")
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
boton_graficar = tk.Button(ventana, text="Graficar", command=graficar_funcion)
boton_graficar.pack(pady=10)

# Área para el gráfico
fig, ax = plt.subplots(figsize=(7, 5))
canvas = FigureCanvasTkAgg(fig, master=ventana)
canvas.get_tk_widget().pack()

# Vincular las teclas de dirección y la rueda del ratón para mover el gráfico y hacer zoom
ventana.bind("<Left>", mover_izquierda)
ventana.bind("<Right>", mover_derecha)
ventana.bind("<Up>", mover_arriba)
ventana.bind("<Down>", mover_abajo)
ventana.bind("<Button-4>", zoom)   # Linux (rueda arriba)
ventana.bind("<Button-5>", zoom)   # Linux (rueda abajo)

# Iniciar el bucle principal de la aplicación
ventana.mainloop()
