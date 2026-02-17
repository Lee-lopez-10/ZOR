from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from database import get_connection
import json
import os
import re
import unicodedata
from decimal import Decimal, InvalidOperation
from werkzeug.utils import secure_filename 

app = Flask(__name__)
app.secret_key = "magnate_secreto"

# --- CONFIGURACIÓN PARA IMÁGENES (ESTO ES LO IMPORTANTE) ---
# 1. Definimos la carpeta (asegúrate de haberla creado en static/img/perfumes)
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'img', 'perfumes')

# 2. Definimos las extensiones permitidas (Esto arregla el KeyError)
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'webp','avif'}
PERFUME_IMG_EXTS = ['webp', 'png', 'jpg', 'jpeg', 'avif']

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def normalize_static_image_path(image_value):
    if not image_value:
        return ''
    image_value = str(image_value).strip()
    if not image_value:
        return ''
    image_value = image_value.lstrip('/')
    if image_value.startswith('static/'):
        image_value = image_value[len('static/'):]
    if '/' in image_value:
        return image_value
    return f'img/perfumes/{image_value}'

def slugify_nombre(nombre):
    if not nombre:
        return ''
    texto = unicodedata.normalize('NFD', str(nombre))
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
    texto = texto.lower().strip()
    texto = re.sub(r'[^a-z0-9]+', '_', texto)
    texto = re.sub(r'^_+|_+$', '', texto)
    return texto

def resolve_perfume_image(nombre, imagen_val):
    # 1) Usar imagen guardada si existe físicamente
    norm = normalize_static_image_path(imagen_val)
    if norm:
        abs_path = os.path.join(app.root_path, 'static', norm.replace('/', os.sep))
        if os.path.exists(abs_path):
            return norm
        # probar otras extensiones con el mismo nombre base
        base = norm.rsplit('.', 1)[0] if '.' in norm else norm
        for ext in PERFUME_IMG_EXTS:
            cand = f"{base}.{ext}"
            abs_cand = os.path.join(app.root_path, 'static', cand.replace('/', os.sep))
            if os.path.exists(abs_cand):
                return cand

    # 2) Buscar por slug del nombre
    slug = slugify_nombre(nombre)
    if slug:
        for ext in PERFUME_IMG_EXTS:
            cand = f"img/perfumes/{slug}.{ext}"
            abs_cand = os.path.join(app.root_path, 'static', cand.replace('/', os.sep))
            if os.path.exists(abs_cand):
                return cand

    return ''

# ==========================================
#  A PARTIR DE AQUÍ TUS RUTAS (@app.route...)
# =====================================================================

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Intentamos conectarnos
        conn = get_connection()
        if not conn:
            flash("Error al conectar a la base de datos.", "error")
            return render_template('login.html')

        try:
            cursor = conn.cursor()
            
            # Obtenemos también el Nombre del Rol haciendo JOIN
            sql = """
                SELECT U.ID_Usuario, U.Nombre, R.NombreRol 
                FROM Usuario U
                INNER JOIN Rol R ON U.ID_Rol = R.ID_Rol
                WHERE U.Email = ? AND U.Contrasena = ?
            """
            cursor.execute(sql, (email, password))
            usuario = cursor.fetchone()
        except Exception as e:
            flash(f"Error en la consulta: {e}", "error")
            usuario = None
        finally:
            conn.close()

        if usuario:
            session['id_usuario'] = usuario[0]
            session['nombre'] = usuario[1]
            session['rol'] = usuario[2]  # Guardamos 'Administrador' o 'Vendedor'

            # REGLA DE NEGOCIO: Redirección inteligente
            if session['rol'] == 'Administrador':
                return redirect(url_for('dashboard'))  # Admin va al Inventario
            else:
                return redirect(url_for('ventas'))     # Vendedor va directo a Vender
        else:
            flash("Credenciales incorrectas", "error")

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ==========================================
#  2. INVENTARIO (SOLO ADMIN) 🔒
# ==========================================

@app.route('/dashboard')
def dashboard():
    if 'id_usuario' not in session: return redirect(url_for('login'))
    if session['rol'] != 'Administrador':
        flash("⛔ Acceso denegado.", "error")
        return redirect(url_for('ventas'))
    
    conn = get_connection()
    if not conn:
        flash("Error al conectar a la base de datos.", "error")
        return render_template('dashboard.html', lista=[], ventas=0, alertas=0)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            ID_Perfume,
            Nombre,
            Marca,
            Precio,
            Stock,
            Genero,
            Mililitros,
            Imagen,
            Estado
        FROM Perfume
        WHERE Estado = 1 OR Estado IS NULL
        ORDER BY ID_Perfume DESC
    """)
    lista = cursor.fetchall()

    # KPIs Rápidos
    cursor.execute("SELECT ISNULL(SUM(Total), 0) FROM Pedido WHERE CAST(FechaPedido AS DATE) = CAST(GETDATE() AS DATE)")
    ventas_hoy = cursor.fetchone()[0] or 0
    
    cursor.execute("SELECT COUNT(*) FROM Perfume WHERE Stock <= 5 AND (Estado = 1 OR Estado IS NULL)")
    alertas = cursor.fetchone()[0] or 0
    
    conn.close()
    return render_template('dashboard.html', lista=lista, ventas=ventas_hoy, alertas=alertas)
# --- RUTAS DE EDICIÓN (PROTEGIDAS) ---

@app.route('/guardar', methods=['POST'])
def guardar_producto():
    if 'id_usuario' not in session: return redirect(url_for('login'))
    if session['rol'] != 'Administrador': return redirect(url_for('ventas'))
    
    # RECUPERAR EL ORIGEN
    origen = request.form.get('origen')
    
    id_prod = request.form.get('id_producto')
    nombre = request.form['nombre']
    marca = request.form.get('marca', '').strip()
    descripcion = request.form.get('descripcion', '').strip()
    genero = request.form.get('genero', '').strip()
    mililitros = request.form.get('mililitros') or None
    precio = request.form['precio']
    stock = request.form['stock']
    estado = 1 if request.form.get('estado') == 'on' else 0
    
    archivo = request.files['imagen']
    nombre_imagen = None 

    if archivo and archivo.filename != '' and allowed_file(archivo.filename):
        filename = secure_filename(archivo.filename)
        archivo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        nombre_imagen = filename

    conn = get_connection()
    cursor = conn.cursor()
    
    if id_prod:
        if nombre_imagen:
            sql = """
                UPDATE Perfume 
                SET Nombre=?, Marca=?, Descripcion=?, Precio=?, Stock=?, Genero=?, Mililitros=?, Imagen=?, Estado=?
                WHERE ID_Perfume=?
            """
            cursor.execute(sql, (nombre, marca, descripcion, precio, stock, genero, mililitros, nombre_imagen, estado, id_prod))
        else:
            sql = """
                UPDATE Perfume 
                SET Nombre=?, Marca=?, Descripcion=?, Precio=?, Stock=?, Genero=?, Mililitros=?, Estado=?
                WHERE ID_Perfume=?
            """
            cursor.execute(sql, (nombre, marca, descripcion, precio, stock, genero, mililitros, estado, id_prod))
        flash("Perfume actualizado correctamente", "success")
    else:
        imagen_final = nombre_imagen if nombre_imagen else ''
        sql = """
            INSERT INTO Perfume (Nombre, Marca, Descripcion, Precio, Stock, Genero, Mililitros, Imagen, Estado)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(sql, (nombre, marca, descripcion, precio, stock, genero, mililitros, imagen_final, estado))
        flash("Perfume creado con éxito", "success")
        
    conn.commit()
    conn.close()
    
    # REDIRECCIÓN INTELIGENTE
    if origen == 'entrada_stock':
        # Si venimos de registrar pedido, volvemos ahí
        return redirect(url_for('entrada_stock'))
    
    return redirect(url_for('dashboard'))

