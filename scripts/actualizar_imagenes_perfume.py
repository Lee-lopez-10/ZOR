import os
import re
import unicodedata
import pyodbc

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
IMG_DIR = os.path.join(REPO, 'static', 'img', 'perfumes')

EXT_PRIORITY = ['webp', 'avif', 'png', 'jpg', 'jpeg', 'gif']


def slugify(text):
    if text is None:
        return ''
    text = unicodedata.normalize('NFD', str(text))
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    text = text.lower().strip()
    text = re.sub(r'[^a-z0-9]+', '_', text)
    text = re.sub(r'^_+|_+$', '', text)
    return text


def build_file_index():
    files = {}
    if not os.path.isdir(IMG_DIR):
        return files
    for name in os.listdir(IMG_DIR):
        path = os.path.join(IMG_DIR, name)
        if not os.path.isfile(path):
            continue
        base, ext = os.path.splitext(name)
        ext = ext.lstrip('.').lower()
        if ext not in EXT_PRIORITY:
            continue
        key = base.lower()
        if key not in files or EXT_PRIORITY.index(ext) < EXT_PRIORITY.index(files[key][1]):
            files[key] = (name, ext)
    return files


def get_connection():
    return pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=DESKTOP-01R0RM2;'
        'DATABASE=PerfumeriaDB;'
        'Trusted_Connection=yes;'
    )


def main():
    index = build_file_index()
    if not index:
        print('No se encontraron imágenes en static/img/perfumes')
        return

    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT ID_Perfume, Nombre, Marca, Imagen FROM Perfume')
    rows = cur.fetchall()

    updates = []

    for (pid, nombre, marca, imagen) in rows:
        if imagen:
            img_path = str(imagen).strip().replace('static/', '')
            if '/' not in img_path:
                img_path = f'img/perfumes/{img_path}'
            abs_path = os.path.join(REPO, 'static', img_path.replace('/', os.sep))
            if os.path.exists(abs_path):
                continue

        candidates = []
        s_nombre = slugify(nombre)
        s_marca = slugify(marca)
        if s_nombre:
            candidates.append(s_nombre)
        if s_marca and s_nombre:
            candidates.append(f'{s_marca}_{s_nombre}')
            candidates.append(f'{s_nombre}_{s_marca}')

        match = None
        for key in candidates:
            if key in index:
                match = index[key][0]
                break

        if match:
            new_val = f'img/perfumes/{match}'
            updates.append((new_val, pid, nombre))

    if updates:
        for new_val, pid, _ in updates:
            cur.execute('UPDATE Perfume SET Imagen = ? WHERE ID_Perfume = ?', (new_val, pid))
        conn.commit()

    conn.close()

    print(f'Actualizados: {len(updates)}')
    for new_val, pid, nombre in updates:
        print(f'  {pid} | {nombre} -> {new_val}')


if __name__ == '__main__':
    main()
