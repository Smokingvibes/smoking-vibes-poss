# reportes.py
import os
from db import conectar, formatear_moneda


def reporte_dia(fecha):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id_factura, fecha, hora, empleado, cliente_cedula, total, metodo_pago
        FROM ventas WHERE fecha=?
    """, (fecha, ))
    ventas = cursor.fetchall()
    conn.close()
    totales = {}
    for v in ventas:
        metodo = v[6]
        totales[metodo] = totales.get(metodo, 0) + v[5]
    # Puedes imprimir por pantalla o guardar como txt
    return ventas, totales
