# Explicación del funcionamiento del programa

## 1. ¿Qué hace el programa?

Este programa resuelve problemas de **programación lineal** utilizando el método
Simplex. Un problema de programación lineal busca maximizar o minimizar una
función, llamada **función objetivo**, respetando una serie de restricciones.

De forma general, el problema que intenta resolver es:

```text
Maximizar o minimizar:

    Z = c1 X1 + c2 X2 + ... + cn Xn

Sujeto a:

    a11 X1 + a12 X2 + ... + a1n Xn <=, >= o = b1
    a21 X1 + a22 X2 + ... + a2n Xn <=, >= o = b2
    ...

Y, dependiendo de la opción elegida:

    Xj >= 0
    o
    Xj puede ser positiva o negativa
```

El programa funciona por consola. El usuario introduce los coeficientes y las
restricciones, y el programa transforma esa información en una **tabla
Simplex**. Después realiza pivoteos hasta encontrar una solución óptima, una
solución no factible o detectar que el problema es no acotado.

---

## 2. Organización de los archivos

El programa está separado en varios archivos para que cada uno tenga una
responsabilidad concreta:

| Archivo | Responsabilidad |
|---|---|
| `main.py` | Coordina todo el proceso y controla los errores principales. |
| `entrada.py` | Solicita los datos al usuario y crea el problema. |
| `modelo.py` | Contiene las clases que representan el problema y la tabla. |
| `canonico.py` | Convierte el problema a una tabla canónica. |
| `metodos.py` | Ejecuta Simplex, Dos fases o Gran M. |
| `simplex.py` | Contiene una implementación clásica de Simplex. |
| `salida.py` | Imprime tablas, iteraciones y resultados. |
| `interfaz.py` | Contiene la interfaz gráfica realizada con Tkinter. |

Esta separación es útil porque permite cambiar la forma de leer los datos sin
tener que modificar el algoritmo matemático, o cambiar la forma de mostrar los
resultados sin cambiar la resolución.

---

## 3. Inicio del programa: `main.py`

La ejecución comienza en:

```python
if __name__ == "__main__":
    main()
```

Esto significa que la función `main()` solamente se ejecuta cuando el archivo
se inicia directamente, por ejemplo:

```text
python main.py
```

La función `main()` realiza estos pasos:

1. Llama a `leer_problema()`.
2. Comprueba si el usuario canceló la selección inicial.
3. Envía el problema a `resolver_problema()`.
4. Muestra la tabla final.
5. Muestra la traza cuando el método seleccionado la genera.
6. Muestra la solución final.

Cuando se utiliza el método Simplex directo, las tablas se imprimen durante la
resolución: primero se muestra la tabla inicial y después la tabla resultante
de cada iteración. Por eso este método no necesita una traza resumida adicional
al terminar.

El bloque `try` permite controlar errores:

- `ValueError`: normalmente representa datos o elecciones inválidas.
- `Exception`: captura errores inesperados para que el programa muestre un
  mensaje en lugar de terminar silenciosamente.

---

## 4. Captura de datos: `entrada.py`

### 4.1 Selección del tipo de problema

La función `leer_problema()` primero pregunta si se desea:

1. Maximizar.
2. Minimizar.

Internamente, esas opciones se convierten en los textos `"max"` y `"min"`.
Guardar el tipo como texto permite que las demás funciones sepan cómo preparar
la función objetivo.

Si el usuario escribe otra opción, el programa muestra `"Opción no válida."`
y devuelve `None`. En ese caso, `main()` termina sin intentar resolver nada.

### 4.2 Restricción de no negatividad

Después se pregunta si las variables deben cumplir:

```text
Xj >= 0
```

Si se elige que sí, cada variable se conserva como una sola columna:

```text
X1, X2, X3, ...
```

Si se elige que no, cada variable libre se representa como la diferencia de dos
variables no negativas:

```text
Xj = Xj+ - Xj-

con Xj+ >= 0 y Xj- >= 0
```

