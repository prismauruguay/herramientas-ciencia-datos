"""Caja de herramientas del Manual de Ciencia de Datos.

Cada función tiene su docstring, el texto entre triple comilla que explica qué
hace, qué recibe y qué devuelve. Desde un cuaderno se lee con help(), por
ejemplo: help(fn.detectar_outliers).
"""
import importlib  # viene con Python: no hace falta instalarla
import subprocess  # librería para ejecutar comandos del sistema
import sys
import unicodedata

# pandas y numpy se importan con protección: si faltan, el módulo igual carga
# y check_libraries() puede informar qué instalar.
try:
    import numpy as np
    import pandas as pd
except ImportError:
    print('Faltan pandas o numpy. Ejecuta check_libraries() para ver qué instalar.')


def conectar_a_base_de_datos(user, password, host_ip, database):
    """Abre una conexión a una base de datos MySQL.

    Parámetros:
        user, password: usuario y contraseña de la base.
        host_ip: dirección del servidor.
        database: nombre de la base de datos.

    Devuelve la conexión, o None si no se pudo conectar. En ese caso imprime el
    motivo: acceso denegado, cuenta bloqueada, servidor fuera de línea u otro error.
    Necesita la librería mysql-connector-python.
    """
    # Se importa aquí para que el resto del módulo funcione sin MySQL instalado
    import mysql.connector  # pip install mysql-connector-python

    try:
        conexion = mysql.connector.connect(user=user, password=password,
                                           host=host_ip, database=database)
        if conexion.is_connected():
            return conexion
        return None
    except mysql.connector.Error as e:
        if e.errno == 1045:
            print('Acceso denegado:', e.msg)
        elif e.errno == 3118:
            print('Error: cuenta bloqueada.')
        elif e.errno == 2003:
            print('Error: servidor fuera de línea.')
        else:
            print(f'Error de MySQL {e.errno}: {e.msg}')
        return None
    except Exception as e:
        print(f'Error inesperado: {e}')
        return None


def correr_consulta(conexion, consulta, parametros=()):
    """Ejecuta una consulta SQL y devuelve sus filas.

    Parámetros:
        conexion: la conexión que devuelve conectar_a_base_de_datos().
        consulta: el texto SQL, con %s en el lugar de cada valor.
        parametros: los valores, en una tupla. Nunca se escriben dentro de la
            consulta con f-strings. Ejemplo:
            correr_consulta(con, 'SELECT * FROM t WHERE id = %s', (5,))

    Devuelve una lista de filas (vacía en INSERT, UPDATE o DELETE), o None si no
    hay conexión. Si la consulta modifica datos, confirma los cambios con commit().
    """
    if not conexion:
        return None
    with conexion.cursor() as cursor:  # el cursor se cierra aunque haya un error
        cursor.execute(consulta, parametros)
        resultado = cursor.fetchall()  # en INSERT, UPDATE o DELETE devuelve []
        if not consulta.strip().upper().startswith(('SELECT', 'SHOW', 'DESCRIBE', 'WITH')):
            conexion.commit()
    return resultado


def crear_dataframe(conexion, consulta, parametros=()):
    """Ejecuta una consulta SQL y devuelve el resultado como DataFrame.

    Recibe lo mismo que correr_consulta(). Las columnas del DataFrame llevan los
    nombres de las columnas de la consulta. Si no hay conexión, devuelve un
    DataFrame vacío.
    """
    if not conexion:
        return pd.DataFrame()
    with conexion.cursor() as cursor:
        cursor.execute(consulta, parametros)
        columnas = [col[0] for col in cursor.description]
        filas = cursor.fetchall()
    return pd.DataFrame(filas, columns=columnas)


crear_Dataframe = crear_dataframe  # nombre anterior, para no romper código existente


def normalizar_texto(texto, conservar_enie=False):
    """Deja un texto listo para comparar: minúsculas, sin espacios en los extremos y sin tildes.

    Parámetros:
        texto: el texto a normalizar.
        conservar_enie: por defecto la ñ también se convierte en n
            ('año' -> 'ano'); con True se mantiene ('año' -> 'año').

    Devuelve el texto normalizado, o NaN si el texto está vacío o es NaN.
    """
    if pd.isna(texto) or str(texto).strip() == '':  # cadena vacía o NaN
        return np.nan
    texto = str(texto).strip().lower()
    if conservar_enie:
        texto = texto.replace('ñ', '\x00')  # se protege la ñ antes de quitar tildes
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ascii')
    if conservar_enie:
        texto = texto.replace('\x00', 'ñ')
    return texto


