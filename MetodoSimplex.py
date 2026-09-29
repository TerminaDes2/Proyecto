#Metodo Simplex
def FuncionObjetivo ():
    cant_var = int(input("Ingrese la cantidad de variables que tiene el problema: "))
    coeficientes = []
    for i in range(cant_var):
        val_co = float(input(f"Ingrese el coeficiente de la variable X{i+1}: "))
        coeficientes.append(val_co)
    cant_res = int(input("Ingrese la cantidad de restricciones que tiene el problema: "))
    restricciones = Restriccion(cant_res, cant_var, coeficientes)
    Simplex(restricciones)
    
def Restriccion (cant_res, cant_var, coeficientes):
    restricciones = []
    for i in range(cant_res):
        val = []
        for j in range(cant_var):
            val_res = float(input(f"Ingrese el coeficiente de la restricción X{j + 1}: "))
            val.append(val_res)
        res = float(input(f"Ingrese el resultado de la restricción {i + 1}: "))
        val.insert(0,res)
        igualdad = int(input(f"Ingrese la igualdad de su restricción {i + 1}:\n1. Para <= (menor o igual)\n2. Para >= (mayor o igual)\n3. Para = (igua)\n"))
        val.insert(0,igualdad)
        restricciones.append(val)
    restricciones.append(coeficientes)
    return restricciones

def Simplex(restricciones):
    for i in range (len(restricciones)):
        for j in range (len(restricciones[i])):
            print()

FuncionObjetivo()