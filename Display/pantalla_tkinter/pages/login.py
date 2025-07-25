import tkinter as tk
from tkinter import messagebox
import util.util_ventana as util_ventana
from util.teclado import TecladoWindow
from util.util_mensaje import mostrar_mensaje

class LoginWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.overrideredirect(True)
        self.geometry("480x800")
        self.config(bg="#EF9480")
        self.resizable(False, False)
        self.grab_set()

        # Crear un frame para el logo en la parte superior
        self.frame_logo = tk.Frame(self, bg='#EF9480', height=100)
        self.frame_logo.pack(side=tk.TOP, fill="x",pady=22)
        
        # Crear el logo en la ventana secundaria
        self.crear_logo(self.frame_logo)

        # Crear un frame para los campos de usuario y contraseña
        self.frame_contenido = tk.Frame(self, bg="#EF9480")  # Crear el frame de contenido
        self.frame_contenido.pack(side=tk.TOP, fill="both", expand=True)

        self.frame_campos = tk.Frame(self.frame_contenido, bg="#EF9480")
        self.frame_campos.pack(pady=80)

        # Crear el campo para el usuario
        self.label_usuario = tk.Label(self.frame_campos, text="Usuario:", bg="#EF9480", font=("Helvetica", 16))
        self.label_usuario.grid(row=0, column=0, pady=15, padx=5)

        self.entry_usuario = tk.Entry(self.frame_campos, font=("Helvetica", 14), width=20)
        self.entry_usuario.grid(row=0, column=1, pady=10, padx=10)
        self.entry_usuario.bind("<Button-1>", lambda e: self.mostrar_teclado(self.entry_usuario))

        # Crear el campo para la contraseña
        self.label_contrasena = tk.Label(self.frame_campos, text="Contraseña:", bg="#EF9480", font=("Helvetica", 16))
        self.label_contrasena.grid(row=1, column=0, pady=10, padx=5)

        self.entry_contrasena = tk.Entry(self.frame_campos, font=("Helvetica", 14), show="*", width=20)
        self.entry_contrasena.grid(row=1, column=1, pady=10, padx=10)
        self.entry_contrasena.bind("<Button-1>", lambda e: self.mostrar_teclado(self.entry_contrasena))

        # Crear el botón "Ingresar" (ahora agregado)
        self.boton_ingresar = tk.Button(self.frame_contenido, text="Ingresar", font=("Helvetica", 16), command=self.ingresar, bg="red", fg="#ffffff", bd=7)
        self.boton_ingresar.pack(pady=20)

        # Crear un frame inferior para el botón "Atrás"
        self.frame_boton_atras = tk.Frame(self, bg="#EF9480", height=60)
        self.frame_boton_atras.pack(side=tk.BOTTOM, fill="x")
        # Botón para volver a la ventana principal
        boton_atras = tk.Button(self, text="<< Atrás", font=("Helvetica", 16), command=self.cerrar_ventana, bg="red", fg="#ffffff", bd=7)
        boton_atras.pack(side=tk.LEFT, padx=10, pady=10)

        # Centrar la ventana de login
        util_ventana.centrar_ventana(self, 480, 800)
        self.grab_set()

    def mostrar_teclado(self, entry_widget):
        """Muestra el teclado virtual y lo asocia al Entry"""
        TecladoWindow(self.master, entry_widget)

    def crear_logo(self, frame):
        """Función para crear y ubicar el logo en un frame dado"""
        label = tk.Label(frame, image=self.master.logo, bg='#EF9480')
        label.place(relx=0.5, rely=0.5, anchor="center")

    def cerrar_ventana(self):
        """Cerrar la ventana de login"""
        self.master.deiconify()  # Restaurar la ventana principal
        self.destroy()  # Cierra la ventana de login
   
    def ingresar(self):
        """Validación de las credenciales y manejo de la ventana de login"""
        usuario = self.entry_usuario.get()
        contrasena = self.entry_contrasena.get()

        if usuario == "admin" and contrasena == "1234":
            mostrar_mensaje(self, "Ingreso Correcto", "¡Bienvenido!", "info")
            self.master.master.restaurar_ventana_principal()  # Restauramos la ventana principal
            self.destroy()  # Cierra la ventana de login
        else:
            if usuario != "admin":
                mostrar_mensaje(self, "Usuario Incorrecto", "El usuario no es correcto.", "error")
            elif contrasena != "1234":
                mostrar_mensaje(self, "Contraseña Incorrecta", "La contraseña no es correcta.", "error")
            