Esta transformación es necesaria porque el método Simplex trabaja
naturalmente con variables no negativas.

### 4.3 Selección del método

El usuario puede seleccionar:

1. **Simplex**.
2. **Dos fases**.
3. **Gran M**.

La selección se guarda como:

```text
"simplex"
"dos_fases"
"gran_m"
```

El método Simplex directo es el más sencillo, pero solamente acepta problemas
con variables no negativas y restricciones `<=`. Dos fases y Gran M son más
generales porque pueden trabajar con restricciones `>=`, restricciones de
igualdad y variables libres.

### 4.4 Lectura de la función objetivo

El programa pregunta cuántas variables existen y luego solicita un coeficiente
para cada una. Por ejemplo, si se escribe:

```text
3
```

para el número de variables, se solicitan:

```text
Coeficiente de X1
Coeficiente de X2
Coeficiente de X3
```

Los valores se convierten a `float` y se guardan en una lista:

```python
[coeficiente_x1, coeficiente_x2, coeficiente_x3]
```

### 4.5 Lectura de restricciones

Para cada restricción se solicitan:

1. El coeficiente de cada variable.
2. El tipo de relación: `<=`, `>=` o `=`.
3. El lado derecho de la restricción.

Cada restricción se guarda en un objeto `Restriccion`. Por ejemplo:

```python
Restriccion([2, 1], "<=", 8)
```

representa:

```text
2X1 + X2 <= 8
```

---

## 5. Clases del modelo: `modelo.py`

### 5.1 Clase `Restriccion`

Esta clase agrupa la información de una restricción:

- `coeficientes`: coeficientes de las variables.
- `signo`: `<=`, `>=` o `=`.
- `rhs`: resultado del lado derecho.

El nombre `rhs` significa **Right Hand Side**, es decir, lado derecho.

### 5.2 Clase `Problema`

La clase `Problema` reúne todos los datos necesarios para resolver:

- función objetivo;
- lista de restricciones;
- tipo de optimización;
- uso o no de no negatividad;
- método seleccionado.

Tener estos datos dentro de un solo objeto evita enviar muchas variables
separadas entre las funciones.

### 5.3 Clase `TablaSimplex`

Esta clase representa el tableau:

- `matriz`: números de restricciones y función objetivo;
- `columnas`: nombres de variables, holguras, exceso, artificiales y `RHS`;
- `base`: variable básica de cada fila.

Durante los pivoteos, la matriz y la base se modifican directamente.

---

## 6. Construcción de la tabla canónica: `canonico.py`

La función `construir_tabla_canonica()` convierte el problema original a la
estructura que necesitan los algoritmos.

### 6.1 Variables originales

Cuando las variables son no negativas, una variable se agrega directamente:

```text
X1
```

Cuando son libres, se agregan dos columnas:

```text
X1+ y X1-
```

La relación que se conserva es:

```text
X1 = X1+ - X1-
```

El programa guarda esta relación en `transformaciones_nombres` para poder
reconstruir al final los valores de las variables originales.

### 6.2 Corrección de restricciones con lado derecho negativo

Si el lado derecho de una restricción es negativo, se multiplican todos sus
coeficientes y su resultado por `-1`. Al hacer esto, también se invierte el
signo:

```text
<= se convierte en >=
>= se convierte en <=
= permanece =
```

Esto permite trabajar con un lado derecho positivo y evita iniciar el método
con una representación inconsistente.

### 6.3 Variables de holgura, exceso y artificiales

Para transformar cada tipo de restricción se agregan variables auxiliares:

#### Restricción `<=`

Se agrega una variable de holgura:

```text
aX1 + bX2 <= c

aX1 + bX2 + S1 = c
```

La variable `S1` mide cuánto espacio queda disponible.

#### Restricción `>=`

Se resta una variable de exceso y se agrega una variable artificial:

