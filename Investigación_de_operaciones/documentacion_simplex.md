# Explicación del programa de Simplex

Este proyecto resuelve problemas de programación lineal usando el método simplex, con variantes para variables libres y con dos métodos alternativos: dos fases y gran M.

## 1. ¿Cómo funciona el programa en general?

El flujo principal es el siguiente:

1. Se pide al usuario el tipo de problema: maximización o minimización.
2. Se define si las variables son no negativas o libres.
3. Se elige el método de solución:
   - Simplex
   - Dos fases
   - Gran M
4. Se ingresan la función objetivo y las restricciones.
5. El programa crea un objeto `Problema` con esos datos.
6. Se llama a `resolver_problema` para decidir qué algoritmo usar.
7. Se obtiene una tabla final con la solución óptima o el estado del problema.
8. Se muestran la tabla, la traza de iteraciones y el resultado final.

La lógica principal se divide en cuatro partes:

- Entrada de datos: archivos de entrada y modelo
- Conversión a tabla canónica: archivo canonico.py
- Solución: archivos metodos.py y simplex.py
- Salida: archivo salida.py

---

## 2. Estructura de datos principales

### Restriccion
En `modelo.py` la clase `Restriccion` representa cada restricción del modelo.

Atributos:
- `coeficientes`: lista con los coeficientes de cada variable.
- `signo`: símbolo de la restricción (`<=`, `>=` o `=`).
- `rhs`: lado derecho de la restricción.

Ejemplo:
- `3x1 + 2x2 <= 10` se representaría como:
  - coeficientes = `[3, 2]`
  - signo = `"<="`
  - rhs = `10`

### Problema
La clase `Problema` guarda el modelo completo.

Atributos:
- `objetivo`: lista de coeficientes de la función objetivo
- `restricciones`: lista de objetos `Restriccion`
- `tipo`: `"max"` o `"min"`
- `no_negativas`: si las variables son no negativas
- `metodo`: método elegido (`"simplex"`, `"dos_fases"`, `"gran_m"`)

### TablaSimplex
La clase `TablaSimplex` representa la matriz del simplex y la base actual.

Atributos:
- `matriz`: tabla con filas de restricciones y la fila de z
- `columnas`: nombres de columnas (variables y holguras)
- `base`: lista con qué variable básica está en cada fila

---

## 3. Funciones de entrada

### leer_problema
Archivo: `entrada.py`

Esta es la función central para capturar el problema desde consola.

Hace lo siguiente:
- pregunta si es maximización o minimización
- pregunta si las variables son no negativas
- pregunta el método a usar
- pide la cantidad de variables y las lee con `leer_funcion_objetivo`
- pide la cantidad de restricciones y las lee con `leer_restricciones`
- crea un objeto `Problema` con todos esos valores

### leer_no_negatividad
Esta función pregunta si las variables cumplen `Xj >= 0`.

- si el usuario elige `1`, devuelve `True`
- si elige `2`, devuelve `False`
- si escribe algo inválido, lanza una excepción con `ValueError`

Esto es importante porque si las variables son libres, el método simplex clásico no sirve directamente; hay que usar dos fases o gran M.

### leer_metodo
Permite elegir entre:
- `1` → `simplex`
- `2` → `dos_fases`
- `3` → `gran_m`

### leer_funcion_objetivo
Recibe la cantidad de variables y solicita cada coeficiente de la función objetivo.

Ejemplo:
- si hay 3 variables, pregunta por `X1`, `X2`, `X3`
- guarda los valores en una lista

### leer_restricciones
Pide todos los coeficientes de cada restricción, luego llama a `leer_signo` para saber el tipo de desigualdad y solicita el lado derecho (`rhs`).

Cada restricción se guarda como un objeto `Restriccion`.

### leer_signo
Esta función convierte una opción numérica en un signo matemático:
- `1` → `<=`
- `2` → `>=`
- `3` → `=`

Si la opción es inválida, vuelve a pedirla hasta que sea correcta.

---

## 4. Funciones del modelo y preparación de la tabla

### construir_tabla_canonica
Archivo: `canonico.py`

Esta es una de las funciones más importantes. Convierte las restricciones a una forma canónica para que el simplex pueda trabajar con ellas.

