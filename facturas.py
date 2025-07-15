import tkinter as tk
from tkinter import ttk, messagebox
from db import (obtener_ventas, obtener_venta_por_id,
                obtener_cliente_por_cedula, formatear_moneda, formatear_fecha,
                formatear_hora)
import os


class FacturasFrame(ttk.Frame):

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.crear_interfaz()
        self.cargar_facturas()

    def crear_interfaz(self):
        # Header
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

        # Configura colores por estado
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
            estado = v[11] if len(v) > 11 and v[11] else "completada"
            tag = (estado.lower() if estado else "completada")
            cliente_nombre = "-"
            if len(v) > 10 and v[10]:
                cliente = obtener_cliente_por_cedula(v[10])
                if cliente:
                    cliente_nombre = cliente[1][:15]
            try:
                total_val = float(v[6])
            except:
                total_val = 0
            if estado.lower() == "completada":
                total += total_val
                cantidad += 1
            self.tree.insert("",
                             "end",
                             values=(v[1], v[2], v[3]
                                     or "-", v[4], cliente_nombre,
                                     formatear_moneda(total_val), v[8],
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
            if filtro == "Todos":
                incluir = True
            elif filtro == "ID Factura" and texto in str(v[1]).lower():
                incluir = True
            elif filtro == "Cliente" and len(v) > 10 and texto in (str(
                    v[10]).lower()):
                incluir = True
            elif filtro == "Empleado" and texto in (v[4] or "").lower():
                incluir = True
            if incluir:
                resultados.append(v)
        total = 0
        cantidad = 0
        for v in resultados:
            estado = v[11] if len(v) > 11 and v[11] else "completada"
            tag = (estado.lower() if estado else "completada")
            cliente_nombre = "-"
            if len(v) > 10 and v[10]:
                cliente = obtener_cliente_por_cedula(v[10])
                if cliente:
                    cliente_nombre = cliente[1][:15]
            try:
                total_val = float(v[6])
            except:
                total_val = 0
            if estado.lower() == "completada":
                total += total_val
                cantidad += 1
            self.tree.insert("",
                             "end",
                             values=(v[1], v[2], v[3]
                                     or "-", v[4], cliente_nombre,
                                     formatear_moneda(total_val), v[8],
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
            messagebox.showerror("No encontrada",
                                 "No se encuentra esa factura.")
            return

        # Obtener info de cliente
        info_cliente = ""
        if len(v) > 10 and v[10]:
            cliente = obtener_cliente_por_cedula(v[10])
            if cliente:
                info_cliente = f"\nCLIENTE: {cliente[1]}\nCÉDULA: {cliente[2]}"
                if cliente[3]:
                    info_cliente += f"\nCELULAR: {cliente[3]}"

        detalle = f"""
{'='*60}
                420 SMOKING VIBES
                DETALLE DE FACTURA
{'='*60}

ID FACTURA: {v[1]}
FECHA: {v[2]}
HORA: {v[3] or "No registrada"}
EMPLEADO: {v[4]}
{info_cliente}

{'-'*60}
PRODUCTOS VENDIDOS:
{'-'*60}
{v[5]}

{'-'*60}
TOTAL: {formatear_moneda(v[6])}
{'-'*60}

PAGO:
  • Método: {v[8]}
  • Recibido: {formatear_moneda(v[9])}
  • Cambio: {formatear_moneda(v[7])}

ESTADO: {v[11].upper() if len(v) > 11 and v[11] else 'COMPLETADA'}
{'='*60}
"""

        ventana = tk.Toplevel(self)
        ventana.title(f"Detalle Factura {v[1]}")
        ventana.geometry("650x500")
        ventana.configure(bg="#f0f8ff")

        txt = tk.Text(ventana, width=80, height=26, font=("Consolas", 10))
        txt.pack(padx=10, pady=10)
        txt.insert("1.0", detalle)
        txt.config(state="disabled")

        btn_frame = tk.Frame(ventana)
        btn_frame.pack(pady=6)

        def imprimir():
            archivo = f"Facturas_Reimpresiones/Impresion_{id_factura}.txt"
            os.makedirs("Facturas_Reimpresiones", exist_ok=True)
            with open(archivo, "w", encoding="utf-8") as f:
                f.write(detalle)
            messagebox.showinfo("Impreso", f"Factura impresa en {archivo}")

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

        info_cliente = ""
        if len(v) > 10 and v[10]:
            cliente = obtener_cliente_por_cedula(v[10])
            if cliente:
                info_cliente = f"CLIENTE: {cliente[1]}\nCÉDULA: {cliente[2]}\n"

        with open(archivo, "w", encoding="utf-8") as f:
            f.write("=" * 60 + "\n")
            f.write("                420 SMOKING VIBES\n")
            f.write("              REIMPRESIÓN DE FACTURA\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"FACTURA N°: {id_factura}\n")
            f.write(f"Fecha Original: {v[2]}   Hora: {v[3] or 'N/A'}\n")
            f.write(
                f"Fecha Reimpresión: {formatear_fecha()}   Hora: {formatear_hora()}\n"
            )
            f.write(f"Empleado: {v[4]}\n\n")
            if info_cliente:
                f.write(info_cliente + "\n")
            f.write("-" * 60 + "\n")
            f.write("PRODUCTOS:\n")
            f.write("-" * 60 + "\n")
            f.write(f"{v[5]}\n")
            f.write("-" * 60 + "\n")
            f.write(f"TOTAL: {formatear_moneda(v[6])}\n")
            f.write("=" * 60 + "\n")
            f.write(f"Método de Pago: {v[8]}\n")
            f.write(f"Recibido: {formatear_moneda(v[9])}\n")
            f.write(f"Cambio: {formatear_moneda(v[7])}\n")
            f.write("=" * 60 + "\n")
            f.write("         ¡GRACIAS POR SU COMPRA!\n")
            f.write("            420 SMOKING VIBES\n")
            f.write("=" * 60 + "\n")
        messagebox.showinfo("Reimpresión", f"Factura reimpresa en:\n{archivo}")

    def reporte_dia(self):
        fecha = formatear_fecha()
        ventas = obtener_ventas()
        ventas_hoy = [v for v in ventas if v[2] == fecha]
        total = 0
        detalles = ""
        for v in ventas_hoy:
            try:
                total_val = float(v[6])
            except:
                total_val = 0
            detalles += f"- Factura {v[1]}: {formatear_moneda(total_val)}  ({v[4]})\n"
            total += total_val
        reporte = f"""
420 SMOKING VIBES
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