@app.route('/eliminar/<int:id>')
def eliminar_producto(id):
    if 'id_usuario' not in session: return redirect(url_for('login'))
    if session['rol'] != 'Administrador': return redirect(url_for('ventas')) # Protección extra
    
    conn = get_connection()
    try:
        conn.cursor().execute("DELETE FROM Perfume WHERE ID_Perfume = ?", (id,))
        conn.commit()
        flash("Eliminado correctamente", "success")
    except:
        flash("No se puede eliminar: Tiene ventas registradas", "error")
    finally:
        conn.close()
    return redirect(url_for('dashboard'))

@app.route('/producto/nuevo')
@app.route('/producto/editar/<int:id>')
def formulario_producto(id=None):
    if 'id_usuario' not in session: return redirect(url_for('login'))
    if session['rol'] != 'Administrador': return redirect(url_for('ventas'))
    
    # CAPTURAR SI VENIMOS DE OTRA PANTALLA
    origen = request.args.get('origen')
    
    conn = get_connection()
    cursor = conn.cursor()
    prod = None
    if id:
        cursor.execute("""
            SELECT ID_Perfume, Nombre, Marca, Descripcion, Precio, Stock, Genero, Mililitros, Imagen, Estado
            FROM Perfume
            WHERE ID_Perfume=?
        """, (id,))
        prod = cursor.fetchone()
    
    conn.close()
    return render_template('formulario.html', producto=prod, origen=origen)

# ==========================================
#  3. PUNTO DE VENTA Y REPORTES (PARA TODOS)
# ==========================================

@app.route('/ventas')
def ventas():
    if 'id_usuario' not in session: return redirect(url_for('login'))   
    # Tanto Admin como Vendedor pueden entrar aquí
    return render_template('ventas.html')

@app.route('/reporte_diario')
def reporte_diario():
    if 'id_usuario' not in session: return redirect(url_for('login'))
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. LISTA DE TICKETS (Como antes)
    sql_ventas = """
        SELECT P.ID_Pedido, P.FechaPedido, P.Total, P.Estado, U.Nombre, C.Nombre, P.Descuento
        FROM Pedido P
        INNER JOIN Usuario U ON P.ID_Usuario = U.ID_Usuario
        LEFT JOIN Cliente C ON P.ID_Cliente = C.ID_Cliente
        WHERE CAST(P.FechaPedido AS DATE) = CAST(GETDATE() AS DATE) 
        ORDER BY P.ID_Pedido DESC
    """
    cursor.execute(sql_ventas)
    ventas_raw = cursor.fetchall()
    
    # Sumamos el total (índice 2)
    total = sum(v[2] for v in ventas_raw)

    ventas = []
    for v in ventas_raw:
        estado = v[3] if v[3] else ''
        if estado == 'Pagado':
            estado_class = 'badge bg-success bg-opacity-10 text-success border border-success px-3 rounded-pill'
        elif estado == 'Devuelto':
            estado_class = 'badge bg-danger bg-opacity-10 text-danger border border-danger px-3 rounded-pill'
        else:
            estado_class = 'badge bg-secondary'
        vendedor = v[4] if v[4] else ''
        cliente = v[5] if v[5] else 'Público General'
        ventas.append({
            'id': v[0],
            'hora': v[1].strftime('%I:%M %p') if v[1] else '',
            'total': v[2],
            'estado': estado if estado else '—',
            'estado_class': estado_class,
            'vendedor': vendedor,
            'vendedor_inicial': vendedor[0].upper() if vendedor else '?',
            'cliente': cliente,
            'descuento': v[6]
        })
    
    # 2. NUEVO: RESUMEN DE PRODUCTOS VENDIDOS HOY (Agrupado)
    sql_productos = """
        SELECT Pr.Nombre, SUM(DP.Cantidad) as CantidadTotal, SUM(DP.Cantidad * DP.PrecioUnitario) as Subtotal
        FROM DetallePedido DP
        INNER JOIN Pedido Ped ON DP.ID_Pedido = Ped.ID_Pedido
        INNER JOIN Perfume Pr ON DP.ID_Perfume = Pr.ID_Perfume
        WHERE CAST(Ped.FechaPedido AS DATE) = CAST(GETDATE() AS DATE)
        GROUP BY Pr.Nombre
        ORDER BY CantidadTotal DESC
    """
    cursor.execute(sql_productos)
    resumen_productos = cursor.fetchall()
    
    conn.close()
    return render_template('reporte_diario.html', ventas=ventas, total_dia=total, resumen=resumen_productos)

