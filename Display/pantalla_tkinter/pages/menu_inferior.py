import tkinter as tk
import util.util_ventana as util_ventana
from pages.login import LoginWindow
from pages.gestion_animal import GestionAnimalWindow
from pages.configuracion import ConfiguracionWindow
from pages.datos import DatosWindow
from pages.alarma import AlarmaWindow

class MenuInferiorWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.overrideredirect(True)
        w, h = 480, 800
        self.config(bg="#EF9480")
        util_ventana.centrar_ventana(self, w, h)
        self.focus_set()
        self.crear_componentes()

    def crear_componentes(self):
        # --- Frame del logo ---
        self.frame_logo = tk.Frame(self, bg='#EF9480', height=100)
        self.frame_logo.grid(row=0, column=0, sticky="ew", pady=20)
        self.frame_logo.grid_columnconfigure(0, weight=1)

        self.logo = self.master.logo
        self.crear_logo(self.frame_logo)

        # --- Frame del contenido central con los botones ---
        self.frame_contenido = tk.Frame(self, bg="#EF9480")
        self.frame_contenido.grid(row=1, column=0, sticky="nsew", padx=0, pady=(0, 25))
        self.frame_contenido.grid_columnconfigure(0, weight=1)

        # Botones de opciones
        botones = [
            ("Gestión Animal", self.mostrar_gestion_animal),
            ("Login", self.mostrar_login),
            ("Configuración", self.mostrar_configuracion),
            ("Datos", self.mostrar_datos),
            ("Alarma", self.mostrar_alarma),
        ]

        for i, (texto, comando) in enumerate(botones):
            btn = tk.Button(self.frame_contenido, text=texto, font=("Helvetica", 18),
                            command=comando, bg="red", fg="#ffffff", bd=9)
            btn.grid(row=i, column=0, padx=100, pady=10, sticky="ew")

        # --- Frame inferior con el botón "Atrás" abajo a la izquierda ---
        self.frame_boton_atras = tk.Frame(self, bg="#EF9480", height=80)
        self.frame_boton_atras.grid(row=2, column=0, sticky="ew")
        self.frame_boton_atras.grid_columnconfigure(0, weight=0)
        self.frame_boton_atras.grid_columnconfigure(1, weight=1)

        boton_atras = tk.Button(self.frame_boton_atras, text="<< Atrás", font=("Helvetica", 16),
                                command=self.cerrar_ventana, bg="red", fg="#ffffff", bd=7)
        boton_atras.grid(row=0, column=0, padx=10, pady=70, sticky="w")

        # Estructura general del grid principal
        self.rowconfigure(1, weight=1)  # contenido central expandible
        self.columnconfigure(0, weight=1)

    def crear_logo(self, frame):
        label = tk.Label(frame, image=self.logo, bg='#EF9480')
        label.grid(row=0, column=0, sticky="n")

    def mostrar_gestion_animal(self):
        ventana = GestionAnimalWindow(self)
        ventana.grab_set()

    def mostrar_login(self):
        ventana = LoginWindow(self)
        ventana.grab_set()

    def mostrar_configuracion(self):
        ventana = ConfiguracionWindow(self)
        ventana.grab_set()

    def mostrar_datos(self):
        ventana = DatosWindow(self)
        ventana.grab_set()

    def mostrar_alarma(self):
        ventana = AlarmaWindow(self)
        ventana.grab_set()

    def cerrar_ventana(self):
        self.withdraw()
        self.master.deiconify()
        self.master.focus_set()
        self.destroy()
