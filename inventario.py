import tkinter as tk
from tkinter import ttk, messagebox
from db import (obtener_productos, obtener_producto_por_sku, agregar_producto,
                editar_producto, eliminar_producto, formatear_moneda)


class InventarioFrame(ttk.Frame):

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.sku_original = None
        self.crear_interfaz()

    def crear_interfaz(self):
        # Header
        header_frame = tk.Frame(self, bg="#2e8b57", height=40)
        header_frame.pack(fill="x", pady=(0, 10))
        header_frame.pack_propagate(False)

        tk.Label(header_frame,
                 text="📦 INVENTARIO DE PRODUCTOS",
                 bg="#2e8b57",
                 fg="white",
                 font=('Arial', 14, 'bold')).pack(expand=True)

        # Frame principal con borde
        main_frame = tk.Frame(self, bg="#f0f8ff", relief="groove", bd=2)
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Formulario
        form_frame = tk.LabelFrame(main_frame,
                                   text="Agregar/Editar Producto",
                                   font=("Arial", 11, "bold"),
                                   bg="#f0f8ff")
        form_frame.pack(fill="x", padx=10, pady=10)

        # Primera fila del formulario
        row1 = tk.Frame(form_frame, bg="#f0f8ff")
        row1.pack(pady=5)

        tk.Label(row1, text="SKU:", bg="#f0f8ff", width=8).pack(side="left",
                                                                padx=2)
        self.entry_sku = tk.Entry(row1, width=15, font=("Arial", 10))
        self.entry_sku.pack(side="left", padx=5)

        tk.Label(row1, text="Nombre:", bg="#f0f8ff", width=8).pack(side="left",
                                                                   padx=2)
        self.entry_nombre = tk.Entry(row1, width=30, font=("Arial", 10))
        self.entry_nombre.pack(side="left", padx=5)

        tk.Label(row1, text="Precio:", bg="#f0f8ff", width=8).pack(side="left",
                                                                   padx=2)
        self.entry_precio = tk.Entry(row1, width=12, font=("Arial", 10))
        self.entry_precio.pack(side="left", padx=5)

        # Segunda fila del formulario
        row2 = tk.Frame(form_frame, bg="#f0f8ff")
        row2.pack(pady=5)

        tk.Label(row2, text="Stock:", bg="#f0f8ff", width=8).pack(side="left",
                                                                  padx=2)
        self.entry_stock = tk.Entry(row2, width=10, font=("Arial", 10))
        self.entry_stock.pack(side="left", padx=5)

        tk.Label(row2, text="Mínimo:", bg="#f0f8ff", width=8).pack(side="left",
                                                                   padx=2)
        self.entry_stock_min = tk.Entry(row2, width=10, font=("Arial", 10))
        self.entry_stock_min.pack(side="left", padx=5)
        self.entry_stock_min.insert(0, "5")

        # Botones del formulario
        btn_frame = tk.Frame(form_frame, bg="#f0f8ff")
        btn_frame.pack(pady=10)

        tk.Button(btn_frame,
                  text="✅ Guardar",
                  command=self.agregar_actualizar_producto,
                  bg="#90ee90",
                  font=("Arial", 10, "bold"),
                  width=12).pack(side="left", padx=5)

        tk.Button(btn_frame,
                  text="🔄 Limpiar",
                  command=self.limpiar_campos,
                  bg="#fffacd",
                  font=("Arial", 10, "bold"),
                  width=12).pack(side="left", padx=5)

        tk.Button(btn_frame,
                  text="🔍 Buscar SKU",
                  command=self.buscar_por_sku,
                  bg="#87ceeb",
                  font=("Arial", 10, "bold"),
                  width=12).pack(side="left", padx=5)

        # Frame de búsqueda
        search_frame = tk.Frame(main_frame, bg="#f0f8ff")
        search_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(search_frame, text="🔍 Filtrar:",
                 bg="#f0f8ff").pack(side="left", padx=5)
        self.entry_filtro = tk.Entry(search_frame,
                                     width=30,
                                     font=("Arial", 10))
        self.entry_filtro.pack(side="left", padx=5)
        self.entry_filtro.bind('<KeyRelease>', self.filtrar_productos)

        self.lbl_info = tk.Label(search_frame,
                                 text="",
                                 bg="#f0f8ff",
                                 font=("Arial", 9))
        self.lbl_info.pack(side="right", padx=10)

        # Tabla de productos con scrollbar
        table_frame = tk.Frame(main_frame, bg="#f0f8ff")
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side="right", fill="y")

        # Treeview
        cols = ("SKU", "Producto", "Precio", "Stock", "Mínimo", "Estado")
        self.tree = ttk.Treeview(table_frame,
                                 columns=cols,
                                 show="headings",
                                 height=13,
                                 yscrollcommand=scrollbar.set)

        # Configurar columnas
        self.tree.heading("SKU", text="SKU")
        self.tree.heading("Producto", text="Producto")
        self.tree.heading("Precio", text="Precio")
        self.tree.heading("Stock", text="Stock")
        self.tree.heading("Mínimo", text="Mínimo")
        self.tree.heading("Estado", text="Estado")

        self.tree.column("SKU", width=100)
        self.tree.column("Producto", width=250)
        self.tree.column("Precio", width=100)
        self.tree.column("Stock", width=80)
        self.tree.column("Mínimo", width=80)
        self.tree.column("Estado", width=100)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.tree.yview)

        # Configurar tags para colores
        self.tree.tag_configure('stock_bajo', background='#ffcccc')
        self.tree.tag_configure('stock_critico',
                                background='#ff7272',
                                foreground='white')
        self.tree.tag_configure('stock_ok', background='#ccffcc')

        self.tree.bind("<Double-1>", self.on_tree_select)

        # Frame de botones inferiores
        bottom_frame = tk.Frame(main_frame, bg="#f0f8ff")
        bottom_frame.pack(fill="x", padx=10, pady=10)

        tk.Button(bottom_frame,
                  text="🗑️ Eliminar",
                  command=self.eliminar_producto,
                  bg="#ff7272",
                  font=("Arial", 10, "bold"),
                  width=15).pack(side="left", padx=5)

        tk.Button(bottom_frame,
                  text="📊 Reporte Stock",
                  command=self.generar_reporte_stock,
                  bg="#ffd700",
                  font=("Arial", 10, "bold"),
                  width=15).pack(side="left", padx=5)

        tk.Button(bottom_frame,
                  text="🔄 Actualizar",
                  command=self.cargar_inventario,
                  bg="#87ceeb",
                  font=("Arial", 10, "bold"),
                  width=15).pack(side="left", padx=5)

        # Cargar inventario inicial
        self.cargar_inventario()

        # Atajos de teclado
        self.bind_all('<Control-n>', lambda e: self.limpiar_campos())
        self.bind_all('<Control-s>',
                      lambda e: self.agregar_actualizar_producto())
        self.bind_all('<F5>', lambda e: self.cargar_inventario())

    def cargar_inventario(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        productos = obtener_productos()
        total_productos = len(productos)
        stock_bajo = 0
        stock_critico = 0

        for p in productos:
            sku, nombre, precio, stock_inicial, fecha, salidas, stock_actual, stock_minimo = p

            # Determinar estado y tag
            if stock_actual == 0:
                estado = "⚠️ AGOTADO"
                tag = 'stock_critico'
                stock_critico += 1
            elif stock_actual < stock_minimo:
                estado = "⚠️ BAJO"
                tag = 'stock_bajo'
                stock_bajo += 1
            else:
                estado = "✅ OK"
                tag = 'stock_ok'

            self.tree.insert("",
                             "end",
                             values=(sku, nombre, formatear_moneda(precio),
                                     stock_actual, stock_minimo, estado),
                             tags=(tag, ))

        # Actualizar información
        info = f"Total: {total_productos} | Stock Bajo: {stock_bajo} | Agotados: {stock_critico}"
        self.lbl_info.config(text=info)

    def limpiar_campos(self):
        for entry in [
                self.entry_sku, self.entry_nombre, self.entry_precio,
                self.entry_stock, self.entry_stock_min
        ]:
            entry.delete(0, tk.END)
        self.entry_stock_min.insert(0, "5")
        self.sku_original = None
        self.entry_sku.focus()

    def validar_datos(self):
        """Valida los datos del formulario"""
        sku = self.entry_sku.get().strip()
        nombre = self.entry_nombre.get().strip()

        if not sku or not nombre:
            messagebox.showerror("Error", "SKU y nombre son obligatorios")
            return None

        try:
            precio = float(self.entry_precio.get().replace("$", "").replace(
                ".", "").replace(",", "."))
            stock = int(self.entry_stock.get())
            stock_min = int(self.entry_stock_min.get())
        except ValueError:
            messagebox.showerror(
                "Error", "Precio, stock y mínimo deben ser números válidos")
            return None

        if precio <= 0:
            messagebox.showerror("Error", "El precio debe ser mayor a 0")
            return None

        if stock < 0:
            messagebox.showerror("Error", "El stock no puede ser negativo")
            return None

        if stock_min < 0:
            messagebox.showerror("Error",
                                 "El stock mínimo no puede ser negativo")
            return None

        return sku, nombre, precio, stock, stock_min

    def agregar_actualizar_producto(self):
        datos = self.validar_datos()
        if not datos:
            return

        sku, nombre, precio, stock, stock_min = datos

        if self.sku_original:  # Edición
            try:
                editar_producto(self.sku_original, sku, nombre, precio, stock,
                                stock_min)
                messagebox.showinfo(
                    "Actualizado", f"Producto {sku} actualizado correctamente")
            except Exception as e:
                messagebox.showerror("Error", f"Error al actualizar: {e}")
        else:  # Nuevo producto
            try:
                agregar_producto(sku, nombre, precio, stock, stock_min)
                messagebox.showinfo("Agregado",
                                    f"Producto {sku} agregado correctamente")
            except Exception as e:
                if "ya existe" in str(e):
                    messagebox.showerror(
                        "Error", f"El SKU {sku} ya existe en el inventario")
                else:
                    messagebox.showerror("Error", f"Error al agregar: {e}")

        self.cargar_inventario()
        self.limpiar_campos()

    def on_tree_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return

        values = self.tree.item(selected[0])["values"]
        self.limpiar_campos()

        # Cargar datos en el formulario
        self.entry_sku.insert(0, values[0])
        self.entry_nombre.insert(0, values[1])
        self.entry_precio.insert(
            0,
            str(values[2]).replace("$", "").replace(".", ""))
        self.entry_stock.insert(0, values[3])
        self.entry_stock_min.insert(0, values[4])

        self.sku_original = values[0]

    def buscar_por_sku(self):
        sku = self.entry_sku.get().strip()
        if not sku:
            messagebox.showwarning("Advertencia", "Ingrese un SKU para buscar")
            return

        producto = obtener_producto_por_sku(sku)
        if producto:
            self.limpiar_campos()
            self.entry_sku.insert(0, producto[0])
            self.entry_nombre.insert(0, producto[1])
            self.entry_precio.insert(0, str(producto[2]))
            self.entry_stock.insert(0, producto[6])  # stock_actual
            self.entry_stock_min.insert(0, producto[7])  # stock_minimo
            self.sku_original = producto[0]
            messagebox.showinfo("Encontrado",
                                f"Producto {producto[1]} encontrado")
        else:
            messagebox.showinfo("No encontrado",
                                f"No se encontró el producto con SKU: {sku}")

    def filtrar_productos(self, event=None):
        filtro = self.entry_filtro.get().strip().lower()

        for item in self.tree.get_children():
            self.tree.delete(item)

        productos = obtener_productos()
        resultados = 0

        for p in productos:
            sku, nombre, precio, stock_inicial, fecha, salidas, stock_actual, stock_minimo = p

            # Buscar en SKU y nombre
            if filtro in sku.lower() or filtro in nombre.lower():
                # Determinar estado y tag
                if stock_actual == 0:
                    estado = "⚠️ AGOTADO"
                    tag = 'stock_critico'
                elif stock_actual < stock_minimo:
                    estado = "⚠️ BAJO"
                    tag = 'stock_bajo'
                else:
                    estado = "✅ OK"
                    tag = 'stock_ok'

                self.tree.insert("",
                                 "end",
                                 values=(sku, nombre, formatear_moneda(precio),
                                         stock_actual, stock_minimo, estado),
                                 tags=(tag, ))
                resultados += 1

        self.lbl_info.config(
            text=f"Mostrando {resultados} de {len(productos)} productos")

    def eliminar_producto(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selecciona",
                                   "Selecciona un producto para eliminar")
            return

        values = self.tree.item(selected[0])["values"]
        sku = values[0]
        nombre = values[1]

        if messagebox.askyesno(
                "Confirmar eliminación",
                f"¿Está seguro de eliminar el producto?\n\nSKU: {sku}\n{nombre}",
                icon="warning"):
            try:
                eliminar_producto(sku)
                self.cargar_inventario()
                self.limpiar_campos()
                messagebox.showinfo("Eliminado",
                                    f"Producto {sku} eliminado correctamente")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar: {e}")

    def generar_reporte_stock(self):
        """Genera un reporte del estado del inventario"""
        productos = obtener_productos()

        if not productos:
            messagebox.showinfo("Reporte", "No hay productos en el inventario")
            return

        # Clasificar productos
        stock_ok = []
        stock_bajo = []
        stock_agotado = []
        valor_total = 0

        for p in productos:
            sku, nombre, precio, stock_inicial, fecha, salidas, stock_actual, stock_minimo = p
            valor_producto = precio * stock_actual
            valor_total += valor_producto

            producto_info = {
                'sku': sku,
                'nombre': nombre,
                'precio': precio,
                'stock': stock_actual,
                'minimo': stock_minimo,
                'valor': valor_producto
            }

            if stock_actual == 0:
                stock_agotado.append(producto_info)
            elif stock_actual < stock_minimo:
                stock_bajo.append(producto_info)
            else:
                stock_ok.append(producto_info)

        # Crear ventana de reporte
        reporte_window = tk.Toplevel(self)
        reporte_window.title("📊 Reporte de Inventario")
        reporte_window.geometry("700x600")
        reporte_window.configure(bg="#f0f8ff")

        # Header
        header = tk.Frame(reporte_window, bg="#2e8b57", height=50)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(header,
                 text="REPORTE DE INVENTARIO",
                 font=("Arial", 16, "bold"),
                 bg="#2e8b57",
                 fg="white").pack(expand=True)

        # Frame para el contenido
        content_frame = tk.Frame(reporte_window, bg="#f0f8ff")
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Text widget con scrollbar
        text_frame = tk.Frame(content_frame)
        text_frame.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side="right", fill="y")

        text_widget = tk.Text(text_frame,
                              wrap="word",
                              font=("Consolas", 10),
                              yscrollcommand=scrollbar.set)
        text_widget.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=text_widget.yview)

        # Generar contenido del reporte
        from db import obtener_fecha, obtener_hora

        reporte = f"""
{'='*60}
                 REPORTE DE INVENTARIO
                 420 SMOKING VIBES
{'='*60}

Fecha: {obtener_fecha()}
Hora: {obtener_hora()}

RESUMEN GENERAL:
----------------
Total de productos: {len(productos)}
Productos con stock OK: {len(stock_ok)}
Productos con stock bajo: {len(stock_bajo)}
Productos agotados: {len(stock_agotado)}
Valor total del inventario: {formatear_moneda(valor_total)}

{'='*60}

PRODUCTOS AGOTADOS ({len(stock_agotado)}):
"""

        if stock_agotado:
            for p in stock_agotado:
                reporte += f"\n  • {p['sku']:10} | {p['nombre']:30} | Mín: {p['minimo']}"
        else:
            reporte += "\n  (No hay productos agotados)"

        reporte += f"\n\n{'='*60}\n\nPRODUCTOS CON STOCK BAJO ({len(stock_bajo)}):\n"

        if stock_bajo:
            for p in stock_bajo:
                reporte += f"\n  • {p['sku']:10} | {p['nombre']:30}"
                reporte += f"\n    Stock: {p['stock']} | Mínimo: {p['minimo']} | Faltan: {p['minimo'] - p['stock']}"
        else:
            reporte += "\n  (No hay productos con stock bajo)"

        reporte += f"\n\n{'='*60}\n\nPRODUCTOS CON STOCK OK ({len(stock_ok)}):\n"

        for p in stock_ok[:10]:  # Mostrar solo los primeros 10
            reporte += f"\n  • {p['sku']:10} | {p['nombre']:30} | Stock: {p['stock']}"

        if len(stock_ok) > 10:
            reporte += f"\n  ... y {len(stock_ok) - 10} productos más"

        reporte += f"\n\n{'='*60}\n"

        # Insertar reporte
        text_widget.insert("1.0", reporte)
        text_widget.config(state="disabled")

        # Botones
        btn_frame = tk.Frame(reporte_window, bg="#f0f8ff")
        btn_frame.pack(pady=10)

        def guardar_reporte():
            import os
            carpeta = "Reportes_Inventario"
            os.makedirs(carpeta, exist_ok=True)

            archivo = os.path.join(
                carpeta,
                f"Reporte_Inventario_{obtener_fecha().replace('/', '_')}.txt")

            with open(archivo, "w", encoding="utf-8") as f:
                f.write(reporte)

            messagebox.showinfo("Guardado", f"Reporte guardado en:\n{archivo}")

        tk.Button(btn_frame,
                  text="💾 Guardar",
                  command=guardar_reporte,
                  bg="#90ee90",
                  font=("Arial", 10, "bold"),
                  width=12).pack(side="left", padx=5)

        tk.Button(btn_frame,
                  text="❌ Cerrar",
                  command=reporte_window.destroy,
                  bg="#ff7272",
                  font=("Arial", 10, "bold"),
                  width=12).pack(side="left", padx=5)
