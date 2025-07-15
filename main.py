import tkinter as tk
from tkinter import ttk, messagebox
from inventario import InventarioFrame
from ventas import VentasFrame
from facturas import FacturasFrame
from clientes import GestionClientes
from login import LoginWindow
from db import inicializar_bd, migrar_bd, backup_database, obtener_productos_stock_bajo, formatear_moneda

# Inicializar y migrar BD
inicializar_bd()
migrar_bd()


def main():
    # Mostrar login primero
    login = LoginWindow()
    login.root.mainloop()

    if not hasattr(login, "nombre") or not login.nombre:
        return  # Si se cierra el login, no abre el sistema

    root = tk.Tk()
    root.title("420 Smoking Vibes - Punto de Venta")
    root.geometry("1050x730")
    root.configure(bg="#f0f8ff")

    # Configurar estilo
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure("TNotebook", background="#f0f8ff", borderwidth=0)
    style.configure("TNotebook.Tab",
                    font=("Arial", 12, "bold"),
                    padding=[16, 8],
                    background="#e0ffe0",
                    foreground="#2e8b57")
    style.map("TNotebook.Tab", background=[("selected", "#c5e1a5")])

    # Crear menú principal
    menubar = tk.Menu(root)
    root.config(menu=menubar)

    # Menú Archivo
    menu_archivo = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Archivo", menu=menu_archivo)
    menu_archivo.add_command(label="Hacer Backup",
                             command=lambda: hacer_backup())
    menu_archivo.add_separator()
    menu_archivo.add_command(label="Salir", command=root.quit)

    # Menú Herramientas
    menu_herramientas = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Herramientas", menu=menu_herramientas)
    menu_herramientas.add_command(label="Gestión de Clientes",
                                  command=lambda: GestionClientes(root))
    menu_herramientas.add_command(label="Ver Stock Bajo",
                                  command=lambda: mostrar_stock_bajo())

    # Barra de estado
    status_bar = tk.Frame(root, bg="#2e8b57", height=30)
    status_bar.pack(side="bottom", fill="x")

    lbl_empleado = tk.Label(status_bar,
                            text=f"👤 Empleado: {login.nombre}",
                            bg="#2e8b57",
                            fg="white",
                            font=("Arial", 10, "bold"))
    lbl_empleado.pack(side="left", padx=10)

    lbl_fecha = tk.Label(status_bar,
                         text=f"📅 {formatear_fecha()}",
                         bg="#2e8b57",
                         fg="white",
                         font=("Arial", 10))
    lbl_fecha.pack(side="right", padx=10)

    # Crear notebook
    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True, padx=14, pady=16)

    # Agregar pestañas
    frame_inventario = InventarioFrame(notebook)
    notebook.add(frame_inventario, text="📦 Inventario")

    frame_ventas = VentasFrame(notebook, empleado=login.nombre)
    notebook.add(frame_ventas, text="💸 Ventas")

    frame_facturas = FacturasFrame(notebook)
    notebook.add(frame_facturas, text="🧾 Facturas")

    # Verificar productos con stock bajo al iniciar
    verificar_stock_bajo()

    root.mainloop()


def hacer_backup():
    """Realiza backup de la base de datos"""
    try:
        archivo_backup = backup_database()
        messagebox.showinfo("Backup Exitoso",
                            f"Backup creado exitosamente:\n{archivo_backup}")
    except Exception as e:
        messagebox.showerror("Error", f"Error al crear backup: {e}")


def mostrar_stock_bajo():
    """Muestra ventana con productos con stock bajo"""
    productos_bajo = obtener_productos_stock_bajo()

    if not productos_bajo:
        messagebox.showinfo("Stock", "No hay productos con stock bajo")
        return

    ventana = tk.Toplevel()
    ventana.title("⚠️ Productos con Stock Bajo")
    ventana.geometry("600x400")
    ventana.configure(bg="#fff5f5")

    tk.Label(ventana,
             text="PRODUCTOS CON STOCK BAJO",
             font=("Arial", 14, "bold"),
             bg="#fff5f5",
             fg="#d32f2f").pack(pady=10)

    # Frame para la lista
    frame_lista = tk.Frame(ventana, bg="#fff5f5")
    frame_lista.pack(fill="both", expand=True, padx=20, pady=10)

    # Scrollbar
    scrollbar = tk.Scrollbar(frame_lista)
    scrollbar.pack(side="right", fill="y")

    # Listbox
    listbox = tk.Listbox(frame_lista,
                         yscrollcommand=scrollbar.set,
                         font=("Consolas", 11),
                         bg="#ffffff",
                         selectmode="single")
    listbox.pack(side="left", fill="both", expand=True)
    scrollbar.config(command=listbox.yview)

    # Agregar productos
    for prod in productos_bajo:
        texto = f"SKU: {prod[0]:10} | {prod[1]:25} | Stock: {prod[6]:3} | Mín: {prod[7]:3}"
        listbox.insert("end", texto)

    # Resumen
    tk.Label(ventana,
             text=f"Total productos con stock bajo: {len(productos_bajo)}",
             font=("Arial", 11, "bold"),
             bg="#fff5f5").pack(pady=5)

    tk.Button(ventana,
              text="Cerrar",
              command=ventana.destroy,
              bg="#ff7272",
              width=15).pack(pady=10)


def verificar_stock_bajo():
    """Verifica y alerta sobre productos con stock bajo"""
    productos_bajo = obtener_productos_stock_bajo()

    if productos_bajo:
        mensaje = f"⚠️ Hay {len(productos_bajo)} producto(s) con stock bajo.\n"
        mensaje += "Revisa el inventario para más detalles."

        # Crear ventana de notificación personalizada
        notif = tk.Toplevel()
        notif.title("Alerta de Stock")
        notif.geometry("400x150")
        notif.configure(bg="#fff5f5")
        notif.transient()

        tk.Label(notif,
                 text="⚠️ ALERTA DE INVENTARIO",
                 font=("Arial", 12, "bold"),
                 bg="#fff5f5",
                 fg="#d32f2f").pack(pady=10)

        tk.Label(notif, text=mensaje, font=("Arial", 10),
                 bg="#fff5f5").pack(pady=5)

        tk.Button(notif,
                  text="Ver Detalles",
                  command=lambda: [notif.destroy(),
                                   mostrar_stock_bajo()],
                  bg="#ffd700",
                  width=15).pack(side="left", padx=50, pady=10)

        tk.Button(notif,
                  text="Cerrar",
                  command=notif.destroy,
                  bg="#90ee90",
                  width=15).pack(side="right", padx=50, pady=10)

        # Centrar ventana
        notif.update_idletasks()
        x = (notif.winfo_screenwidth() // 2) - (notif.winfo_width() // 2)
        y = (notif.winfo_screenheight() // 2) - (notif.winfo_height() // 2)
        notif.geometry(f"+{x}+{y}")


# Importar función para obtener fecha
from db import formatear_fecha

if __name__ == "__main__":
    main()
