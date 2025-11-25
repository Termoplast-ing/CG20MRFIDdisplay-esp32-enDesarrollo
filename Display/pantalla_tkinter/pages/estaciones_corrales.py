import tkinter as tk
import util.util_ventana as util_ventana
from util.util_teclado import TecladoNumerico

class EstacionesCorralesWindow(tk.Toplevel):
    def __init__(self, master, configuracion_window):
        super().__init__(master)
        self.configuracion_window = configuracion_window
        self.overrideredirect(True)
        self.geometry("480x800")
        self.config(bg="#EF9480")
        self.resizable(False, False)
        self.grab_set() 

        # === Frame del logo ===
        self.frame_logo = tk.Frame(self, bg="#EF9480", height=100)
        self.frame_logo.pack(side=tk.TOP, fill="x", pady=(15, 10))
        self.crear_logo(self.frame_logo)

        # === Frame principal (contenido) ===
        self.frame_contenido = tk.Frame(self, bg="#EF9480")
        self.frame_contenido.pack(fill="both", expand=True)

        # Contenedor de botones (corrales)
        self.frame_estaciones = tk.Frame(self.frame_contenido, bg="#EF9480")
        self.frame_estaciones.pack(expand=True)
        self.crear_botones_corrales()

        # === Frame inferior (botones de acción) ===
        self.frame_inferior = tk.Frame(self, bg="#EF9480", height=100)
        self.frame_inferior.pack(side=tk.BOTTOM, fill="x", pady=(10, 25))

        # Botón Atrás
        boton_atras = tk.Button(self.frame_inferior,text="<< Atrás",font=("Helvetica", 16),command=self.cerrar_ventana,bg="red",fg="#ffffff",bd=7)
        boton_atras.pack(side=tk.LEFT, padx=40)

        # Botón Escanear
        boton_escanear = tk.Button(self.frame_inferior,text="Escanear",font=("Helvetica", 16),bg="green",fg="#ffffff",bd=7)
        boton_escanear.pack(side=tk.RIGHT, padx=40)

        # Centrar ventana
        util_ventana.centrar_ventana(self, 480, 800)

    # === Funciones auxiliares ===
    def crear_logo(self, frame):
        """Cargar el logo del master"""
        label = tk.Label(frame, image=self.master.logo, bg='#EF9480')
        label.place(relx=0.5, rely=0.5, anchor="center")

    def crear_botones_corrales(self):
        """Crea los botones C1–C10 en dos columnas"""
        botones = []
        for i in range(1, 11):
            boton = tk.Button(self.frame_estaciones,text=f"C{i}",font=("Helvetica", 16, "bold"),bg="#ABABAB",fg="black",bd=5,relief="raised",width=6,height=2,command=lambda n=i: self.abrir_modal_corral(n))
            botones.append(boton)

        # Colocar en grid dentro del frame_estaciones (solo aquí)
        for i in range(5):
            botones[i*2].grid(row=i, column=0, padx=35, pady=12)
            botones[i*2+1].grid(row=i, column=1, padx=35, pady=12)
            
    def abrir_modal_corral(self, numero_corral):
        self.grab_release()        
        modal = tk.Toplevel(self)
        modal.overrideredirect(True)
        modal.title(f"Corral C{numero_corral}")
        modal.geometry("380x300")
        modal.config(bg="#FFD966")
        
        
        x = self.winfo_x() + (self.winfo_width() - 380) // 2
        y = self.winfo_y() + (self.winfo_height() - 300) // 2
        modal.geometry(f"+{x}+{y}")
        frame_borde = tk.Frame(modal, bg="#FFD966", bd=3, relief="solid")
        frame_borde.pack(fill="both", expand=True, padx=5, pady=5)
        #modal.grab_set()
        #modal.transient(self)
        #modal.after(200, modal.attributes, '-topmost', False)
        boton_cerrar = tk.Button(frame_borde, text="X", font=("Helvetica", 12, "bold"),bg="#DBC0A2", fg="white",width=3,command=modal.destroy)
        boton_cerrar.place(x=300, y=10)

        etiqueta = tk.Label(frame_borde, text=f"Ingrese un numero (1 a 255)", font=("Helvetica", 14), bg="#FFD966")
        etiqueta.pack(pady=20)
        
        valor_entry = tk.StringVar()
        entrada = tk.Entry(frame_borde, textvariable=valor_entry, font=("Helvetica",18), justify="center", width=8)
        entrada.pack(pady=10)
        
        def mostrar_teclado(event):
            #modal.grab_release()
            teclado = TecladoNumerico(self, valor_entry)
            teclado_ancho = 480
            teclado_alto = 400
            teclado_x = x + (380 - teclado_ancho) // 2
            teclado_y = y - 100
            
            #if teclado_y < 0:
            #    teclado_y = y + 300 + 10
            
            teclado.geometry(f"+{teclado_x}+{teclado_y}")
            teclado.attributes('-topmost', True)
            teclado.lift()
            teclado.focus_force()
            #teclado.grab_set()
            
            #def restaurar_modal():
                #modal.grab_set()
                #modal.lift()
            #teclado.bind("<Destroy>", lambda e: restaurar_modal())
        
        #abre el teclado numerico al hacer clic en la entrada
        entrada.bind("<Button-1>", mostrar_teclado)
        boton_aceptar = tk.Button(frame_borde, text="Ok", font=("Helvetica", 14), bg="green",fg="#ffffff",bd=5,command=lambda: self.validar_valor(modal, valor_entry.get()))
        boton_aceptar.pack(pady=20)
        
        #modal.grab_set()
        modal.focus_force()
        modal.lift()
        #comento esto de prueba 21_10
        #def mantener_frente():
        #    if modal.winfo_exists():
        #        modal.lift()
        #        self.after(100, mantener_frente)
        #mantener_frente()
        #modal.attributes('-topmost', True)
        #modal.protocol("WM_DELETE_WINDOW", lambda: self.cerrar_modal(modal))
        
    def validar_valor(self, modal, valor):
        try:
            numero = int(valor)
            if 1 <= numero <= 255:
                print(f"Valor aceptado: {numero}")
                modal.destroy()
            else:
                self.mostrar_error(modal, "El numero debe estar entre 1 y 255")
        except ValueError:
            self.mostrar_error(modal, "Debe ingresar un numero valido")
            
    def mostrar_error(self, modal, mensaje):
        for widget in modal.winfo_children():
            if isinstance(widget, tk.Label) and widget.cget('fg') == 'red':
                widget.destroy()
        etiqueta_error = tk.Label(modal, text=mensaje, font=("Helvetica", 12), fg= "red",  bg="#FFD966")
        etiqueta_error.pack(pady=5)
    
    def cerrar_modal(self, modal):
        modal.destroy()
        self.grab_set()

    def cerrar_ventana(self):
        """Cerrar y volver a la ventana de configuración"""
        if self.configuracion_window:
            self.grab_release()
            self.destroy()
            self.configuracion_window.deiconify()
        else:
            print("Error: configuracion_window es None")
