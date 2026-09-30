def mostrar_tabla(tabla):

    print("\n" + "=" * 60)
    print("TABLA SIMPLEX")
    print("=" * 60)
    print(f"{'Base':>8}", end="")
    for columna in tabla.columnas:
        print(f"{columna:>10}", end="")
    print()

    for indice, fila in enumerate(tabla.matriz[:-1]):
        print(f"{tabla.base[indice]:>8}", end="")
        for valor in fila:
            print(f"{valor:10.2f}", end="")
        print()

    print(f"{'Z':>8}", end="")
    for valor in tabla.matriz[-1]:
        print(f"{valor:10.2f}", end="")
    print()


def mostrar_traza(traza):

    print("\n===== DETALLE DE ITERACIONES =====")
    if not traza:
        print("No se necesitaron pivoteos.")
        return

    for numero, paso in enumerate(traza, 1):
        razones = ", ".join(
            f"{base}: {valor:.4f}" for base, valor in paso["divisiones"]
        ) or "ninguna"
        print(
            f"Iteración {numero} (fase {paso['fase']}): "
            f"columna pivote = {paso['columna']}; "
            f"divisiones = {razones}; "
            f"elemento pivote = {paso['elemento']}"
        )


def obtener_solucion(tabla, cantidad_variables):

    valores = [0.0] * cantidad_variables
    cantidad_restricciones = len(tabla.matriz) - 1
    for variable, transformacion in enumerate(tabla.transformaciones_nombres):
        for nombre, signo in transformacion:
            if nombre not in tabla.columnas:
                continue
            columna = tabla.columnas.index(nombre)
            for fila in range(cantidad_restricciones):
                if (abs(tabla.matriz[fila][columna] - 1) < 1e-9 and
                        all(fila == otra or abs(tabla.matriz[otra][columna]) < 1e-9
                            for otra in range(cantidad_restricciones))):
                    valores[variable] += signo * tabla.matriz[fila][-1]
                    break
    z = tabla.matriz[-1][-1]
    if tabla.tipo_objetivo == "min":
        z = -z
    return valores, z


def mostrar_resultado(resultado, cantidad_variables, problema):

    print("\n" + "=" * 60)
    print("RESULTADO")
    print("=" * 60)
    estado = resultado["estado"]

    if estado == "sin_solucion":
        print("El problema no tiene solución factible (no existe BF).")
        return
    if estado == "no_acotado":
        print("El problema es no acotado; no tiene solución óptima finita.")
        return
    if estado != "optimo":
        print(f"No se pudo obtener una solución: {estado}.")
        return

    valores, z = obtener_solucion(resultado["tabla"], cantidad_variables)
    print("\nSolución óptima / solución BF:")
    for indice, valor in enumerate(valores):
        print(f"X{indice + 1} = {valor:.4f}")
    print(f"\nZ = {z:.4f}")
    print(f"Iteraciones: {resultado['iteraciones']}")