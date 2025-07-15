import tkinter as tk
from tkinter import ttk, messagebox
from db import (obtener_ventas, obtener_venta_por_id,
                obtener_cliente_por_cedula, formatear_moneda, formatear_fecha,
                formatear_hora)
import os
import platform
import subprocess

class FacturasFrame(ttk.Frame):

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.crear_interfaz()
        self.cargar_facturas()

    def crear_interfaz(self):
        header = tk.Label(self,
                          text="GESTIÓN DE FACTURAS",
                          bg="#f0f8ff",
                          font=('Arial', 14, 'bold'))
        header.pack(pady=5)

        # Filtros
        frm_filtros = tk.Frame(self)
        frm_filtros.pack(pady=5)
        tk.Label(frm_filtros, text="Buscar por:").pack(side="left", padx=3)
        self.combo_filtro = ttk.Combobox(
            frm_filtros,
            values=["Todos", "ID Factura", "Cliente", "Empleado"],
            width=12)
        self.combo_filtro.set("Todos")
        self.combo_filtro.pack(side="left", padx=3)
        tk.Label(frm_filtros, text="Texto:").pack(side="left", padx=3)
        self.entry_buscar = tk.Entry(frm_filtros, width=18)
        self.entry_buscar.pack(side="left", padx=3)
        tk.Button(frm_filtros,
                  text="Buscar",
                  command=self.filtrar_facturas,
                  bg="#87ceeb").pack(side="left", padx=6)
        tk.Button(frm_filtros,
                  text="Mostrar Todas",
                  command=self.cargar_facturas,
                  bg="#90ee90").pack(side="left", padx=6)

        # Tabla
        cols = ("ID", "Fecha", "Hora", "Empleado", "Cliente", "Total",
                "Método", "Estado")
        self.tree = ttk.Treeview(self,
                                 columns=cols,
                                 show="headings",
                                 height=15)
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=110 if col != "Cliente" else 170)
        self.tree.pack(padx=15, pady=8, fill="x")
        self.tree.bind("<Double-1>", self.ver_detalle)

        # Colores según estado
        self.tree.tag_configure('completada', background='#ccffcc')
        self.tree.tag_configure('anulada', background='#ffcccc')

        # Botones
        frm_btns = tk.Frame(self)
        frm_btns.pack(pady=8)
        tk.Button(frm_btns,
                  text="Ver Detalle",
                  command=self.ver_detalle,
                  bg="#aee1ff").pack(side="left", padx=7)
        tk.Button(frm_btns,
                  text="🖨️ Reimprimir",
                  command=self.reimprimir,
                  bg="#90ee90").pack(side="left", padx=7)
        tk.Button(frm_btns,
                  text="📊 Reporte del Día",
                  command=self.reporte_dia,
                  bg="#ffd700").pack(side="left", padx=7)

        # Resumen
        self.lbl_resumen = tk.Label(self,
                                    text="",
                                    font=('Arial', 11, 'bold'),
                                    bg="#f0f8ff")
        self.lbl_resumen.pack(pady=3)

    def cargar_facturas(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        ventas = obtener_ventas()
        total = 0
        cantidad = 0
        for v in ventas:
            # ORDEN CORRECTO según la estructura REAL de la base de datos
            id_factura      = v[1]
            fecha           = v[2]
            empleado        = v[3] if len(v) > 3 and v[3] else "-"
            productos       = v[4] if len(v) > 4 else ""
            total_venta     = v[5] if len(v) > 5 else 0
            valor_pagado    = v[6] if len(v) > 6 else 0  # VALOR_PAGADO está en índice 6
            cambio          = v[7] if len(v) > 7 else 0  # CAMBIO está en índice 7
            metodo_pago     = v[8] if len(v) > 8 and v[8] else "-"  # METODO_PAGO está en índice 8
            estado          = v[9] if len(v) > 9 and v[9] else "completada"
            cliente_cedula  = v[10] if len(v) > 10 and v[10] else None
            hora            = v[11] if len(v) > 11 and v[11] else "-"  # HORA está al final en índice 11
            
            tag = (estado.lower() if estado else "completada")
            cliente_nombre = "-"
            if cliente_cedula:
                cliente = obtener_cliente_por_cedula(cliente_cedula)
                if cliente:
                    cliente_nombre = cliente[1][:15]
            
            try:
                total_val = float(total_venta)
            except:
                total_val = 0
                
            if estado.lower() == "completada":
                total += total_val
                cantidad += 1
                
            # Insertar con el orden correcto: ID, Fecha, Hora, Empleado, Cliente, Total, Método, Estado
            self.tree.insert("",
                             "end",
                             values=(id_factura, 
                                   fecha, 
                                   hora,
                                   empleado, 
                                   cliente_nombre,
                                   formatear_moneda(total_val), 
                                   metodo_pago,
                                   estado.capitalize()),
                             tags=(tag, ))
                             
        self.lbl_resumen.config(
            text=
            f"Total facturas: {cantidad} | Total ventas: {formatear_moneda(total)}"
        )

    def filtrar_facturas(self):
        filtro = self.combo_filtro.get()
        texto = self.entry_buscar.get().strip().lower()
        for item in self.tree.get_children():
            self.tree.delete(item)
        ventas = obtener_ventas()
        resultados = []
        for v in ventas:
            incluir = False
            
            # ORDEN CORRECTO según la estructura REAL de la base de datos
            id_factura      = v[1]
            empleado        = v[3] if len(v) > 3 and v[3] else ""
            cliente_cedula  = v[10] if len(v) > 10 and v[10] else None
            
            if filtro == "Todos":
                incluir = True
            elif filtro == "ID Factura" and texto in str(id_factura).lower():
                incluir = True
            elif filtro == "Cliente" and cliente_cedula and texto in str(cliente_cedula).lower():
                incluir = True
            elif filtro == "Empleado" and texto in empleado.lower():
                incluir = True
            if incluir:
                resultados.append(v)
                
        total = 0
        cantidad = 0
        for v in resultados:
            # ORDEN CORRECTO según la estructura REAL de la base de datos
            id_factura      = v[1]
            fecha           = v[2]
            empleado        = v[3] if len(v) > 3 and v[3] else "-"
            productos       = v[4] if len(v) > 4 else ""
            total_venta     = v[5] if len(v) > 5 else 0
            valor_pagado    = v[6] if len(v) > 6 else 0  # VALOR_PAGADO está en índice 6
            cambio          = v[7] if len(v) > 7 else 0  # CAMBIO está en índice 7
            metodo_pago     = v[8] if len(v) > 8 and v[8] else "-"  # METODO_PAGO está en índice 8
            estado          = v[9] if len(v) > 9 and v[9] else "completada"
            cliente_cedula  = v[10] if len(v) > 10 and v[10] else None
            hora            = v[11] if len(v) > 11 and v[11] else "-"  # HORA está al final en índice 11
            
            tag = (estado.lower() if estado else "completada")
            cliente_nombre = "-"
            if cliente_cedula:
                cliente = obtener_cliente_por_cedula(cliente_cedula)
                if cliente:
                    cliente_nombre = cliente[1][:15]
                    
            try:
                total_val = float(total_venta)
            except:
                total_val = 0
                
            if estado.lower() == "completada":
                total += total_val
                cantidad += 1
                
            # Insertar con el orden correcto: ID, Fecha, Hora, Empleado, Cliente, Total, Método, Estado
            self.tree.insert("",
                             "end",
                             values=(id_factura, 
                                   fecha, 
                                   hora,
                                   empleado, 
                                   cliente_nombre,
                                   formatear_moneda(total_val), 
                                   metodo_pago,
                                   estado.capitalize()),
                             tags=(tag, ))
                             
        self.lbl_resumen.config(
            text=
            f"Total facturas: {cantidad} | Total ventas: {formatear_moneda(total)}"
        )

    def ver_detalle(self, event=None):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Sin selección", "Selecciona una factura")
            return
        id_factura = self.tree.item(seleccion[0])["values"][0]
        v = obtener_venta_por_id(id_factura)
        if not v:
            messagebox.showerror("No encontrada", "No se encuentra esa factura.")
            return

        # ORDEN CORRECTO según la estructura REAL de la base de datos
        id_factura      = v[1]
        fecha           = v[2]
        empleado        = v[3]
        productos       = v[4]
        total           = v[5]
        valor_pagado    = v[6]  # VALOR_PAGADO está en índice 6
        cambio          = v[7]  # CAMBIO está en índice 7
        metodo_pago     = v[8]  # METODO_PAGO está en índice 8
        estado          = v[9] if len(v) > 9 else "completada"
        cliente_cedula  = v[10]
        hora            = v[11] if len(v) > 11 else "-"  # HORA está al final

        info_cliente = ""
        if cliente_cedula:
            cliente = obtener_cliente_por_cedula(cliente_cedula)
            if cliente:
                info_cliente = f"CLIENTE: {cliente[1]}\nCÉDULA: {cliente[2]}"
                if cliente[3]:
                    info_cliente += f"\nCELULAR: {cliente[3]}"

        detalle = f"""
{'='*54}
420 Smoking Vibes
Cel: 3126251302
Calle 1 #29 - 438
{'='*54}

ID FACTURA: {id_factura}
FECHA: {fecha}
HORA: {hora}
EMPLEADO: {empleado}

{info_cliente}

{'-'*54}
PRODUCTOS VENDIDOS:
{'-'*54}
{productos}

{'-'*54}
TOTAL: {formatear_moneda(total)}
{'-'*54}

PAGO:
  • Método: {metodo_pago}
  • Recibido: {formatear_moneda(valor_pagado)}
  • Cambio: {formatear_moneda(cambio)}

{'='*54}
¡Gracias por tu compra y Suave La Vida! 😎✨
{'='*54}
"""

        ventana = tk.Toplevel(self)
        ventana.title(f"Detalle Factura {id_factura}")
        ventana.geometry("650x500")
        ventana.configure(bg="#f0f8ff")

        txt = tk.Text(ventana, width=80, height=26, font=("Consolas", 10))
        txt.pack(padx=10, pady=10)
        txt.insert("1.0", detalle)
        txt.config(state="disabled")

        btn_frame = tk.Frame(ventana)
        btn_frame.pack(pady=6)

        def imprimir():
            archivo = f"Factura_{id_factura}.txt"
            with open(archivo, "w", encoding="utf-8") as f:
                f.write(detalle)
            try:
                if platform.system() == "Windows":
                    os.startfile(archivo, "print")
                else:
                    subprocess.run(["lp", archivo])
                messagebox.showinfo("Impresión", f"Factura enviada a la impresora.\nArchivo: {archivo}")
            except Exception as e:
                messagebox.showerror("Error de impresión", f"No se pudo imprimir: {e}")

        tk.Button(btn_frame, text="Imprimir", command=imprimir,
                  bg="#90ee90").pack(side="left", padx=10)
        tk.Button(btn_frame,
                  text="Cerrar",
                  command=ventana.destroy,
                  bg="#ff7272").pack(side="left", padx=10)

    def reimprimir(self):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Selecciona",
                                   "Selecciona una factura para reimprimir")
            return
        id_factura = self.tree.item(seleccion[0])["values"][0]
        v = obtener_venta_por_id(id_factura)
        if not v:
            messagebox.showerror("No encontrada", "Factura no encontrada")
            return
        carpeta = "Facturas_Reimpresiones"
        os.makedirs(carpeta, exist_ok=True)
        archivo = os.path.join(carpeta, f"REIMPRESION_{id_factura}.txt")

        # ORDEN CORRECTO según la estructura REAL de la base de datos
        id_factura      = v[1]
        fecha           = v[2]
        empleado        = v[3]
        productos       = v[4]
        total           = v[5]
        valor_pagado    = v[6]  # VALOR_PAGADO está en índice 6
        cambio          = v[7]  # CAMBIO está en índice 7
        metodo_pago     = v[8]  # METODO_PAGO está en índice 8
        estado          = v[9] if len(v) > 9 else "completada"
        cliente_cedula  = v[10]
        hora            = v[11] if len(v) > 11 else "-"  # HORA está al final

        info_cliente = ""
        if cliente_cedula:
            cliente = obtener_cliente_por_cedula(cliente_cedula)
            if cliente:
                info_cliente = f"CLIENTE: {cliente[1]}\nCÉDULA: {cliente[2]}"
                if cliente[3]:
                    info_cliente += f"\nCELULAR: {cliente[3]}"

        with open(archivo, "w", encoding="utf-8") as f:
            f.write("=" * 54 + "\n")
            f.write("420 Smoking Vibes\n")
            f.write("Cel: 3126251302\n")
            f.write("Calle 1 #29 - 438\n")
            f.write("=" * 54 + "\n\n")
            f.write(f"FACTURA N°: {id_factura}\n")
            f.write(f"Fecha Original: {fecha}   Hora: {hora}\n")
            f.write(f"Empleado: {empleado}\n\n")
            if info_cliente:
                f.write(info_cliente + "\n")
            f.write("-" * 54 + "\n")
            f.write("PRODUCTOS VENDIDOS:\n")
            f.write("-" * 54 + "\n")
            f.write(f"{productos}\n")
            f.write("-" * 54 + "\n")
            f.write(f"TOTAL: {formatear_moneda(total)}\n")
            f.write("=" * 54 + "\n")
            f.write(f"Método de Pago: {metodo_pago}\n")
            f.write(f"Recibido: {formatear_moneda(valor_pagado)}\n")
            f.write(f"Cambio: {formatear_moneda(cambio)}\n")
            f.write("=" * 54 + "\n")
            f.write("¡Gracias por tu compra y por apoyar el poder de la buena vibra! 😎✨\n")
            f.write("=" * 54 + "\n")
        messagebox.showinfo("Reimpresión", f"Factura reimpresa en:\n{archivo}")

    def reporte_dia(self):
        fecha = formatear_fecha()
        ventas = obtener_ventas()
        ventas_hoy = [v for v in ventas if v[2] == fecha]
        total = 0
        detalles = ""
        for v in ventas_hoy:
            # ORDEN CORRECTO según la estructura REAL de la base de datos
            id_factura = v[1]
            empleado = v[3] if len(v) > 3 else ""
            total_venta = v[5] if len(v) > 5 else 0
            
            try:
                total_val = float(total_venta)
            except:
                total_val = 0
            detalles += f"- Factura {id_factura}: {formatear_moneda(total_val)}  ({empleado})\n"
            total += total_val
        reporte = f"""
420 Smoking Vibes
REPORTE DEL DÍA: {fecha}

Total ventas: {formatear_moneda(total)}
Cantidad de ventas: {len(ventas_hoy)}

DETALLE:
{detalles}
"""
        ventana = tk.Toplevel(self)
        ventana.title("Reporte del Día")
        ventana.geometry("480x350")
        txt = tk.Text(ventana, width=58, height=16, font=("Consolas", 10))
        txt.pack(padx=10, pady=10)
        txt.insert("1.0", reporte)
        txt.config(state="disabled")

        def guardar():
            carpeta = "Reportes"
            os.makedirs(carpeta, exist_ok=True)
            archivo = os.path.join(carpeta,
                                   f"Reporte_{fecha.replace('/', '_')}.txt")
            with open(archivo, "w", encoding="utf-8") as f:
                f.write(reporte)
            messagebox.showinfo("Reporte", f"Reporte guardado en {archivo}")

        tk.Button(ventana,
                  text="Guardar Reporte",
                  command=guardar,
                  bg="#90ee90").pack(side="left", padx=12, pady=7)
        tk.Button(ventana,
                  text="Cerrar",
                  command=ventana.destroy,
                  bg="#ff7272").pack(side="right", padx=12, pady=7)