# === NUEVA RUTA PARA IMPRIMIR TICKET ===
@app.route('/imprimir_ticket/<int:id_pedido>')
def imprimir_ticket(id_pedido):
    if 'id_usuario' not in session: return redirect(url_for('login'))
    
    conn = get_connection()
    c = conn.cursor()
    
    # MODIFICADO: Agregamos P.Descuento al final (índice 5)
    # Índices: 0=ID, 1=Fecha, 2=Total, 3=Vendedor, 4=Cliente, 5=Descuento
    c.execute("""
        SELECT P.ID_Pedido, P.FechaPedido, P.Total, U.Nombre, C.Nombre, P.Descuento
        FROM Pedido P 
        INNER JOIN Usuario U ON P.ID_Usuario = U.ID_Usuario 
        LEFT JOIN Cliente C ON P.ID_Cliente = C.ID_Cliente
        WHERE P.ID_Pedido = ?
    """, (id_pedido,))
    pedido = c.fetchone()
    
    c.execute("""
        SELECT Pr.Nombre, DP.Cantidad, DP.PrecioUnitario, (DP.Cantidad * DP.PrecioUnitario) as Subtotal
        FROM DetallePedido DP
        INNER JOIN Perfume Pr ON DP.ID_Perfume = Pr.ID_Perfume
        WHERE DP.ID_Pedido = ?
    """, (id_pedido,))
    detalles = c.fetchall()
    
    conn.close()
    return render_template('ticket_impresion.html', pedido=pedido, detalles=detalles)

