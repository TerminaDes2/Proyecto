from modelo import TablaSimplex


def preparar_simplex(problema):

    validar_problema(problema)

    cantidad_restricciones = len(
        problema.restricciones
    )

    cantidad_variables = len(
        problema.objetivo
    )

    matriz = []

    columnas = []

    base = []

    # -----------------------------------------
    # Nombres de variables originales
    # -----------------------------------------

    for i in range(cantidad_variables):

        columnas.append(
            f"X{i + 1}"
        )

    # -----------------------------------------
    # Nombres de variables de holgura
    # -----------------------------------------

    for i in range(cantidad_restricciones):

        columnas.append(
            f"S{i + 1}"
        )

    columnas.append("RHS")

    # -----------------------------------------
    # Crear restricciones
    # -----------------------------------------

    for i, restriccion in enumerate(
        problema.restricciones
    ):

        fila = []

        # Variables originales
        for coeficiente in restriccion.coeficientes:
            fila.append(coeficiente)

        # Variables de holgura
        for j in range(cantidad_restricciones):

            if i == j:
                fila.append(1)

            else:
                fila.append(0)

        # RHS
        fila.append(restriccion.rhs)

        matriz.append(fila)

        # Variable básica inicial
        base.append(
            f"S{i + 1}"
        )

    # -----------------------------------------
    # Fila Z
    # -----------------------------------------

    fila_objetivo = []

    for coeficiente in problema.objetivo:

        fila_objetivo.append(
            -coeficiente
        )

    # Holguras
    for _ in range(cantidad_restricciones):

        fila_objetivo.append(0)

    # RHS
    fila_objetivo.append(0)

    matriz.append(fila_objetivo)

    return TablaSimplex(
        matriz,
        columnas,
        base
    )


def validar_problema(problema):

    for restriccion in problema.restricciones:

        if restriccion.signo != "<=":

            raise ValueError(
                "Esta versión de Simplex solamente "
                "acepta restricciones <=."
            )