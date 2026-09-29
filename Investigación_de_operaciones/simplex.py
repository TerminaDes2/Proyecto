from math import isclose


EPSILON = 1e-9


def resolver(tabla):

    iteracion = 0

    while True:

        columna_pivote = buscar_columna_pivote(
            tabla
        )

        # No existen coeficientes negativos.
        # La solución es óptima.
        if columna_pivote == -1:

            return {
                "estado": "optimo",
                "tabla": tabla,
                "iteraciones": iteracion
            }

        fila_pivote = buscar_fila_pivote(
            tabla,
            columna_pivote
        )

        # Ninguna fila puede salir.
        if fila_pivote == -1:

            return {
                "estado": "no_acotado",
                "tabla": tabla,
                "iteraciones": iteracion
            }

        pivotear(
            tabla,
            fila_pivote,
            columna_pivote
        )

        actualizar_base(
            tabla,
            fila_pivote,
            columna_pivote
        )

        iteracion += 1


def buscar_columna_pivote(tabla):

    fila_objetivo = tabla.matriz[-1]

    columna_pivote = -1

    menor = 0

    # No revisar RHS
    for columna in range(
        len(fila_objetivo) - 1
    ):

        valor = fila_objetivo[columna]

        if valor < menor:

            menor = valor

            columna_pivote = columna

    return columna_pivote


def buscar_fila_pivote(
    tabla,
    columna_pivote
):

    fila_pivote = -1

    menor_razon = float("inf")

    cantidad_filas = (
        len(tabla.matriz) - 1
    )

    for fila in range(cantidad_filas):

        elemento = (
            tabla.matriz[fila][columna_pivote]
        )

        rhs = (
            tabla.matriz[fila][-1]
        )

        # Solo valores positivos
        if elemento > EPSILON:

            razon = rhs / elemento

            if razon < menor_razon:

                menor_razon = razon

                fila_pivote = fila

    return fila_pivote


def pivotear(
    tabla,
    fila_pivote,
    columna_pivote
):

    matriz = tabla.matriz

    pivote = (
        matriz[fila_pivote][columna_pivote]
    )

    # -----------------------------------------
    # 1. Normalizar fila pivote
    # -----------------------------------------

    for columna in range(
        len(matriz[fila_pivote])
    ):

        matriz[fila_pivote][columna] /= pivote

    # -----------------------------------------
    # 2. Hacer ceros
    # -----------------------------------------

    for fila in range(len(matriz)):

        if fila == fila_pivote:
            continue

        factor = (
            matriz[fila][columna_pivote]
        )

        for columna in range(
            len(matriz[fila])
        ):

            matriz[fila][columna] -= (
                factor
                * matriz[fila_pivote][columna]
            )

    limpiar_decimales(tabla)


def actualizar_base(
    tabla,
    fila_pivote,
    columna_pivote
):

    tabla.base[fila_pivote] = (
        tabla.columnas[columna_pivote]
    )


def limpiar_decimales(tabla):

    for fila in tabla.matriz:

        for columna in range(len(fila)):

            if isclose(
                fila[columna],
                0,
                abs_tol=EPSILON
            ):

                fila[columna] = 0.0