from canonico import construir_tabla_canonica
from simplex import resolver as resolver_simplex_clasico
from salida import mostrar_tabla


TOLERANCIA = 1e-9


def resolver_problema(problema):
    if problema.metodo == "simplex":
        return resolver_simplex(problema)
    tabla = construir_tabla_canonica(problema)
    print("\n===== TABLA INICIAL =====")
    if problema.metodo == "gran_m":
        tabla.mostrar_m = True
        mostrar_tabla(tabla, mostrar_m=True)
        return resolver_gran_m(tabla)
    mostrar_tabla(tabla)
    return resolver_dos_fases(tabla)


def resolver_simplex(problema):
    if not problema.no_negativas:
        raise ValueError(
            "El método Simplex requiere variables de no negatividad. "
            "Use Dos fases o Gran M para variables libres."
        )

    if any(restriccion.signo != "<=" for restriccion in problema.restricciones):
        raise ValueError(
            "El método Simplex requiere restricciones <=. "
            "Use Dos fases o Gran M para >= o =."
        )

    tabla = construir_tabla_canonica(problema)
    print("\n===== TABLA INICIAL =====")
    mostrar_tabla(tabla)

    resultado = resolver_simplex_clasico(
        tabla,
        mostrar_iteracion
    )
    resultado["traza"] = None
    return resultado


def mostrar_iteracion(tabla, iteracion):
    print(f"\n===== ITERACIÓN {iteracion} =====")
    mostrar_tabla(tabla)


def resolver_dos_fases(tabla):
    traza = []
    preparar_objetivo(tabla, {nombre: -1.0 for nombre in tabla.artificiales})
    estado = simplex(tabla, traza, 1, mostrar_tablas=True)
    if estado == "no_acotado" or tabla.matriz[-1][-1] < -TOLERANCIA:
        return resultado(tabla, traza, "sin_solucion")
    quitar_artificiales(tabla)
    preparar_objetivo(tabla, tabla.costos_objetivo)
    estado = simplex(tabla, traza, 2, mostrar_tablas=True)
    return resultado(tabla, traza, "optimo" if estado == "optimo" else estado)


def resolver_gran_m(tabla):
    traza = []
    costos = {nombre: -1_000_000.0 for nombre in tabla.artificiales}
    costos.update(tabla.costos_objetivo)
    preparar_objetivo(tabla, costos)
    estado = simplex(tabla, traza, 1, mostrar_tablas=True)
    if any(nombre in tabla.artificiales and tabla.matriz[fila][-1] > TOLERANCIA
            for fila, nombre in enumerate(tabla.base)):
        estado = "sin_solucion"
    return resultado(tabla, traza, "optimo" if estado == "optimo" else estado)


def preparar_objetivo(tabla, costos):
    fila = [0.0] * len(tabla.columnas)
    for columna, nombre in enumerate(tabla.columnas[:-1]):
        fila[columna] = -costos.get(nombre, 0.0)
    for fila_restriccion, nombre in enumerate(tabla.base):
        costo = costos.get(nombre, 0.0)
        for columna, valor in enumerate(tabla.matriz[fila_restriccion]):
            fila[columna] += costo * valor
    tabla.matriz[-1] = fila


def simplex(tabla, traza, fase, mostrar_tablas=False):
    iteracion = 0
    if mostrar_tablas:
        mostrar_tabla_fase(tabla, fase, inicial=True)

    while True:
        columna = columna_pivote(tabla)
        if columna == -1:
            return "optimo"
        fila, divisiones = fila_pivote(tabla, columna)
        traza.append({
            "fase": fase,
            "columna": tabla.columnas[columna],
            "divisiones": divisiones,
            "fila": fila,
            "elemento": None if fila == -1 else tabla.matriz[fila][columna]
        })
        if fila == -1:
            return "no_acotado"
        pivotear(tabla, fila, columna)
        tabla.base[fila] = tabla.columnas[columna]
        iteracion += 1
        if mostrar_tablas:
            mostrar_tabla_fase(tabla, fase, iteracion)


def mostrar_tabla_fase(tabla, fase, iteracion=0, inicial=False):
    if inicial:
        print(f"\n===== FASE {fase} - TABLA INICIAL =====")
    else:
        print(f"\n===== FASE {fase} - ITERACIÓN {iteracion} =====")
    mostrar_tabla(tabla, mostrar_m=getattr(tabla, "mostrar_m", False))


def columna_pivote(tabla):
    valores = tabla.matriz[-1][:-1]
    minimo = min(valores, default=0)
    return valores.index(minimo) if minimo < 0 else -1


def fila_pivote(tabla, columna):
    divisiones = []
    mejor = -1
    menor = float("inf")
    for fila in range(len(tabla.matriz) - 1):
        elemento = tabla.matriz[fila][columna]
        if elemento > 0:
            razon = tabla.matriz[fila][-1] / elemento
            divisiones.append((tabla.base[fila], razon))
            if razon < menor:
                menor = razon
                mejor = fila
    return mejor, divisiones


def pivotear(tabla, fila_pivote, columna_pivote):
    matriz = tabla.matriz
    pivote = matriz[fila_pivote][columna_pivote]
    matriz[fila_pivote] = [valor / pivote for valor in matriz[fila_pivote]]
    for fila, valores in enumerate(matriz):
        if fila == fila_pivote:
            continue
        factor = valores[columna_pivote]
        matriz[fila] = [valor - factor * pivote_valor
                        for valor, pivote_valor in zip(valores, matriz[fila_pivote])]
    for valores in matriz:
        for columna, valor in enumerate(valores):
            if valor == 0:
                valores[columna] = 0.0


def quitar_artificiales(tabla):
    indices = [i for i, nombre in enumerate(tabla.columnas) if nombre in tabla.artificiales]
    for indice in reversed(indices):
        tabla.columnas.pop(indice)
        for fila in tabla.matriz:
            fila.pop(indice)
    tabla.transformaciones_nombres = [
        [(nombre, signo) for nombre, signo in transformacion
            if nombre not in tabla.artificiales]
        for transformacion in tabla.transformaciones_nombres
    ]
    tabla.artificiales = []


def resultado(tabla, traza, estado):
    return {"estado": estado, "tabla": tabla, "traza": traza, "iteraciones": len(traza)}