import tkinter as tk
from tkinter import messagebox, ttk
from db import obtener_clientes, agregar_cliente, editar_cliente, eliminar_cliente, obtener_cliente_por_cedula


class GestionClientes:

    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Gestión de Clientes")
        self.window.geometry("900x500")
        self.window.configure(bg="#f0f8ff")

        # Centrar ventana
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() //
             2) - (self.window.winfo_width() // 2)
        y = (self.window.winfo_screenheight() //
             2) - (self.window.winfo_height() // 2)
        self.window.geometry(f"+{x}+{y}")

        self.cedula_original = None
        self.crear_interfaz()
        self.cargar_clientes()

    def crear_interfaz(self):
        # Header
        header_frame = tk.Frame(self.window, bg="#2e8b57", height=50)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)

        tk.Label(header_frame,
                 text="👥 GESTIÓN DE CLIENTES",
                 font=("Arial", 16, "bold"),
                 bg="#2e8b57",
                 fg="white").pack(expand=True)

        # Frame de formulario
        form_frame = tk.LabelFrame(self.window,
                                   text="Datos del Cliente",
                                   font=("Arial", 11, "bold"),
                                   bg="#f0f8ff")
        form_frame.pack(pady=10, padx=20, fill="x")

        row1 = tk.Frame(form_frame, bg="#f0f8ff")
        row1.pack(pady=5)

        tk.Label(row1, text="Nombre:", bg="#f0f8ff",
                 width=10).pack(side="left", padx=5)
        self.entry_nombre = tk.Entry(row1, width=25, font=("Arial", 10))
        self.entry_nombre.pack(side="left", padx=5)

        tk.Label(row1, text="Cédula:", bg="#f0f8ff",
                 width=10).pack(side="left", padx=5)
        self.entry_cedula = tk.Entry(row1, width=15, font=("Arial", 10))
        self.entry_cedula.pack(side="left", padx=5)

        tk.Label(row1, text="Celular:", bg="#f0f8ff",
                 width=10).pack(side="left", padx=5)
        self.entry_celular = tk.Entry(row1, width=15, font=("Arial", 10))
        self.entry_celular.pack(side="left", padx=5)

        tk.Label(row1, text="Correo:", bg="#f0f8ff",
                 width=10).pack(side="left", padx=5)
        self.entry_correo = tk.Entry(row1, width=25, font=("Arial", 10))
        self.entry_correo.pack(side="left", padx=5)

        btn_frame = tk.Frame(form_frame, bg="#f0f8ff")
        btn_frame.pack(pady=10)

        tk.Button(btn_frame,
                  text="➕ Agregar",
                  command=self.agregar_cliente,
                  bg='#90ee90',
                  font=('Arial', 10, 'bold'),
                  width=12).pack(side="left", padx=5)
        tk.Button(btn_frame,
                  text="💾 Actualizar",
                  command=self.actualizar_cliente,
                  bg='#87ceeb',
                  font=('Arial', 10, 'bold'),
                  width=12).pack(side="left", padx=5)
        tk.Button(btn_frame,
                  text="🔄 Limpiar",
                  command=self.limpiar_campos,
                  bg='#fffacd',
                  font=('Arial', 10, 'bold'),
                  width=12).pack(side="left", padx=5)

        # Tabla de clientes
        table_frame = tk.Frame(self.window, bg="#f0f8ff")
        table_frame.pack(pady=5, padx=20, fill="both", expand=True)
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side="right", fill="y")

        cols = ("ID", "Nombre", "Cédula", "Celular", "Correo",
                "Fecha Registro")
        self.tree = ttk.Treeview(table_frame,
                                 columns=cols,
                                 show='headings',
                                 height=12,
                                 yscrollcommand=scrollbar.set)
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=140 if col != "ID" else 50)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.tree.yview)
        self.tree.bind("<Double-1>", self.on_tree_select)

        # Frame de botones inferiores
        bottom_frame = tk.Frame(self.window, bg="#f0f8ff")
        bottom_frame.pack(pady=10)
        tk.Button(bottom_frame,
                  text="🗑️ Eliminar",
                  command=self.eliminar_cliente,
                  bg='#ff7272',
                  font=('Arial', 10, 'bold'),
                  width=12).pack(side="left", padx=5)
        tk.Button(bottom_frame,
                  text="📊 Estadísticas",
                  command=self.mostrar_estadisticas,
                  bg='#ffd700',
                  font=('Arial', 10, 'bold'),
                  width=12).pack(side="left", padx=5)
        tk.Button(bottom_frame,
                  text="❌ Cerrar",
                  command=self.window.destroy,
                  bg='#dcdcdc',
                  font=('Arial', 10, 'bold'),
                  width=12).pack(side="left", padx=5)

    def agregar_cliente(self):
        nombre = self.entry_nombre.get().strip()
        cedula = self.entry_cedula.get().strip()
        celular = self.entry_celular.get().strip()
        correo = self.entry_correo.get().strip()
        if not nombre or not cedula:
            messagebox.showerror("Error",
                                 "Nombre y cédula son obligatorios",
                                 parent=self.window)
            return
        if not cedula.isdigit():
            messagebox.showerror("Error",
                                 "La cédula debe contener solo números",
                                 parent=self.window)
            return
        if celular and not celular.replace(" ", "").replace("-", "").isdigit():
            messagebox.showerror("Error",
                                 "El celular debe contener solo números",
                                 parent=self.window)
            return
        try:
            agregar_cliente(nombre.upper(), cedula, celular, correo)
            messagebox.showinfo("Éxito",
                                f"Cliente {nombre} agregado correctamente",
                                parent=self.window)
            self.cargar_clientes()
            self.limpiar_campos()
            self.entry_nombre.focus()
        except Exception as e:
            if "ya existe" in str(e):
                messagebox.showerror(
                    "Error",
                    f"Ya existe un cliente con la cédula {cedula}",
                    parent=self.window)
            else:
                messagebox.showerror("Error",
                                     f"Error al agregar cliente: {e}",
                                     parent=self.window)

    def actualizar_cliente(self):
        if not self.cedula_original:
            messagebox.showwarning("Advertencia",
                                   "Selecciona un cliente para actualizar",
                                   parent=self.window)
            return
        nombre = self.entry_nombre.get().strip()
        cedula = self.entry_cedula.get().strip()
        celular = self.entry_celular.get().strip()
        correo = self.entry_correo.get().strip()
        if not nombre or not cedula:
            messagebox.showerror("Error",
                                 "Nombre y cédula son obligatorios",
                                 parent=self.window)
            return
        try:
            editar_cliente(self.cedula_original, nombre.upper(), cedula,
                           celular, correo)
            messagebox.showinfo("Éxito",
                                "Cliente actualizado correctamente",
                                parent=self.window)
            self.cargar_clientes()
            self.limpiar_campos()
        except Exception as e:
            messagebox.showerror("Error",
                                 f"Error al actualizar cliente: {e}",
                                 parent=self.window)

    def eliminar_cliente(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia",
                                   "Selecciona un cliente para eliminar",
                                   parent=self.window)
            return
        values = self.tree.item(selected[0])["values"]
        nombre = values[1]
        cedula = values[2]
        if messagebox.askyesno(
                "Confirmar",
                f"¿Está seguro de eliminar al cliente?\n\n{nombre}\nCédula: {cedula}",
                parent=self.window):
            try:
                eliminar_cliente(cedula)
                messagebox.showinfo("Éxito",
                                    "Cliente eliminado correctamente",
                                    parent=self.window)
                self.cargar_clientes()
                self.limpiar_campos()
            except Exception as e:
                messagebox.showerror("Error",
                                     f"Error al eliminar cliente: {e}",
                                     parent=self.window)

    def cargar_clientes(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        clientes = obtener_clientes()
        for c in clientes:
            self.tree.insert("", "end", values=c)

    def on_tree_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0])["values"]
        self.limpiar_campos()
        self.entry_nombre.insert(0, values[1])
        self.entry_cedula.insert(0, values[2])
        self.entry_celular.insert(0, values[3] or "")
        self.entry_correo.insert(0, values[4] or "")
        self.cedula_original = values[2]

    def limpiar_campos(self):
        self.entry_nombre.delete(0, tk.END)
        self.entry_cedula.delete(0, tk.END)
        self.entry_celular.delete(0, tk.END)
        self.entry_correo.delete(0, tk.END)
        self.cedula_original = None
        self.entry_nombre.focus()

    def mostrar_estadisticas(self):
        clientes = obtener_clientes()
        if not clientes:
            messagebox.showinfo("Estadísticas",
                                "No hay clientes registrados",
                                parent=self.window)
            return
        con_celular = sum(1 for c in clientes if c[3])
        con_correo = sum(1 for c in clientes if c[4])
        from collections import defaultdict
        from datetime import datetime
        registros_por_mes = defaultdict(int)
        for c in clientes:
            if c[5]:  # Fecha registro
                try:
                    fecha = datetime.strptime(c[5], "%d/%m/%Y")
                    mes_año = fecha.strftime("%B %Y")
                    registros_por_mes[mes_año] += 1
                except:
                    pass
        estadisticas = f"""📊 ESTADÍSTICAS DE CLIENTES

Total de clientes: {len(clientes)}
Clientes con celular: {con_celular} ({con_celular/len(clientes)*100:.1f}%)
Clientes con correo: {con_correo} ({con_correo/len(clientes)*100:.1f}%)
Clientes sin celular: {len(clientes) - con_celular} ({(len(clientes) - con_celular)/len(clientes)*100:.1f}%)
Clientes sin correo: {len(clientes) - con_correo} ({(len(clientes) - con_correo)/len(clientes)*100:.1f}%)

Registros por mes:
"""
        for mes, cantidad in sorted(registros_por_mes.items()):
            estadisticas += f"  • {mes}: {cantidad} clientes\n"
        stats_window = tk.Toplevel(self.window)
        stats_window.title("Estadísticas de Clientes")
        stats_window.geometry("400x350")
        stats_window.configure(bg="#f0f8ff")
        text_widget = tk.Text(stats_window, wrap="word", font=("Consolas", 10))
        text_widget.pack(fill="both", expand=True, padx=10, pady=10)
        text_widget.insert("1.0", estadisticas)
        text_widget.config(state="disabled")
        tk.Button(stats_window,
                  text="Cerrar",
                  command=stats_window.destroy,
                  bg="#90ee90",
                  width=15).pack(pady=10)


# Para testing
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    GestionClientes(root)
    root.mainloop()
