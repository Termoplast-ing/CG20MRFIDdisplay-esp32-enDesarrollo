import tkinter as tk
import util.util_ventana as util_ventana
from util.teclado import TecladoWindow
from util.util_mensaje import mostrar_mensaje
from util import sqlite as db_local


class LoginWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.overrideredirect(True)
        self.geometry("480x800")
        self.config(bg="#EF9480")
        self.resizable(False, False)
        self.grab_set()

        # Asegurar usuario por defecto en SQLite
        try:
            db_local.crearUsuarioPorDefecto()
        except Exception as e:
            print("Error creando usuario por defecto en SQLite:", e)

        #Logo arriba
        self.frame_logo = tk.Frame(self, bg='#EF9480', height=100)
        self.frame_logo.pack(side=tk.TOP, fill="x", pady=22)
        self.crear_logo(self.frame_logo)

        #Contenido
        self.frame_contenido = tk.Frame(self, bg="#EF9480")
        self.frame_contenido.pack(side=tk.TOP, fill="both", expand=True)

        self.frame_campos = tk.Frame(self.frame_contenido, bg="#EF9480")
        self.frame_campos.pack(pady=80)

        # Usuario
        self.label_usuario = tk.Label(
            self.frame_campos,
            text="Usuario:",
            bg="#EF9480",
            font=("Helvetica", 16)
        )
        self.label_usuario.grid(row=0, column=0, pady=15, padx=5)

        self.entry_usuario = tk.Entry(
            self.frame_campos,
            font=("Helvetica", 14),
            width=20
        )
        self.entry_usuario.grid(row=0, column=1, pady=10, padx=10)
        self.entry_usuario.bind(
            "<Button-1>",
            lambda e: self.mostrar_teclado(self.entry_usuario)
        )

        # Contraseña
        self.label_contrasena = tk.Label(
            self.frame_campos,
            text="Contraseña:",
            bg="#EF9480",
            font=("Helvetica", 16)
        )
        self.label_contrasena.grid(row=1, column=0, pady=10, padx=5)

        self.entry_contrasena = tk.Entry(
            self.frame_campos,
            font=("Helvetica", 14),
            show="*",
            width=20
        )
        self.entry_contrasena.grid(row=1, column=1, pady=10, padx=10)
        self.entry_contrasena.bind(
            "<Button-1>",
            lambda e: self.mostrar_teclado(self.entry_contrasena)
        )

        # Botón Ingresar
        self.boton_ingresar = tk.Button(
            self.frame_contenido,
            text="Ingresar",
            font=("Helvetica", 16),
            command=self.ingresar,
            bg="red",
            fg="#ffffff",
            bd=7
        )
        self.boton_ingresar.pack(pady=20)

        #Botón Atrás abajo
        self.frame_boton_atras = tk.Frame(self, bg="#EF9480", height=60)
        self.frame_boton_atras.pack(side=tk.BOTTOM, fill="x")

        boton_atras = tk.Button(
            self,
            text="<< Atrás",
            font=("Helvetica", 16),
            command=self.cerrar_ventana,
            bg="red",
            fg="#ffffff",
            bd=7
        )
        boton_atras.pack(side=tk.LEFT, padx=10, pady=10)

        util_ventana.centrar_ventana(self, 480, 800)
        self.grab_set()

    def mostrar_teclado(self, entry_widget):
        TecladoWindow(self.master, entry_widget)

    def crear_logo(self, frame):
        label = tk.Label(frame, image=self.master.logo, bg='#EF9480')
        label.place(relx=0.5, rely=0.5, anchor="center")

    def cerrar_ventana(self):
        self.master.deiconify()
        self.destroy()

    def ingresar(self):
        usuario = self.entry_usuario.get().strip()
        contrasena = self.entry_contrasena.get().strip()

        if not usuario or not contrasena:
            mostrar_mensaje(self, "Error", "Ingrese usuario y contraseña.", "error")
            return

        try:
            fila = db_local.obtenerUsuarioPorNombre(usuario)
        except Exception as e:
            print("Error consultando usuario en SQLite:", e)
            fila = None

        if fila is None:
            # Usuario no encontrado
            mostrar_mensaje(self, "Usuario Incorrecto", "El usuario no es correcto.", "error")
            return

        id_usuario, nombre_db, contrasenia_db = fila

        if contrasena != contrasenia_db:
            mostrar_mensaje(self, "Contraseña Incorrecta", "La contraseña no es correcta.", "error")
            return

        # Login OK
        mostrar_mensaje(self, "Ingreso Correcto", f"¡Bienvenido {nombre_db}!", "info")
        # Mantengo tu lógica original:
        self.master.master.restaurar_ventana_principal()
        self.destroy()