```text
aX1 + bX2 >= c

aX1 + bX2 - E1 + A1 = c
```

`E1` convierte la desigualdad en igualdad. `A1` proporciona una variable
básica inicial para poder comenzar las fases de resolución.

#### Restricción `=`

Se agrega una variable artificial:

```text
aX1 + bX2 = c

aX1 + bX2 + A1 = c
```

Las variables artificiales no pertenecen al problema original. Solamente se
utilizan temporalmente y deben eliminarse o penalizarse antes de aceptar una
solución.

### 6.4 Preparación de la función objetivo

El algoritmo busca coeficientes negativos en la fila objetivo. Por esa razón,
la función objetivo se guarda con los signos apropiados para que:

- en maximización se use `-c` en la fila `Z`;
- en minimización se invierta primero la función para resolverla con la misma
  lógica de pivoteo.

La última columna se llama `RHS` y contiene los valores del lado derecho de las
restricciones.

---

## 7. Selección del algoritmo: `metodos.py`

La función `resolver_problema()` decide qué procedimiento ejecutar.

### 7.1 Método Simplex directo

Antes de usarlo, el programa comprueba que:

- se utilizaron variables no negativas;
- todas las restricciones son `<=`.
- todos los lados derechos (`RHS`) son no negativos.

Si alguna condición no se cumple, se lanza un `ValueError` y se recomienda
utilizar Dos fases o Gran M.

Con las condiciones admitidas por el Simplex directo, el punto `X = 0` es
factible inicialmente. Por eso este método puede detectar correctamente un
problema `no_acotado`, pero los problemas con restricciones incompatibles,
igualdades, restricciones `>=` o `RHS` negativo deben resolverse con Dos fases
o Gran M. El programa ya rechaza explícitamente un `RHS` negativo para evitar
clasificarlo incorrectamente como `no_acotado`.

La tabla canónica se muestra antes del primer pivote con el encabezado
`TABLA INICIAL`. Después de cada pivote se imprime la tabla actual con el
encabezado correspondiente a la iteración:

```text
===== TABLA INICIAL =====
...
===== ITERACIÓN 1 =====
...
===== ITERACIÓN 2 =====
...
```

El callback `mostrar_iteracion()` conecta la implementación de
`simplex.py` con `mostrar_tabla()` de `salida.py`. Así, el algoritmo conserva
la responsabilidad de resolver y la salida conserva la responsabilidad de
formatear las tablas.

### 7.2 Método de Dos fases

Este método trabaja en dos etapas:

#### Fase 1: encontrar factibilidad

Se crea una función objetivo temporal que intenta eliminar las variables
artificiales. La idea es comprobar si existe una solución que satisfaga todas
las restricciones.

Si una variable artificial permanece con un valor positivo o el proceso no
puede continuar, el problema se considera sin solución factible.

La comprobación del valor final de la fase 1 utiliza una tolerancia de
`1e-9`. Esto evita confundir errores mínimos de redondeo, como
`-4.44e-16`, con una inconsistencia real. Un valor negativo menor que
`-1e-9` sí indica que quedó artificial positiva y el problema se marca como
`sin_solucion`.

#### Fase 2: optimizar la función original

Después de encontrar una base factible, se eliminan las columnas de las
variables artificiales. Luego se restaura la función objetivo original y se
continúa pivotando para encontrar el máximo o mínimo solicitado.

Durante la ejecución se muestran las tablas de ambas fases. Cada fase imprime
su tableau inicial y una tabla después de cada pivote:

```text
===== FASE 1 - TABLA INICIAL =====
===== FASE 1 - ITERACIÓN 1 =====
...
===== FASE 2 - TABLA INICIAL =====
===== FASE 2 - ITERACIÓN 1 =====
...
```

### 7.3 Método de Gran M

Este método conserva las variables artificiales, pero les asigna una penalización
muy grande:

```text
-1 000 000
```