def ver_niveles_categoricos(df, diccionario):
    """Muestra, para cada columna categórica, cuántos niveles se esperan y cuántos hay.

    Parámetros:
        df: el DataFrame.
        diccionario: {nombre_de_columna: cantidad_de_niveles_esperada}.

    Imprime los niveles encontrados y la frecuencia de cada uno, incluidos los NaN.
    No devuelve nada.
    """
    for columna, nivel in diccionario.items():
        print('\nColumna:', columna)
        print(f'Nivel máximo esperado: {nivel} | Niveles encontrados: {df[columna].nunique()}')
        print('Frecuencias:')
        print(df[columna].value_counts(dropna=False))  # dropna=False muestra también los NaN


def detectar_outliers(data, factor=1.5):
    """Detecta valores atípicos con el método de Tukey (rango intercuartílico).

    Un valor es atípico si está por debajo de Q1 - factor * IQR o por encima de
    Q3 + factor * IQR, donde Q1 y Q3 son los cuartiles e IQR = Q3 - Q1.

    Parámetros:
        data: una Series de pandas con los valores.
        factor: 1.5 es el criterio habitual de Tukey (valores atípicos);
            3.0 es el criterio para valores atípicos extremos.

    Devuelve una Series con los valores atípicos y su índice original. Si no
    hay ninguno, la Series está vacía.

    El método supone una distribución más o menos simétrica. Con datos muy
    asimétricos marca demasiados valores en la cola larga; en ese caso conviene
    transformar antes (por ejemplo, con logaritmo) o usar el boxplot ajustado de
    Hubert y Vandervieren (2008).
    """
    q1 = data.quantile(0.25)
    q3 = data.quantile(0.75)
    iqr = q3 - q1
    return data[(data < q1 - factor * iqr) | (data > q3 + factor * iqr)]


# Funciones para determinar la cantidad de bins (intervalos) de un histograma.
# Todas descartan los NaN, devuelven al menos 1 bin y devuelven dos cosas: la
# cantidad de bins y el nombre de la regla.

def _preparar(muestra):
    """Convierte la muestra en una Series de números decimales, sin NaN. Uso interno."""
    return pd.Series(muestra, dtype=float).dropna()


def _bins_por_ancho(muestra, ancho):
    """Cuántos bins de un ancho dado hacen falta para cubrir la muestra. Uso interno.

    Devuelve al menos 1, también cuando el ancho es 0 o todos los valores son iguales.
    """
    rango = muestra.max() - muestra.min()
    if ancho <= 0 or rango == 0:
        return 1
    return max(1, int(np.ceil(rango / ancho)))


def bins_sturges(muestra):
    """Cantidad de bins según la regla de Sturges: log2(n) + 1.

    Simple y rápida. Supone datos aproximadamente normales; con muestras muy
    grandes da pocos bins.

    Devuelve (cantidad_de_bins, 'Regla de Sturges').
    """
    n = len(_preparar(muestra))
    bins = int(np.ceil(np.log2(n))) + 1 if n > 0 else 1
    return bins, 'Regla de Sturges'


def bins_freedman_diaconis(muestra):
    """Cantidad de bins según la regla de Freedman-Diaconis.

    El ancho de cada bin es 2 * IQR / n^(1/3), donde IQR es el rango
    intercuartílico y n la cantidad de datos. Como usa el IQR, igual que el
    método de Tukey, es robusta frente a valores atípicos. Si más de la mitad de
    los datos son iguales (IQR = 0), usa la regla de Scott.

    Devuelve (cantidad_de_bins, 'Regla de Freedman-Diaconis').
    """
    muestra = _preparar(muestra)
    n = len(muestra)
    if n == 0:
        return 1, 'Regla de Freedman-Diaconis'
    iqr = muestra.quantile(0.75) - muestra.quantile(0.25)
    if iqr == 0:  # más de la mitad de los datos son iguales: se usa Scott
        return bins_scott(muestra)
    ancho = 2 * iqr * n ** (-1 / 3)
    return _bins_por_ancho(muestra, ancho), 'Regla de Freedman-Diaconis'


def bins_scott(muestra):
    """Cantidad de bins según la regla de Scott.

    El ancho de cada bin es 3.5 * desviación estándar / n^(1/3). Pensada para
    datos con distribución aproximadamente normal.

    Devuelve (cantidad_de_bins, 'Regla de Scott').
    """
    muestra = _preparar(muestra)
    n = len(muestra)
    if n == 0:
        return 1, 'Regla de Scott'
    sigma = muestra.std(ddof=0)
    ancho = 3.5 * sigma * n ** (-1 / 3)
    return _bins_por_ancho(muestra, ancho), 'Regla de Scott'


