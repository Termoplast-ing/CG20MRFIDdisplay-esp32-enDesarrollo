import tkinter as tk
from pages.estaciones import Estaciones
from tkinter.font import BOLD
import util.util_imagenes as util_img
import util.util_ventana as util_ventana
from pages.gestion_animal import GestionAnimalWindow
from pages.login import LoginWindow
from pages.configuracion import ConfiguracionWindow
from pages.datos import DatosWindow
from pages.alarma import AlarmaWindow
from pages.menu_inferior import MenuInferiorWindow
from pages.wifi_hora import WifiHoraWindow
from util.util_calendario import seleccionar_fecha
import time
from datetime import datetime

class MasterPanel(tk.Tk):
    def __init__(self):
        super().__init__()
        self.logo = util_img.leer_imagen('./imagenes/Logo_negro.png',(300,100))   #240,75
        self.config(bg="#EF9480")
        self.config_windows()
        self.secciones()                
        #Variable de control para evitar abrir múltiples pantallas
        self.ventana_opciones_abierta = None
        self.menu_visible = False
        self.bind_all("<Control-q>", lambda event: self.destroy())
        self.after(100, lambda: self._mantener_foco())
        self.ventanas_secundarias = {}  # Diccionario para manejar las ventanas secundarias
        self.ventana_login = None
        
    def _mantener_foco(self):
        self.focus_force()
        self.after(500, self._mantener_foco)

    def crear_logo(self,frame):
        label = tk.Label(frame, image = self.logo, bg='#EF9480')
        label.grid(row=0, column=0, sticky="nsew",pady=0)
                      
    def config_windows(self):
        #configuracion inicial de la ventana
        self.overrideredirect(True)
        w, h = 480, 800
        util_ventana.centrar_ventana(self,w,h)
                       
    def secciones(self):
        #Frame superior para el logo                       
        self.frame_superior = tk.Frame(self, bd=0, bg='#EF9480',height=100)
        self.frame_superior.grid(row=0, column=0, sticky="nsew", pady=0)

        # Configuración de columnas para que ocupen todo el espacio
        self.frame_superior.grid_columnconfigure(0, weight=1)  # Logo centrado
        self.frame_superior.grid_rowconfigure(0, weight=1)  # Fila para centrar el logo

        # Crear el logo centrado en el centro de la sección superior
        self.frame_logo = tk.Frame(self.frame_superior, bg="#EF9480")
        self.frame_logo.grid(row=0, column=0, padx=0,pady=0,sticky="nsew")
        label_logo = tk.Label(self.frame_logo,image=self.logo,bg="#EF9480")
        label_logo.grid(row=0, column=0, padx=88,pady=20,sticky="nsew")
        
        # Aquí se coloca el frame de las estaciones entre el menú superior e inferior
        self.frame_estaciones = Estaciones(self)
        
        self.frame_estaciones.iniciar_recepcion_uart()
        
        # Menú en la parte inferior (horizontal)
        self.frame_inferior = tk.Frame(self, bg="#EF9480", height=100)
        self.frame_inferior.grid(row=2, column=0, sticky="nsew", padx=0, pady=0)

        # Configurar la columna para que el contenido se distribuya equitativamente
        self.frame_inferior.grid_columnconfigure(0, weight=1)  # Columna vacía
        self.frame_inferior.grid_columnconfigure(1, weight=0)  # Columna central para centrar el botón
        self.frame_inferior.grid_columnconfigure(2, weight=1)  # Columna vacía
        #self.frame_inferior.grid_columnconfigure(3, weight=1)
        
        # Crear un frame que ocupe todo el ancho para el botón
        self.frame_boton_inferior = tk.Frame(self.frame_inferior, bg="#EF9480")
        self.frame_boton_inferior.grid(row=0, column=1, sticky="nsew")
        self.boton_menu_inferior = tk.Button(self.frame_boton_inferior, text="Menú", font=("Helvetica", 20), command=self.mostrar_opciones, bg="red", fg="#ffffff",activebackground="#FF6347",highlightbackground="#EF9480",highlightcolor="#FF6347", bd=9)
        # Vincular los eventos de mouse (hover) para cambiar el color de fondo
        self.boton_menu_inferior.bind("<Enter>", self.on_enter)
        self.boton_menu_inferior.bind("<Leave>", self.on_leave)
        self.boton_menu_inferior.grid(row=0, column=2,sticky="nsew", pady=10)
        
        #boton fecha
        self.variable_fecha = tk.StringVar()
        self.boton_fecha = tk.Button(self.frame_inferior, text="Fecha", font=("Helvetica", 20), command=self.abrir_calendario,bg="red", fg="#ffffff",activebackground="#FF6347",highlightbackground="#EF9480",highlightcolor="#FF6347", bd=9)
        self.boton_fecha.grid(row=0, column=3, sticky="nsew", pady=10, padx=20)
        
        #contenedor para la fecha y hora (reloj)
        self.frame_reloj = tk.Frame(self, bg="#EF9480", height=60)
        self.frame_reloj.grid(row=3, column=0, sticky="e", padx=10, pady=45)
        
        #Label para la fecha (arriba)
        self.label_reloj = tk.Label(self.frame_reloj, font=("Helvetica", 14, "bold"), bg="#EF9480", fg="black")
        self.label_reloj.grid(row=0, column=1, sticky="e")
        
        #Label para la hora (abajo)
        self.label_hora = tk.Label(self.frame_reloj, font=("Helvetica", 18, "bold"), bg="#EF9480", fg="black")
        self.label_hora.grid(row=1, column=1, sticky="e")
        
        self.actualizar_reloj()
        
        # Configurar las filas y columnas de la ventana principal
        self.grid_rowconfigure(0, weight=0)  # Fila superior (logo)
        self.grid_rowconfigure(1, weight=0)  # Fila central (estaciones)
        self.grid_rowconfigure(2, weight=0)  # Fila inferior (menú)
        self.grid_rowconfigure(3, weight=0)  # Fila reloj
        self.grid_columnconfigure(0, weight=1)  # Columna única

    def abrir_calendario(self):
        self.lift()
        self.attributes('-topmost', 1)
        self.after(100, lambda: self.attributes('-topmost', 0))
        seleccionar_fecha(self, self.variable_fecha)
        self.wait_variable(self.variable_fecha)
        fecha = self.variable_fecha.get()
        if fecha:
            self.frame_estaciones.filtrar_por_fecha(fecha)
    def actualizar_reloj(self):
        fecha_actual = datetime.now().strftime("%d/%m/%Y")
        hora_actual = datetime.now().strftime("%H:%M")
        self.label_reloj.config(text=fecha_actual)
        self.label_hora.config(text=hora_actual)
        self.after(1000, self.actualizar_reloj)

    def on_enter(self, event):
        """Función para cambiar el color cuando el ratón entra en el botón"""
        event.widget.config(bg="red")  # Cambiar el color de fondo cuando el ratón pasa sobre el botón
        self.update_idletasks()

    def on_leave(self, event):
        """Función para restaurar el color cuando el ratón sale del botón"""        
        event.widget.config(bg="red")  # Volver al color original cuando el ratón deja el botón
        self.update_idletasks()
        
    def mostrar_opciones(self):
        """Muestra la ventana del menú inferior con las opciones"""
    # Verificar si la ventana ya está abierta
        if not self.ventana_opciones_abierta or not self.ventana_opciones_abierta.winfo_exists():
        # Si la ventana no está abierta, crear una nueva instancia
            self.ventana_opciones_abierta = MenuInferiorWindow(self)
            self.ventana_opciones_abierta.grab_set()
            self.ventana_opciones_abierta.lift()  # Asegurar que la ventana esté por encima de la principal
            self.ventana_opciones_abierta.deiconify()
        else: 
             self.ventana_opciones_abierta.lift()
            
    def mostrar_gestion_animal(self):
            ventana = GestionAnimalWindow(self)
            ventana.grab_set()  # Hacer que la ventana se quede encima de la principal

    def mostrar_login(self):
        """Abre la ventana de login y oculta la ventana principal"""
        if self.ventana_login is None or not self.ventana_login.winfo_exists():
            self.withdraw()
            self.ventana_login = LoginWindow(self)
            self.ventana_login.grab_set()  # La ventana de login será la ventana activa
            self.ventana_login.lift()  # Asegura que la ventana de login esté encima de la principal
            self.boton_menu_inferior.config(state=tk.DISABLED)  # Deshabilitar el botón mientras el login está abierto

    def mostrar_configuracion(self):
            ventana = ConfiguracionWindow(self, self.logo)
            ventana.grab_set()

    def mostrar_datos(self):
            ventana = DatosWindow(self,self.logo)
            ventana.grab_set()

    def mostrar_alarma(self):
            ventana = AlarmaWindow(self)
            ventana.grab_set()

    def mostrar_wifi_hora(self):
         ventana = WifiHoraWindow(self, self.logo)
         ventana.grab_set()
    
    def restaurar_ventana_principal(self):
        """Cerrar la ventana de login y restaurar la ventana principal"""
        if self.ventana_login:
            self.ventana_login.destroy() 
            self.ventana_login = None  # Limpia la referencia
        self.deiconify()
        self.boton_menu_inferior.config(state=tk.NORMAL)
        self.focus_force()  # Asegura que la ventana principal sea interactiva nuevamente
        self.ventana_opciones_abierta = None  # Asegúrate de que la ventana de opciones esté lista para ser abierta nuevamente
