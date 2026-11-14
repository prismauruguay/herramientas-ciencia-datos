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
   %load_ext autoreload
   %autoreload 2
   import functions as fn
   ```

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
| `conectar_a_base_de_datos(user, password, host_ip, database)` | Abre una conexión a MySQL. |
| `correr_consulta(conexion, consulta, parametros=())` | Ejecuta una consulta SQL; los valores se pasan en `parametros` con `%s`. |
| `crear_dataframe(conexion, consulta, parametros=())` | Ejecuta una consulta SQL y devuelve el resultado como DataFrame. |

## Requisitos

- Python 3 (probado con Python 3.13).
- `pandas` y `numpy` para la mayoría de las funciones.
- `mysql-connector-python` solo para las funciones de base de datos.

`check_libraries()` verifica además matplotlib, seaborn, tabulate, scipy, scikit-learn
y las librerías de Jupyter, que se usan a lo largo del manual.

## Licencia

Código bajo licencia [MIT](LICENSE): puedes usarlo, modificarlo y distribuirlo,
incluso con fines comerciales, siempre que conserves el aviso de copyright.
La licencia cubre solo este código, no el contenido del manual.