La penalización hace que el algoritmo intente evitar esas variables. Si al
terminar alguna artificial sigue siendo básica con un valor positivo, el
problema se marca como `sin_solucion`.

La comprobación de artificiales positivas también utiliza la tolerancia
`1e-9`, de modo que pequeños residuos numéricos no alteren el estado final.

El tableau inicial con la función objetivo penalizada y cada tableau posterior
a un pivote se muestran con el mismo formato que en el método Simplex:

```text
===== FASE 1 - TABLA INICIAL =====
===== FASE 1 - ITERACIÓN 1 =====
...
```

En las tablas de Gran M, los coeficientes que dependen de la penalización se
presentan simbólicamente. Por ejemplo, un valor numérico equivalente a
`12 000 000` se muestra como `12M`, y `-1 000 000 + 5` se muestra como
`-M + 5`. Los cálculos internos continúan utilizando `M = 1 000 000`.

La ventaja es que se realiza una sola secuencia principal de pivoteos. La
desventaja es que el uso de un número muy grande puede provocar problemas de
precisión numérica en casos complicados.

---

## 8. Cómo se realiza un pivoteo

Las implementaciones de Simplex repiten el proceso hasta terminar. La función
`resolver()` de `simplex.py` se utiliza para el Simplex directo, mientras que
la función `simplex()` de `metodos.py` se utiliza en las fases de Dos fases y
Gran M.

### Paso 1: elegir la columna pivote

`columna_pivote()` revisa la fila objetivo, sin revisar la columna `RHS`.

Busca el coeficiente más negativo. Si existe, esa columna representa una
variable que todavía puede mejorar el objetivo.

Si no hay coeficientes negativos, se considera que se alcanzó el óptimo.

### Paso 2: elegir la fila pivote

`fila_pivote()` aplica la prueba de la razón mínima:

```text
razón = RHS / elemento_de_la_columna_pivote
```

Solamente se consideran elementos positivos de la columna pivote. La fila con
la razón positiva más pequeña es la que sale de la base.

Esto evita que el lado derecho se vuelva negativo y ayuda a conservar la
factibilidad.

Si ninguna fila tiene un elemento positivo, el objetivo puede aumentar
indefinidamente. En ese caso el problema se marca como `no_acotado`.

### Paso 3: normalizar la fila pivote

Se divide toda la fila pivote entre el elemento pivote. De esta forma, el
elemento pivote se convierte en `1`.

### Paso 4: hacer ceros en la columna pivote

Para todas las demás filas se resta un múltiplo de la fila pivote. El objetivo
es que la columna pivote quede así:

```text
0
0
1
0
...
```

Esto convierte la nueva variable en una variable básica.

### Paso 5: actualizar la base

La variable que corresponde a la columna pivote reemplaza a la variable que
estaba en la fila pivote.

La información de cada iteración se almacena en `traza`, incluyendo:

- fase;
- columna pivote;
- razones calculadas;
- fila seleccionada;
- elemento pivote.

---

## 9. Obtención de la solución

La función `obtener_solucion()` reconstruye las variables originales a partir
de la tabla final.

Para cada variable busca una columna que tenga la estructura de una columna
básica: un `1` en una fila y ceros en las demás. El valor de esa variable es el
`RHS` de la fila correspondiente.

Si una variable original era libre, el programa combina sus dos columnas:

```text
Xj = Xj+ - Xj-
```

Finalmente, toma el valor de la esquina inferior derecha de la tabla como
valor de `Z`. Para problemas de minimización se invierte nuevamente el signo
para mostrar el resultado en el sentido original.

---

## 10. Estados posibles

El programa puede terminar con estos estados:

### `optimo`

Se encontró una solución que satisface las restricciones y no puede mejorarse
con los pivoteos disponibles.

### `sin_solucion`

No existe una solución factible que cumpla todas las restricciones. En Dos
fases, esto ocurre cuando la fase de factibilidad no logra eliminar el valor
artificial. En Gran M, ocurre si una artificial queda positiva en la base.

