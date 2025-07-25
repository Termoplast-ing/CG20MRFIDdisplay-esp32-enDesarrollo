import tkinter as tk
import util.util_ventana as util_ventana

class EstacionesCorralesWindow(tk.Toplevel):
    def __init__(self, master, configuracion_window):
        super().__init__(master)
        self.configuracion_window = configuracion_window
        self.overrideredirect(True)
        self.geometry("480x800")
        self.config(bg="#EF9480")
        self.resizable(False, False)
        self.grab_set() 

        # Frame del logo
        self.frame_logo = tk.Frame(self, bg='#EF9480', height=100)
        self.frame_logo.pack(side=tk.TOP, fill="x", pady=22)

        # Logo
        self.crear_logo(self.frame_logo)

        # Contenido principal
        self.frame_contenido = tk.Frame(self, bg="#EF9480")
        self.frame_contenido.pack(side=tk.TOP, fill="both", expand=True)
        label = tk.Label(self.frame_contenido, text="Estaciones Corrales", bg="#EF9480", font=("Helvetica", 30))
        label.pack(pady=50)

        # Botón Atrás
        self.frame_boton_atras = tk.Frame(self, bg="#EF9480", height=60)
        self.frame_boton_atras.pack(side=tk.BOTTOM, fill="x")

        boton_atras = tk.Button(self.frame_boton_atras,text="<< Atrás",font=("Helvetica", 16),command=self.cerrar_ventana,bg="red",fg="#ffffff",bd=7)
        boton_atras.pack(side=tk.LEFT, padx=10, pady=70)
        # Centrar
        util_ventana.centrar_ventana(self, 480, 800)

    def crear_logo(self, frame):
        """Cargar el logo del master"""
        label = tk.Label(frame, image=self.master.logo, bg='#EF9480')
        label.place(relx=0.5, rely=0.5, anchor="center")

    def cerrar_ventana(self):
        """Cerrar y mostrar la ventana de configuración"""
        if self.configuracion_window:
            self.grab_release()
            self.destroy()
            self.configuracion_window.deiconify()
        else:
            print("Error: configuracion_window es None")
