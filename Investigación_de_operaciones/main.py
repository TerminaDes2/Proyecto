from entrada import leer_problema
from metodos import resolver_problema
from salida import (
    mostrar_tabla,
    mostrar_traza,
    mostrar_resultado
)


def main():

    try:

        problema = leer_problema()

        if problema is None:
            return

        resultado = resolver_problema(problema)

        print("\n===== TABLA FINAL =====")
        mostrar_tabla(resultado["tabla"])
        if resultado.get("traza") is not None:
            mostrar_traza(resultado["traza"])

        # -----------------------------------------
        # Mostrar resultado
        # -----------------------------------------

        mostrar_resultado(
            resultado,
            len(problema.objetivo),
            problema
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