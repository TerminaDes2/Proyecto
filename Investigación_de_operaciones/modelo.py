class Restriccion:

    def __init__(self, coeficientes, signo, rhs):
        self.coeficientes = coeficientes
        self.signo = signo
        self.rhs = rhs


class Problema:

    def __init__(self, objetivo, restricciones, tipo="max"):
        self.objetivo = objetivo
        self.restricciones = restricciones
        self.tipo = tipo


class TablaSimplex:

    def __init__(self, matriz, columnas, base):
        self.matriz = matriz
        self.columnas = columnas
        self.base = base