import sqlite3
from datetime import datetime
import os
import shutil

DB_PATH = "pos_420_smoking_vibes.db"

# ======================== CONEXIÓN ========================
def conectar():
    return sqlite3.connect(DB_PATH)

# ======================== FECHAS Y MONEDA ========================
def formatear_fecha():
    return datetime.now().strftime("%d/%m/%Y")

def formatear_hora():
    return datetime.now().strftime("%H:%M:%S")

def formatear_fecha_hora():
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")

def formatear_moneda(valor):
    try:
        valor = float(valor)
    except Exception:
        valor = 0
    return f"${valor:,.0f}".replace(",", ".")

# ======================== PRODUCTOS / INVENTARIO ========================
def obtener_productos():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM productos ORDER BY nombre")
    productos = cursor.fetchall()
    conn.close()
    return productos

def obtener_producto_por_sku(sku):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM productos WHERE sku=?", (sku,))
    producto = cursor.fetchone()
    conn.close()
    return producto

def agregar_producto(sku, nombre, precio, stock, stock_min=5):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT sku FROM productos WHERE sku=?", (sku,))
    if cursor.fetchone():
        conn.close()
        raise Exception(f"El producto con SKU {sku} ya existe")
    cursor.execute("""
        INSERT INTO productos (sku, nombre, precio, stock, fecha_actualizacion, salidas_ventas, stock_actual, stock_minimo)
        VALUES (?, ?, ?, ?, ?, 0, ?, ?)
    """, (sku, nombre, precio, stock, formatear_fecha(), stock, stock_min))
    conn.commit()
    conn.close()

def editar_producto(sku_original, sku, nombre, precio, stock, stock_min=5):
    conn = conectar()
    cursor = conn.cursor()
    if sku != sku_original:
        cursor.execute("SELECT sku FROM productos WHERE sku=?", (sku,))
        if cursor.fetchone():
            conn.close()
            raise Exception(f"El SKU {sku} ya está en uso")
    cursor.execute("""
        UPDATE productos
        SET sku=?, nombre=?, precio=?, stock=?, stock_actual=?, stock_minimo=?, fecha_actualizacion=?
        WHERE sku=?
    """, (sku, nombre, precio, stock, stock, stock_min, formatear_fecha(), sku_original))
    conn.commit()
    conn.close()

def eliminar_producto(sku):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM productos WHERE sku=?", (sku,))
    conn.commit()
    conn.close()

def actualizar_stock(sku, cantidad_vendida):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT stock_actual FROM productos WHERE sku=?", (sku,))
    res = cursor.fetchone()
    if res:
        nuevo_stock = res[0] - cantidad_vendida
        cursor.execute("UPDATE productos SET stock_actual=?, fecha_actualizacion=? WHERE sku=?", (nuevo_stock, formatear_fecha(), sku))
        conn.commit()
    conn.close()

