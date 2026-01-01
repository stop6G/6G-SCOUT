import sys
import re
import csv
import ast

def clean_js_content(js_string):
    """
    Limpia el string de JS para que sea interpretable por Python.
    1. Elimina comentarios (// ...)
    2. Pone comillas a las claves (id: -> "id":)
    3. Convierte true/false a True/False
    """
    # Eliminar comentarios de línea (// ...)
    js_string = re.sub(r'//.*', '', js_string)
    
    # Reemplazos básicos para compatibilidad JS -> Python
    replacements = {
        'true': 'True',
        'false': 'False',
        'null': 'None'
    }
    for old, new in replacements.items():
        js_string = re.sub(r'\b' + old + r'\b', new, js_string)

    # Poner comillas a las claves del objeto (ej: group: 1 -> "group": 1)
    # Busca palabras seguidas de : pero evita URL (http:)
    js_string = re.sub(r'(?<!https)(?<!http)(\s*)(\w+)(\s*):', r'\1"\2":', js_string)
    
    return js_string

def parse_and_write(raw_array_string, filename):
    clean_str = clean_js_content(raw_array_string)
    
    try:
        # Usamos ast.literal_eval que es más permisivo que json.loads para estructuras de Python/JS
        data_list = ast.literal_eval(clean_str)
        
        if not data_list or not isinstance(data_list, list):
            print(f"  [!] No se encontraron datos de lista válidos para {filename}")
            return

        # Obtener encabezados dinámicamente
        keys = set()
        for item in data_list:
            keys.update(item.keys())
        
        # Ordenar columnas (poniendo id/source/target primero si existen)
        header = sorted(list(keys))
        priority_cols = ['id', 'source', 'target', 'label', 'group']
        for col in reversed(priority_cols):
            if col in header:
                header.insert(0, header.pop(header.index(col)))

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=header)
            writer.writeheader()
            writer.writerows(data_list)
        
        print(f"  [OK] '{filename}' creado exitosamente ({len(data_list)} filas).")

    except Exception as e:
        print(f"  [ERROR] Falló al procesar {filename}: {e}")
        # Debug: guardar el texto que falló para inspección
        with open(f"debug_{filename}.txt", "w", encoding="utf-8") as f:
            f.write(clean_str)
        print(f"         (Se guardó 'debug_{filename}.txt' para revisar el error de sintaxis)")

def main():
    if len(sys.argv) < 2:
        print("Uso: python nodes-links2csv.py <archivo.html>")
        sys.exit(1)

    filepath = sys.argv[1]
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print("El archivo no existe.")
        sys.exit(1)

    print(f"Procesando {filepath}...")

    # Extraer el bloque de nodos usando Regex específico para tu estructura "nodes: [ ... ]"
    # Buscamos desde "nodes: [" hasta el cierre "]," (asumiendo indentación o estructura similar)
    # El flag DOTALL permite que el punto coincida con saltos de línea
    nodes_match = re.search(r'nodes:\s*(\[\s*\{.*?\n\s*\])', content, re.DOTALL)
    links_match = re.search(r'links:\s*(\[\s*\{.*?\n\s*\])', content, re.DOTALL)

    if nodes_match:
        print("Variables 'nodes' encontrada. Extrayendo...")
        parse_and_write(nodes_match.group(1), 'nodes.csv')
    else:
        print("No se encontró la estructura 'nodes: [...]'")

    if links_match:
        print("Variables 'links' encontrada. Extrayendo...")
        parse_and_write(links_match.group(1), 'links.csv')
    else:
        print("No se encontró la estructura 'links: [...]'")

if __name__ == "__main__":
    main()