### `no_acotado`

El objetivo puede crecer o disminuir indefinidamente porque no existe una fila
pivote válida que limite la mejora.

Otros estados se muestran como un mensaje genérico de que no se pudo obtener la
solución.

---

## 11. Presentación de resultados: `salida.py`

### Tabla final

`mostrar_tabla()` imprime:

- nombre de la base;
- nombres de las columnas;
- valores de cada restricción;
- fila `Z`.

En Simplex y Dos fases los valores numéricos se imprimen con dos decimales
para facilitar la lectura. En Gran M, las tablas de la fase penalizada se
imprimen con `mostrar_m=True`, por lo que los valores relacionados con la
penalización se muestran usando la letra `M`.

La función `formatear_valor()` convierte la representación numérica interna a
una representación simbólica para la salida. Algunos ejemplos son:

```text
12 000 000       -> 12M
-1 000 000       -> -M
-500 000         -> -0.5M
-999 995         -> -M + 5.00
```

Esta conversión solamente afecta la presentación. El algoritmo continúa
operando internamente con `M = 1 000 000` y con valores de tipo `float`.

### Detalle de iteraciones

`mostrar_traza()` imprime cada pivoteo. Esta información sirve para comprobar
qué variable entró, qué variable salió y qué razones se compararon.

Dos fases y Gran M almacenan esta información en `traza` y la muestran al
terminar la resolución. Cada registro incluye la fase, la columna pivote, las
divisiones de la razón mínima, la fila seleccionada y el elemento pivote.

En Simplex directo, las tablas de cada iteración se imprimen durante el
proceso mediante `mostrar_iteracion()`. Dos fases y Gran M utilizan
`mostrar_tabla_fase()` para imprimir la tabla inicial y cada resultado de
pivote, incluyendo el número de fase. Por ello las tablas permiten seguir el
proceso completo en los tres métodos. En Gran M, `mostrar_tabla_fase()` activa
la representación simbólica de `M` para todas las tablas de la fase penalizada.

Cuando un método que usa `mostrar_traza()` no realiza pivoteos, se muestra:

```text
No se necesitaron pivoteos.
```

### Resultado final

`mostrar_resultado()` primero revisa el estado. Si el estado es `optimo`,
muestra:

```text
X1 = ...
X2 = ...
...
Z = ...
Iteraciones: ...
```

Si el problema no es factible o es no acotado, muestra una explicación en vez
de presentar valores que podrían ser incorrectos.

---

## 12. Ejemplo del flujo completo

Supóngase que se desea resolver:

```text
Maximizar Z = 3X1 + 2X2

Sujeto a:

    X1 + X2 <= 4
    2X1 + X2 <= 5
    X1, X2 >= 0
```

El usuario debe introducir:

1. `1` para maximización.
2. `1` para usar no negatividad.
3. `1` para el método Simplex.
4. `2` variables.
5. Coeficientes `3` y `2` para la función objetivo.
6. `2` restricciones.
7. Los coeficientes, signos y lados derechos de cada restricción.

Para las restricciones `<=`, la tabla agrega `S1` y `S2`:

```text
X1 + X2 + S1       = 4
2X1 + X2     + S2  = 5
```

La base inicial está formada por `S1` y `S2`. Después, el algoritmo selecciona
una columna con coeficiente negativo en la fila objetivo, calcula las razones,
elige la fila pivote, normaliza y repite.

Al terminar, la tabla contiene los valores óptimos en la columna `RHS`.

---

## 13. Visualización del proceso Simplex

La opción **Simplex** muestra el estado del tableau en tres momentos:

1. **Tabla inicial:** se imprime justo después de construir la tabla canónica,
   antes de realizar cualquier pivoteo.
2. **Tablas de iteración:** después de cada pivote se imprime la tabla
   actualizada. El número de iteración comienza en `1`.
