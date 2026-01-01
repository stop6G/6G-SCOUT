import sys
import re
import csv
import ast

def clean_js_content(js_string):
    # Eliminar comentarios de JS (// ...)
    js_string = re.sub(r'//.*', '', js_string)
    # Convertir true/false/null
    js_string = re.sub(r'\btrue\b', 'True', js_string)
    js_string = re.sub(r'\bfalse\b', 'False', js_string)
    js_string = re.sub(r'\bnull\b', 'None', js_string)
    # Poner comillas a las claves (ej: id: -> "id":)
    js_string = re.sub(r'(?<!https)(?<!http)(\s+)(\w+)(\s*):', r'\1"\2":', js_string)
    return js_string

def parse_and_write(raw_array_string, filename):
    clean_str = clean_js_content(raw_array_string)
    try:
        data_list = ast.literal_eval(clean_str)
        if not data_list or not isinstance(data_list, list):
            return

        # Obtener headers dinámicos
        keys = set()
        for item in data_list:
            keys.update(item.keys())
        
        # Ordenar columnas preferidas primero
        header = sorted(list(keys))
        priority = ['id', 'source', 'target', 'label', 'group', 'amount', 'type']
        for col in reversed(priority):
            if col in header:
                header.insert(0, header.pop(header.index(col)))

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=header)
            writer.writeheader()
            writer.writerows(data_list)
        print(f"Creado: {filename}")
    except Exception as e:
        print(f"Error procesando {filename}: {e}")

# Leer el archivo index.html
try:
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # Extraer bloques usando regex
    nodes_match = re.search(r'nodes:\s*(\[\s*\{.*?\n\s*\}\s*\])', content, re.DOTALL)
    links_match = re.search(r'links:\s*(\[\s*\{.*?\n\s*\}\s*\])', content, re.DOTALL)

    if nodes_match: parse_and_write(nodes_match.group(1), 'nodes.csv')
    if links_match: parse_and_write(links_match.group(1), 'links.csv')

except FileNotFoundError:
    print("Por favor guarda el archivo HTML como 'index.html' para ejecutar el script.")
