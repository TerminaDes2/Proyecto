from entrada import leer_problema
from tabla import preparar_simplex
from simplex import resolver
from salida import (
    mostrar_tabla,
    mostrar_iteracion,
    mostrar_resultado
)


def main():

    try:

        problema = leer_problema()

        if problema is None:
            return

        # -----------------------------------------
        # Preparar problema
        # -----------------------------------------

        tabla = preparar_simplex(
            problema
        )

        print("\n===== TABLA INICIAL =====")

        mostrar_tabla(tabla)

        # -----------------------------------------
        # Resolver
        # -----------------------------------------

        resultado = resolver(
            tabla,
            mostrar_iteracion
        )

        # -----------------------------------------
        # Mostrar resultado
        # -----------------------------------------

        mostrar_resultado(
            resultado,
            len(problema.objetivo)
        )

    except ValueError as error:

        print(
            f"\nError: {error}"
        )

    except Exception as error:

        print(
            f"\nError inesperado: {error}"
        )


if __name__ == "__main__":
    main()