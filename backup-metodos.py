""" 
def metodo_tangente2(iteraciones, tolerancia, pInicial):
    nuevoP=pInicial
    print("Aproximacion inicial: ", nuevoP, "\n")
    if (evaluar_funcion(nuevoP)==0):
        print("Valor exacto de la raiz: ", nuevoP)
        return nuevoP   
    i=0
    while(i<iteraciones):
        pAnterior=nuevoP
        i+=1
        print ("Iteración: ", i)
        derivada=evaluar_derivada(pAnterior)

        if ((evaluar_derivada(pAnterior)==0) or derivada is None or not smp.sympify(derivada).is_real):
            print("La derivada es 0. No se puede seguir con el metodo")
            return
        
        nuevoP=(pAnterior-(evaluar_funcion(pAnterior)/evaluar_derivada(pAnterior)))
        if (evaluar_funcion(nuevoP) is None or not smp.sympify(evaluar_funcion(nuevoP)).is_real):
            print(f"El valor de la función en p{i} no es real. No se puede seguir")
            return
        print(f"Valor de p{i}: ", nuevoP)
        print(f"Funcion evaluada en p{i}: ", evaluar_funcion(nuevoP))
        print("Tolerancia: ",abs(nuevoP-pAnterior))
        if (evaluar_funcion(nuevoP)==0):
            print("\nValor exacto de la raiz: ", nuevoP)
            return nuevoP   
        print("\n")
        if(abs(nuevoP-pAnterior)<tolerancia):
            print("Procedimiento terminado por llegar al límite de tolerancia.")
            return nuevoP
        
    if (i==iteraciones):
        print("El metodo se detiene luego de haber realizado la cantidad maxima de iteraciones.")
    print(f"Función evaluada en p{i}", evaluar_funcion(nuevoP))
    return nuevoP
    
    
    
#Tolerancia es la exactitud del 0
def biseccion2(iteraciones, tolerancia, a, b):
    i=0
    c=a+((b-a)/2)
    if (evaluar_funcion(c)==0):
        print("Valor exacto de la raiz: ", c)
        return c
    
    while(i<iteraciones):
        c=a+((b-a)/2)

        i+=1
        print ("Iteración: ", i)
        print("Valor de a: ", a, "      Función evaluada en a: ", evaluar_funcion(a))
        print("Valor de b: ", b, "      Función evaluada en b: ", evaluar_funcion(b))
        if (evaluar_funcion(c)==0):
            print("Valor exacto de la raiz: ", c)
            return c
        print("Valor aproximado de la raiz (c): ", c)
        
        if ((signo(evaluar_funcion(c))*signo(evaluar_funcion(a)))>0):
            anterior=a
            a=c
        else:
            anterior=b
            b=c
            
        if(abs(c-anterior)<tolerancia):
            print("Procedimiento terminado por llegar al límite de tolerancia.")
            return c
        
        print("\n")
        
    if (i==iteraciones):
        print("El metodo se detiene luego de haber realizado la cantidad maxima de iteraciones.")
    print("Valor de la función en c: ", evaluar_funcion(c))
    return c
 """