def obtener_productos_stock_bajo():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM productos 
        WHERE stock_actual < stock_minimo 
        ORDER BY nombre
    """)
    productos = cursor.fetchall()
    conn.close()
    return productos

# ======================== CLIENTES ========================
def obtener_clientes():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clientes ORDER BY nombre")
    clientes = cursor.fetchall()
    conn.close()
    return clientes

def obtener_cliente_por_cedula(cedula):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clientes WHERE cedula=?", (cedula,))
    cliente = cursor.fetchone()
    conn.close()
    return cliente

def agregar_cliente(nombre, cedula, celular, correo):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT cedula FROM clientes WHERE cedula=?", (cedula,))
    if cursor.fetchone():
        conn.close()
        raise Exception(f"Ya existe un cliente con cédula {cedula}")
    cursor.execute("""
        INSERT INTO clientes (nombre, cedula, celular, correo, fecha_registro)
        VALUES (?, ?, ?, ?, ?)
    """, (nombre, cedula, celular, correo, formatear_fecha()))
    conn.commit()
    conn.close()

def editar_cliente(cedula_original, nombre, cedula, celular, correo):
    conn = conectar()
    cursor = conn.cursor()
    if cedula != cedula_original:
        cursor.execute("SELECT cedula FROM clientes WHERE cedula=?", (cedula,))
        if cursor.fetchone():
            conn.close()
            raise Exception(f"La cédula {cedula} ya está registrada")
    cursor.execute("""
        UPDATE clientes
        SET nombre=?, cedula=?, celular=?, correo=?
        WHERE cedula=?
    """, (nombre, cedula, celular, correo, cedula_original))
    conn.commit()
    conn.close()

def eliminar_cliente(cedula):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM clientes WHERE cedula=?", (cedula,))
    conn.commit()
    conn.close()

# ======================== EMPLEADOS (Trabajadores) ========================
def agregar_empleado(usuario, nombre, cedula, contrasena):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT usuario FROM empleados WHERE usuario=?", (usuario,))
    if cursor.fetchone():
        conn.close()
        raise Exception(f"El usuario {usuario} ya existe")
    cursor.execute("SELECT cedula FROM empleados WHERE cedula=?", (cedula,))
    if cursor.fetchone():
        conn.close()
        raise Exception(f"La cédula {cedula} ya está registrada")
    cursor.execute("""
        INSERT INTO empleados (usuario, nombre, cedula, contrasena, fecha_ingreso)
        VALUES (?, ?, ?, ?, ?)
    """, (usuario, nombre, cedula, contrasena, formatear_fecha()))
    conn.commit()
    conn.close()

def obtener_empleado_por_usuario(usuario):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM empleados WHERE usuario=?", (usuario,))
    empleado = cursor.fetchone()
    conn.close()
    return empleado

def validar_empleado(usuario, contrasena):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM empleados WHERE usuario=? AND contrasena=?", (usuario, contrasena))
    empleado = cursor.fetchone()
    conn.close()
    return empleado

# ======================== VENTAS ========================
def guardar_venta(
    productos_str,
    total,
    cambio,
    metodo_pago,
    valor_pagado,
    empleado,
    cliente_cedula=None
):
    conn = conectar()
    cursor = conn.cursor()
    id_factura = f"F{datetime.now().strftime('%Y%m%d%H%M%S')}"
    cursor.execute("""
        INSERT INTO ventas (
            id_factura, fecha, hora, empleado, productos, total, 
            cambio, metodo_pago, valor_pagado, cliente_cedula, estado
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'completada')
    """, (
        id_factura,            # id_factura
        formatear_fecha(),     # fecha
        formatear_hora(),      # hora
        empleado,              # empleado
        productos_str,         # productos
        total,                 # total
        cambio,                # cambio
        metodo_pago,           # metodo_pago
        valor_pagado,          # valor_pagado
        cliente_cedula         # cliente_cedula
    ))
    conn.commit()
    conn.close()
    return id_factura

def obtener_ventas():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ventas ORDER BY id DESC")
    ventas = cursor.fetchall()
    conn.close()
    return ventas

def obtener_venta_por_id(id_factura):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ventas WHERE id_factura=?", (id_factura,))
    venta = cursor.fetchone()
    conn.close()
    return venta

def obtener_ventas_por_fecha(fecha):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ventas WHERE fecha=? ORDER BY hora DESC", (fecha,))
    ventas = cursor.fetchall()
    conn.close()
    return ventas

def obtener_ventas_por_empleado(empleado, fecha_inicio=None, fecha_fin=None):
    conn = conectar()
    cursor = conn.cursor()
    if fecha_inicio and fecha_fin:
        cursor.execute("""
            SELECT * FROM ventas 
            WHERE empleado=? AND fecha BETWEEN ? AND ?
            ORDER BY fecha DESC, hora DESC
        """, (empleado, fecha_inicio, fecha_fin))
    else:
        cursor.execute("""
            SELECT * FROM ventas 
            WHERE empleado=?
            ORDER BY fecha DESC, hora DESC
        """, (empleado,))
    ventas = cursor.fetchall()
    conn.close()
    return ventas

# ======================== INICIOS DE SESION ========================
def registrar_inicio_sesion(usuario, nombre, cedula, fecha, hora_entrada):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO inicios_sesion (usuario, nombre, cedula, fecha, hora_entrada, hora_salida)
        VALUES (?, ?, ?, ?, ?, NULL)
    """, (usuario, nombre, cedula, fecha, hora_entrada))
    conn.commit()
    conn.close()

def registrar_logout(usuario, fecha, hora_salida):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id FROM inicios_sesion 
        WHERE usuario=? AND fecha=? AND (hora_salida IS NULL OR hora_salida='')
        ORDER BY id DESC LIMIT 1
    """, (usuario, fecha))
    res = cursor.fetchone()
    if res:
        cursor.execute("""
            UPDATE inicios_sesion 
            SET hora_salida=?
            WHERE id=?
        """, (hora_salida, res[0]))
        conn.commit()
    conn.close()

def obtener_logins():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT usuario, nombre, cedula, fecha, 
               hora_entrada, 
               COALESCE(hora_salida, '-') as hora_salida
        FROM inicios_sesion 
        ORDER BY id DESC
    """)
    logins = cursor.fetchall()
    conn.close()
    return logins

# ======================== COMPRAS ========================
def agregar_compra(fecha, hora, metodo_pago, proveedor, factura, productos, valor_total):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO compras (fecha, hora, metodo_pago, proveedor, factura, productos, valor_total)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (fecha, hora, metodo_pago, proveedor, factura, productos, valor_total))
    conn.commit()
    conn.close()

def obtener_compras():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM compras ORDER BY id DESC")
    compras = cursor.fetchall()
    conn.close()
    return compras

