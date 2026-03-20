import tkinter as tk
from tkinter import ttk
import util.util_imagenes as util_img
import util.util_ventana as util_ventana

class SplashScreen(tk.Tk):
    def __init__(self):
        super().__init__()
        self.overrideredirect(True)
        self.config(bg="#EF9480")
        
        # Tamaño y posición para ocultar todo el fondo
        w, h = 480, 800
        util_ventana.centrar_ventana(self, w, h)
        # O pcionalmente forzar fullscreen total si el OS lo permite
        # self.attributes("-fullscreen", True)
        
        # Logo
        try:
            self.logo = util_img.leer_imagen('./imagenes/Logo_negro.png', (300, 100))
            label_logo = tk.Label(self, image=self.logo, bg="#EF9480")
            label_logo.pack(pady=(40, 20))
        except Exception:
            pass
            
        # Mensaje
        self.label_msg = tk.Label(
            self, 
            text="Iniciando por favor espere...", 
            font=("Helvetica", 18, "bold"), 
            bg="#EF9480", 
            fg="black"
        )
        self.label_msg.pack(pady=20)
        
        # Estilo barra de progreso
        style = ttk.Style()
        style.theme_use('default')
        style.configure(
            "Splash.Horizontal.TProgressbar", 
            thickness=30, 
            troughcolor='#EF9480', 
            background='red', 
            bordercolor='black', 
            lightcolor='red', 
            darkcolor='red'
        )
        
        # Barra de progreso
        self.progress = ttk.Progressbar(
            self, 
            orient=tk.HORIZONTAL, 
            length=400, 
            mode='determinate', 
            style="Splash.Horizontal.TProgressbar"
        )
        self.progress.pack(pady=30)
        
        # Label de detalle (opcional)
        self.label_detalle = tk.Label(
            self, 
            text="Iniciando periféricos...", 
            font=("Helvetica", 12), 
            bg="#EF9480", 
            fg="#555555"
        )
        self.label_detalle.pack(pady=10)
        
        self.update()

    def set_progress(self, value, text=None):
        self.progress['value'] = value
        if text:
            self.label_detalle.config(text=text)
        self.update()

    def show_error(self, message):
        """Muestra un error crítico y bloquea la ejecución."""
        # Limpiar elementos actuales
        self.progress.pack_forget()
        self.label_msg.pack_forget()
        self.label_detalle.pack_forget()
        
        # Mostrar error
        self.config(bg="red")
        label_error = tk.Label(
            self, 
            text=message, 
            font=("Helvetica", 20, "bold"), 
            bg="red", 
            fg="white",
            justify="center"
        )
        label_error.pack(expand=True, padx=20, pady=20)
        
        # Mantener la ventana abierta e impedir el cierre normal
        self.update()
        self.mainloop() # Esto bloquea el hilo principal para siempre