¿Qué hace?
1. Revisa la cantidad de variables del problema.
2. Crea columnas para cada variable original.
3. Si la variable es no negativa, usa una sola columna.
4. Si la variable es libre, crea dos columnas: `X+` y `X-`.
5. Para cada restricción:
   - transforma los coeficientes según la variable
   - ajusta el lado derecho si este es negativo
   - agrega variables de holgura o artificiales según el signo
6. Genera la matriz del simplex con:
   - columnas de variables originales
   - columnas auxiliares (holgura / artificiales)
   - columna RHS
7. Define la base inicial: la variable artificial o de holgura que entra como básica
8. Calcula la fila objetivo con los coeficientes apropiados

#### Variables de holgura
Se usan para convertir desigualdades del tipo `<=` en igualdades.

Ejemplo:
- `2x1 + x2 <= 10`
- se transforma en:
  - `2x1 + x2 + s1 = 10`

#### Variables artificiales
Se usan para restricciones `>=` o `=` cuando hace falta una base inicial artificial.

Ejemplo:
- `2x1 + x2 >= 5`
- se transforma en:
  - `2x1 + x2 - e1 + a1 = 5`

### preparar_simplex
Archivo: `tabla.py`

Es una versión más básica de preparación del simplex. Aunque no es la que usa el flujo principal, sirve para ver la idea original:
- crea columnas para variables originales y holguras
- genera la matriz simplex inicial
- la base inicial usa variables de holgura
- pone la fila objetivo con coeficientes negativos

### validar_problema
Verifica que todas las restricciones sean del tipo `<=`.

Esta validación solo se usa en la versión antigua de simplex, porque esa implementación no maneja `>=` ni `=`.

---

## 5. Funciones del simplex principal

### resolver_problema
Archivo: `metodos.py`

Es el punto de decisión del programa.

Hace esto:
- si el problema usa `simplex`, llama a `resolver_simplex`
- si usa `gran_m`, construye la tabla canónica y llama a `resolver_gran_m`
- de lo contrario, usa `resolver_dos_fases`

### resolver_simplex
Valida que:
- las variables sean no negativas
- las restricciones sean todas `<=`

Si alguna condición falla, levanta un `ValueError`.

Luego construye la tabla canónica y llama al algoritmo clásico de simplex de `simplex.py`.

### resolver_dos_fases
Este método sirve cuando hay variables libres y/o restricciones `>=` o `=`.

Su idea:
1. Se crea una función objetivo artificial con las variables artificiales con coeficiente `-1`.
2. Se resuelve una primera fase para minimizar esas artificiales.
3. Si la primera fase no alcanza 0, entonces el problema no tiene solución factible.
4. Si sí, se eliminan las variables artificiales.
5. Se reemplaza la función objetivo original y se resuelve la segunda fase.

### resolver_gran_m
Este método también maneja variables libres o restricciones no estándar.

Su idea:
1. Se asigna a cada variable artificial un costo enorme negativo (`-1_000_000`) o equivalente.
2. Se resuelve el simplex con esa función objetivo artificial.
3. Si alguna variable artificial queda con valor positivo en la solución final, el problema es infactible.
4. Si no, se acepta la solución óptima.

### preparar_objetivo
Modifica la fila de la función objetivo para que corresponda con la base y el costo actual.

Se usa para:
- preparar la fase 1 de dos fases
- preparar la función objetivo artificial de gran M
- volver a la función objetivo real antes de continuar

### simplex
Archivo: `metodos.py`

Es la lógica iterativa del simplex.

Función:
- decide qué columna entra a la base (`columna_pivote`)
- si no hay columna negativa, la solución es óptima
- decide qué fila sale de la base (`fila_pivote`)
- si no existe fila de pivote, el problema es no acotado
- hace el pivoteo y actualiza la base
- guarda la traza de cada iteración

### columna_pivote
Busca la columna que debe entrar a la base.

Se observa la última fila (fila z) y se toma la columna con el valor más negativo.

Esto indica el coeficiente con mayor potencial de mejora para la función objetivo.

### fila_pivote
Para la columna elegida, busca la fila que debe salir.

Se calcula la razón:

$$
\frac{RHS}{elemento\_pivote}
$$

Se toma la fila con la razón más pequeña y positiva.

Esto garantiza que la nueva solución siga siendo factible.

### pivotear
Hace el pivoteo matemático:

1. Divide la fila pivote por el valor del pivote para convertirlo en 1.
2. Resta múltiplos de esa fila al resto para hacer cero el resto de la columna.
3. Redondea valores cercanos a cero para evitar errores numéricos.