# --- APIs (JSON) ---
@app.route("/api/buscar_perfume")
def api_buscar_perfume():
    q = request.args.get("q", "").strip()

    if q == "":
        return jsonify([])

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT ID_Perfume, Nombre, Precio, Stock, Imagen
        FROM Perfume
        WHERE Nombre LIKE ? AND (Estado = 1 OR Estado IS NULL)
        ORDER BY Nombre
    """, (f"%{q}%",))

    rows = cursor.fetchall()

    perfumes = []
    for r in rows:
        perfumes.append({
            "id": r[0],
            "nombre": r[1],
            "precio": float(r[2]) if r[2] is not None else 0,
            "stock": int(r[3]) if r[3] is not None else 0,
            "imagen": resolve_perfume_image(r[1], r[4])
        })

    conn.close()
    return jsonify(perfumes)



@app.route('/api/procesar_venta', methods=['POST'])
def api_venta():
    if 'id_usuario' not in session: return jsonify({'error':'No auth'}), 401
    
    data = request.json
    items = data.get('items', [])
    id_cliente = data.get('id_cliente', 1) 
    descuento = data.get('descuento', 0)

    if not isinstance(items, list) or not items:
        return jsonify({'error':'El carrito está vacío'}), 400
    
    conn = get_connection()
    if not conn:
        return jsonify({'error':'Error de conexión a BD'}), 500

    try:
        c = conn.cursor()
        uid = session.get('id_usuario')
        total_venta = data.get('total', 0)

        # 1. Validar items y preparar datos
        ids = []
        cantidades = {}
        for i in items:
            pid = int(i.get('id', 0))
            cant = int(i.get('cantidad', 0))
            if pid <= 0 or cant <= 0:
                return jsonify({'error':'Cantidad inválida'}), 400
            ids.append(pid)
            cantidades[pid] = cantidades.get(pid, 0) + cant

        # 2. Cargar perfumes y validar stock actual
        placeholders = ",".join(["?"] * len(ids))
        c.execute(f"SELECT ID_Perfume, Nombre, Precio, Stock FROM Perfume WHERE ID_Perfume IN ({placeholders})", ids)
        rows = c.fetchall()
        perf_map = {r[0]: r for r in rows}

        subtotal = Decimal('0')
        for pid, cant in cantidades.items():
            _, nombre, precio_db, stock_db = perf_map[pid]
            if stock_db is None or int(stock_db) < cant:
                return jsonify({'error': f"Stock insuficiente para {nombre}. Disponible: {stock_db}"}), 400
            subtotal += (Decimal(str(precio_db)) * Decimal(cant))

        # 3. Calcular total final
        descuento_dec = Decimal(str(descuento))
        total_calc = (subtotal - descuento_dec).quantize(Decimal('0.01'))

        # 4. INSERTAR PEDIDO
        c.execute("""
            INSERT INTO Pedido (ID_Usuario, ID_Cliente, Total, Descuento, Estado) 
            VALUES (?, ?, ?, ?, 'Pagado')
        """, (uid, id_cliente, float(total_calc), float(descuento_dec)))
        
        c.execute("SELECT @@IDENTITY")
        id_pedido_generado = c.fetchone()[0]
        
        # 5. ACTUALIZAR STOCK Y DETALLES (EL PUNTO CLAVE)
        for pid_item, cant_vendida in cantidades.items():
            _, nombre_p, precio_p, _ = perf_map[pid_item]

            # Insertar el producto en el detalle de la venta
            c.execute("""
                INSERT INTO DetallePedido (ID_Pedido, ID_Perfume, Cantidad, PrecioUnitario) 
                VALUES (?, ?, ?, ?)
            """, (id_pedido_generado, pid_item, cant_vendida, float(precio_p)))

            # DESCUENTO REAL DEL STOCK EN LA TABLA PERFUME
            # Esta es la línea que actualiza el inventario
            c.execute("""
                UPDATE Perfume 
                SET Stock = Stock - ? 
                WHERE ID_Perfume = ?
            """, (int(cant_vendida), int(pid_item)))
        
        # 6. Actualizar fidelidad del cliente si no es "Público General"
        if int(id_cliente) != 1:
            c.execute("UPDATE Cliente SET TotalComprado = TotalComprado + ? WHERE ID_Cliente = ?", (float(total_calc), id_cliente))
        
        # FINALIZAR TRANSACCIÓN
        conn.commit()
        return jsonify({'status':'ok', 'id_pedido': id_pedido_generado})

    except Exception as e:
        if conn: conn.rollback()
        print(f"Error en venta: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        if conn: conn.close()

@app.route('/api/detalle_venta/<int:id>')
def api_detalle(id):
    if 'id_usuario' not in session: return jsonify({'error':'No auth'}), 401
    conn = get_connection() 
    c = conn.cursor()
    
    # MODIFICADO: Primero obtenemos información extra del pedido (Cliente)
    c.execute("""
        SELECT C.Nombre 
        FROM Pedido P 
        LEFT JOIN Cliente C ON P.ID_Cliente = C.ID_Cliente 
        WHERE P.ID_Pedido = ?
    """, (id,))
    cliente_info = c.fetchone()
    nombre_cliente = cliente_info[0] if cliente_info else "Público General"

    # Luego los productos
    c.execute("""
        SELECT P.Nombre, DP.Cantidad, DP.PrecioUnitario, (DP.Cantidad*DP.PrecioUnitario) 
        FROM DetallePedido DP 
        INNER JOIN Perfume P ON DP.ID_Perfume=P.ID_Perfume 
        WHERE DP.ID_Pedido=?
    """, (id,))
    
    productos = [{'producto':d[0], 'cantidad':int(d[1]), 'precio':float(d[2]), 'subtotal':float(d[3])} for d in c.fetchall()]
    
    conn.close()
    
    # Devolvemos un objeto que tiene AMBOS datos
    return jsonify({
        'cliente': nombre_cliente,
        'productos': productos
    })

# ==========================================
#  4. GESTIÓN DE EMPLEADOS (USUARIOS)
# ==========================================

@app.route('/admin/usuarios')
def lista_usuarios():
    # ... (esta función se queda igual que antes) ...
    if 'id_usuario' not in session or session['rol'] != 'Administrador': 
        return redirect(url_for('login'))
    
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT U.ID_Usuario, U.Nombre, U.Email, R.NombreRol FROM Usuario U INNER JOIN Rol R ON U.ID_Rol = R.ID_Rol")
    usuarios = c.fetchall()
    conn.close()
    return render_template('lista_usuarios.html', usuarios=usuarios)

# FUNCIÓN COMBINADA: CREAR Y EDITAR USUARIO
@app.route('/admin/usuario/nuevo', methods=['GET', 'POST'])
@app.route('/admin/usuario/editar/<int:id>', methods=['GET', 'POST'])
def formulario_usuario(id=None):
    if 'id_usuario' not in session or session['rol'] != 'Administrador': 
        return redirect(url_for('login'))

    conn = get_connection()
    c = conn.cursor()
    
    # Si hay ID, buscamos al usuario para editar
    usuario_editar = None
    if id:
        c.execute("SELECT * FROM Usuario WHERE ID_Usuario = ?", (id,))
        usuario_editar = c.fetchone()

    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        password = request.form['password']
        rol_id = request.form['rol']

        try:
            if id:
                # --- MODO EDICIÓN ---
                if password: 
                    # Si escribió contraseña nueva, la actualizamos
                    c.execute("UPDATE Usuario SET Nombre=?, Email=?, Contrasena=?, ID_Rol=? WHERE ID_Usuario=?", 
                             (nombre, email, password, rol_id, id))
                else:
                    # Si dejó la contraseña vacía, mantenemos la anterior
                    c.execute("UPDATE Usuario SET Nombre=?, Email=?, ID_Rol=? WHERE ID_Usuario=?", 
                             (nombre, email, rol_id, id))
                flash("Datos del empleado actualizados.", "success")
            else:
                # --- MODO CREACIÓN ---
                if not password:
                    flash("La contraseña es obligatoria para nuevos usuarios.", "error")
                    return render_template('formulario_usuario.html', usuario=None)
                    
                c.execute("INSERT INTO Usuario (Nombre, Email, Contrasena, ID_Rol) VALUES (?, ?, ?, ?)", 
                         (nombre, email, password, rol_id))
                flash("Empleado registrado correctamente.", "success")
            
            conn.commit()
            return redirect(url_for('lista_usuarios'))
            
        except Exception as e:
            conn.rollback()
            flash(f"Error: {e}", "error")
        finally:
            conn.close()

    conn.close()
    return render_template('formulario_usuario.html', usuario=usuario_editar)

@app.route('/admin/usuario/nuevo', methods=['GET', 'POST'])
def nuevo_usuario():
    if 'id_usuario' not in session or session['rol'] != 'Administrador': 
        return redirect(url_for('login'))

    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        password = request.form['password'] # OJO: Idealmente usar hash aquí
        rol_id = request.form['rol'] # 1=Admin, 2=Vendedor

        conn = get_connection()
        c = conn.cursor()
        try:
            c.execute("INSERT INTO Usuario (Nombre, Email, Contrasena, ID_Rol) VALUES (?, ?, ?, ?)", (nombre, email, password, rol_id))
            conn.commit()
            flash("Empleado registrado correctamente", "success")
        except Exception as e:
            flash(f"Error al registrar: {e}", "error")
        finally:
            conn.close()
        return redirect(url_for('lista_usuarios'))

    return render_template('formulario_usuario.html')

@app.route('/admin/usuario/eliminar/<int:id>')
def eliminar_usuario(id):
    if 'id_usuario' not in session or session['rol'] != 'Administrador': return redirect(url_for('login'))
    
    # Evitar que el admin se elimine a sí mismo
    if id == session['id_usuario']:
        flash("No puedes eliminar tu propia cuenta mientras estás conectado.", "error")
        return redirect(url_for('lista_usuarios'))

    conn = get_connection()
    try:
        conn.cursor().execute("DELETE FROM Usuario WHERE ID_Usuario = ?", (id,))
        conn.commit()
        flash("Usuario eliminado", "success")
    except:
        flash("No se puede eliminar este usuario (tiene ventas asociadas)", "error")
    finally:
        conn.close()
    return redirect(url_for('lista_usuarios'))


# ==========================================
#  5. GESTIÓN DE PROVEEDORES
# ==========================================

@app.route('/admin/proveedores')
def lista_proveedores():
    if 'id_usuario' not in session or session['rol'] != 'Administrador': 
        return redirect(url_for('login'))
    
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM Proveedor")
    proveedores = c.fetchall()
    conn.close()
    return render_template('lista_proveedores.html', proveedores=proveedores)

@app.route('/admin/proveedor/guardar', methods=['POST'])
def guardar_proveedor():
    if 'id_usuario' not in session or session['rol'] != 'Administrador': 
        return redirect(url_for('login'))
    
    # Recibimos el ID (si está vacío, es nuevo; si tiene valor, es edición)
    id_prov = request.form.get('id_proveedor')
    nombre = request.form['nombre']
    contacto = request.form['contacto']
    telefono = request.form['telefono']

    conn = get_connection()
    c = conn.cursor()
    
    if id_prov:
        # ACTUALIZAR EXISTENTE
        c.execute("UPDATE Proveedor SET NombreEmpresa=?, Contacto=?, Telefono=? WHERE ID_Proveedor=?", 
                 (nombre, contacto, telefono, id_prov))
        flash("Proveedor actualizado correctamente", "success")
    else:
        # CREAR NUEVO
        c.execute("INSERT INTO Proveedor (NombreEmpresa, Contacto, Telefono) VALUES (?, ?, ?)", 
                 (nombre, contacto, telefono))
        flash("Proveedor agregado exitosamente", "success")
        
    conn.commit()
    conn.close()
    
    return redirect(url_for('lista_proveedores'))

@app.route('/admin/proveedor/eliminar/<int:id>')
def eliminar_proveedor(id):
    if 'id_usuario' not in session or session['rol'] != 'Administrador': return redirect(url_for('login'))
    
    conn = get_connection()
    try:
        conn.cursor().execute("DELETE FROM Proveedor WHERE ID_Proveedor = ?", (id,))
        conn.commit()
        flash("Proveedor eliminado", "success")
    except:
        # Si el proveedor tiene productos asociados, SQL no dejará borrarlo
        flash("No se puede eliminar: Este proveedor tiene productos asociados.", "error")
    finally:
        conn.close()
    return redirect(url_for('lista_proveedores'))

@app.route('/api/buscar_cliente')
def api_buscar_cliente():
    if 'id_usuario' not in session: return jsonify({'error':'No auth'}), 401
    q = request.args.get('q', '')
    
    conn = get_connection()
    c = conn.cursor()
    # Buscamos por nombre o teléfono
    c.execute("SELECT ID_Cliente, Nombre, Telefono, TotalComprado FROM Cliente WHERE Nombre LIKE ? OR Telefono LIKE ?", (f'%{q}%', f'%{q}%'))
    data = [{'id': row[0], 'nombre': row[1], 'telefono': row[2], 'compras': float(row[3])} for row in c.fetchall()]
    conn.close()
    return jsonify(data)

@app.route('/api/crear_cliente', methods=['POST'])
def api_crear_cliente():
    if 'id_usuario' not in session: return jsonify({'error':'No auth'}), 401
    data = request.json
    nombre = (data.get('nombre') or '').strip()
    telefono = (data.get('telefono') or '').strip()
    email = (data.get('email') or '').strip()

    if not nombre or not re.fullmatch(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ\s]+", nombre):
        return jsonify({'error':'Nombre inválido. Solo letras y espacios.'}), 400
    if telefono and not re.fullmatch(r"\d{8}", telefono):
        return jsonify({'error':'Teléfono inválido. Debe tener 8 dígitos.'}), 400
    if email and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        return jsonify({'error':'Correo inválido.'}), 400

    nombre = nombre.upper()
    
    conn = get_connection()
    try:
        c = conn.cursor()
        c.execute("INSERT INTO Cliente (Nombre, Telefono, Email) VALUES (?, ?, ?)", 
                 (nombre, telefono, email))
        c.execute("SELECT @@IDENTITY")
        new_id = c.fetchone()[0]
        conn.commit()
        return jsonify({'status': 'ok', 'id': new_id, 'nombre': nombre})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()
        
# 6.3 REABASTECER (ACTUALIZADO PARA CARGA MASIVA Y SINGULAR)
# 6.3 REABASTECER (ACTUALIZADO: ENVÍO GLOBAL INTELIGENTE)
@app.route('/producto/reabastecer', methods=['POST'])
def reabastecer_producto():
    if 'id_usuario' not in session: return redirect(url_for('login'))
    if session['rol'] != 'Administrador': return redirect(url_for('ventas'))
    
    origen = request.form.get('origen', 'dashboard')
    conn = get_connection()
    
    try:
        cursor = conn.cursor()
        uid = session['id_usuario']

        productos_ids = request.form.getlist('id_producto[]')
        
        if productos_ids:
            # --- MODO MASIVO (TABLA) ---
            cantidades = request.form.getlist('cantidad[]')
            costos = request.form.getlist('costo[]')
            
            # RECIBIMOS EL ENVÍO TOTAL DEL PEDIDO
            envio_global_input = request.form.get('envio_global', '')
            envio_global = float(envio_global_input) if envio_global_input else 0.0
            
            # 1. Calculamos el total de unidades para saber cómo dividir el envío
            total_unidades_pedido = sum(int(c) for c in cantidades if c and int(c) > 0)
            
            items_procesados = 0
            
            for i in range(len(productos_ids)):
                pid = productos_ids[i]
                cant = int(cantidades[i]) if cantidades[i] else 0
                
                if cant <= 0: continue
                
                costo_u = float(costos[i]) if costos[i] else 0.0
                
                # LÓGICA DE PRORRATEO:
                # Si pagaste $100 de envío por 10 productos, a cada producto le tocan $10.
                # Fórmula: (Cantidad de este item / Total del pedido) * Envío Global
                if total_unidades_pedido > 0:
                    envio_asignado = (cant / total_unidades_pedido) * envio_global
                else:
                    envio_asignado = 0
                
                cursor.execute("""
                    INSERT INTO EntradaInventario (ID_Perfume, Cantidad, CostoUnitario, CostoEnvio, ID_Usuario)
                    VALUES (?, ?, ?, ?, ?)
                """, (pid, cant, costo_u, envio_asignado, uid))
                
                cursor.execute("UPDATE Perfume SET Stock = Stock + ? WHERE ID_Perfume = ?", (cant, pid))
                items_procesados += 1
            
            flash(f"✅ Pedido registrado. El envío de ${envio_global} se distribuyó entre {items_procesados} productos.", "success")

        else:
            # --- MODO INDIVIDUAL (DASHBOARD) ---
            # (Se mantiene igual, para entradas rápidas de 1 solo producto)
            id_prod = request.form.get('id_producto')
            cantidad = int(request.form.get('cantidad', 0))
            costo = float(request.form.get('costo', 0) or 0)
            envio = float(request.form.get('envio', 0) or 0) # Aquí sí es individual
            
            if cantidad > 0:
                cursor.execute("""
                    INSERT INTO EntradaInventario (ID_Perfume, Cantidad, CostoUnitario, CostoEnvio, ID_Usuario)
                    VALUES (?, ?, ?, ?, ?)
                """, (id_prod, cantidad, costo, envio, uid))
                cursor.execute("UPDATE Perfume SET Stock = Stock + ? WHERE ID_Perfume = ?", (cantidad, id_prod))
                
                cursor.execute("SELECT Nombre FROM Perfume WHERE ID_Perfume = ?", (id_prod,))
                nom = cursor.fetchone()[0]
                flash(f"✅ Entrada: {cantidad} u. de '{nom}'", "success")

        conn.commit()
        
    except Exception as e:
        conn.rollback()
        flash(f"Error al procesar: {e}", "error")
    finally:
        conn.close()
    
    if origen == 'entrada_stock': return redirect(url_for('entrada_stock'))
    else: return redirect(url_for('dashboard'))

# 6.1 API HISTORIAL PROVEEDOR (NUEVO)
@app.route('/api/historial_proveedor/<int:id_prov>')
def api_historial_proveedor(id_prov):
    if 'id_usuario' not in session: return jsonify({'error':'No auth'}), 401
    
    conn = get_connection()
    c = conn.cursor()
    
    # Buscamos el nombre del proveedor para filtrar por Marca en Perfume
    c.execute("SELECT NombreEmpresa FROM Proveedor WHERE ID_Proveedor = ?", (id_prov,))
    prov_row = c.fetchone()
    prov_nombre = prov_row[0] if prov_row else None

    if not prov_nombre:
        conn.close()
        return jsonify([])

    sql = """
        SELECT E.FechaEntrada, P.Nombre, E.Cantidad, E.CostoUnitario, E.CostoEnvio
        FROM EntradaInventario E
        INNER JOIN Perfume P ON E.ID_Perfume = P.ID_Perfume
        WHERE P.Marca = ?
        ORDER BY E.FechaEntrada DESC
    """
    c.execute(sql, (prov_nombre,))
    
    # Formateamos los datos para JSON
    data = []
    for row in c.fetchall():
        cantidad = row[2]
        costo_u = float(row[3]) if row[3] else 0
        envio = float(row[4]) if row[4] else 0
        total_movimiento = (cantidad * costo_u) + envio
        
        data.append({
            'fecha': row[0].strftime('%d/%m/%Y'),
            'producto': row[1],
            'cantidad': cantidad,
            'costo_u': costo_u,
            'envio': envio,
            'total': total_movimiento
        })
        
    conn.close()
    return jsonify(data)

@app.route('/api/productos_por_proveedor/<int:id_prov>')
def api_productos_por_proveedor(id_prov):
    if 'id_usuario' not in session: return jsonify([])
    
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT NombreEmpresa FROM Proveedor WHERE ID_Proveedor = ?", (id_prov,))
    prov_row = c.fetchone()
    prov_nombre = prov_row[0] if prov_row else None
    if not prov_nombre:
        conn.close()
        return jsonify([])

    c.execute("SELECT ID_Perfume, Nombre FROM Perfume WHERE Marca = ? AND (Estado = 1 OR Estado IS NULL)", (prov_nombre,))
    productos = [{'id': row[0], 'nombre': row[1]} for row in c.fetchall()]
    conn.close()
    return jsonify(productos)

@app.route('/admin/entrada_stock')
def entrada_stock():
    if 'id_usuario' not in session or session['rol'] != 'Administrador': 
        return redirect(url_for('login'))
    
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT ID_Proveedor, NombreEmpresa FROM Proveedor")
    proveedores = c.fetchall()
    
    # NUEVO: Enviamos también las categorías para el modal
    c.execute("SELECT ID_Categoria, Nombre FROM Categoria")
    categorias = c.fetchall()
    
    conn.close()
    
    return render_template('entrada_stock.html', proveedores=proveedores, categorias=categorias)

# ==========================================
#  7. REPORTES AVANZADOS (POR FECHAS) 📅
# ==========================================

@app.route('/reportes/fechas', methods=['GET', 'POST'])
def reporte_fechas():
    if 'id_usuario' not in session: return redirect(url_for('login'))
    
    ventas = []
    total_periodo = 0
    fecha_inicio = ""
    fecha_fin = ""
    
    # Variables para gráficos (Listas vacías por defecto para que no falle el GET)
    cat_labels = []
    cat_values = []
    top_labels = []
    top_values = []
    time_labels = []
    time_values = []
    
    if request.method == 'POST':
        fecha_inicio = request.form['fecha_inicio']
        fecha_fin = request.form['fecha_fin']
        
        conn = get_connection()
        c = conn.cursor()
        
        # A. TABLA DE VENTAS
        sql = """
            SELECT P.ID_Pedido, P.FechaPedido, U.Nombre, C.Nombre, P.Total, P.Descuento
            FROM Pedido P
            INNER JOIN Usuario U ON P.ID_Usuario = U.ID_Usuario
            LEFT JOIN Cliente C ON P.ID_Cliente = C.ID_Cliente
            WHERE CAST(P.FechaPedido AS DATE) BETWEEN ? AND ?
            ORDER BY P.FechaPedido DESC
        """
        c.execute(sql, (fecha_inicio, fecha_fin))
        ventas = c.fetchall()
        total_periodo = sum(v[4] for v in ventas)

        # B. DATOS PARA GRÁFICOS (FILTRADOS POR LA MISMA FECHA)
        
        # 1. Géneros (basado en Perfume.Genero)
        c.execute("""
            SELECT P.Genero, ISNULL(SUM(DP.Cantidad), 0)
            FROM Perfume P
            LEFT JOIN DetallePedido DP ON P.ID_Perfume = DP.ID_Perfume
            LEFT JOIN Pedido Ped ON DP.ID_Pedido = Ped.ID_Pedido
            WHERE CAST(Ped.FechaPedido AS DATE) BETWEEN ? AND ?
            GROUP BY P.Genero
        """, (fecha_inicio, fecha_fin))
        data_cat = c.fetchall()
        cat_labels = [row[0] for row in data_cat]
        cat_values = [row[1] for row in data_cat]

        # 2. Top 5 Productos
        c.execute("""
            SELECT TOP 5 P.Nombre, SUM(DP.Cantidad) as Total
            FROM DetallePedido DP
            INNER JOIN Perfume P ON DP.ID_Perfume = P.ID_Perfume
            INNER JOIN Pedido Ped ON DP.ID_Pedido = Ped.ID_Pedido
            WHERE CAST(Ped.FechaPedido AS DATE) BETWEEN ? AND ?
            GROUP BY P.Nombre
            ORDER BY Total DESC
        """, (fecha_inicio, fecha_fin))
        data_top = c.fetchall()
        top_labels = [row[0] for row in data_top]
        top_values = [row[1] for row in data_top]

        # 3. Línea de Tiempo
        c.execute("""
            SELECT FORMAT(FechaPedido, 'dd/MM'), SUM(Total)
            FROM Pedido
            WHERE CAST(FechaPedido AS DATE) BETWEEN ? AND ?
            GROUP BY FORMAT(FechaPedido, 'dd/MM'), CAST(FechaPedido AS DATE)
            ORDER BY CAST(FechaPedido AS DATE)
        """, (fecha_inicio, fecha_fin))
        data_time = c.fetchall()
        time_labels = [row[0] for row in data_time]
        time_values = [float(row[1]) for row in data_time]

        conn.close()

    return render_template('reporte_fechas.html', 
                           ventas=ventas, total=total_periodo, 
                           f_ini=fecha_inicio, f_fin=fecha_fin,
                           # Pasamos los datos JSON para Chart.js
                           cat_labels=json.dumps(cat_labels), cat_values=json.dumps(cat_values),
                           top_labels=json.dumps(top_labels), top_values=json.dumps(top_values),
                           time_labels=json.dumps(time_labels), time_values=json.dumps(time_values))


# ==========================================
#  8. CONTROL DE CAJA (APERTURA Y CIERRE) 💰
# ==========================================

@app.route('/caja/panel')
def panel_caja():
    if 'id_usuario' not in session: return redirect(url_for('login'))
    
    uid = session['id_usuario']
    conn = get_connection()
    c = conn.cursor()
    
    # 1. Buscar caja abierta
    c.execute("SELECT TOP 1 * FROM Caja WHERE ID_Usuario = ? AND Estado = 'Abierta' ORDER BY ID_Caja DESC", (uid,))
    caja_abierta = c.fetchone()
    
    # INICIALIZAMOS TODAS LAS VARIABLES EN 0 POR SI LA CAJA ESTÁ CERRADA
    ventas_sesion = 0
    gastos_sesion = 0
    devoluciones_sesion = 0
    resumen_productos = []
    saldo_esperado = 0
    
    if caja_abierta:
        fecha_apertura = caja_abierta[2]
        
        # A. Ventas
        c.execute("SELECT ISNULL(SUM(Total), 0) FROM Pedido WHERE ID_Usuario = ? AND FechaPedido >= ? AND Estado = 'Pagado'", (uid, fecha_apertura))
        ventas_sesion = c.fetchone()[0]
        
        # B. Gastos
        c.execute("SELECT ISNULL(SUM(Monto), 0) FROM Gasto WHERE ID_Usuario = ? AND Fecha >= ?", (uid, fecha_apertura))
        gastos_sesion = c.fetchone()[0]
        
        # C. Devoluciones
        c.execute("""
            SELECT ISNULL(SUM(Total), 0) 
            FROM Pedido 
            WHERE ID_Usuario = ? AND Estado = 'Devuelto' 
            AND CAST(FechaPedido AS DATE) = CAST(GETDATE() AS DATE)
        """, (uid,))
        devoluciones_sesion = c.fetchone()[0]

        # D. Productos vendidos
        c.execute("""
            SELECT Pr.Nombre, SUM(DP.Cantidad) as CantidadTotal, SUM(DP.Cantidad * DP.PrecioUnitario) as Subtotal
            FROM DetallePedido DP
            INNER JOIN Pedido Ped ON DP.ID_Pedido = Ped.ID_Pedido
            INNER JOIN Perfume Pr ON DP.ID_Perfume = Pr.ID_Perfume
            WHERE Ped.ID_Usuario = ? AND Ped.FechaPedido >= ? AND Ped.Estado = 'Pagado'
            GROUP BY Pr.Nombre
            ORDER BY CantidadTotal DESC
        """, (uid, fecha_apertura))
        resumen_productos = c.fetchall()
        
        # Cálculo del Saldo
        saldo_esperado = (caja_abierta[3] + ventas_sesion) - (gastos_sesion + devoluciones_sesion)
    
    conn.close()
    
    # AQUÍ ESTABA EL ERROR: FALTABA ENVIAR ESTAS VARIABLES
    return render_template('control_caja.html', 
                           caja=caja_abierta, 
                           ventas_hoy=ventas_sesion, 
                           gastos=gastos_sesion,          
                           devoluciones=devoluciones_sesion, 
                           saldo_esperado=saldo_esperado, 
                           resumen=resumen_productos)

@app.route('/caja/abrir', methods=['POST'])
def abrir_caja():
    if 'id_usuario' not in session: return redirect(url_for('login'))
    
    monto_inicial = request.form['monto_inicial']
    uid = session['id_usuario']
    
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO Caja (ID_Usuario, MontoInicial, Estado) VALUES (?, ?, 'Abierta')", (uid, monto_inicial))
    conn.commit()
    conn.close()
    
    flash("✅ Caja Abierta Correctamente", "success")
    return redirect(url_for('panel_caja'))

@app.route('/caja/cerrar', methods=['POST'])
def cerrar_caja():
    if 'id_usuario' not in session: return redirect(url_for('login'))
    
    id_caja = request.form['id_caja']
    monto_sistema = float(request.form['monto_sistema']) # Inicial + Ventas
    monto_real = float(request.form['monto_real'])       # Lo que contó el cajero
    
    diferencia = monto_real - monto_sistema
    
    conn = get_connection()
    c = conn.cursor()
    
    c.execute("""
        UPDATE Caja 
        SET FechaCierre = GETDATE(), 
            MontoFinalSistema = ?, 
            MontoFinalReal = ?, 
            Diferencia = ?, 
            Estado = 'Cerrada'
        WHERE ID_Caja = ?
    """, (monto_sistema, monto_real, diferencia, id_caja))
    
    conn.commit()
    conn.close()
    
    if diferencia == 0:
        flash("✅ Caja cuadrada perfectamente.", "success")
    elif diferencia < 0:
        flash(f"⚠️ Atención: Faltan ${abs(diferencia):.2f} en caja.", "error")
    else:
        flash(f"ℹ️ Sobra dinero: ${diferencia:.2f}", "success")
        
    return redirect(url_for('panel_caja'))

# ... (código existente) ...

# 4.1 API HISTORIAL DE EMPLEADO (NUEVO: VENTAS Y ASISTENCIA)
@app.route('/api/historial_empleado/<int:id_usuario>')
def api_historial_empleado(id_usuario):
    if 'id_usuario' not in session or session['rol'] != 'Administrador': 
        return jsonify({'error':'No auth'}), 401
    
    conn = get_connection()
    c = conn.cursor()
    
    # 1. Total Vendido Histórico (Cuánto dinero ha ingresado a la empresa)
    c.execute("SELECT ISNULL(SUM(Total), 0), COUNT(*) FROM Pedido WHERE ID_Usuario = ?", (id_usuario,))
    res_ventas = c.fetchone()
    total_vendido = res_ventas[0]
    num_ventas = res_ventas[1]
    
    # 2. Historial de Turnos (Basado en Apertura/Cierre de Caja)
    # Aquí vemos asistencia y honestidad en el manejo de dinero
    c.execute("""
        SELECT FechaApertura, FechaCierre, Diferencia, Estado 
        FROM Caja 
        WHERE ID_Usuario = ? 
        ORDER BY FechaApertura DESC
    """, (id_usuario,))
    
    turnos = []
    for row in c.fetchall():
        apertura = row[0]
        cierre = row[1]
        diferencia = float(row[2]) if row[2] is not None else 0
        estado = row[3]
        
        # Formatear fechas y horas
        fecha_str = apertura.strftime('%d/%m/%Y')
        hora_entrada = apertura.strftime('%I:%M %p')
        hora_salida = cierre.strftime('%I:%M %p') if cierre else "🔴 En turno"
        
        # Analizar si entregó bien la caja
        status_entrega = "Pendiente"
        clase_css = "bg-secondary"
        
        if estado == 'Cerrada':
            if diferencia == 0: 
                status_entrega = "✅ Caja Cuadrada"
                clase_css = "bg-success"
            elif diferencia < 0: 
                status_entrega = f"⚠️ Faltó ${abs(diferencia):.2f}"
                clase_css = "bg-danger"
            else: 
                status_entrega = f"ℹ️ Sobró ${diferencia:.2f}"
                clase_css = "bg-warning text-dark"
        else:
            status_entrega = "⏳ Trabajando..."
            clase_css = "bg-info text-dark"
            
        turnos.append({
            'fecha': fecha_str,
            'entrada': hora_entrada,
            'salida': hora_salida,
            'status': status_entrega,
            'css': clase_css
        })
        
    conn.close()
    
    return jsonify({
        'total_vendido': total_vendido,
        'num_ventas': num_ventas,
        'turnos': turnos
    })
    
# ==========================================
#  9. GESTIÓN DE GASTOS 📉 (NUEVO)
# ==========================================

@app.route('/gastos', methods=['GET', 'POST'])
def gastos():
    if 'id_usuario' not in session: return redirect(url_for('login'))
    
    conn = get_connection()
    c = conn.cursor()
    
    if request.method == 'POST':
        descripcion = request.form['descripcion']
        monto = float(request.form['monto'])
        uid = session['id_usuario']
        
        c.execute("INSERT INTO Gasto (Descripcion, Monto, ID_Usuario) VALUES (?, ?, ?)", (descripcion, monto, uid))
        conn.commit()
        flash("Gasto registrado correctamente.", "success")
        return redirect(url_for('gastos'))
    
    # Listar gastos del día
    c.execute("SELECT * FROM Gasto WHERE CAST(Fecha AS DATE) = CAST(GETDATE() AS DATE) ORDER BY Fecha DESC")
    gastos_hoy = c.fetchall()
    
    conn.close()
    return render_template('gastos.html', gastos=gastos_hoy)

# ==========================================
#  10. DEVOLUCIONES ↩️ (NUEVO)
# ==========================================

@app.route('/venta/devolver/<int:id_pedido>')
def devolver_venta(id_pedido):
    if 'id_usuario' not in session: return redirect(url_for('login'))
    if session['rol'] != 'Administrador': 
        flash("Solo administradores pueden autorizar devoluciones.", "error")
        return redirect(url_for('reporte_diario'))
    
    conn = get_connection()
    try:
        c = conn.cursor()
        
        # 1. Verificar estado actual
        c.execute("SELECT Estado FROM Pedido WHERE ID_Pedido = ?", (id_pedido,))
        estado = c.fetchone()[0]
        
        if estado == 'Devuelto':
            flash("Este pedido ya fue devuelto anteriormente.", "error")
        else:
            # 2. Marcar pedido como Devuelto
            c.execute("UPDATE Pedido SET Estado = 'Devuelto' WHERE ID_Pedido = ?", (id_pedido,))
            
            # 3. Devolver productos al Stock (Revertir inventario)
            c.execute("SELECT ID_Perfume, Cantidad FROM DetallePedido WHERE ID_Pedido = ?", (id_pedido,))
            items = c.fetchall()
            
            for item in items:
                pid, cant = item
                c.execute("UPDATE Perfume SET Stock = Stock + ? WHERE ID_Perfume = ?", (cant, pid))
            
            conn.commit()
            flash(f"✅ Ticket #{id_pedido} devuelto. El stock ha sido restaurado y el dinero descontado.", "success")
            
    except Exception as e:
        conn.rollback()
        flash(f"Error al procesar devolución: {e}", "error")
    finally:
        conn.close()
        
    return redirect(url_for('reporte_diario'))

# 6.5 API CREAR O BUSCAR PRODUCTO RÁPIDO (MEJORADA)
@app.route('/api/crear_producto_rapido', methods=['POST'])
def api_crear_producto_rapido():
    if 'id_usuario' not in session: return jsonify({'error': 'No autorizado'}), 401
    
    data = request.json
    nombre = data.get('nombre').strip() # Quitamos espacios extra
    precio = data.get('precio')
    id_cat = data.get('id_categoria')
    id_prov = data.get('id_proveedor')
    
    if not nombre or not precio:
        return jsonify({'error': 'Faltan datos obligatorios'}), 400
        
    conn = get_connection()
    try:
        c = conn.cursor()
        
        # Resolver Marca (Proveedor) y Género (Categoría) por nombre
        marca = None
        genero = None
        if id_prov:
            c.execute("SELECT NombreEmpresa FROM Proveedor WHERE ID_Proveedor = ?", (id_prov,))
            row = c.fetchone()
            marca = row[0] if row else None
        if id_cat:
            c.execute("SELECT Nombre FROM Categoria WHERE ID_Categoria = ?", (id_cat,))
            row = c.fetchone()
            genero = row[0] if row else None

        # 1. VERIFICAR SI YA EXISTE (Por Nombre y Marca)
        if marca:
            c.execute("""
                SELECT ID_Perfume, Nombre 
                FROM Perfume 
                WHERE Nombre = ? AND Marca = ?
            """, (nombre, marca))
        else:
            c.execute("""
                SELECT ID_Perfume, Nombre 
                FROM Perfume 
                WHERE Nombre = ?
            """, (nombre,))
        
        producto_existente = c.fetchone()
        
        if producto_existente:
            # Si existe, devolvemos el ID del que ya estaba
            return jsonify({
                'status': 'ok', 
                'id': producto_existente[0], 
                'nombre': producto_existente[1],
                'mensaje': 'Producto existente seleccionado.'
            })
        
        # 2. SI NO EXISTE, LO CREAMOS
        c.execute("""
            INSERT INTO Perfume (Nombre, Marca, Descripcion, Precio, Stock, Genero, Mililitros, Imagen, Estado) 
            VALUES (?, ?, '', ?, 0, ?, NULL, '', 1)
        """, (nombre, marca, precio, genero))
        
        c.execute("SELECT @@IDENTITY")
        new_id = c.fetchone()[0]
        conn.commit()
        
        return jsonify({
            'status': 'ok', 
            'id': new_id, 
            'nombre': nombre,
            'mensaje': 'Producto nuevo creado.'
        })
        
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)