# ======================== BACKUP ========================
def backup_database():
    backup_dir = "backups"
    os.makedirs(backup_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"{backup_dir}/pos_backup_{timestamp}.db"
    try:
        shutil.copy2(DB_PATH, backup_file)
        return backup_file
    except Exception as e:
        raise Exception(f"Error al crear backup: {e}")

# ======================== INICIALIZAR BASE DE DATOS ========================
def inicializar_bd():
    conn = conectar()
    cursor = conn.cursor()
    # Tabla productos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            sku TEXT PRIMARY KEY,
            nombre TEXT NOT NULL,
            precio REAL NOT NULL,
            stock INTEGER NOT NULL,
            fecha_actualizacion TEXT,
            salidas_ventas INTEGER DEFAULT 0,
            stock_actual INTEGER NOT NULL,
            stock_minimo INTEGER DEFAULT 5
        )
    """)
    # Tabla clientes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            cedula TEXT UNIQUE NOT NULL,
            celular TEXT,
            correo TEXT,
            fecha_registro TEXT
        )
    """)
    # Tabla ventas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_factura TEXT UNIQUE,
            fecha TEXT,
            hora TEXT,
            empleado TEXT,
            productos TEXT,
            total REAL,
            cambio REAL,
            metodo_pago TEXT,
            valor_pagado REAL,
            cliente_cedula TEXT,
            estado TEXT DEFAULT 'completada'
        )
    """)
    # Tabla empleados
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS empleados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE,
            nombre TEXT,
            cedula TEXT UNIQUE,
            contrasena TEXT,
            fecha_ingreso TEXT,
            hora_entrada TEXT
        )
    """)
    # Tabla inicios de sesión
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inicios_sesion (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT,
            nombre TEXT,
            cedula TEXT,
            fecha TEXT,
            hora_entrada TEXT,
            hora_salida TEXT
        )
    """)
    # Tabla compras
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS compras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT,
            hora TEXT,
            metodo_pago TEXT,
            proveedor TEXT,
            factura TEXT,
            productos TEXT,
            valor_total REAL
        )
    """)
    conn.commit()
    conn.close()

# Migración para agregar campos si hacen falta
def migrar_bd():
    conn = conectar()
    cursor = conn.cursor()
    # Clientes: correo
    cursor.execute("PRAGMA table_info(clientes)")
    columnas = [columna[1] for columna in cursor.fetchall()]
    if 'correo' not in columnas:
        cursor.execute("ALTER TABLE clientes ADD COLUMN correo TEXT")
        conn.commit()

    # Ventas: cliente_cedula, hora
    cursor.execute("PRAGMA table_info(ventas)")
    columnas_ventas = [columna[1] for columna in cursor.fetchall()]
    if 'cliente_cedula' not in columnas_ventas:
        cursor.execute("ALTER TABLE ventas ADD COLUMN cliente_cedula TEXT")
        conn.commit()
    if 'hora' not in columnas_ventas:
        cursor.execute("ALTER TABLE ventas ADD COLUMN hora TEXT")
        conn.commit()

    # Empleados
    cursor.execute("PRAGMA table_info(empleados)")
    columnas_empleados = [columna[1] for columna in cursor.fetchall()]
    if not columnas_empleados:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS empleados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT UNIQUE,
                nombre TEXT,
                cedula TEXT UNIQUE,
                contrasena TEXT,
                fecha_ingreso TEXT,
                hora_entrada TEXT
            )
        """)
        conn.commit()
    
    # Inicios de sesión (con hora_entrada y hora_salida)
    cursor.execute("PRAGMA table_info(inicios_sesion)")
    columnas_sesion = [columna[1] for columna in cursor.fetchall()]
    campos_necesarios = ["hora_entrada", "hora_salida"]
    for campo in campos_necesarios:
        if campo not in columnas_sesion:
            cursor.execute(f"ALTER TABLE inicios_sesion ADD COLUMN {campo} TEXT")
            conn.commit()
    # Compras
    cursor.execute("PRAGMA table_info(compras)")
    columnas_compras = [columna[1] for columna in cursor.fetchall()]
    campos_compras = ["fecha", "hora", "metodo_pago", "proveedor", "factura", "productos", "valor_total"]
    if not columnas_compras:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS compras (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT,
                hora TEXT,
                metodo_pago TEXT,
                proveedor TEXT,
                factura TEXT,
                productos TEXT,
                valor_total REAL
            )
        """)
        conn.commit()
    else:
        for campo in campos_compras:
            if campo not in columnas_compras:
                tipo = "TEXT" if campo != "valor_total" else "REAL"
                cursor.execute(f"ALTER TABLE compras ADD COLUMN {campo} {tipo}")
                conn.commit()
    conn.close()

if __name__ == "__main__":
    inicializar_bd()
    migrar_bd()
    print("Base de datos creada/actualizada correctamente.")