### quitar_artificiales
Cuando termina la fase 1 del método dos fases, se eliminan las columnas artificiales y se ajustan las transformaciones.

Esto permite continuar con la función objetivo original sin esas variables extra.

### resultado
Recibe la tabla, la traza y el estado final y devuelve un diccionario con:
- `estado`
- `tabla`
- `traza`
- `iteraciones`

---

## 6. Simplex clásico en `simplex.py`

Este archivo implementa una versión más directa del algoritmo simplex.

### resolver
Es el ciclo principal del simplex clásico.

Mientras haya una variable no básica que pueda mejorar la solución:
- busca la columna pivote
- busca la fila pivote
- hace el pivoteo
- actualiza la base
- incrementa el número de iteraciones
- muestra la iteración

Cuando ya no hay coeficientes negativos en la fila z, la solución es óptima.

### buscar_columna_pivote
Busca la columna con el valor más negativo en la fila objetivo.

### buscar_fila_pivote
Calcula la razón `RHS / elemento` solo cuando el elemento de la columna pivote es positivo.

### pivotear
Hace el mismo procedimiento de pivoteo matemático, pero en una versión lineal con bucles explicitos.

### actualizar_base
Cuando se pivotea, la variable que entra a la base reemplaza a la variable que sale.

---

## 7. Funciones de salida

### mostrar_tabla
Muestra la tabla simplex en formato legible.

Imprime:
- la base actual
- cada columna
- la fila objetivo final

### mostrar_traza
Muestra el detalle de cada iteración.

Para cada paso imprime:
- número de iteración
- fase
- columna pivote
- divisiones calculadas
- elemento pivote

Esto ayuda a seguir el proceso paso a paso del algoritmo.

### obtener_solucion
Se usa para recuperar los valores reales de las variables a partir de la tabla final.

La lógica es:
- revisa cada variable original y sus transformaciones
- busca la columna correspondiente
- identifica la fila básica donde esa variable tiene un 1 y el resto de la columna es 0
- toma el valor del RHS en esa fila
- calcula el valor de z

Si el problema es de minimización, el valor de z se cambia de signo para devolver el resultado correcto.

### mostrar_resultado
Se encarga de interpretar el resultado final:
- si el estado es `sin_solucion`, imprime que no existe solución factible
- si es `no_acotado`, imprime que no tiene solución óptima finita
- si es `optimo`, muestra los valores de las variables y el valor de `Z`

---

## 8. ¿Qué hace `main.py`?

El archivo `main.py` conecta todo el flujo del programa.

### main
Esta función hace lo siguiente:
1. llama a `leer_problema()`
2. si el problema no es válido, termina
3. resuelve el problema con `resolver_problema(problema)`
4. muestra la tabla final con `mostrar_tabla`
5. muestra la traza con `mostrar_traza`
6. imprime la solución final con `mostrar_resultado`

Todo esto ocurre dentro de un bloque `try/except` para capturar errores y mostrar mensajes amigables.

---

## 9. Resumen del flujo completo

El programa funciona así:

1. El usuario escribe un problema lineal en consola.
2. `entrada.py` lo transforma a un objeto `Problema`.
3. `metodos.py` decide si aplica simplex, dos fases o gran M.
4. `canonico.py` convierte la formulación a una representación tabular adecuada.
5. El simplex pivotea filas y columnas hasta encontrar la solución óptima.
6. `salida.py` presenta la solución en formato legible.

---

## 10. Concepto general de simplex

El método simplex busca la mejor solución de un problema lineal entre las soluciones factibles.

La idea principal es:
- transformar restricciones en ecuaciones con holguras o artificiales
- construir una tabla inicial
- elegir una variable que entre a la base
- elegir una variable que salga de la base
- repetir iteraciones hasta que no haya mejora posible

Cuando la fila objetivo ya no tiene coeficientes negativos, la solución actual es óptima.

---

## 11. En resumen

Las funciones más importantes del proyecto son:

- `leer_problema`: captura el problema
- `construir_tabla_canonica`: prepara la tabla para simplex
- `resolver_problema`: selecciona el método
- `resolver_dos_fases` y `resolver_gran_m`: manejan variables libres y restricciones complejas
- `simplex` / `pivotear`: realizan el algoritmo de mejora iterativa
- `mostrar_resultado`: presenta la solución final

Con estas funciones, el programa puede resolver modelos de optimización lineal con diferentes tipos de restricciones y métodos de solución.
