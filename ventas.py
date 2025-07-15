import tkinter as tk
from tkinter import ttk, messagebox
from db import (obtener_producto_por_sku, actualizar_stock,
                obtener_cliente_por_cedula, guardar_venta, formatear_moneda)
import os

class VentasFrame(ttk.Frame):

    def __init__(self, parent, empleado=None):
        super().__init__(parent)
        self.parent = parent
        self.empleado = empleado
        self.productos_venta = []
        self.total = 0
        self.cliente_actual = None
        self._crear_interfaz()

    def _crear_interfaz(self):
        # Header
        header = tk.Frame(self, bg="#228b57")
        header.pack(fill="x", padx=0, pady=(0, 10))
        tk.Label(header,
                 text="💸 PUNTO DE VENTA",
                 bg="#228b57",
                 fg="white",
                 font=("Arial", 15, "bold")).pack(side="top", pady=2)
        tk.Label(header,
                 text=f"Empleado: {self.empleado}",
                 bg="#228b57",
                 fg="#b0ffb0",
                 font=("Arial", 11)).pack(side="top")

        # Main frame
        main_frame = tk.Frame(self, bg="#f0f8ff")
        main_frame.pack(fill="both", expand=True, padx=6, pady=4)

        # Input frame
        input_frame = tk.LabelFrame(main_frame,
                                    text="AGREGAR PRODUCTO",
                                    bg="#f0f8ff",
                                    font=("Arial", 11, "bold"))
        input_frame.pack(fill="x", padx=8, pady=6)
        row = tk.Frame(input_frame, bg="#f0f8ff")
        row.pack(pady=4, fill="x")
        tk.Label(row, text="SKU:", bg="#f0f8ff",
                 font=("Arial", 10, "bold")).pack(side="left", padx=(0, 2))
        self.entry_sku = tk.Entry(row, width=12, font=("Arial", 11))
        self.entry_sku.pack(side="left")
        tk.Label(row,
                 text="Cantidad:",
                 bg="#f0f8ff",
                 font=("Arial", 10, "bold")).pack(side="left", padx=5)
        self.entry_cant = tk.Entry(row, width=5, font=("Arial", 11))
        self.entry_cant.pack(side="left")
        self.entry_cant.insert(0, "1")
        tk.Button(row,
                  text="Agregar",
                  command=self.agregar_producto,
                  bg="#90ee90",
                  font=("Arial", 10, "bold")).pack(side="left", padx=5)
        tk.Button(row,
                  text="Limpiar",
                  command=self.limpiar_campos,
                  bg="#ffd700",
                  font=("Arial", 10, "bold")).pack(side="left", padx=3)
        self.lbl_producto_info = tk.Label(row,
                                          text="",
                                          bg="#f0f8ff",
                                          fg="#555",
                                          font=("Arial", 9))
        self.lbl_producto_info.pack(side="left", padx=7)

        # Cliente row
        row2 = tk.Frame(input_frame, bg="#f0f8ff")
        row2.pack(pady=3, fill="x")
        tk.Label(row2,
                 text="Cliente (Cédula):",
                 bg="#f0f8ff",
                 font=("Arial", 10, "bold")).pack(side="left", padx=(0, 2))
        self.entry_cliente = tk.Entry(row2, width=15, font=("Arial", 11))
        self.entry_cliente.pack(side="left")
        tk.Button(row2,
                  text="Buscar",
                  command=self.buscar_cliente,
                  bg="#87ceeb",
                  font=("Arial", 10)).pack(side="left", padx=4)
        self.lbl_cliente_info = tk.Label(row2,
                                         text="(Cliente opcional)",
                                         bg="#f0f8ff",
                                         font=("Arial", 9),
                                         fg="#888")
        self.lbl_cliente_info.pack(side="left", padx=8)

        self.entry_sku.bind('<Return>', lambda e: self.entry_cant.focus())
        self.entry_cant.bind('<Return>', lambda e: self.agregar_producto())

        # Productos tabla
        tabla_frame = tk.LabelFrame(main_frame,
                                    text="PRODUCTOS EN LA VENTA",
                                    bg="#f0f8ff",
                                    font=("Arial", 11, "bold"))
        tabla_frame.pack(fill="both", expand=True, padx=8, pady=5)
        tree_scroll = ttk.Scrollbar(tabla_frame)
        tree_scroll.pack(side="right", fill="y")
        cols = ("SKU", "Nombre", "Cantidad", "Precio Unit", "Subtotal")
        self.tree = ttk.Treeview(tabla_frame,
                                 columns=cols,
                                 show="headings",
                                 yscrollcommand=tree_scroll.set,
                                 height=7)
        for col, width in zip(cols, [85, 220, 70, 100, 100]):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width)
        self.tree.pack(side="left", fill="both", expand=True)
        tree_scroll.config(command=self.tree.yview)

        # Botones tabla
        row_b = tk.Frame(main_frame, bg="#f0f8ff")
        row_b.pack(pady=3)
        tk.Button(row_b,
                  text="Eliminar Producto",
                  command=self.eliminar_producto,
                  bg="#ff6b6b",
                  fg="white").pack(side="left", padx=5)
        tk.Button(row_b,
                  text="Vaciar Venta",
                  command=self.vaciar_venta,
                  bg="#ffd700").pack(side="left", padx=5)

        # Totales
        tot_frame = tk.LabelFrame(main_frame,
                                  text="TOTALES",
                                  bg="#f0f8ff",
                                  font=("Arial", 11, "bold"))
        tot_frame.pack(fill="x", padx=8, pady=5)
        self.lbl_items = tk.Label(tot_frame,
                                  text="Items: 0",
                                  font=("Arial", 11),
                                  bg="#f0f8ff",
                                  fg="#228b57")
        self.lbl_items.pack()
        self.lbl_total = tk.Label(tot_frame,
                                  text="TOTAL: $0",
                                  font=("Arial", 17, "bold"),
                                  bg="#f0f8ff",
                                  fg="#228b57")
        self.lbl_total.pack()

        # FINALIZAR VENTA
        fin_frame = tk.LabelFrame(main_frame,
                                  text="FINALIZAR VENTA",
                                  bg="#f0f8ff",
                                  font=("Arial", 11, "bold"))
        fin_frame.pack(fill="x", padx=8, pady=(8, 10))
        rowf = tk.Frame(fin_frame, bg="#f0f8ff")
        rowf.pack(pady=5)
        tk.Label(rowf,
                 text="Método:",
                 bg="#f0f8ff",
                 font=("Arial", 10, "bold")).pack(side="left", padx=(2, 2))
        self.combo_pago = ttk.Combobox(
            rowf,
            values=["Efectivo", "Transferencia", "Datáfono"],
            width=13,
            font=("Arial", 11))
        self.combo_pago.set("Efectivo")
        self.combo_pago.pack(side="left", padx=2)
        tk.Label(rowf,
                 text="Recibido:",
                 bg="#f0f8ff",
                 font=("Arial", 10, "bold")).pack(side="left", padx=(7, 2))
        self.entry_recibido = tk.Entry(rowf, width=12, font=("Arial", 11))
        self.entry_recibido.pack(side="left", padx=2)
        self.lbl_cambio = tk.Label(rowf,
                                   text="Cambio: $0",
                                   bg="#f0f8ff",
                                   font=("Arial", 12, "bold"),
                                   fg="green")
        self.lbl_cambio.pack(side="left", padx=18)

        self.combo_pago.bind("<<ComboboxSelected>>", self._on_pago_change)
        self.entry_recibido.bind("<KeyRelease>", self._actualizar_cambio)

        btnf = tk.Button(fin_frame,
                         text="FINALIZAR Y GUARDAR VENTA",
                         command=self.finalizar_venta,
                         bg="#32cd32",
                         fg="white",
                         font=("Arial", 13, "bold"),
                         width=32,
                         height=2)
        btnf.pack(pady=10)

        self.entry_sku.focus()

    # ------------ FUNCIONES PRINCIPALES ----------------

    def agregar_producto(self):
        sku = self.entry_sku.get().strip()
        cant = self.entry_cant.get().strip()
        if not sku:
            messagebox.showerror("Error", "Ingrese el código del producto")
            self.entry_sku.focus()
            return
        try:
            cant = int(cant)
            if cant <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Error", "Cantidad inválida. Debe ser un número mayor a 0")
            self.entry_cant.focus()
            return
        prod = obtener_producto_por_sku(sku)
        if not prod:
            messagebox.showerror("Error", f"Producto con SKU '{sku}' no existe")
            self.entry_sku.focus()
            return
        if prod[6] < cant:
            respuesta = messagebox.askyesno(
                "Stock insuficiente",
                f"Stock disponible: {prod[6]}\n¿Agregar solo la cantidad disponible?"
            )
            if respuesta:
                cant = prod[6]
            else:
                return
        if cant == 0:
            messagebox.showerror("Error", "No hay stock disponible para este producto")
            return
        for item in self.productos_venta:
            if item['sku'] == sku:
                nueva_cantidad = item['cantidad'] + cant
                if nueva_cantidad > prod[6]:
                    messagebox.showerror("Error", f"No hay suficiente stock. Máximo disponible: {prod[6]}")
                    return
                item['cantidad'] = nueva_cantidad
                self.actualizar_tabla()
                self.limpiar_campos()
                self.entry_sku.focus()
                return
        self.productos_venta.append({
            'sku': sku,
            'nombre': prod[1],
            'precio': prod[2],
            'cantidad': cant
        })
        self.actualizar_tabla()
        self.limpiar_campos()
        self.entry_sku.focus()

    def actualizar_tabla(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        subtotal = 0
        total_items = 0
        for item in self.productos_venta:
            subtotal_producto = item['cantidad'] * item['precio']
            subtotal += subtotal_producto
            total_items += item['cantidad']
            self.tree.insert("",
                             "end",
                             values=(item['sku'], item['nombre'],
                                     item['cantidad'],
                                     formatear_moneda(item['precio']),
                                     formatear_moneda(subtotal_producto)))
        self.total = subtotal
        self.lbl_items.config(text=f"Items: {total_items}")
        self.lbl_total.config(text=f"TOTAL: {formatear_moneda(self.total)}")
        self._actualizar_cambio()

    def limpiar_campos(self):
        self.entry_sku.delete(0, tk.END)
        self.entry_cant.delete(0, tk.END)
        self.entry_cant.insert(0, "1")
        self.lbl_producto_info.config(text="", fg="#666666")

    def eliminar_producto(self):
        seleccionado = self.tree.selection()
        if not seleccionado:
            messagebox.showwarning("Selecciona un producto", "Selecciona el producto a eliminar.")
            return
        item_values = self.tree.item(seleccionado[0])["values"]
        sku_seleccionado = str(item_values[0])
        self.productos_venta = [
            p for p in self.productos_venta
            if str(p['sku']) != sku_seleccionado
        ]
        self.actualizar_tabla()

    def vaciar_venta(self):
        if not self.productos_venta:
            messagebox.showinfo("Información", "No hay productos en la venta actual.")
            return
        if messagebox.askyesno("Confirmar", "¿Vaciar toda la venta actual?"):
            self.productos_venta.clear()
            self.actualizar_tabla()
            self.entry_cliente.delete(0, tk.END)
            self.lbl_cliente_info.config(text="(Cliente opcional)", fg="#888")
            self.cliente_actual = None
            self.entry_recibido.delete(0, tk.END)
            self.lbl_cambio.config(text="Cambio: $0", fg="green")
            self.combo_pago.set("Efectivo")
            self.entry_sku.focus()

    def buscar_cliente(self):
        cedula = self.entry_cliente.get().strip()
        if not cedula:
            self.lbl_cliente_info.config(text="(Cliente opcional)", fg="#888")
            self.cliente_actual = None
            return
        cliente = obtener_cliente_por_cedula(cedula)
        if cliente:
            self.cliente_actual = cliente
            self.lbl_cliente_info.config(
                text=f"✓ {cliente[1]} - {cliente[3] or 'Sin celular'}",
                fg="green")
        else:
            self.cliente_actual = None
            self.lbl_cliente_info.config(text="❌ Cliente no encontrado", fg="red")

    def _on_pago_change(self, event=None):
        metodo = self.combo_pago.get()
        if metodo in ["Transferencia", "Datáfono"]:
            self.entry_recibido.config(state="normal")
            self.entry_recibido.delete(0, tk.END)
            self.entry_recibido.insert(0, str(int(self.total)))
            self.entry_recibido.config(state="readonly")
        else:
            self.entry_recibido.config(state="normal")
            self.entry_recibido.delete(0, tk.END)
        self._actualizar_cambio()

    def _actualizar_cambio(self, event=None):
        try:
            recibido_str = self.entry_recibido.get().replace("$", "").replace(".", "").replace(",", "")
            recibido = float(recibido_str) if recibido_str else 0
        except:
            recibido = 0
        cambio = recibido - self.total
        if cambio < 0:
            self.lbl_cambio.config(text=f"FALTA: {formatear_moneda(abs(cambio))}", fg="red")
        else:
            self.lbl_cambio.config(text=f"Cambio: {formatear_moneda(cambio)}", fg="green")

    def finalizar_venta(self):
        if not self.productos_venta:
            messagebox.showerror("Error", "Agrega productos a la venta")
            return
        if not self.combo_pago.get():
            messagebox.showerror("Error", "Selecciona un método de pago")
            return
        try:
            recibido_str = self.entry_recibido.get().replace("$", "").replace(".", "").replace(",", "")
            recibido = float(recibido_str)
        except:
            messagebox.showerror("Error", "Valor recibido inválido")
            return
        if recibido < self.total:
            messagebox.showerror("Error", "El valor recibido es menor al total")
            return

        try:
            cambio = recibido - self.total
            productos_str = "\n".join([
                f"{x['sku']} - {x['nombre']} x{x['cantidad']} = {formatear_moneda(x['cantidad'] * x['precio'])}"
                for x in self.productos_venta
            ])
            for x in self.productos_venta:
                actualizar_stock(x['sku'], x['cantidad'])
            cliente_cedula = self.entry_cliente.get().strip() or None

            # ORDEN DE LOS ARGUMENTOS EN guardar_venta:
            # productos_str, total, metodo_pago, valor_pagado, cambio, empleado, cliente_cedula
            id_factura = guardar_venta(
                productos_str,
                self.total,
                self.combo_pago.get(),
                recibido,
                cambio,
                self.empleado,
                cliente_cedula
            )

            self._generar_factura(id_factura, recibido, cambio)
            messagebox.showinfo("Venta Exitosa", f"Venta guardada correctamente\nFactura: {id_factura}")
            self.vaciar_venta()
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar la venta: {e}")

    def _generar_factura(self, id_factura, recibido, cambio):
        carpeta = "Facturas"
        os.makedirs(carpeta, exist_ok=True)
        archivo = os.path.join(carpeta, f"{id_factura}.txt")
        with open(archivo, "w", encoding="utf-8") as f:
            f.write("=" * 54 + "\n")
            f.write("420 Smoking Vibes\n")
            f.write("Cel: 3126251302\n")
            f.write("Calle 1 #29 - 438\n")
            f.write("=" * 54 + "\n")
            f.write(f"ID FACTURA: {id_factura}\n")
            f.write(f"EMPLEADO: {self.empleado}\n")
            if self.cliente_actual:
                f.write(f"CLIENTE: {self.cliente_actual[1]} | CÉDULA: {self.cliente_actual[2]}\n")
            f.write("-" * 54 + "\n")
            for item in self.productos_venta:
                f.write(f"{item['sku']} - {item['nombre']} x{item['cantidad']} = {formatear_moneda(item['cantidad'] * item['precio'])}\n")
            f.write("-" * 54 + "\n")
            f.write(f"TOTAL: {formatear_moneda(self.total)}\n")
            f.write(f"RECIBIDO: {formatear_moneda(recibido)}\n")
            f.write(f"CAMBIO: {formatear_moneda(cambio)}\n")
            f.write(f"MÉTODO DE PAGO: {self.combo_pago.get()}\n")
            f.write("=" * 54 + "\n")
            f.write("¡GRACIAS POR TU COMPRA Y POR APOYAR EL PODER DE LA BUENA VIBRA! 😎✨\n")
            f.write("=" * 54 + "\n")