def bins_rice(muestra):
    """Cantidad de bins según la regla de Rice: 2 * n^(1/3).

    No supone ninguna distribución en particular.

    Devuelve (cantidad_de_bins, 'Regla de Rice').
    """
    n = len(_preparar(muestra))
    bins = int(np.ceil(2 * n ** (1 / 3))) if n > 0 else 1
    return bins, 'Regla de Rice'


# Funciones para gráficos y para presentar resultados

def aplicar_estilo():
    """Aplica un estilo común a todos los gráficos de matplotlib.

    Sin bordes superior y derecho, con una cuadrícula suave detrás de los datos
    y el título en negrita. Modifica plt.rcParams, así que vale para todos los
    gráficos que se hagan después. No cambia los colores: esos son una decisión
    de cada proyecto y van en su config.py. No devuelve nada.
    """
    # Se importa aquí para que el módulo funcione sin matplotlib
    import matplotlib.pyplot as plt

    plt.rcParams.update({
        'axes.spines.top': False,
        'axes.spines.right': False,
        'axes.grid': True,
        'grid.color': '#e1e0d9',
        'axes.axisbelow': True,
        'axes.titleweight': 'bold',
    })


def formato_es(numero):
    """Escribe un número sin decimales y con punto de miles, como se escribe en español.

    Ejemplo: formato_es(1430810) devuelve '1.430.810'.

    El formato ',.0f' escribe el número sin decimales y con coma de miles
    ('1,430,810'); después se cambia la coma por el punto. Devuelve un texto.
    """
    return f'{numero:,.0f}'.replace(',', '.')


def correlaciones(datos, columna_1, columna_2, decimales=2):
    """Coeficientes de correlación de Pearson y de Spearman entre dos columnas.

    Parámetros:
        datos: el DataFrame.
        columna_1, columna_2: los nombres de las dos columnas.
        decimales: con cuántos decimales se redondean los coeficientes.

    Devuelve (pearson, spearman, filas): los dos coeficientes y la cantidad de
    filas que tienen los dos valores, que son las que usa corr().
    Spearman necesita la librería scipy instalada.
    """
    valores_1 = datos[columna_1]
    valores_2 = datos[columna_2]
    pearson = valores_1.corr(valores_2, method='pearson')
    spearman = valores_1.corr(valores_2, method='spearman')
    filas = (valores_1.notna() & valores_2.notna()).sum()
    return round(pearson, decimales), round(spearman, decimales), filas


def resumen_general(df):
    """Imprime un resumen de un DataFrame.

    Muestra la dimensión (filas, columnas), el tipo de cada columna, la cantidad
    de valores nulos por columna y la descripción estadística de describe(), con
    todas las columnas. No devuelve nada.
    """
    print("\n- Dimensión del DataFrame:", df.shape)
    print("\n- Tipos de datos:\n", df.dtypes)
    print("\n- Valores nulos por columna:\n", df.isna().sum())
    print("\n- Descripción estadística:\n", df.describe(include='all'))


def check_libraries(auto_install=False):
    """Verifica si las librerías necesarias están instaladas y permite su instalación.

    Parámetros:
        auto_install: con False (por defecto) solo informa qué falta y el comando
            para instalarlo; con True lo instala con pip.

    No devuelve nada.
    """
    # (nombre para importar, nombre para pip install): no siempre coinciden
    required_libraries = [
        ("mysql.connector", "mysql-connector-python"),
        ("pandas", "pandas"),
        ("numpy", "numpy"),
        ("matplotlib", "matplotlib"),
        ("seaborn", "seaborn"),
        ("tabulate", "tabulate"),
        ("scipy", "scipy"),
        ("sklearn", "scikit-learn"),
        ("sqlalchemy", "sqlalchemy"),
        ("jupyter_client", "jupyter_client"),
        ("jupyter_core", "jupyter_core"),
        ("ipykernel", "ipykernel"),
    ]

    missing_libs = []
    for modulo, paquete in required_libraries:
        try:
            importlib.import_module(modulo)
        except ImportError:
            missing_libs.append(paquete)

    if missing_libs:
        print(f"Las siguientes librerías faltan en el entorno virtual:\n{missing_libs}")
        if auto_install:
            print("Instalando librerías automáticamente...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", *missing_libs])
            print("Instalación completa. Vuelve a ejecutar tu código.")
        else:
            print("Ejecuta manualmente: pip install " + " ".join(missing_libs))
    else:
        print("Todas las librerías necesarias están correctamente instaladas.")
