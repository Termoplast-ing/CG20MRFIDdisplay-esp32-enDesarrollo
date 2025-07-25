import tkinter as tk
import util.util_ventana as util_ventana
from pages.wifi_hora import WifiHoraWindow
from pages.funcionalidad import FuncionalidadWindow
from pages.alarma_errores import AlarmaErroresWindow
from pages.estaciones_corrales import EstacionesCorralesWindow 

class ConfiguracionWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.overrideredirect(True)
        self.geometry("480x800")
        self.config(bg="#EF9480")
        self.resizable(False, False)
        util_ventana.centrar_ventana(self, 480, 800)

        # Asegurar que esta ventana tenga el enfoque
        self.grab_set()
        # Crear un frame para el logo en la parte superior
        self.frame_logo = tk.Frame(self, bg='#EF9480', height=100)
        self.frame_logo.pack(side=tk.TOP, fill="x",pady=22)

        # Crear el logo en la ventana secundaria
        self.crear_logo(self.frame_logo, self.master.logo)

        # Crear un frame para contener todos los botones
        self.frame_botones = tk.Frame(self, bg="#EF9480")
        self.frame_botones.pack(side=tk.TOP, fill="both", expand=True, padx=20, pady=25)

        # Crear el botón para configurar wifi y hora
        self.boton_wifi_hora = tk.Button(self.frame_botones, text="Wifi y Hora", font=("Helvetica", 18),width=18, command=self.mostrar_wifi_hora, bg="red", fg="#ffffff", bd=9)
        self.boton_wifi_hora.pack(side=tk.TOP,padx=20, pady=10)
        
        # Crear el botón para configurar la configuracion funcional
        self.boton_configuracion_funcional = tk.Button(self.frame_botones, text="Funcionalidad", font=("Helvetica", 18),width=18, command=self.mostrar_funcionalidad, bg="red", fg="#ffffff", bd=9)
        self.boton_configuracion_funcional.pack(side=tk.TOP,padx=20, pady=10)

        # Crear el botón para configurar alarmas y errores
        self.boton_alarmas_errores = tk.Button(self.frame_botones, text="Alarmas y Errores", font=("Helvetica", 18),width=18, command=self.mostrar_alarmas_errores, bg="red", fg="#ffffff", bd=9)
        self.boton_alarmas_errores.pack(side=tk.TOP,padx=20, pady=10)

        # Crear el botón para configurar estaciones y corrales
        self.boton_estaciones_corrales = tk.Button(self.frame_botones, text="Estaciones", font=("Helvetica", 18),width=18, command=self.mostrar_estaciones_corrales, bg="red", fg="#ffffff", bd=9)
        self.boton_estaciones_corrales.pack(side=tk.TOP, padx=20, pady=10)

        # Crear un frame inferior para el botón "Atrás"
        self.frame_boton_atras = tk.Frame(self, bg="#EF9480", height=60)
        self.frame_boton_atras.pack(side=tk.BOTTOM, fill="x")
        # Botón para volver a la ventana principal
        boton_atras = tk.Button(self, text="<< Atrás", font=("Helvetica", 16), command=self.cerrar_ventana, bg="red", fg="#ffffff", bd=7)
        boton_atras.pack(side=tk.LEFT, padx=10, pady=10)

    def crear_logo(self, frame, logo):
        """Función para crear y ubicar el logo en un frame dado"""
        label = tk.Label(frame, image=logo, bg='#EF9480')
        label.place(relx=0.5, rely=0.5, anchor="center")
    
    def mostrar_wifi_hora(self):
        """Abre la pantalla de configuración de Wifi y Hora"""
        WifiHoraWindow(self.master,self)

    def mostrar_funcionalidad(self):
        """Abre la pantalla de configuración funcional"""
        FuncionalidadWindow(self.master, self.master.logo)

    def mostrar_alarmas_errores(self):
        """Abre la pantalla de Alarmas y Errores"""
        AlarmaErroresWindow(self.master,self)
    
    def mostrar_estaciones_corrales(self):
        """Abre la pantalla de Estaciones y Corrales"""
        EstacionesCorralesWindow(self.master,self)

    def cerrar_ventana(self):
        self.grab_set()
        self.destroy()
