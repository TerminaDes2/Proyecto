import io
import math
import tkinter as tk
from copy import deepcopy
from contextlib import redirect_stdout
from tkinter import messagebox, ttk

from modelo import Problema, Restriccion
from metodos import resolver_problema
from salida import (
    mostrar_resultado,
    mostrar_tabla,
    mostrar_traza,
    obtener_solucion,
)


class InterfazSimplex:

    def __init__(self, ventana):
        self.ventana = ventana
        self.ventana.title("Métodos de programación lineal")
        self.ventana.geometry("1280x850")
        self.ventana.minsize(1000, 700)
        self.ventana.configure(bg="#f2f5f1")
        self._configurar_estilos()

        self.tipo = tk.StringVar(value="max")
        self.no_negativas = tk.BooleanVar(value=True)
        self.metodo = tk.StringVar(value="simplex")
        self.cantidad_variables = tk.IntVar(value=2)
        self.cantidad_restricciones = tk.IntVar(value=2)
        self.coeficientes_objetivo = []
        self.coeficientes_restricciones = []
        self.signos_restricciones = []
        self.rhs_restricciones = []

        self._crear_encabezado()
        self._crear_formulario()
        self._crear_controles()
        self._crear_salida()
        self._actualizar_formulario()

    def _configurar_estilos(self):
        estilos = ttk.Style(self.ventana)
        estilos.theme_use("clam")
        estilos.configure(".", font=("Segoe UI", 10))
        estilos.configure("App.TFrame", background="#f2f5f1")
        estilos.configure("Header.TFrame", background="#173b35")
        estilos.configure(
            "Card.TLabelframe",
            background="#ffffff",
            bordercolor="#d5ded7",
            relief="solid",
            borderwidth=1,
        )
        estilos.configure(
            "Card.TLabelframe.Label",
            background="#ffffff",
            foreground="#24443d",
            font=("Segoe UI Semibold", 10),
        )
        estilos.configure(
            "TLabel", background="#ffffff", foreground="#34443e"
        )
        estilos.configure(
            "Title.TLabel",
            background="#173b35",
            foreground="#ffffff",
            font=("Segoe UI Semibold", 22),
        )
        estilos.configure(
            "Subtitle.TLabel",
            background="#173b35",
            foreground="#c5d7ce",
            font=("Segoe UI", 10),
        )
        estilos.configure(
            "Section.TLabel",
            background="#ffffff",
            foreground="#63736b",
            font=("Segoe UI Semibold", 9),
        )
        estilos.configure(
            "TNotebook", background="#ffffff", borderwidth=0
        )
        estilos.configure(
            "TNotebook.Tab", padding=(14, 8), font=("Segoe UI Semibold", 9)
        )
        estilos.configure(
            "Treeview",
            background="#ffffff",
            fieldbackground="#ffffff",
            foreground="#263a33",
            rowheight=27,
            borderwidth=0,
        )
        estilos.configure(
            "Treeview.Heading",
            background="#e8eee9",
            foreground="#24443d",
            font=("Segoe UI Semibold", 9),
            padding=7,
        )
        estilos.configure(
            "Accent.TButton",
            background="#b94732",
            foreground="#ffffff",
            borderwidth=0,
            padding=(16, 8),
            font=("Segoe UI Semibold", 10),
        )
        estilos.map(
            "Accent.TButton",
            background=[("active", "#a13c2a"), ("pressed", "#873321")],
        )
        estilos.configure(
            "Secondary.TButton",
            background="#e6ece7",
            foreground="#29443b",
            borderwidth=0,
            padding=(12, 8),
        )
        estilos.map(
            "Secondary.TButton",
            background=[("active", "#d4dfd6"), ("pressed", "#c5d3c8")],
        )
        estilos.configure(
            "TEntry",
            fieldbackground="#fbfdff",
            bordercolor="#cbd8d0",
            padding=5,
        )
        estilos.configure(
            "TCombobox",
            fieldbackground="#ffffff",
            bordercolor="#cbd8d0",
            padding=4,
        )

    def _crear_encabezado(self):
        encabezado = ttk.Frame(self.ventana, style="Header.TFrame")
        encabezado.pack(fill="x", padx=20, pady=(18, 12))
        ttk.Label(
            encabezado,
            text="Programación lineal",
            style="Title.TLabel",
        ).pack(anchor="w", padx=20, pady=(14, 0))
        ttk.Label(
            encabezado,
            text="Resuelve problemas con Simplex, Dos fases o Gran M",
            style="Subtitle.TLabel",
        ).pack(anchor="w", padx=20, pady=(2, 14))

    def _crear_controles(self):
        controles = ttk.LabelFrame(
            self.panel_entrada, text="  Configuración  ",
            style="Card.TLabelframe",
        )
        controles.grid(row=0, column=0, sticky="ew", pady=(0, 10), ipady=5)
        for columna in range(4):
            controles.columnconfigure(columna, weight=1)

        ttk.Label(controles, text="OBJETIVO", style="Section.TLabel").grid(
            row=0, column=0, columnspan=4, padx=12, pady=(8, 2), sticky="w"
        )
        ttk.Radiobutton(
            controles, text="Maximización", variable=self.tipo, value="max"
        ).grid(row=1, column=0, columnspan=2, padx=12, pady=(0, 4), sticky="w")
        ttk.Radiobutton(
            controles, text="Minimización", variable=self.tipo, value="min"
        ).grid(row=1, column=2, columnspan=2, padx=4, pady=(0, 4), sticky="w")

        ttk.Checkbutton(
            controles,
            text="Variables no negativas (Xj >= 0)",
            variable=self.no_negativas,
        ).grid(row=2, column=0, columnspan=4, padx=12, pady=(0, 8), sticky="w")

        ttk.Label(controles, text="MÉTODO", style="Section.TLabel").grid(
            row=3, column=0, columnspan=4, padx=12, pady=(0, 2), sticky="w"
        )
        metodos = ttk.Combobox(
            controles,
            textvariable=self.metodo,
            values=("simplex", "dos_fases", "gran_m"),
            state="readonly",
            width=16,
        )
        metodos.grid(row=4, column=0, columnspan=4, padx=12, pady=(0, 8), sticky="ew")

        ttk.Label(controles, text="DIMENSIONES", style="Section.TLabel").grid(
            row=5, column=0, columnspan=4, padx=12, pady=(0, 2), sticky="w"
        )
        ttk.Label(controles, text="Variables").grid(
            row=6, column=0, padx=(12, 4), pady=(0, 8), sticky="w"
        )
        ttk.Spinbox(
            controles,
            from_=1,
            to=20,
            textvariable=self.cantidad_variables,
            width=5,
            command=self._actualizar_formulario,
        ).grid(row=6, column=1, padx=(0, 6), pady=(0, 8), sticky="w")
        ttk.Label(controles, text="Restricciones").grid(
            row=6, column=2, padx=(4, 2), pady=(0, 8), sticky="w"
        )
        ttk.Spinbox(
            controles,
            from_=1,
            to=20,
            textvariable=self.cantidad_restricciones,
            width=5,
            command=self._actualizar_formulario,
        ).grid(row=6, column=3, padx=(0, 12), pady=(0, 8), sticky="w")

        ttk.Button(
            controles, text="Actualizar formulario",
            command=self._actualizar_formulario,
            style="Secondary.TButton",
        ).grid(row=7, column=0, columnspan=4, padx=12, pady=(0, 6), sticky="ew")
        ttk.Button(
            controles, text="Resolver",
            command=self._resolver,
            style="Accent.TButton",
        ).grid(row=8, column=0, columnspan=2, padx=(12, 4), pady=(0, 8), sticky="ew")
        ttk.Button(
            controles, text="Graficar",
            command=self._graficar,
            style="Secondary.TButton",
        ).grid(row=8, column=2, columnspan=2, padx=(4, 12), pady=(0, 8), sticky="ew")

    def _crear_formulario(self):
        self.contenido = ttk.Panedwindow(self.ventana, orient="horizontal")
        self.contenido.pack(fill="both", expand=True, padx=20, pady=(0, 18))
        self.formulario = ttk.Frame(self.contenido, style="App.TFrame")
        self.contenido.add(self.formulario, weight=1)
        self.panel_entrada = ttk.Frame(self.formulario, style="App.TFrame")
        self.panel_entrada.grid(row=0, column=0, sticky="nsew")
        self.formulario.rowconfigure(0, weight=1)
        self.formulario.columnconfigure(0, weight=1)
        self.panel_entrada.rowconfigure(1, weight=1)
        self.panel_entrada.columnconfigure(0, weight=1)

        self.formulario_canvas = tk.Canvas(
            self.panel_entrada, bg="#f2f5f1", highlightthickness=0
        )
        barra_vertical = ttk.Scrollbar(
            self.panel_entrada, orient="vertical", command=self.formulario_canvas.yview
        )
        barra_horizontal = ttk.Scrollbar(
            self.panel_entrada, orient="horizontal", command=self.formulario_canvas.xview
        )
        self.formulario_canvas.configure(
            yscrollcommand=barra_vertical.set,
            xscrollcommand=barra_horizontal.set,
        )
        self.formulario_canvas.grid(row=1, column=0, sticky="nsew")
        barra_vertical.grid(row=1, column=1, sticky="ns")
        barra_horizontal.grid(row=2, column=0, sticky="ew")
        self.formulario_interior = ttk.Frame(
            self.formulario_canvas, style="App.TFrame"
        )
        self.formulario_id = self.formulario_canvas.create_window(
            (0, 0), window=self.formulario_interior, anchor="nw"
        )
        self.formulario_interior.bind(
            "<Configure>",
            lambda _evento: self.formulario_canvas.configure(
                scrollregion=self.formulario_canvas.bbox("all")
            ),
        )
        self.formulario_canvas.bind("<Configure>", self._ajustar_formulario)

        self.objetivo_frame = ttk.LabelFrame(
            self.formulario_interior, text="  Función objetivo  ",
            style="Card.TLabelframe",
        )
        self.objetivo_frame.pack(fill="x", pady=5, ipady=4)

        self.restricciones_frame = ttk.LabelFrame(
            self.formulario_interior, text="  Restricciones  ",
            style="Card.TLabelframe",
        )
        self.restricciones_frame.pack(fill="x", pady=5, ipady=4)

    def _ajustar_formulario(self, evento):
        ancho_contenido = self.formulario_interior.winfo_reqwidth()
        self.formulario_canvas.itemconfigure(
            self.formulario_id, width=max(evento.width, ancho_contenido)
        )

    def _crear_salida(self):
        marco = ttk.LabelFrame(
            self.contenido, text="  Resultados y gráfica  ",
            style="Card.TLabelframe",
        )
        self.contenido.add(marco, weight=2)
        marco.rowconfigure(0, weight=1)
        marco.columnconfigure(0, weight=1)
        self.tablas = ttk.Notebook(marco)
        self.tablas.grid(row=0, column=0, sticky="nsew")
        self.resumen = ttk.Frame(self.tablas, style="App.TFrame")
        self.tablas.add(self.resumen, text="Resumen")
        ttk.Label(
            self.resumen,
            text="La solución aparecerá aquí al resolver el modelo.",
            padding=24,
        ).pack(anchor="nw")
        self.grafica_tab = ttk.Frame(self.tablas, style="App.TFrame")
        self.tablas.add(self.grafica_tab, text="Gráfica")
        self.grafica_canvas = tk.Canvas(
            self.grafica_tab,
            bg="#ffffff",
            highlightthickness=1,
            highlightbackground="#d5ded7",
        )
        self.grafica_canvas.pack(fill="both", expand=True, padx=8, pady=8)
        self.grafica_problema = None
        self.grafica_resultado = None
        self.grafica_canvas.bind("<Configure>", self._actualizar_grafica)

    def _limpiar_frame(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()

    def _actualizar_formulario(self):
        try:
            variables = self.cantidad_variables.get()
            restricciones = self.cantidad_restricciones.get()
        except tk.TclError:
            return

        if variables < 1 or restricciones < 1:
            return

        self._limpiar_frame(self.objetivo_frame)
        self._limpiar_frame(self.restricciones_frame)
        self.coeficientes_objetivo = []
        self.coeficientes_restricciones = []
        self.signos_restricciones = []
        self.rhs_restricciones = []

        for indice in range(variables):
            ttk.Label(self.objetivo_frame, text=f"X{indice + 1}:").grid(
                row=0, column=indice * 2, padx=4, pady=5
            )
            entrada = ttk.Entry(self.objetivo_frame, width=9)
            entrada.insert(0, "0")
            entrada.grid(row=0, column=indice * 2 + 1, padx=4, pady=5)
            self.coeficientes_objetivo.append(entrada)

        encabezados = ["Restricción"] + [
            f"X{indice + 1}" for indice in range(variables)
        ] + ["Signo", "Resultado"]
        for columna, encabezado in enumerate(encabezados):
            ttk.Label(
                self.restricciones_frame, text=encabezado
            ).grid(row=0, column=columna, padx=4, pady=3)

        for fila in range(restricciones):
            ttk.Label(
                self.restricciones_frame, text=str(fila + 1)
            ).grid(row=fila + 1, column=0, padx=4)
            entradas = []
            for columna in range(variables):
                entrada = ttk.Entry(self.restricciones_frame, width=9)
                entrada.insert(0, "0")
                entrada.grid(
                    row=fila + 1, column=columna + 1, padx=4, pady=2
                )
                entradas.append(entrada)
            signo = ttk.Combobox(
                self.restricciones_frame,
                values=("<=", ">=", "="),
                state="readonly",
                width=5,
            )
            signo.set("<=")
            signo.grid(row=fila + 1, column=variables + 1, padx=4)
            rhs = ttk.Entry(self.restricciones_frame, width=9)
            rhs.insert(0, "0")
            rhs.grid(row=fila + 1, column=variables + 2, padx=4)
            self.coeficientes_restricciones.append(entradas)
            self.signos_restricciones.append(signo)
            self.rhs_restricciones.append(rhs)

        self.formulario.update_idletasks()
        self.formulario_canvas.configure(
            scrollregion=self.formulario_canvas.bbox("all")
        )

    def _leer_numero(self, entrada, descripcion):
        try:
            return float(entrada.get().strip())
        except ValueError as error:
            raise ValueError(f"El valor de {descripcion} debe ser numérico.") from error

    def _crear_problema(self):
        objetivo = [
            self._leer_numero(entrada, f"X{indice + 1}")
            for indice, entrada in enumerate(self.coeficientes_objetivo)
        ]
        restricciones = []
        for fila, entradas in enumerate(self.coeficientes_restricciones):
            coeficientes = [
                self._leer_numero(entrada, f"X{columna + 1} de la restricción {fila + 1}")
                for columna, entrada in enumerate(entradas)
            ]
            rhs = self._leer_numero(
                self.rhs_restricciones[fila],
                f"el resultado de la restricción {fila + 1}",
            )
            restricciones.append(
                Restriccion(coeficientes, self.signos_restricciones[fila].get(), rhs)
            )
        return Problema(
            objetivo,
            restricciones,
            tipo=self.tipo.get(),
            no_negativas=self.no_negativas.get(),
            metodo=self.metodo.get(),
        )

    def _resolver(self):
        try:
            problema = self._crear_problema()
            capturas = []

            def observar(tabla, titulo, _iteracion):
                capturas.append((titulo, deepcopy(tabla)))

            with redirect_stdout(io.StringIO()):
                resultado = resolver_problema(problema, observar)
        except (ValueError, ZeroDivisionError) as error:
            messagebox.showerror("Datos inválidos", str(error))
            return
        except Exception as error:
            messagebox.showerror("Error inesperado", str(error))
            return

        self._mostrar_resultado_grafico(resultado, problema, capturas)

    def _mostrar_resultado_grafico(self, resultado, problema, capturas):
        for pestaña in self.tablas.tabs():
            if pestaña not in (str(self.resumen), str(self.grafica_tab)):
                self.tablas.forget(pestaña)
        for widget in self.resumen.winfo_children():
            widget.destroy()

        estado = resultado["estado"]
        if estado == "optimo":
            valores, z = obtener_solucion(resultado["tabla"], len(problema.objetivo))
            texto = "Solución óptima\n\n"
            texto += "\n".join(
                f"X{indice + 1} = {valor:.4f}"
                for indice, valor in enumerate(valores)
            )
            texto += f"\n\nZ = {z:.4f}\nIteraciones: {resultado['iteraciones']}"
        elif estado == "sin_solucion":
            texto = "El problema no tiene solución factible."
        elif estado == "no_acotado":
            texto = "El problema es no acotado."
        else:
            texto = f"No se pudo obtener una solución: {estado}."
        ttk.Label(
            self.resumen, text=texto, justify="left",
            font=("Segoe UI Semibold", 14), padding=24,
        ).pack(anchor="nw")
        self.grafica_problema = None
        self.grafica_resultado = None
        self._actualizar_grafica()
        self.tablas.select(self.resumen)

        for titulo, tabla in capturas:
            self._agregar_tabla(titulo, tabla)

    def _agregar_tabla(self, titulo, tabla):
        marco = ttk.Frame(self.tablas)
        self.tablas.add(marco, text=titulo[:18])
        columnas = ["Base"] + tabla.columnas
        vista = ttk.Treeview(marco, columns=columnas, show="headings")
        for columna in columnas:
            vista.heading(columna, text=columna)
            vista.column(columna, width=92, anchor="center")
        mostrar_m = getattr(tabla, "mostrar_m", False)
        from salida import formatear_valor
        for indice, fila in enumerate(tabla.matriz[:-1]):
            vista.insert(
                "", "end",
                values=[tabla.base[indice]] + [
                    formatear_valor(valor, mostrar_m) for valor in fila
                ],
            )
        vista.insert(
            "", "end",
            values=["Z"] + [
                formatear_valor(valor, mostrar_m)
                for valor in tabla.matriz[-1]
            ],
        )
        barra = ttk.Scrollbar(marco, orient="vertical", command=vista.yview)
        barra_horizontal = ttk.Scrollbar(
            marco, orient="horizontal", command=vista.xview
        )
        vista.configure(
            yscrollcommand=barra.set,
            xscrollcommand=barra_horizontal.set,
        )
        vista.grid(row=0, column=0, sticky="nsew")
        barra.grid(row=0, column=1, sticky="ns")
        barra_horizontal.grid(row=1, column=0, sticky="ew")
        marco.rowconfigure(0, weight=1)
        marco.columnconfigure(0, weight=1)

    def _graficar(self):
        try:
            problema = self._crear_problema()
        except ValueError as error:
            messagebox.showerror("Datos inválidos", str(error))
            return

        if len(problema.objetivo) != 2:
            messagebox.showinfo(
                "Gráfica no disponible",
                "La gráfica está disponible para problemas con exactamente "
                "dos variables.",
            )
            return
        if not problema.no_negativas:
            messagebox.showinfo(
                "Gráfica no disponible",
                "La gráfica requiere variables no negativas para mostrar "
                "la región en el primer cuadrante.",
            )
            return

        resultado = None
        try:
            captura = io.StringIO()
            with redirect_stdout(captura):
                resultado = resolver_problema(problema)
        except (ValueError, ZeroDivisionError) as error:
            messagebox.showerror("Datos inválidos", str(error))
            return
        except Exception as error:
            messagebox.showerror("Error inesperado", str(error))
            return

        self.grafica_problema = problema
        self.grafica_resultado = resultado
        self.tablas.select(self.grafica_tab)
        self.grafica_canvas.update_idletasks()
        self._dibujar_grafica(
            self.grafica_canvas, self.grafica_problema, self.grafica_resultado
        )

    def _actualizar_grafica(self, evento=None):
        if self.grafica_problema is not None:
            self._dibujar_grafica(
                self.grafica_canvas,
                self.grafica_problema,
                self.grafica_resultado,
            )
            return

        ancho = evento.width if evento else self.grafica_canvas.winfo_width()
        alto = evento.height if evento else self.grafica_canvas.winfo_height()
        self.grafica_canvas.delete("all")
        self.grafica_canvas.create_text(
            ancho / 2,
            alto / 2,
            text="La gráfica aparecerá aquí al pulsar Graficar.",
            fill="#63736b",
            font=("Segoe UI", 11),
        )

    def _punto_factible(self, problema, x, y):
        tolerancia = 1e-7
        if x < -tolerancia or y < -tolerancia:
            return False
        for restriccion in problema.restricciones:
            valor = (
                restriccion.coeficientes[0] * x
                + restriccion.coeficientes[1] * y
            )
            if restriccion.signo == "<=" and valor > restriccion.rhs + tolerancia:
                return False
            if restriccion.signo == ">=" and valor < restriccion.rhs - tolerancia:
                return False
            if restriccion.signo == "=" and abs(valor - restriccion.rhs) > tolerancia:
                return False
        return True

    def _intersecciones_grafica(self, problema):
        lineas = [
            (restriccion.coeficientes[0],
             restriccion.coeficientes[1],
             restriccion.rhs)
            for restriccion in problema.restricciones
        ]
        lineas.extend(((1.0, 0.0, 0.0), (0.0, 1.0, 0.0)))
        puntos = []
        for indice, (a1, b1, c1) in enumerate(lineas):
            for a2, b2, c2 in lineas[indice + 1:]:
                determinante = a1 * b2 - a2 * b1
                if abs(determinante) < 1e-12:
                    continue
                x = (c1 * b2 - c2 * b1) / determinante
                y = (a1 * c2 - a2 * c1) / determinante
                if self._punto_factible(problema, x, y):
                    if not any(
                        abs(x - px) < 1e-7 and abs(y - py) < 1e-7
                        for px, py in puntos
                    ):
                        puntos.append((x, y))
        return puntos

    def _dibujar_grafica(self, lienzo, problema, resultado):
        ancho = lienzo.winfo_width()
        alto = lienzo.winfo_height()
        if ancho < 100 or alto < 100:
            return
        lienzo.delete("all")

        puntos = self._intersecciones_grafica(problema)
        maximo = max(
            [10.0] + [max(x, y) for x, y in puntos] +
            [abs(restriccion.rhs / coeficiente)
             for restriccion in problema.restricciones
             for coeficiente in restriccion.coeficientes
             if abs(coeficiente) > 1e-12 and restriccion.rhs / coeficiente > 0]
        )
        maximo *= 1.15
        margen_izquierdo, margen_superior = 68, 28
        margen_derecho, margen_inferior = 28, 52
        ancho_grafica = ancho - margen_izquierdo - margen_derecho
        alto_grafica = alto - margen_superior - margen_inferior

        def convertir(x, y):
            return (
                margen_izquierdo + x / maximo * ancho_grafica,
                margen_superior + alto_grafica - y / maximo * alto_grafica,
            )

        for indice in range(0, int(maximo) + 1):
            x1, y1 = convertir(indice, 0)
            x2, y2 = convertir(indice, maximo)
            lienzo.create_line(x1, y1, x2, y2, fill="#edf1f7")
            x1, y1 = convertir(0, indice)
            x2, y2 = convertir(maximo, indice)
            lienzo.create_line(x1, y1, x2, y2, fill="#edf1f7")

        origen_x, origen_y = convertir(0, 0)
        lienzo.create_line(
            origen_x, margen_superior, origen_x, origen_y,
            fill="#334155", width=2, arrow=tk.LAST
        )
        lienzo.create_line(
            origen_x, origen_y, margen_izquierdo + ancho_grafica, origen_y,
            fill="#334155", width=2, arrow=tk.LAST
        )
        lienzo.create_text(
            margen_izquierdo + ancho_grafica - 4, origen_y - 12,
            text="X1", fill="#334155", anchor="e"
        )
        lienzo.create_text(
            origen_x + 14, margen_superior + 4,
            text="X2", fill="#334155", anchor="w"
        )

        if len(puntos) >= 3:
            centro_x = sum(x for x, _ in puntos) / len(puntos)
            centro_y = sum(y for _, y in puntos) / len(puntos)
            puntos_ordenados = sorted(
                puntos,
                key=lambda punto: math.atan2(
                    punto[1] - centro_y, punto[0] - centro_x
                ),
            )
            coordenadas = [
                coordenada
                for punto in puntos_ordenados
                for coordenada in convertir(*punto)
            ]
            lienzo.create_polygon(
                coordenadas, fill="#bfdbfe", outline="#2563eb",
                stipple="gray50", tags="region"
            )

        colores = ("#ef4444", "#f59e0b", "#8b5cf6", "#10b981", "#ec4899")
        for indice, restriccion in enumerate(problema.restricciones):
            a, b = restriccion.coeficientes
            puntos_linea = []
            if abs(b) > 1e-12:
                puntos_linea.extend(((0, restriccion.rhs / b),
                                     (maximo, (restriccion.rhs - a * maximo) / b)))
            elif abs(a) > 1e-12:
                x = restriccion.rhs / a
                puntos_linea.append((x, 0))
                puntos_linea.append((x, maximo))
            if len(puntos_linea) == 2:
                lienzo.create_line(
                    *[coordenada for punto in puntos_linea
                      for coordenada in convertir(*punto)],
                    fill=colores[indice % len(colores)], width=2,
                )

        for x, y in puntos:
            px, py = convertir(x, y)
            lienzo.create_oval(px - 4, py - 4, px + 4, py + 4,
                               fill="#1d4ed8", outline="#ffffff", width=1)

        if resultado and resultado.get("estado") == "optimo":
            valores, _ = obtener_solucion(resultado["tabla"], 2)
            if self._punto_factible(problema, valores[0], valores[1]):
                px, py = convertir(valores[0], valores[1])
                lienzo.create_oval(
                    px - 7, py - 7, px + 7, py + 7,
                    fill="#16a34a", outline="#ffffff", width=2
                )
                lienzo.create_text(
                    px + 10, py - 12,
                    text=f"Óptimo ({valores[0]:.2f}, {valores[1]:.2f})",
                    fill="#166534", anchor="w",
                )

def iniciar_interfaz():
    ventana = tk.Tk()
    InterfazSimplex(ventana)
    ventana.mainloop()
