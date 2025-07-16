import tkinter as tk
from tkinter import ttk, messagebox
from db import (
    obtener_ventas,
    obtener_venta_por_id,
    obtener_cliente_por_cedula,
    formatear_moneda,
    formatear_fecha
)
import os
import platform
import subprocess
import pandas as pd
from datetime import datetime

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
        # Filtro de fechas para reportes
        tk.Label(frm_filtros, text="Desde:").pack(side="left", padx=(18, 1))
        self.entry_fecha_ini = tk.Entry(frm_filtros, width=11)
        self.entry_fecha_ini.pack(side="left", padx=1)
        self.entry_fecha_ini.insert(0, formatear_fecha())
        tk.Label(frm_filtros, text="Hasta:").pack(side="left", padx=1)
        self.entry_fecha_fin = tk.Entry(frm_filtros, width=11)
        self.entry_fecha_fin.pack(side="left", padx=1)
        self.entry_fecha_fin.insert(0, formatear_fecha())
        tk.Button(frm_filtros,
                  text="Reporte de Ventas",
                  command=self.abrir_reporte_ventas,
                  bg="#ffd700").pack(side="left", padx=6)
        tk.Button(frm_filtros,
                  text="Exportar Excel",
                  command=self.exportar_excel_reporte,
                  bg="#b4ffa8").pack(side="left", padx=3)

        # Tabla de facturas
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

        self.tree.tag_configure('completada', background='#ccffcc')
        self.tree.tag_configure('anulada', background='#ffcccc')

        # Botones acción
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

        # Resumen
        self.lbl_resumen = tk.Label(self,
                                    text="",
                                    font=('Arial', 11, 'bold'),
                                    bg="#f0f8ff")
        self.lbl_resumen.pack(pady=3)

        # DataFrame temporal para exportación de reportes
        self.df_reporte = pd.DataFrame()

    def cargar_facturas(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        ventas = obtener_ventas()
        total = 0
        cantidad = 0
        completadas = 0
        anuladas = 0
        efectivo = transferencia = datafono = 0
        rows = []
        for v in ventas:
            # Desempaquetar datos correctamente
            id_factura = v[1]
            fecha = v[2]
            hora = v[11] if len(v) > 11 else "-"
            empleado = v[3] if len(v) > 3 else "-"
            cliente_cedula = v[10] if len(v) > 10 else None
            cliente_nombre = "-"
            if cliente_cedula:
                cliente = obtener_cliente_por_cedula(cliente_cedula)
                if cliente:
                    cliente_nombre = cliente[1][:18]
            total_venta = float(v[5]) if v[5] else 0
            metodo = (v[8] or "").lower()
            estado = v[9] if len(v) > 9 and v[9] else "completada"
            tag = (estado.lower() if estado else "completada")
            rows.append([id_factura, fecha, hora, empleado, cliente_nombre, total_venta, v[8], estado.capitalize()])
            if estado.lower() == "completada":
                completadas += 1
                total += total_venta
                cantidad += 1
                if "efectivo" in metodo:
                    efectivo += total_venta
                if "trans" in metodo:
                    transferencia += total_venta
                if "dat" in metodo:
                    datafono += total_venta
            elif "anul" in estado.lower() or "elimin" in estado.lower():
                anuladas += 1
        for row in rows:
            self.tree.insert("",
                             "end",
                             values=(row),
                             tags=(row[7].lower(),))
        self.lbl_resumen.config(
            text=f"Ventas completadas: {completadas} | Anuladas: {anuladas} | Total ventas: {formatear_moneda(total)}\n"
                 f"Efectivo: {formatear_moneda(efectivo)} | Transferencia: {formatear_moneda(transferencia)} | Datáfono: {formatear_moneda(datafono)}"
        )
        # Para exportar el último reporte mostrado en tabla
        self.df_reporte = pd.DataFrame(rows, columns=["ID", "Fecha", "Hora", "Empleado", "Cliente", "Total", "Método", "Estado"])

    def filtrar_facturas(self):
        filtro = self.combo_filtro.get()
        texto = self.entry_buscar.get().strip().lower()
        for item in self.tree.get_children():
            self.tree.delete(item)
        ventas = obtener_ventas()
        resultados = []
        for v in ventas:
            id_factura = v[1]
            empleado = v[3] if len(v) > 3 else ""
            cliente_cedula = v[10] if len(v) > 10 else None
            if filtro == "Todos":
                incluir = True
            elif filtro == "ID Factura" and texto in str(id_factura).lower():
                incluir = True
            elif filtro == "Cliente" and cliente_cedula and texto in str(cliente_cedula).lower():
                incluir = True
            elif filtro == "Empleado" and texto in empleado.lower():
                incluir = True
            else:
                incluir = False
            if incluir:
                resultados.append(v)
        # El resto igual a cargar_facturas, pero solo con resultados
        total = 0
        completadas = 0
        anuladas = 0
        efectivo = transferencia = datafono = 0
        rows = []
        for v in resultados:
            id_factura = v[1]
            fecha = v[2]
            hora = v[11] if len(v) > 11 else "-"
            empleado = v[3] if len(v) > 3 else "-"
            cliente_cedula = v[10] if len(v) > 10 else None
            cliente_nombre = "-"
            if cliente_cedula:
                cliente = obtener_cliente_por_cedula(cliente_cedula)
                if cliente:
                    cliente_nombre = cliente[1][:18]
            total_venta = float(v[5]) if v[5] else 0
            metodo = (v[8] or "").lower()
            estado = v[9] if len(v) > 9 and v[9] else "completada"
            tag = (estado.lower() if estado else "completada")
            rows.append([id_factura, fecha, hora, empleado, cliente_nombre, total_venta, v[8], estado.capitalize()])
            if estado.lower() == "completada":
                completadas += 1
                total += total_venta
                if "efectivo" in metodo:
                    efectivo += total_venta
                if "trans" in metodo:
                    transferencia += total_venta
                if "dat" in metodo:
                    datafono += total_venta
            elif "anul" in estado.lower() or "elimin" in estado.lower():
                anuladas += 1
        for row in rows:
            self.tree.insert("",
                             "end",
                             values=(row),
                             tags=(row[7].lower(),))
        self.lbl_resumen.config(
            text=f"Ventas completadas: {completadas} | Anuladas: {anuladas} | Total ventas: {formatear_moneda(total)}\n"
                 f"Efectivo: {formatear_moneda(efectivo)} | Transferencia: {formatear_moneda(transferencia)} | Datáfono: {formatear_moneda(datafono)}"
        )
        self.df_reporte = pd.DataFrame(rows, columns=["ID", "Fecha", "Hora", "Empleado", "Cliente", "Total", "Método", "Estado"])

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
        # ORDEN CORRECTO
        id_factura = v[1]
        fecha = v[2]
        empleado = v[3]
        productos = v[4]
        total = v[5]
        valor_pagado = v[6]
        cambio = v[7]
        metodo_pago = v[8]
        estado = v[9] if len(v) > 9 else "completada"
        cliente_cedula = v[10]
        hora = v[11] if len(v) > 11 else "-"
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
        id_factura = v[1]
        fecha = v[2]
        empleado = v[3]
        productos = v[4]
        total = v[5]
        valor_pagado = v[6]
        cambio = v[7]
        metodo_pago = v[8]
        estado = v[9] if len(v) > 9 else "completada"
        cliente_cedula = v[10]
        hora = v[11] if len(v) > 11 else "-"
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

    def abrir_reporte_ventas(self):
        # Ventana de reporte de ventas con rango de fechas
        ventana = tk.Toplevel(self)
        ventana.title("Reporte de Ventas")
        ventana.geometry("900x500")
        ventana.configure(bg="#f0f8ff")

        # Selector de fechas
        frm = tk.Frame(ventana, bg="#f0f8ff")
        frm.pack(pady=10)
        tk.Label(frm, text="Desde:", bg="#f0f8ff").pack(side="left")
        desde = tk.Entry(frm, width=12)
        desde.pack(side="left", padx=3)
        desde.insert(0, self.entry_fecha_ini.get())
        tk.Label(frm, text="Hasta:", bg="#f0f8ff").pack(side="left")
        hasta = tk.Entry(frm, width=12)
        hasta.pack(side="left", padx=3)
        hasta.insert(0, self.entry_fecha_fin.get())
        tk.Button(frm, text="Buscar", bg="#ffd700", command=lambda: actualizar()).pack(side="left", padx=6)

        # Tabla
        cols = ("ID", "Fecha", "Hora", "Empleado", "Cliente", "Total", "Método", "Estado")
        tree = ttk.Treeview(ventana, columns=cols, show="headings", height=16)
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=110 if col != "Cliente" else 170)
        tree.pack(padx=12, pady=5, fill="x")

        resumen_lbl = tk.Label(ventana, text="", font=('Arial', 11, 'bold'), bg="#f0f8ff")
        resumen_lbl.pack(pady=4)

        def exportar_excel(df):
            carpeta = "reportes de ventas"
            os.makedirs(carpeta, exist_ok=True)
            desde_fecha = desde.get().replace("/", "-")
            hasta_fecha = hasta.get().replace("/", "-")
            nombre = f"Reporte_Ventas_{desde_fecha}_a_{hasta_fecha}.xlsx"
            ruta = os.path.join(carpeta, nombre)
            df.to_excel(ruta, index=False)
            messagebox.showinfo("Exportar", f"Reporte exportado a:\n{ruta}")

        def actualizar():
            tree.delete(*tree.get_children())
            ventas = obtener_ventas()
            fecha_ini = desde.get()
            fecha_fin = hasta.get()
            data = []
            resumen = {
                'completadas': 0, 'anuladas': 0, 'total': 0,
                'efectivo': 0, 'transferencia': 0, 'datafono': 0
            }
            for v in ventas:
                fecha = v[2]
                try:
                    f_dt = datetime.strptime(fecha, "%d/%m/%Y")
                    d_dt = datetime.strptime(fecha_ini, "%d/%m/%Y")
                    h_dt = datetime.strptime(fecha_fin, "%d/%m/%Y")
                except:
                    continue
                if not (d_dt <= f_dt <= h_dt):
                    continue
                id_factura = v[1]
                hora = v[11] if len(v) > 11 else "-"
                empleado = v[3] if len(v) > 3 else "-"
                cliente_nombre = "-"
                if len(v) > 10 and v[10]:
                    cliente = obtener_cliente_por_cedula(v[10])
                    if cliente: cliente_nombre = cliente[1][:18]
                total = float(v[5]) if v[5] else 0
                metodo = (v[8] or "").lower()
                estado = v[9] if len(v) > 9 and v[9] else "completada"
                data.append([id_factura, fecha, hora, empleado, cliente_nombre, total, v[8], estado.capitalize()])
                if estado.lower() == "completada":
                    resumen['completadas'] += 1
                    resumen['total'] += total
                    if "efectivo" in metodo: resumen['efectivo'] += total
                    if "trans" in metodo: resumen['transferencia'] += total
                    if "dat" in metodo: resumen['datafono'] += total
                elif "anul" in estado.lower() or "elimin" in estado.lower():
                    resumen['anuladas'] += 1

            for row in data:
                tree.insert("", "end", values=(row))
            resumen_lbl.config(
                text=f"Ventas completadas: {resumen['completadas']} | Anuladas: {resumen['anuladas']} | "
                     f"Total ventas: {formatear_moneda(resumen['total'])}\n"
                     f"Efectivo: {formatear_moneda(resumen['efectivo'])} | "
                     f"Transferencia: {formatear_moneda(resumen['transferencia'])} | "
                     f"Datáfono: {formatear_moneda(resumen['datafono'])}"
            )
            ventana.df_reporte = pd.DataFrame(data, columns=cols)

        tk.Button(ventana, text="Exportar Excel", command=lambda: exportar_excel(ventana.df_reporte),
                  bg="#b4ffa8").pack(pady=7)

        actualizar()  # Primera carga

    def exportar_excel_reporte(self):
        if self.df_reporte.empty:
            messagebox.showwarning("Exportar", "Primero filtra o muestra las ventas que quieres exportar.")
            return
        carpeta = "reportes de ventas"
        os.makedirs(carpeta, exist_ok=True)
        fecha_ini = self.entry_fecha_ini.get().replace("/", "-")
        fecha_fin = self.entry_fecha_fin.get().replace("/", "-")
        nombre = f"Reporte_Ventas_{fecha_ini}_a_{fecha_fin}.xlsx"
        ruta = os.path.join(carpeta, nombre)
        self.df_reporte.to_excel(ruta, index=False)
        messagebox.showinfo("Exportar", f"Reporte exportado a:\n{ruta}")