3. **Tabla final:** `main.py` vuelve a mostrar la tabla cuando termina el
   algoritmo, antes de presentar el resultado.

La tabla inicial permite verificar la base de holguras y la fila objetivo antes
de comenzar. Las tablas de iteración permiten seguir los cambios producidos
por la normalización de la fila pivote, la eliminación de los demás elementos
de la columna pivote y la actualización de la base.

La función `resolver()` recibe `mostrar_iteracion` como callback. En
`metodos.py`, el callback se conecta con:

```python
def mostrar_iteracion(tabla, iteracion):
    print(f"\n===== ITERACIÓN {iteracion} =====")
    mostrar_tabla(tabla)
```

De esta forma, el algoritmo no depende de detalles específicos del formato de
salida y cada iteración se muestra inmediatamente después de completarse.

---

## 14. Resumen del recorrido

El recorrido completo puede resumirse así:

```text
Inicio
  |
  v
Leer tipo, variables, restricciones y método
  |
  v
Crear objeto Problema
  |
  v
Convertir el problema a tabla canónica
  |
  +--> Simplex directo
  |
  +--> Dos fases: factibilidad y optimización
  |
  +--> Gran M: penalización de artificiales
  |
  v
Elegir columna pivote
  |
  v
Elegir fila pivote con razón mínima
  |
  v
Normalizar y hacer ceros
  |
  v
Actualizar la base y guardar la traza
  |
  v
Repetir hasta óptimo, sin solución o no acotado
  |
  v
Reconstruir X1, X2, ... y Z
  |
  v
Mostrar resultados
```

La idea central es que el programa no trabaja directamente con las ecuaciones
que escribe el usuario. Primero las transforma a una tabla organizada para que
el algoritmo pueda realizar operaciones elementales de filas y mejorar
gradualmente la solución.

---

## 15. Interfaz gráfica

El archivo `interfaz.py` implementa una interfaz gráfica con **Tkinter**, que
forma parte de la biblioteca estándar de Python. No se instalaron librerías
externas.

Para iniciar la interfaz se ejecuta:

```text
python main.py
```

La ventana permite seleccionar:

- maximización o minimización;
- variables no negativas;
- método Simplex, Dos fases o Gran M;
- cantidad de variables;
- cantidad de restricciones.

Después de pulsar `Actualizar formulario`, se muestran los campos para los
coeficientes de la función objetivo y de cada restricción. El botón `Resolver`
construye un objeto `Problema` y utiliza las mismas funciones matemáticas que
el modo de consola.

El resultado se presenta en un área de texto con desplazamiento vertical y
horizontal. Esto permite consultar la tabla inicial, las tablas de cada
iteración, la traza y el resultado final. En Gran M se conserva la
representación simbólica de la penalización, por ejemplo `12M` o `-M + 5.00`.

En la interfaz gráfica, las tablas no se presentan como texto de terminal.
Cada una se muestra como una tabla independiente dentro de una pestaña, con
encabezados para la base, las variables y `RHS`. La pestaña `Resumen` muestra
el estado, las variables de la solución y el valor de `Z`; las demás pestañas
contienen la tabla inicial y los tableaux de cada iteración o fase. Las tablas
incluyen barras de desplazamiento cuando tienen muchas columnas o filas.

El botón `Graficar` abre una ventana con la representación visual del problema.
La gráfica está disponible para problemas de exactamente dos variables y con
variables no negativas. En ella se muestran:

- los ejes `X1` y `X2`;
- las rectas de las restricciones;
- los puntos de intersección factibles;
- la región factible sombreada;
- el punto óptimo, cuando el método encuentra una solución óptima.

La gráfica se construye con `tkinter.Canvas`, por lo que no requiere
`matplotlib` ni ninguna otra librería externa. Para problemas con más de dos
variables, la interfaz informa que no es posible representarlos directamente
en este plano.

El modo de consola anterior se conserva y puede iniciarse explícitamente con:

```text
python main.py --consola
```
