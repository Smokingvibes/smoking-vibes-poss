import tkinter as tk
from tkinter import messagebox
from db import (
    formatear_fecha,
    formatear_hora,
    conectar,
    registrar_inicio_sesion,
    registrar_logout
)
import json
import os

class LoginWindow:

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("420 Smoking Vibes - Login")
        self.root.geometry("420x420")
        self.root.configure(bg='#2e8b57')
        self.root.resizable(False, False)

        # Centrar ventana
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
        self.root.geometry(f"+{x}+{y}")

        self.usuario = None
        self.nombre = None
        self.cedula = None
        self.intentos = 0
        self.max_intentos = 3

        self.crear_interfaz()
        self.cargar_ultimo_usuario()

    def crear_interfaz(self):
        # Logo/Título
        tk.Label(self.root,
                 text="🌿 420 SMOKING VIBES 🌿",
                 font=('Arial', 18, 'bold'),
                 bg='#2e8b57',
                 fg='white').pack(pady=16)

        tk.Label(self.root,
                 text="Sistema Punto de Venta",
                 font=('Arial', 12),
                 bg='#2e8b57',
                 fg='#f0f8ff').pack(pady=3)

        # Frame principal
        frm = tk.Frame(self.root, bg='white', relief='ridge', bd=3)
        frm.pack(pady=25, padx=30, fill='both', expand=True)

        # Usuario
        tk.Label(frm,
                 text="USUARIO:",
                 font=('Arial', 12, 'bold'),
                 bg='white',
                 fg='#2e8b57').pack(pady=6)
        self.entry_usuario = tk.Entry(frm, font=('Arial', 12), width=22, bd=2)
        self.entry_usuario.pack(pady=3)

        # Contraseña
        tk.Label(frm,
                 text="CONTRASEÑA:",
                 font=('Arial', 12, 'bold'),
                 bg='white',
                 fg='#2e8b57').pack(pady=6)
        self.entry_contrasena = tk.Entry(frm,
                                         font=('Arial', 12),
                                         width=22,
                                         bd=2,
                                         show='*')
        self.entry_contrasena.pack(pady=3)

        # Botón login
        self.btn_login = tk.Button(frm,
                                   text="🔑 INGRESAR",
                                   command=self.login,
                                   bg='#32cd32',
                                   fg='white',
                                   font=('Arial', 13, 'bold'),
                                   width=20,
                                   height=2,
                                   bd=3,
                                   cursor='hand2')
        self.btn_login.pack(pady=13)

        # Checkbox recordar usuario
        self.var_recordar = tk.BooleanVar()
        tk.Checkbutton(frm,
                       text="Recordar usuario",
                       variable=self.var_recordar,
                       bg='white',
                       fg='#2e8b57',
                       font=('Arial', 10)).pack(pady=2)

        # Botón registrar usuario nuevo
        tk.Button(frm,
                  text="Crear perfil de trabajador",
                  command=self.registro_usuario,
                  bg='#aee1ff',
                  fg='#003333',
                  font=('Arial', 10, 'bold')).pack(pady=4)

        # Footer con fecha y hora
        footer = tk.Frame(self.root, bg='#2e8b57')
        footer.pack(side='bottom', fill='x', pady=5)
        self.lbl_fecha_hora = tk.Label(
            footer,
            text=f"{formatear_fecha()} - {formatear_hora()}",
            font=('Arial', 9),
            bg='#2e8b57',
            fg='#b0ffb0')
        self.lbl_fecha_hora.pack()

        # Actualizar hora cada segundo
        self.actualizar_hora()

        # Focus en el primer campo
        self.entry_usuario.focus()

        # Binds enter
        self.entry_usuario.bind('<Return>',
                                lambda e: self.entry_contrasena.focus())
        self.entry_contrasena.bind('<Return>', lambda e: self.login())

    def actualizar_hora(self):
        self.lbl_fecha_hora.config(
            text=f"{formatear_fecha()} - {formatear_hora()}")
        self.root.after(1000, self.actualizar_hora)

    def cargar_ultimo_usuario(self):
        try:
            if os.path.exists("ultimo_usuario.json"):
                with open("ultimo_usuario.json", "r") as f:
                    data = json.load(f)
                    self.entry_usuario.insert(0, data.get("usuario", ""))
                    self.var_recordar.set(True)
                    self.entry_contrasena.focus()
        except:
            pass

    def guardar_ultimo_usuario(self):
        try:
            if self.var_recordar.get():
                data = {"usuario": self.usuario}
                with open("ultimo_usuario.json", "w") as f:
                    json.dump(data, f)
            else:
                if os.path.exists("ultimo_usuario.json"):
                    os.remove("ultimo_usuario.json")
        except:
            pass

    def login(self):
        usuario = self.entry_usuario.get().strip()
        contrasena = self.entry_contrasena.get().strip()

        if not usuario or not contrasena:
            messagebox.showerror("Error", "Complete todos los campos")
            self.entry_usuario.focus()
            return

        # Buscar usuario en base de datos
        try:
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT usuario, nombre, cedula, contrasena FROM empleados WHERE usuario=?",
                (usuario, ))
            fila = cursor.fetchone()
            conn.close()

            if not fila:
                if messagebox.askyesno(
                        "Usuario no existe",
                        "Usuario no registrado.\n¿Desea crear un perfil nuevo?"
                ):
                    self.registro_usuario(usuario_sugerido=usuario)
                else:
                    self.entry_usuario.focus()
                return

            db_usuario, db_nombre, db_cedula, db_contra = fila

            if contrasena != db_contra:
                self.intentos += 1
                if self.intentos >= self.max_intentos:
                    messagebox.showerror(
                        "Error", "Demasiados intentos fallidos. Cerrando.")
                    self.root.destroy()
                else:
                    messagebox.showerror("Error", "Contraseña incorrecta")
                    self.entry_contrasena.delete(0, tk.END)
                    self.entry_contrasena.focus()
                return

            # Login exitoso
            self.usuario = db_usuario
            self.nombre = db_nombre
            self.cedula = db_cedula

            self.guardar_ultimo_usuario()

            # REGISTRAR EN BD EL INICIO DE SESIÓN
            registrar_inicio_sesion(
                self.usuario,
                self.nombre,
                self.cedula,
                formatear_fecha(),
                formatear_hora()
            )

            messagebox.showinfo("Bienvenido",
                                f"¡Hola {self.nombre}!\nAcceso concedido.")
            self.root.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Error al validar login: {e}")

    def registro_usuario(self, usuario_sugerido=""):
        ventana = tk.Toplevel(self.root)
        ventana.title("Registrar trabajador")
        ventana.geometry("340x320")
        ventana.configure(bg="#f0f8ff")
        ventana.grab_set()

        tk.Label(ventana,
                 text="CREAR PERFIL DE TRABAJADOR",
                 font=('Arial', 13, 'bold'),
                 bg="#f0f8ff",
                 fg="#2e8b57").pack(pady=7)

        tk.Label(ventana, text="Usuario:", bg="#f0f8ff").pack(pady=2)
        entry_usuario = tk.Entry(ventana, font=('Arial', 11), width=24)
        entry_usuario.pack()
        entry_usuario.insert(0, usuario_sugerido)

        tk.Label(ventana, text="Nombre completo:", bg="#f0f8ff").pack(pady=2)
        entry_nombre = tk.Entry(ventana, font=('Arial', 11), width=24)
        entry_nombre.pack()

        tk.Label(ventana, text="Cédula:", bg="#f0f8ff").pack(pady=2)
        entry_cedula = tk.Entry(ventana, font=('Arial', 11), width=24)
        entry_cedula.pack()

        tk.Label(ventana, text="Contraseña:", bg="#f0f8ff").pack(pady=2)
        entry_contra = tk.Entry(ventana,
                                font=('Arial', 11),
                                width=24,
                                show="*")
        entry_contra.pack()

        def registrar():
            usuario = entry_usuario.get().strip()
            nombre = entry_nombre.get().strip()
            cedula = entry_cedula.get().strip()
            contra = entry_contra.get().strip()

            if not usuario or not nombre or not cedula or not contra:
                messagebox.showerror("Error", "Complete todos los campos")
                return

            if len(usuario) < 3:
                messagebox.showerror(
                    "Error", "Usuario debe tener al menos 3 caracteres")
                return
            if len(nombre) < 5:
                messagebox.showerror(
                    "Error", "Nombre debe tener al menos 5 caracteres")
                return
            if len(cedula) < 5:
                messagebox.showerror("Error", "Cédula inválida")
                return
            if len(contra) < 4:
                messagebox.showerror("Error", "Contraseña muy corta")
                return

            try:
                conn = conectar()
                cursor = conn.cursor()
                # Revisar si existe usuario
                cursor.execute("SELECT usuario FROM empleados WHERE usuario=?",
                               (usuario, ))
                if cursor.fetchone():
                    messagebox.showerror("Error", "Ese usuario ya existe")
                    conn.close()
                    return

                # Crear usuario
                cursor.execute(
                    """
                    INSERT INTO empleados (usuario, nombre, cedula, contrasena, fecha_ingreso, hora_entrada)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (usuario, nombre, cedula, contra, formatear_fecha(),
                      formatear_hora()))
                conn.commit()
                conn.close()
                messagebox.showinfo("Éxito",
                                    "Trabajador registrado correctamente")
                ventana.destroy()
            except Exception as e:
                messagebox.showerror("Error",
                                     f"Error al registrar trabajador: {e}")

        tk.Button(ventana,
                  text="Registrar",
                  command=registrar,
                  bg="#90ee90",
                  font=('Arial', 10, 'bold')).pack(pady=9)
        tk.Button(ventana,
                  text="Cancelar",
                  command=ventana.destroy,
                  bg="#ff7272",
                  font=('Arial', 10)).pack()

        entry_usuario.focus()
        ventana.transient(self.root)
        ventana.wait_window()

    # ======== NUEVO: método para logout que puedes llamar desde main.py ========
    def logout(self):
        """
        Registrar la salida del usuario actual, para cuadre de horas.
        """
        try:
            from db import registrar_logout
            fecha = formatear_fecha()
            hora_salida = formatear_hora()
            registrar_logout(self.usuario, fecha, hora_salida)
        except Exception as e:
            messagebox.showerror("Error al cerrar sesión", f"{e}")

# Para testing
if __name__ == "__main__":
    login = LoginWindow()
    login.root.mainloop()
    if hasattr(login, "nombre") and login.nombre:
        print(f"Login exitoso: {login.usuario} - {login.nombre}")
    else:
        print("Login cancelado")
