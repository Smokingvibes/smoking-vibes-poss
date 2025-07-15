import sqlite3

def verificar_estructura_ventas():
    """Script para verificar la estructura real de los datos en la tabla ventas"""
    
    try:
        conn = sqlite3.connect("pos_420_smoking_vibes.db")
        cursor = conn.cursor()
        
        print("=== ESTRUCTURA DE LA TABLA VENTAS ===")
        cursor.execute("PRAGMA table_info(ventas)")
        columnas = cursor.fetchall()
        for i, col in enumerate(columnas):
            print(f"Indice {i}: {col[1]} ({col[2]})")
        
        print("\n=== ULTIMAS 3 VENTAS (DATOS REALES) ===")
        cursor.execute("SELECT * FROM ventas ORDER BY id DESC LIMIT 3")
        ventas = cursor.fetchall()
        
        for i, venta in enumerate(ventas):
            print(f"\n--- VENTA {i+1} ---")
            for j, valor in enumerate(venta):
                print(f"Indice {j}: {valor}")
        
        print("\n=== CONSULTA CON NOMBRES DE COLUMNAS ===")
        cursor.execute("SELECT id, id_factura, fecha, hora, empleado, productos, total, cambio, metodo_pago, valor_pagado, cliente_cedula, estado FROM ventas ORDER BY id DESC LIMIT 1")
        venta = cursor.fetchone()
        
        if venta:
            campos = ['id', 'id_factura', 'fecha', 'hora', 'empleado', 'productos', 'total', 'cambio', 'metodo_pago', 'valor_pagado', 'cliente_cedula', 'estado']
            print("\n--- CAMPOS NOMBRADOS ---")
            for i, (campo, valor) in enumerate(zip(campos, venta)):
                print(f"{campo}: {valor}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verificar_estructura_ventas()