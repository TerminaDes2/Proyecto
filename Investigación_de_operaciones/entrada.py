from modelo import Problema, Restriccion


def leer_problema():

    print("\n===== METODO SIMPLEX =====")

    tipo = input(
        "Ingrese el tipo de problema:\n"
        "1. Maximización\n"
        "2. Minimización\n"
        "Opción: "
    )

    if tipo == "1":
        tipo = "max"

    elif tipo == "2":
        tipo = "min"

    else:
        print("Opción no válida.")
        return None

    no_negativas = leer_no_negatividad()
    metodo = leer_metodo()

    cantidad_variables = int(
        input("\nIngrese la cantidad de variables: ")
    )

    objetivo = leer_funcion_objetivo(cantidad_variables)

    cantidad_restricciones = int(
        input("\nIngrese la cantidad de restricciones: ")
    )

    restricciones = leer_restricciones(
        cantidad_variables,
        cantidad_restricciones
    )

    return Problema(
        objetivo,
        restricciones,
        tipo,
        no_negativas,
        metodo
    )


def leer_no_negatividad():

    opcion = input(
        "\n¿Se usarán variables de no negatividad?\n"
        "1. Sí (Xj >= 0)\n"
        "2. No (variables libres)\n"
        "Opción: "
    )

    if opcion == "1":
        return True
    if opcion == "2":
        return False
    raise ValueError("La opción de no negatividad debe ser 1 o 2.")


def leer_metodo():

    opcion = input(
        "\nSeleccione el método:\n"
        "1. Simplex\n"
        "2. Dos fases\n"
        "3. Gran M\n"
        "Opción: "
    )

    if opcion == "1":
        return "simplex"
    if opcion == "2":
        return "dos_fases"
    if opcion == "3":
        return "gran_m"
    raise ValueError("El método debe ser 1, 2 o 3.")


def leer_funcion_objetivo(cantidad_variables):

    objetivo = []

    print("\n===== FUNCIÓN OBJETIVO =====")

    for i in range(cantidad_variables):

        coeficiente = float(
            input(
                f"Ingrese el coeficiente de X{i + 1}: "
            )
        )

        objetivo.append(coeficiente)

    return objetivo


def leer_restricciones(
    cantidad_variables,
    cantidad_restricciones
):

    restricciones = []

    print("\n===== RESTRICCIONES =====")

    for i in range(cantidad_restricciones):

        print(f"\n--- Restricción {i + 1} ---")

        coeficientes = []

        for j in range(cantidad_variables):

            coeficiente = float(
                input(
                    f"Ingrese el coeficiente de X{j + 1}: "
                )
            )

            coeficientes.append(coeficiente)

        signo = leer_signo()

        rhs = float(
            input("Ingrese el resultado de la restricción: ")
        )

        restricciones.append(
            Restriccion(
                coeficientes,
                signo,
                rhs
            )
        )

    return restricciones


def leer_signo():

    while True:

        opcion = input(
            "Ingrese la igualdad:\n"
            "1. <=\n"
            "2. >=\n"
            "3. =\n"
            "Opción: "
        )

        if opcion == "1":
            return "<="

        elif opcion == "2":
            return ">="

        elif opcion == "3":
            return "="

        else:
            print("Opción inválida.")