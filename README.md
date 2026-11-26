# Herramientas para Ciencia de Datos

`functions.py` es un módulo con funciones auxiliares de uso frecuente en proyectos de
ciencia de datos con Python. Acompaña al *Manual de Ciencia de Datos con sentido* de
Prisma Uruguay, pero se puede usar en cualquier proyecto.

## Cómo usarlo

1. Descarga [`functions.py`](functions.py) y guárdalo en la misma carpeta que tu cuaderno
   de Jupyter (o tu script).
2. En la primera celda del cuaderno, activa la recarga automática **antes** de importar
   el módulo, para que los cambios que hagas en `functions.py` se apliquen sin reiniciar
   el kernel:

   ```python
   %reload_ext autoreload
   %autoreload 2
   import functions as fn
   ```

   Se usa `%reload_ext` y no `%load_ext` para poder volver a ejecutar la celda sin el
   aviso «The autoreload extension is already loaded».

3. Usa las funciones con el prefijo `fn.`:

   ```python
   fn.check_libraries(auto_install=False)
   ```

Se recomienda `import functions as fn` y no `from functions import *`: con el prefijo,
quien lee el código sabe qué funciones son propias y cuáles vienen de otra librería.

## Funciones disponibles

| Función | Para qué sirve |
|---|---|
| `check_libraries(auto_install=False)` | Verifica que estén instaladas las librerías necesarias y, si se indica, las instala. |
| `resumen_general(df)` | Muestra dimensiones, tipos de datos, valores nulos y resumen estadístico de un DataFrame. |
| `normalizar_texto(texto, conservar_enie=False)` | Pasa a minúsculas, quita espacios en los extremos y quita tildes. Con `conservar_enie=True` mantiene la ñ. |
| `ver_niveles_categoricos(df, diccionario)` | Compara la cantidad de categorías esperada con la encontrada en cada columna. |
| `detectar_outliers(serie, factor=1.5)` | Devuelve los valores atípicos según el método de Tukey (rango intercuartílico). |
| `bins_sturges(muestra)`, `bins_freedman_diaconis(muestra)`, `bins_scott(muestra)`, `bins_rice(muestra)` | Calculan la cantidad de intervalos (bins) de un histograma según distintas reglas. |
| `aplicar_estilo()` | Aplica un estilo común a todos los gráficos de matplotlib: sin bordes superior y derecho, cuadrícula suave detrás de los datos y título en negrita. |
| `formato_es(numero)` | Escribe un número sin decimales y con punto de miles, como en español: `1430810` → `'1.430.810'`. Sirve como `fmt` de `bar_label()`. |
| `correlaciones(datos, columna_1, columna_2, decimales=2)` | Devuelve los coeficientes de Pearson y de Spearman entre dos columnas, y cuántas filas tienen los dos valores. Spearman necesita scipy. |
| `conectar_a_base_de_datos(user, password, host_ip, database)` | Abre una conexión a MySQL. |
| `correr_consulta(conexion, consulta, parametros=())` | Ejecuta una consulta SQL; los valores se pasan en `parametros` con `%s`. |
| `crear_dataframe(conexion, consulta, parametros=())` | Ejecuta una consulta SQL y devuelve el resultado como DataFrame. |

## Versión documentada

[`functions_documentado.py`](functions_documentado.py) tiene el mismo código que
`functions.py`, y además cada función con su docstring: el texto entre triple comilla que
explica qué hace, qué recibe y qué devuelve. Sirve para leer cómo funciona cada una. El
manual descarga y usa `functions.py`; si prefieres la versión documentada, guárdala como
`functions.py`, porque se comportan igual. Desde un cuaderno, el docstring se lee con
`help()`, por ejemplo `help(fn.detectar_outliers)`.

## Versiones usadas en el manual

[`requirements.txt`](requirements.txt) fija las versiones de las librerías con las que se
ejecutó todo el código del manual (Python 3.13). Para obtener exactamente las mismas
salidas, instálalas con el entorno virtual activo:

```bash
pip install -r requirements.txt
```

El ejemplo de `fg-data-profiling` (antes `ydata-profiling`) no está incluido: todavía no es
compatible con pandas 3 y se instala en un entorno aparte, como explica el manual.

## Datos de los ejemplos

La carpeta [`datos/`](datos) tiene los archivos que usan los ejemplos del manual:

| Archivo | Contenido |
|---|---|
| `alumnos.txt` | Dos alumnos de ejemplo, separados por comas. |
| `temperaturas.csv` | Temperaturas y precipitaciones anuales de ejemplo para 15 ciudades de Uruguay, 2015–2024. |
| `notas_2021.xlsx`, `notas_2022.xlsx`, `notas_2023.xlsx` | Notas de 100 estudiantes ficticios por año. |
| `archivo.csv`, `archivo_delimitado.txt`, `archivo_latin1.csv` | Doce personas ficticias, en CSV con coma, con punto y coma, y codificado en Latin-1. |
| `archivo.xlsx` | Excel con dos hojas (`Hoja1` y `Hoja2`). |
| `archivo_grande.csv`, `archivo_grande.xlsx` | 2500 filas, para leer por bloques. |
| `archivo.json`, `archivo.jsonl` | Tres registros en JSON y en JSON Lines. |
| `datos_clientes.csv` | CSV con un error de origen a propósito (falta una coma en la tercera línea). |

Los archivos genéricos se crean con [`generar_archivos_ejemplo.py`](datos/generar_archivos_ejemplo.py).

Son datos de ejemplo, pensados para practicar. El manual explica cómo descargarlos a una
carpeta `data/` junto al cuaderno.

## Requisitos

- Python 3 (probado con Python 3.13).
- `pandas` y `numpy` para la mayoría de las funciones.
- `matplotlib` para `aplicar_estilo()`, y `scipy` para el coeficiente de Spearman de `correlaciones()`.
- `mysql-connector-python` solo para las funciones de base de datos.

`check_libraries()` verifica además matplotlib, seaborn, tabulate, scipy, scikit-learn,
SQLAlchemy y las librerías de Jupyter, que se usan a lo largo del manual.

## Licencia

Código bajo licencia [MIT](LICENSE): puedes usarlo, modificarlo y distribuirlo,
incluso con fines comerciales, siempre que conserves el aviso de copyright.
La licencia cubre solo este código, no el contenido del manual.
