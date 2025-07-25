import tkinter as tk
from tkinter import ttk
import util.util_ventana as util_ventana
from util.util_calendario import seleccionar_fecha
from util.util_hora import seleccionar_hora
from util.teclado import TecladoWindow
import datetime
import json 
import serial

class WifiHoraWindow(tk.Toplevel):
    def __init__(self, master, configuracion_window):
        super().__init__(master)
        self.master = master
        self.configuracion_window = configuracion_window
        self.overrideredirect(True)
        util_ventana.centrar_ventana(self, 480, 800)
        self.config(bg="#EF9480")
        self.resizable(False, False)
        self.grab_set()

        # Crear un frame para el logo en la parte superior
        self.frame_logo = tk.Frame(self, bg='#EF9480', height=100)
        self.frame_logo.pack(side=tk.TOP, fill="x",pady=22)
        
        # Crear el logo en la ventana secundaria
        self.crear_logo(self.frame_logo)

        # Crear un frame para el selector de red wifi
        self.frame_wifi = tk.Frame(self, bg='#EF9480',height=50)
        self.frame_wifi.pack(side=tk.TOP, fill="x",pady=6)
        self.selector_wifi(self.frame_wifi)

        #Crear un frame para el selector de contraseña
        self.frame_contraseña = tk.Frame(self, bg='#EF9480',height=50)
        self.frame_contraseña.pack(side=tk.TOP, fill="x",pady=6)
        self.selector_contraseña(self.frame_contraseña)

        #Crear un frame para el boton de conectar
        self.frame_boton = tk.Frame(self, bg='#EF9480',height=50)
        self.frame_boton.pack(side=tk.TOP, fill="x",pady=6)
        self.boton_conectar(self.frame_boton)

        #Crear un frame para el boton Sincronizar fecha y hora
        self.frame_sincronizar = tk.Frame(self, bg='#EF9480',height=50)
        self.frame_sincronizar.pack(side=tk.TOP, fill="x",pady=6)
        self.boton_sincronizar(self.frame_sincronizar)

        #Crear un frame para la fecha y el Entry
        self.frame_fecha = tk.Frame(self, bg='#EF9480',height=50)
        self.frame_fecha.pack(side=tk.TOP, fill="x",pady=6)
        self.boton_fecha(self.frame_fecha)

        #Crear un frame para el Entry de la hora
        self.frame_hora = tk.Frame(self, bg='#EF9480',height=50)
        self.frame_hora.pack(side=tk.TOP, fill="x",pady=6)
        self.boton_hora(self.frame_hora)

        # Crear un frame para los botones "Guardar" y "Atrás" en la misma línea
        self.frame_botones_finales = tk.Frame(self, bg='#EF9480')
        self.frame_botones_finales.pack(side=tk.BOTTOM, fill="x", pady=68)

        # Botón "Atrás"
        boton_atras = tk.Button(self.frame_botones_finales, text="<< Atrás", font=("Helvetica", 16), command=self.cerrar_ventana, bg="red", fg="#ffffff", bd=7)
        boton_atras.pack(side=tk.LEFT, padx=10, pady=2)

        # Botón "Guardar"
        boton_guardar = tk.Button(self.frame_botones_finales, text="Guardar", font=("Helvetica", 16), command=self.guardar, bg="red", fg="#ffffff", bd=7)
        boton_guardar.pack(side=tk.RIGHT, padx=10, pady=2)

    def crear_logo(self, frame):
        """Función para crear y ubicar el logo en un frame dado"""
        label = tk.Label(frame, image=self.master.logo, bg='#EF9480')
        label.place(relx=0.5, rely=0.5, anchor="center")
    
    def selector_wifi(self, frame):
        """Función para crear y ubicar el selector de red wifi en un frame dado"""
        redes_wifi = ['','ByNInvitados','Termoplast','Nueva']
        label_wifi = tk.Label (frame, text="Red Wifi:", font=("Helvetica", 14),bg='#EF9480',fg="black")
        label_wifi.pack(side=tk.LEFT, padx=20)

        self.entry_wifi = tk.Entry(frame, font=("Helvetica", 14), width=18)
        self.entry_wifi.pack(side=tk.LEFT, padx=22)
        # Configurar el evento de clic para abrir el teclado
        self.entry_wifi.bind("<Button-1>", lambda e: self.abrir_teclado(self.entry_wifi))

    def selector_contraseña(self, frame):
        """Función para crear y ubicar el selector de contraseña en un frame dado"""
        label_contraseña = tk.Label(frame, text="Contraseña:", font=("Helvetica", 14), bg='#EF9480', fg="black")
        label_contraseña.pack(side=tk.LEFT, padx=20)

        self.entry_contraseña = tk.Entry(frame, font=("Helvetica", 14), show="*", width=18)
        self.entry_contraseña.pack(side=tk.LEFT, padx=0)       
        # Configurar el evento de clic para abrir el teclado
        self.entry_contraseña.bind("<Button-1>", lambda e: self.abrir_teclado(self.entry_contraseña))

    def abrir_teclado(self, target_entry):
        # Crear el teclado sin deshabilitar la ventana principal
        teclado = TecladoWindow(self, target_entry)

    def actualizar_contraseñas(self, event):
        """Función para actualizar las contraseñas según la red WiFi seleccionada"""
        red_seleccionada = self.combo_wifi.get()
        contraseñas = {'ByNInvitados': '12345678', 'Termoplast': 'admin123', 'Nueva': 'nueva123'}
        # No se usa combobox para contraseñas, pero podemos prellenar el campo si lo deseas
        self.entry_contraseña.delete(0, tk.END)  # Limpiar el campo
        self.entry_contraseña.insert(0, contraseñas.get(red_seleccionada, ''))

    def boton_conectar(self, frame):
        """Función para crear y ubicar el botón de conectar en un frame dado"""
        boton_conectar = tk.Button(frame, text=" Conectar ", font=("Helvetica", 16), command=self.conectar, bg="red", fg="#ffffff", bd=7)
        boton_conectar.pack(side=tk.BOTTOM, padx=10, pady=6)

    def conectar(self, frame):
        """Función para manejar la acción de conectar"""
        red_wifi = self.combo_wifi.get()
        contraseña = self.entry_contraseña.get()
        print(f"Conectando a {red_wifi} con la contraseña {contraseña}")

    def boton_sincronizar(self,frame):
        """Función para manejar la acción de sincronizar hora y fecha"""
        boton_sincronizar = tk.Button(frame, text="Sincronizar", font=("Helvetica", 16), command=self.sincronizar, bg="red", fg="#ffffff", bd=7)
        boton_sincronizar.pack(side=tk.TOP, pady=6)

    def boton_fecha(self, frame):
        """Función para crear el botón de fecha y el Entry para mostrar la fecha seleccionada"""
        # Variable para almacenar la fecha seleccionada
        self.fecha_seleccionada = tk.StringVar()
        self.fecha_seleccionada.set("")  # Valor inicial

        # Botón para abrir el calendario
        boton_fecha = tk.Button(frame, text="Seleccionar Fecha", font=("Helvetica", 16),command=lambda: seleccionar_fecha(self, self.fecha_seleccionada), bg="red", fg="#ffffff", bd=7)
        boton_fecha.pack(side=tk.LEFT, padx=10, pady=6)

        # Entry para mostrar la fecha seleccionada
        self.entry_fecha = tk.Entry(frame, textvariable=self.fecha_seleccionada, font=("Helvetica", 16),width=10, state="readonly")
        self.entry_fecha.pack(side=tk.LEFT, padx=8, pady=6)
    
    def boton_hora(self, frame):
        """Función para crear el botón de hora y el Entry para mostrar la hora seleccionada"""
        # Variable para almacenar la hora seleccionada
        self.hora_seleccionada = tk.StringVar()
        self.hora_seleccionada.set("")  # Valor inicial

        # Botón para abrir el selector de hora
        boton_hora = tk.Button(frame, text="Seleccionar Hora  ", font=("Helvetica", 16),command=lambda: seleccionar_hora(self, self.hora_seleccionada), bg="red", fg="#ffffff", bd=7)
        boton_hora.pack(side=tk.LEFT, padx=10, pady=6)

        # Entry para mostrar la hora seleccionada
        self.entry_hora = tk.Entry(frame, textvariable=self.hora_seleccionada, font=("Helvetica", 16),width=10, state="readonly")
        self.entry_hora.pack(side=tk.LEFT, padx=11, pady=6)

    def boton_guardar(self, frame):
        """Función para crear el botón de guardar configuración"""
        boton_guardar = tk.Button(frame, text=" Guardar ", font=("Helvetica", 16), command=self.guardar, bg="red", fg="#ffffff", bd=7)
        boton_guardar.pack(side=tk.TOP, padx=10, pady=20)
    
    def guardar(self):
        """Función para guardar los datos configurados"""
        # Obtener los valores de los controles de la ventana
        red_wifi = self.combo_wifi.get()
        contraseña = self.entry_contraseña.get()
        fecha = self.fecha_seleccionada.get()
        hora = self.hora_seleccionada.get()

        # Aquí puedes implementar cualquier lógica para guardar los datos (puedes imprimirlos o guardarlos en un archivo o base de datos)
        print(f"Configuración guardada: \nRed Wifi: {red_wifi}\nContraseña: {contraseña}\nFecha: {fecha}\nHora: {hora}")

        # Cerrar la ventana de WifiHoraWindow y regresar a la pantalla de Configuración
        self.cerrar_ventana()
    def sincronizar(self):
        """Función para manejar la acción de sincronizar hora y fecha"""
        fecha = self.fecha_seleccionada.get()
        hora = self.hora_seleccionada.get()
        if fecha and hora:
            self.enviar_timestamp(fecha, hora)
        else:
            print("Debes seleccionar fecha y hora antes de sincronizar.")
            
    def enviar_timestamp(self, fecha_str, hora_str):
        try:
            fecha_hora_str = f"{fecha_str} {hora_str}"
            dt = datetime.datetime.strptime(fecha_hora_str, "%Y-%m-%d %H:%M")
            timestamp = int(dt.timestamp())
            json_timestamp = json.dumps({"timestamp": timestamp})
            mensaje = f"<<<{json_timestamp}>>>"
            ser = serial.Serial('/dev/serial0', 9600, timeout=1)
            ser.write(mensaje.encode())
            ser.close()
            print("Timestamp enviado:", timestamp)
            print("JSON enviado:", mensaje)
        except Exception as e:
            print("Error al enviar timestamp:", e)

    def cerrar_ventana(self):
        """Cerrar la ventana de Wifi y Hora"""
        self.grab_release()
        self.destroy()
        self.configuracion_window.deiconify()
