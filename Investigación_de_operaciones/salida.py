def mostrar_tabla(tabla):

    print("\n" + "=" * 60)
    print("TABLA SIMPLEX")
    print("=" * 60)

    # Encabezado
    print(
        f"{'Base':>8}",
        end=""
    )

    for columna in tabla.columnas:

        print(
            f"{columna:>10}",
            end=""
        )

    print()

    # Filas de restricciones
    for i, fila in enumerate(
        tabla.matriz[:-1]
    ):

        print(
            f"{tabla.base[i]:>8}",
            end=""
        )

        for valor in fila:

            print(
                f"{valor:10.2f}",
                end=""
            )

        print()

    # Z
    print(
        f"{'Z':>8}",
        end=""
    )

    for valor in tabla.matriz[-1]:

        print(
            f"{valor:10.2f}",
            end=""
        )

    print()


def mostrar_iteracion(
    tabla,
    numero
):

    print(
        f"\n===== ITERACIÓN {numero} ====="
    )

    mostrar_tabla(tabla)


def obtener_solucion(
    tabla,
    cantidad_variables
):

    valores = [0.0] * cantidad_variables

    cantidad_restricciones = len(
        tabla.matriz
    ) - 1

    for variable in range(
        cantidad_variables
    ):

        nombre = (
            f"X{variable + 1}"
        )

        if nombre not in tabla.columnas:
            continue

        columna = tabla.columnas.index(
            nombre
        )

        fila_basica = -1

        es_basica = True

        for fila in range(
            cantidad_restricciones
        ):

            valor = (
                tabla.matriz[fila][columna]
            )

            if abs(valor - 1) < 1e-9:

                if fila_basica == -1:
                    fila_basica = fila

                else:
                    es_basica = False

            elif abs(valor) > 1e-9:

                es_basica = False

        if (
            es_basica
            and fila_basica != -1
        ):

            valores[variable] = (
                tabla.matriz[fila_basica][-1]
            )

    z = tabla.matriz[-1][-1]

    return valores, z


def mostrar_resultado(
    resultado,
    cantidad_variables
):

    print("\n" + "=" * 60)
    print("RESULTADO")
    print("=" * 60)

    estado = resultado["estado"]

    if estado == "no_acotado":

        print(
            "El problema no tiene una solución "
            "óptima acotada."
        )

        return

    if estado != "optimo":

        print("No se pudo obtener una solución.")

        return

    valores, z = obtener_solucion(
        resultado["tabla"],
        cantidad_variables
    )

    print("\nSolución óptima:")

    for i, valor in enumerate(valores):

        print(
            f"X{i + 1} = {valor:.4f}"
        )

    print(
        f"\nZ = {z:.4f}"
    )

    print(
        f"Iteraciones: "
        f"{resultado['iteraciones']}"
    )