from modelo import TablaSimplex


def construir_tabla_canonica(problema):
    """Convierte restricciones a un tableau con holguras y artificiales."""
    cantidad_variables = len(problema.objetivo)
    columnas_variables = []
    transformaciones = []

    for indice in range(cantidad_variables):
        nombre = f"X{indice + 1}"
        if problema.no_negativas:
            columnas_variables.append(nombre)
            transformaciones.append([(len(columnas_variables) - 1, 1)])
        else:
            columnas_variables.extend([f"{nombre}+", f"{nombre}-"])
            transformaciones.append([
                (len(columnas_variables) - 2, 1),
                (len(columnas_variables) - 1, -1)
            ])

    restricciones_normalizadas = []
    columnas_auxiliares = []

    for indice, restriccion in enumerate(problema.restricciones):
        coeficientes = [0.0] * len(columnas_variables)
        for variable, coeficiente in enumerate(restriccion.coeficientes):
            for columna, signo in transformaciones[variable]:
                coeficientes[columna] = coeficiente * signo

        signo = restriccion.signo
        rhs = restriccion.rhs
        if rhs < 0:
            coeficientes = [-valor for valor in coeficientes]
            rhs = -rhs
            signo = {"<=": ">=", ">=": "<=", "=": "="}[signo]

        if signo == "<=":
            auxiliares = [(f"S{indice + 1}", 1.0)]
        elif signo == ">=":
            auxiliares = [(f"E{indice + 1}", -1.0), (f"A{indice + 1}", 1.0)]
        elif signo == "=":
            auxiliares = [(f"A{indice + 1}", 1.0)]
        else:
            raise ValueError(f"Signo no válido: {signo}")

        restricciones_normalizadas.append((coeficientes, rhs, auxiliares))
        columnas_auxiliares.extend(nombre for nombre, _ in auxiliares)

    columnas = columnas_variables + columnas_auxiliares
    indices_auxiliares = {
        nombre: len(columnas_variables) + indice
        for indice, nombre in enumerate(columnas_auxiliares)
    }
    filas = []
    bases = []
    artificiales = []
    for coeficientes, rhs, auxiliares in restricciones_normalizadas:
        fila = coeficientes + [0.0] * len(columnas_auxiliares) + [rhs]
        for nombre, coeficiente in auxiliares:
            fila[indices_auxiliares[nombre]] = coeficiente
            if nombre.startswith("A"):
                artificiales.append(nombre)
        bases.append(auxiliares[-1][0] if auxiliares[-1][0].startswith("A")
                     else auxiliares[0][0])
        filas.append(fila)

    cantidad_columnas = len(columnas)

    objetivo = list(problema.objetivo)
    if problema.tipo == "min":
        objetivo = [-valor for valor in objetivo]
    fila_objetivo = [0.0] * cantidad_columnas + [0.0]
    for variable, coeficiente in enumerate(objetivo):
        for columna, signo in transformaciones[variable]:
            fila_objetivo[columna] = -coeficiente * signo

    columnas.append("RHS")
    tabla = TablaSimplex(filas + [fila_objetivo], columnas, bases)
    tabla.artificiales = artificiales
    tabla.columnas_originales = [f"X{i + 1}" for i in range(cantidad_variables)]
    tabla.transformaciones = transformaciones
    tabla.transformaciones_nombres = [
        [(columnas[columna], signo) for columna, signo in transformacion]
        for transformacion in transformaciones
    ]
    tabla.objetivo_original = objetivo
    tabla.costos_objetivo = {
        nombre: objetivo[indice] * signo
        for indice, transformacion in enumerate(tabla.transformaciones_nombres)
        for nombre, signo in transformacion
    }
    tabla.tipo_objetivo = problema.tipo
    return tabla