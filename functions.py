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
    # Los valores van en parametros, con %s en la consulta (nunca con f-strings):
    # correr_consulta(con, 'SELECT * FROM t WHERE id = %s', (5,))
    if not conexion:
        return None
    with conexion.cursor() as cursor:  # el cursor se cierra aunque haya un error
        cursor.execute(consulta, parametros)
        resultado = cursor.fetchall()  # en INSERT, UPDATE o DELETE devuelve []
        if not consulta.strip().upper().startswith(('SELECT', 'SHOW', 'DESCRIBE', 'WITH')):
            conexion.commit()
    return resultado


def crear_dataframe(conexion, consulta, parametros=()):
    # Función práctica para crear un DataFrame a partir de una consulta SQL
    if not conexion:
        return pd.DataFrame()
    with conexion.cursor() as cursor:
        cursor.execute(consulta, parametros)
        columnas = [col[0] for col in cursor.description]
        filas = cursor.fetchall()
    return pd.DataFrame(filas, columns=columnas)


crear_Dataframe = crear_dataframe  # nombre anterior, para no romper código existente


def normalizar_texto(texto, conservar_enie=False):
    # Pasa a minúsculas, quita espacios en los extremos y quita las tildes.
    # Por defecto la ñ también se convierte en n ('año' -> 'ano');
    # con conservar_enie=True se mantiene ('año' -> 'año').
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
    for columna, nivel in diccionario.items():
        print('\nColumna:', columna)
        print(f'Nivel máximo esperado: {nivel} | Niveles encontrados: {df[columna].nunique()}')
        print('Frecuencias:')
        print(df[columna].value_counts(dropna=False))  # dropna=False muestra también los NaN


# Detectar valores atípicos con el método de Tukey (rango intercuartílico)
def detectar_outliers(data, factor=1.5):
    # factor = 1.5: criterio habitual de Tukey (valores atípicos)
    # factor = 3.0: criterio de Tukey para valores atípicos extremos
    # El método supone una distribución más o menos simétrica. Con datos muy
    # asimétricos marca demasiados valores en la cola larga; en ese caso conviene
    # transformar antes (por ejemplo, con logaritmo) o usar el boxplot ajustado
    # de Hubert y Vandervieren (2008).
    q1 = data.quantile(0.25)
    q3 = data.quantile(0.75)
    iqr = q3 - q1
    return data[(data < q1 - factor * iqr) | (data > q3 + factor * iqr)]


# Funciones para determinar la cantidad de bins según el contexto de los datos.
# Todas descartan los NaN y devuelven al menos 1 bin.

def _preparar(muestra):
    return pd.Series(muestra, dtype=float).dropna()


def _bins_por_ancho(muestra, ancho):
    rango = muestra.max() - muestra.min()
    if ancho <= 0 or rango == 0:
        return 1
    return max(1, int(np.ceil(rango / ancho)))


def bins_sturges(muestra):
    # Simple y rápida. Supone datos aproximadamente normales;
    # con muestras muy grandes da pocos bins.
    n = len(_preparar(muestra))
    bins = int(np.ceil(np.log2(n))) + 1 if n > 0 else 1
    return bins, 'Regla de Sturges'


def bins_freedman_diaconis(muestra):
    # Usa el rango intercuartílico: es robusta frente a valores atípicos
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
    # Pensada para datos con distribución aproximadamente normal
    muestra = _preparar(muestra)
    n = len(muestra)
    if n == 0:
        return 1, 'Regla de Scott'
    sigma = muestra.std(ddof=0)
    ancho = 3.5 * sigma * n ** (-1 / 3)
    return _bins_por_ancho(muestra, ancho), 'Regla de Scott'


def bins_rice(muestra):
    # No supone ninguna distribución en particular
    n = len(_preparar(muestra))
    bins = int(np.ceil(2 * n ** (1 / 3))) if n > 0 else 1
    return bins, 'Regla de Rice'


def resumen_general(df):
    print("\n- Dimensión del DataFrame:", df.shape)
    print("\n- Tipos de datos:\n", df.dtypes)
    print("\n- Valores nulos por columna:\n", df.isna().sum())
    print("\n- Descripción estadística:\n", df.describe(include='all'))


def check_libraries(auto_install=False):
    """Verifica si las librerías necesarias están instaladas y permite su instalación."""
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
