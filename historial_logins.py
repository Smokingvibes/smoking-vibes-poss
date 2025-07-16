import tkinter as tk
from tkinter import ttk
from db import obtener_logins

def mostrar_historial_logins(parent=None):
    ventana = tk.Toplevel(parent) if parent else tk.Tk()
    ventana.title("Historial de Inicios de Sesión")
    ventana.geometry("900x430")
    ventana.configure(bg="#e0ffe0")

    tk.Label(ventana, text="HISTORIAL DE INICIOS Y SALIDAS DE SESIÓN DE EMPLEADOS",
             font=("Arial", 15, "bold"), bg="#e0ffe0").pack(pady=10)

    cols = ("Usuario", "Nombre", "Cédula", "Fecha", "Entrada", "Salida")
    tree = ttk.Treeview(ventana, columns=cols, show="headings", height=18)
    for col in cols:
        tree.heading(col, text=col)
        tree.column(col, width=140 if col != "Nombre" else 180, anchor="center")
    tree.pack(padx=10, pady=8, fill="both", expand=True)

    logins = obtener_logins()
    for login in logins:
        # login: (usuario, nombre, cedula, fecha, entrada, salida)
        tree.insert("", "end", values=login)

    tk.Button(ventana, text="Cerrar", command=ventana.destroy, bg="#ff7272", width=16).pack(pady=12)
