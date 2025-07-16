import tkinter as tk
from tkinter import ttk, messagebox
from db import conectar, formatear_fecha
from datetime import datetime

def mostrar_cierre_quincena(parent=None):
    ventana = tk.Toplevel(parent) if parent else tk.Tk()
    ventana.title("Cierre de Quincena / Horas Trabajadas")
    ventana.geometry("830x500")
    ventana.configure(bg="#f4fff7")

    tk.Label(ventana, text="Cierre de Quincena - Horas Trabajadas", font=("Arial", 16, "bold"),
             bg="#f4fff7", fg="#24794c").pack(pady=12)

    frame_filtros = tk.Frame(ventana, bg="#f4fff7")
    frame_filtros.pack(pady=8)

    # --- Empleado ---
    tk.Label(frame_filtros, text="Empleado:", font=("Arial", 11, "bold"), bg="#f4fff7").grid(row=0, column=0, padx=8)
    empleados = obtener_empleados_activos()
    empleados_str = [f"{e[1]} - {e[2]}" for e in empleados]
    cbx_empleado = ttk.Combobox(frame_filtros, values=empleados_str, state="readonly", width=28)
    cbx_empleado.grid(row=0, column=1, padx=5)
    if empleados:
        cbx_empleado.current(0)

    # --- Fechas ---
    tk.Label(frame_filtros, text="Desde:", font=("Arial", 11, "bold"), bg="#f4fff7").grid(row=0, column=2, padx=8)
    entry_fecha_ini = tk.Entry(frame_filtros, width=10, font=("Arial", 11))
    entry_fecha_ini.grid(row=0, column=3, padx=3)
    entry_fecha_ini.insert(0, obtener_fecha_inicio_quincena())

    tk.Label(frame_filtros, text="Hasta:", font=("Arial", 11, "bold"), bg="#f4fff7").grid(row=0, column=4, padx=8)
    entry_fecha_fin = tk.Entry(frame_filtros, width=10, font=("Arial", 11))
    entry_fecha_fin.grid(row=0, column=5, padx=3)
    entry_fecha_fin.insert(0, formatear_fecha())

    btn_filtrar = tk.Button(frame_filtros, text="Consultar", bg="#32cd32", fg="white", font=("Arial", 10, "bold"),
                            command=lambda: cargar_tabla())
    btn_filtrar.grid(row=0, column=6, padx=10)

    # --- Tabla ---
    cols = ("Fecha", "Entrada", "Salida", "Horas Trabajadas")
    tree = ttk.Treeview(ventana, columns=cols, show="headings", height=17)
    for col in cols:
        tree.heading(col, text=col)
        tree.column(col, width=170 if col == "Horas Trabajadas" else 135, anchor="center")
    tree.pack(padx=12, pady=14, fill="both", expand=True)

    lbl_total = tk.Label(ventana, text="", font=("Arial", 12, "bold"), bg="#f4fff7", fg="#0c3d25")
    lbl_total.pack(pady=6)

    def cargar_tabla():
        tree.delete(*tree.get_children())
        idx = cbx_empleado.current()
        if idx < 0 or not empleados:
            messagebox.showerror("Error", "Seleccione un empleado")
            return
        usuario = empleados[idx][0]
        desde = entry_fecha_ini.get().strip()
        hasta = entry_fecha_fin.get().strip()
        sesiones = obtener_sesiones_usuario(usuario, desde, hasta)
        total_horas = 0

        for ses in sesiones:
            fecha, entrada, salida = ses[0], ses[1], ses[2]
            horas_str = "-"
            if entrada and salida and entrada != "-" and salida != "-":
                try:
                    t_entrada = datetime.strptime(f"{fecha} {entrada}", "%d/%m/%Y %H:%M:%S")
                    t_salida = datetime.strptime(f"{fecha} {salida}", "%d/%m/%Y %H:%M:%S")
                    # Si la salida es menor que la entrada, ignorar
                    if t_salida > t_entrada:
                        horas = (t_salida - t_entrada).total_seconds() / 3600
                        horas_str = f"{horas:.2f}"
                        total_horas += horas
                    else:
                        horas_str = "Error"
                except Exception:
                    horas_str = "Error"
            tree.insert("", "end", values=(fecha, entrada or "-", salida or "-", horas_str))
        lbl_total.config(text=f"Total horas trabajadas en el rango: {total_horas:.2f} horas")

    # Primer consulta al abrir
    cargar_tabla()

    tk.Button(ventana, text="Cerrar", command=ventana.destroy, bg="#ff7272", width=18).pack(pady=6)

    # Actualizar tabla al cambiar de empleado
    cbx_empleado.bind("<<ComboboxSelected>>", lambda e: cargar_tabla())

def obtener_empleados_activos():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT usuario, nombre, cedula FROM empleados ORDER BY nombre")
    empleados = cursor.fetchall()
    conn.close()
    return empleados

def obtener_sesiones_usuario(usuario, desde, hasta):
    # Las fechas van formato dd/mm/yyyy
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT fecha, hora_entrada, hora_salida FROM inicios_sesion
        WHERE usuario=? AND fecha BETWEEN ? AND ?
        ORDER BY fecha, hora_entrada
    """, (usuario, desde, hasta))
    sesiones = cursor.fetchall()
    conn.close()
    return sesiones

def obtener_fecha_inicio_quincena():
    """Devuelve el primer día de la quincena actual (si hoy es 1-15, retorna 1, si es 16-31, retorna 16)"""
    hoy = datetime.now()
    if hoy.day < 16:
        return hoy.replace(day=1).strftime("%d/%m/%Y")
    else:
        return hoy.replace(day=16).strftime("%d/%m/%Y")
