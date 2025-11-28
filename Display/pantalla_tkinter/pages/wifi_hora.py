import tkinter as tk
from tkinter import ttk
import util.util_ventana as util_ventana
from util.util_calendario import seleccionar_fecha
from util.util_hora import seleccionar_hora
from util.teclado import TecladoWindow
import datetime
import json
import serial
from util import sqlite as db_local


class WifiHoraWindow(tk.Toplevel):
    def __init__(self, master, configuracion_window):
        super().__init__(master)
        self.master = master
        self.master_panel_ref = self.master.master
        self.configuracion_window = configuracion_window
        self.overrideredirect(True)
        util_ventana.centrar_ventana(self, 480, 800)
        self.config(bg="#EF9480")
        self.resizable(False, False)
        self.grab_set()

        # Frame logo
        self.frame_logo = tk.Frame(self, bg='#EF9480', height=100)
        self.frame_logo.pack(side=tk.TOP, fill="x", pady=22)
        self.crear_logo(self.frame_logo)

        # Frame selector WiFi
        self.frame_wifi = tk.Frame(self, bg='#EF9480', height=50)
        self.frame_wifi.pack(side=tk.TOP, fill="x", pady=6)
        self.selector_wifi(self.frame_wifi)

        # Frame contraseña
        self.frame_contraseña = tk.Frame(self, bg='#EF9480', height=50)
        self.frame_contraseña.pack(side=tk.TOP, fill="x", pady=6)
        self.selector_contraseña(self.frame_contraseña)

        # Frame botón conectar
        self.frame_boton = tk.Frame(self, bg='#EF9480', height=50)
        self.frame_boton.pack(side=tk.TOP, fill="x", pady=6)
        self.boton_conectar(self.frame_boton)

        # Frame botón sincronizar fecha/hora
        self.frame_sincronizar = tk.Frame(self, bg='#EF9480', height=50)
        self.frame_sincronizar.pack(side=tk.TOP, fill="x", pady=6)
        self.boton_sincronizar(self.frame_sincronizar)

        # Frame fecha
        self.frame_fecha = tk.Frame(self, bg='#EF9480', height=50)
        self.frame_fecha.pack(side=tk.TOP, fill="x", pady=6)
        self.boton_fecha(self.frame_fecha)

        # Frame hora
        self.frame_hora = tk.Frame(self, bg='#EF9480', height=50)
        self.frame_hora.pack(side=tk.TOP, fill="x", pady=6)
        self.boton_hora(self.frame_hora)

        # Frame botones finales
        self.frame_botones_finales = tk.Frame(self, bg='#EF9480')
        self.frame_botones_finales.pack(side=tk.BOTTOM, fill="x", pady=68)

        boton_atras = tk.Button(
            self.frame_botones_finales,
            text="<< Atrás",
            font=("Helvetica", 16),
            command=self.cerrar_ventana,
            bg="red",
            fg="#ffffff",
            bd=7
        )
        boton_atras.pack(side=tk.LEFT, padx=10, pady=2)

        boton_guardar = tk.Button(
            self.frame_botones_finales,
            text="Guardar",
            font=("Helvetica", 16),
            command=self.guardar,
            bg="red",
            fg="#ffffff",
            bd=7
        )
        boton_guardar.pack(side=tk.RIGHT, padx=10, pady=2)

        # Cargar WiFi y contraseña guardados en SQLite (si existen)
        self._cargar_wifi_desde_sqlite()

    def crear_logo(self, frame):
        label = tk.Label(frame, image=self.master.logo, bg='#EF9480')
        label.place(relx=0.5, rely=0.5, anchor="center")

    def selector_wifi(self, frame):
        label_wifi = tk.Label(
            frame,
            text="Red Wifi:",
            font=("Helvetica", 14),
            bg='#EF9480',
            fg="black"
        )
        label_wifi.pack(side=tk.LEFT, padx=20)

        self.entry_wifi = tk.Entry(frame, font=("Helvetica", 14), width=18)
        self.entry_wifi.pack(side=tk.LEFT, padx=22)
        self.entry_wifi.bind("<Button-1>", lambda e: self.abrir_teclado(self.entry_wifi))

    def selector_contraseña(self, frame):
        label_contraseña = tk.Label(
            frame,
            text="Contraseña:",
            font=("Helvetica", 14),
            bg='#EF9480',
            fg="black"
        )
        label_contraseña.pack(side=tk.LEFT, padx=20)

        self.entry_contraseña = tk.Entry(frame, font=("Helvetica", 14), show="*", width=18)
        self.entry_contraseña.pack(side=tk.LEFT, padx=0)
        self.entry_contraseña.bind("<Button-1>", lambda e: self.abrir_teclado(self.entry_contraseña))

    def abrir_teclado(self, target_entry):
        TecladoWindow(self, target_entry)

    def boton_conectar(self, frame):
        boton_conectar = tk.Button(
            frame,
            text=" Conectar ",
            font=("Helvetica", 16),
            command=self.conectar,
            bg="red",
            fg="#ffffff",
            bd=7
        )
        boton_conectar.pack(side=tk.BOTTOM, padx=10, pady=6)

    def conectar(self):
        """Simulación de conectar (por ahora solo imprime)."""
        red_wifi = self.entry_wifi.get()
        contraseña = self.entry_contraseña.get()
        print(f"Conectando a {red_wifi} con la contraseña {contraseña}")


    def boton_sincronizar(self, frame):
        boton_sincronizar = tk.Button(
            frame,
            text="Sincronizar",
            font=("Helvetica", 16),
            command=self.sincronizar,
            bg="red",
            fg="#ffffff",
            bd=7
        )
        boton_sincronizar.pack(side=tk.TOP, pady=6)

    def boton_fecha(self, frame):
        self.fecha_seleccionada = tk.StringVar()
        self.fecha_seleccionada.set("")

        boton_fecha = tk.Button(
            frame,
            text="Seleccionar Fecha",
            font=("Helvetica", 16),
            command=lambda: seleccionar_fecha(self, self.fecha_seleccionada),
            bg="red",
            fg="#ffffff",
            bd=7
        )
        boton_fecha.pack(side=tk.LEFT, padx=10, pady=6)

        self.entry_fecha = tk.Entry(
            frame,
            textvariable=self.fecha_seleccionada,
            font=("Helvetica", 16),
            width=10,
            state="readonly"
        )
        self.entry_fecha.pack(side=tk.LEFT, padx=8, pady=6)

    def boton_hora(self, frame):
        self.hora_seleccionada = tk.StringVar()
        self.hora_seleccionada.set("")

        boton_hora = tk.Button(
            frame,
            text="Seleccionar Hora  ",
            font=("Helvetica", 16),
            command=lambda: seleccionar_hora(self, self.hora_seleccionada),
            bg="red",
            fg="#ffffff",
            bd=7
        )
        boton_hora.pack(side=tk.LEFT, padx=10, pady=6)

        self.entry_hora = tk.Entry(
            frame,
            textvariable=self.hora_seleccionada,
            font=("Helvetica", 16),
            width=10,
            state="readonly"
        )
        self.entry_hora.pack(side=tk.LEFT, padx=11, pady=6)

    def guardar(self):
        """Guarda la config de WiFi en SQLite y cierra la ventana."""
        red_wifi = self.entry_wifi.get().strip()
        contraseña = self.entry_contraseña.get().strip()
        fecha = self.fecha_seleccionada.get()
        hora = self.hora_seleccionada.get()

        print(f"Configuración guardada: \nRed Wifi: {red_wifi}\nContraseña: {contraseña}\nFecha: {fecha}\nHora: {hora}")

        try:
            db_local.guardarWifi(red_wifi, contraseña)
        except Exception as e:
            print(f"Error guardando WiFi en SQLite: {e}")

        self.cerrar_ventana()

    def sincronizar(self):
        """Sincroniza la fecha/hora con el ESP32 y con el panel principal."""
        fecha = self.fecha_seleccionada.get()
        hora = self.hora_seleccionada.get()
        if fecha and hora:
            self.enviar_timestamp(fecha, hora)
            fecha_hora_str = f"{fecha} {hora}"
            dt = datetime.datetime.strptime(fecha_hora_str, "%Y-%m-%d %H:%M")
            self.master_panel_ref.forzar_hora(dt)
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

    def _cargar_wifi_desde_sqlite(self):
        """Pre-carga nombre y contraseña de WiFi almacenados."""
        try:
            nombre_wifi, pass_wifi = db_local.obtenerWifi()
        except Exception as e:
            print("Error leyendo WiFi desde SQLite:", e)
            nombre_wifi = None
            pass_wifi = None

        if nombre_wifi:
            self.entry_wifi.delete(0, tk.END)
            self.entry_wifi.insert(0, nombre_wifi)

        if pass_wifi:
            self.entry_contraseña.delete(0, tk.END)
            self.entry_contraseña.insert(0, pass_wifi)

    def cerrar_ventana(self):
        """Cerrar la ventana de Wifi y Hora"""
        self.grab_release()
        self.destroy()
        self.configuracion_window.deiconify()
