import tkinter as tk
from tkinter import ttk, messagebox
from db import agregar_compra, obtener_compras, formatear_fecha, formatear_hora, formatear_moneda

class ComprasFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill="both", expand=True)
        self.config(padding=12)

        # --- Formulario de Nueva Compra ---
        frm_form = tk.LabelFrame(self, text="Registrar Nueva Compra", bg="#f7ffe5")
        frm_form.pack(fill="x", padx=8, pady=6)

        # Proveedor
        tk.Label(frm_form, text="Proveedor:", bg="#f7ffe5").grid(row=0, column=0, sticky="e", padx=4, pady=2)
        self.entry_proveedor = tk.Entry(frm_form, width=25)
        self.entry_proveedor.grid(row=0, column=1, padx=4, pady=2)

        # Número de Factura
        tk.Label(frm_form, text="Factura/Soporte:", bg="#f7ffe5").grid(row=0, column=2, sticky="e", padx=4, pady=2)
        self.entry_factura = tk.Entry(frm_form, width=20)
        self.entry_factura.grid(row=0, column=3, padx=4, pady=2)

        # Método de pago
        tk.Label(frm_form, text="Método de Pago:", bg="#f7ffe5").grid(row=1, column=0, sticky="e", padx=4, pady=2)
        self.metodo_pago_var = tk.StringVar()
        cbx_metodo = ttk.Combobox(frm_form, textvariable=self.metodo_pago_var, state="readonly", width=20)
        cbx_metodo["values"] = ("Efectivo", "Transferencia", "Tarjeta", "Otro")
        cbx_metodo.grid(row=1, column=1, padx=4, pady=2)
        cbx_metodo.current(0)

        # Productos comprados
        tk.Label(frm_form, text="Productos Comprados:", bg="#f7ffe5").grid(row=1, column=2, sticky="e", padx=4, pady=2)
        self.entry_productos = tk.Entry(frm_form, width=40)
        self.entry_productos.grid(row=1, column=3, padx=4, pady=2)

        # Valor Total
        tk.Label(frm_form, text="Valor Total:", bg="#f7ffe5").grid(row=2, column=0, sticky="e", padx=4, pady=2)
        self.entry_valor = tk.Entry(frm_form, width=16)
        self.entry_valor.grid(row=2, column=1, padx=4, pady=2)

        # Botón Guardar Compra
        tk.Button(frm_form, text="Registrar Compra", bg="#32cd32", fg="white", font=("Arial", 11, "bold"),
                  command=self.registrar_compra).grid(row=2, column=3, padx=10, pady=4, sticky="e")

        # --- Tabla de compras ---
        frm_tabla = tk.LabelFrame(self, text="Historial de Compras", bg="#f7ffe5")
        frm_tabla.pack(fill="both", expand=True, padx=8, pady=6)

        cols = ("Fecha", "Hora", "Proveedor", "Factura", "Productos", "Método de Pago", "Valor Total")
        self.tree = ttk.Treeview(frm_tabla, columns=cols, show="headings", height=10)
        for col in cols:
            self.tree.heading(col, text=col)
            if col == "Productos":
                self.tree.column(col, width=180)
            elif col == "Proveedor":
                self.tree.column(col, width=110)
            elif col == "Factura":
                self.tree.column(col, width=100)
            elif col == "Valor Total":
                self.tree.column(col, width=90, anchor="e")
            else:
                self.tree.column(col, width=95, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)

        self.cargar_compras()

    def registrar_compra(self):
        proveedor = self.entry_proveedor.get().strip()
        factura = self.entry_factura.get().strip()
        metodo_pago = self.metodo_pago_var.get()
        productos = self.entry_productos.get().strip()
        valor = self.entry_valor.get().strip()

        if not proveedor or not productos or not valor:
            messagebox.showwarning("Faltan Datos", "Por favor completa todos los campos requeridos.")
            return
        try:
            valor_float = float(valor.replace(".", "").replace(",", ""))
        except Exception:
            messagebox.showerror("Error", "Valor total inválido.")
            return

        agregar_compra(
            formatear_fecha(),
            formatear_hora(),
            metodo_pago,
            proveedor,
            factura,
            productos,
            valor_float
        )
        messagebox.showinfo("Compra registrada", "La compra fue registrada correctamente.")
        self.limpiar_campos()
        self.cargar_compras()

    def limpiar_campos(self):
        self.entry_proveedor.delete(0, tk.END)
        self.entry_factura.delete(0, tk.END)
        self.metodo_pago_var.set("Efectivo")
        self.entry_productos.delete(0, tk.END)
        self.entry_valor.delete(0, tk.END)

    def cargar_compras(self):
        self.tree.delete(*self.tree.get_children())
        compras = obtener_compras()
        for c in compras:
            # c: (id, fecha, hora, metodo_pago, proveedor, factura, productos, valor_total)
            self.tree.insert(
                "", "end",
                values=(
                    c[1], c[2], c[4], c[5], c[6], c[3], formatear_moneda(c[7])
                )
            )
