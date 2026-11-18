"""Genera los archivos genéricos que usan los ejemplos de lectura del manual.

Todos los datos son ficticios. Ejecutar desde la carpeta datos/:
    python generar_archivos_ejemplo.py
"""
import json

import numpy as np
import pandas as pd

personas = pd.DataFrame({
    'ID': range(1, 13),
    'Nombre': ['Juan', 'Ana', 'Pedro', 'María', 'José', 'Lucía',
               'Martín', 'Sofía', 'Diego', 'Valentina', 'Andrés', 'Camila'],
    'Edad': [25, 30, 35, 28, 42, 23, 37, 31, 45, 27, 33, 29],
    'Ciudad': ['Montevideo', 'Salto', 'Paysandú', 'Rivera', 'Maldonado', 'Colonia',
               'Tacuarembó', 'Durazno', 'Florida', 'Rocha', 'Artigas', 'Canelones'],
})

# CSV estándar (UTF-8, separado por comas)
personas.to_csv('archivo.csv', index=False, encoding='utf-8', lineterminator='\n')

# El mismo contenido guardado en Latin-1: al leerlo como UTF-8, las tildes dan error
personas.to_csv('archivo_latin1.csv', index=False, encoding='latin-1', lineterminator='\n')

# Separado por punto y coma
personas.to_csv('archivo_delimitado.txt', sep=';', index=False, encoding='utf-8', lineterminator='\n')

# Archivos grandes, para leer por bloques
rng = np.random.default_rng(42)
grande = pd.DataFrame({
    'ID': range(1, 2501),
    'Categoria': rng.choice(['A', 'B', 'C'], size=2500),
    'Valor': rng.integers(100, 1000, size=2500),
})
grande.to_csv('archivo_grande.csv', index=False, encoding='utf-8', lineterminator='\n')
grande.to_excel('archivo_grande.xlsx', index=False)

# Excel con dos hojas
hoja1 = pd.DataFrame({
    'Columna1': ['Manzanas', 'Naranjas', 'Peras', 'Uvas', 'Bananas'],
    'Columna2': [3.5, 2.75, 4.0, 5.25, 1.9],
    'Columna3': [10, 5, 8, 12, 20],
})
hoja2 = pd.DataFrame({'Mes': ['Enero', 'Febrero', 'Marzo'], 'Ventas': [120, 95, 140]})
with pd.ExcelWriter('archivo.xlsx') as writer:
    hoja1.to_excel(writer, sheet_name='Hoja1', index=False)
    hoja2.to_excel(writer, sheet_name='Hoja2', index=False)

# JSON (lista de registros) y JSON Lines (un registro por línea)
productos = [
    {'Nombre': 'Juan', 'Edad': 25, 'Precio': 120.5},
    {'Nombre': 'Ana', 'Edad': 30, 'Precio': 89.9},
    {'Nombre': 'Pedro', 'Edad': 35, 'Precio': 150.0},
]
with open('archivo.json', 'w', encoding='utf-8', newline='\n') as f:
    json.dump(productos, f, ensure_ascii=False, indent=4)
with open('archivo.jsonl', 'w', encoding='utf-8', newline='\n') as f:
    for registro in productos:
        f.write(json.dumps(registro, ensure_ascii=False) + '\n')

# CSV con un error de origen a propósito: falta la coma entre la edad y la ciudad de Ana
with open('datos_clientes.csv', 'w', encoding='utf-8', newline='\n') as f:
    f.write('nombre,edad,ciudad\nJuan,25,Montevideo\nAna,30Flores\nLuis,22,Maldonado\n')

print('Archivos generados.')
