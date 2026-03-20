import tkinter as tk
from tkinter import ttk
from util.util_ventana import centrar_ventana
from util.util_mensaje import mostrar_mensaje
from datetime import datetime
import json
import serial

from util import sqlite as db_local

class ir_dietaWindow(tk.Toplevel):
    def __init__(self, master, datos_seleccionados, callback_volver, uart, num_corral=1):
        super().__init__(master)
        self.overrideredirect(True)
        self.uart = uart
        self.num_corral = int(num_corral)
        self.geometry("480x800")
        self.config(bg="#EF9480")
        self.resizable(False, False)
        centrar_ventana(self, 480, 800)
        self.mensaje_actual = None
        self.grab_set()
        self.datos_seleccionados = datos_seleccionados
        self.callback_volver = callback_volver

        # Frame logo
        self.frame_logo = tk.Frame(self, bg='#EF9480', height=100)
        self.frame_logo.pack(side=tk.TOP, fill="x", pady=22)
        self.crear_logo(self.frame_logo)

        # Selector de tipo de curva
        self.frame_selector = tk.Frame(self, bg='#EF9480', height=50)
        self.frame_selector.pack(side=tk.TOP, fill="x", pady=5)
        self.crear_selector_curva(self.frame_selector)

        # Selector de índice corporal (ELIMINADO por solicitud del usuario)
        # self.frame_indice = tk.Frame(self, bg='#EF9480', height=50)
        # self.frame_indice.pack(side=tk.TOP, fill="x", pady=5)
        # self.crear_indice_corporal(self.frame_indice)

        # Slider de peso
        self.frame_peso = tk.Frame(self, bg='#EF9480', height=50)
        self.frame_peso.pack(side=tk.TOP, fill="x", pady=20)
        self.crear_slider_peso(self.frame_peso)

        # Cantidad de dosis
        self.frame_dosis = tk.Frame(self, bg='#EF9480', height=50)
        self.frame_dosis.pack(side=tk.TOP, fill="x", pady=10)
        self.crear_frame_dosis(self.frame_dosis)

        # Intervalo
        self.frame_intervalo = tk.Frame(self, bg='#EF9480', height=50)
        self.frame_intervalo.pack(side=tk.TOP, fill="x", pady=10)
        self.crear_frame_intervalo(self.frame_intervalo)

        # Checkbox agua
        self.frame_agua = tk.Frame(self, bg="#EF9480")
        self.frame_agua.pack(fill="both", padx=20, pady=20)
        self.crear_checkbox_agua()

        # Botones inferiores
        self.frame_botones = tk.Frame(self, bg="#EF9480", height=120)
        self.frame_botones.pack(side=tk.BOTTOM, fill="x", pady=20, expand=True)

        boton_atras = tk.Button(self.frame_botones, text="<< Atrás",font=("Helvetica", 16),command=self.cerrar_ventana, bg="red",fg="#ffffff",bd=7)
        boton_atras.pack(side=tk.LEFT, padx=10, pady=10)

        boton_guardar = tk.Button(self.frame_botones,text="Guardar",font=("Helvetica", 16),command=self.guardar_y_volver,bg="red",fg="#ffffff",bd=7)
        boton_guardar.pack(side=tk.RIGHT, padx=10, pady=10)

    def crear_logo(self, frame):
        label = tk.Label(frame, image=self.master.logo, bg='#EF9480')
        label.place(relx=0.5, rely=0.5, anchor="center")

    def crear_selector_curva(self, frame):
        tipos_curva = ['Ascendente', 'Constante', 'Descendente', 'Forma V']
        label_curva = tk.Label(frame,text="Tipo de Curva:",font=("Helvetica", 14),bg='#EF9480',fg="black")
        label_curva.pack(side=tk.LEFT, padx=20)

        self.selector_curva = ttk.Combobox(frame,values=tipos_curva,font=("Helvetica", 12),state="readonly")
        self.selector_curva.set(tipos_curva[0])
        self.selector_curva.pack(side=tk.LEFT, padx=17)

    # def crear_indice_corporal(self, frame):
    #     indice_corporal = ['Gorda (50%)', 'Normal (100%)', 'Flaca (200%)']
    #     label_indice = tk.Label(frame,text="Índice Corporal:",font=("Helvetica", 14),bg='#EF9480',fg="black")
    #     label_indice.pack(side=tk.LEFT, padx=21)
    # 
    #     self.selector_indice = ttk.Combobox(frame,values=indice_corporal,font=("Helvetica", 12),state="readonly")
    #     self.selector_indice.set(indice_corporal[1])
    #     self.selector_indice.pack(side=tk.LEFT, padx=5)

    def crear_slider_peso(self, frame):
        frame_superior = tk.Frame(frame, bg='#EF9480')
        frame_superior.pack(side=tk.TOP, pady=10, anchor='w')

        label_peso = tk.Label(frame_superior,text="Peso diario:",font=("Helvetica", 14),bg='#EF9480',fg="black")
        label_peso.pack(side=tk.LEFT, padx=21)

        self.slider_peso = tk.Scale(frame_superior,from_=0,to=5,resolution=0.1,orient=tk.HORIZONTAL,bg='#c7baba',fg="black",troughcolor="grey",sliderrelief=tk.RAISED,highlightthickness=2,highlightbackground='#000000',font=("Helvetica", 12),length=240,command=self.actualizar_etiqueta_peso)
        self.slider_peso.pack(side=tk.LEFT, padx=10)

        frame_inferior = tk.Frame(frame, bg='#EF9480')
        frame_inferior.pack(side=tk.TOP, pady=5)

        self.label_peso = tk.Label(frame_inferior,text="0.0 kg",font=("Helvetica", 14),bg='#EF9480',fg="black")
        self.label_peso.pack(side=tk.TOP)

    def actualizar_etiqueta_peso(self, valor):
        self.label_peso.config(text=f"{float(valor):.1f} kg")

    def crear_frame_dosis(self, frame):
        frame_superior = tk.Frame(frame, bg='#EF9480')
        frame_superior.pack(side=tk.TOP, pady=10, anchor='w')

        label_dosis = tk.Label(frame_superior,text="Cantidad/Dosis: ",font=("Helvetica", 14),bg='#EF9480',fg="black")
        label_dosis.pack(side=tk.LEFT, padx=20)

        self.var_dosis = tk.IntVar(value=1)

        boton_menos = tk.Button(frame_superior,text="-",font=("Helvetica", 12),command=self.decrementar_dosis,bg="#FF6F61",fg="white",bd=5)
        boton_menos.pack(side=tk.LEFT, padx=10)

        self.label_dosis = tk.Label(frame_superior,textvariable=self.var_dosis,font=("Helvetica", 14),bg='#EF9480',fg="black")
        self.label_dosis.pack(side=tk.LEFT, padx=30)

        boton_mas = tk.Button(frame_superior,text="+",font=("Helvetica", 12),command=self.incrementar_dosis,bg="#FF6F61",fg="white",bd=5)
        boton_mas.pack(side=tk.LEFT, padx=10)

    def incrementar_dosis(self):
        if self.var_dosis.get() < 5:
            self.var_dosis.set(self.var_dosis.get() + 1)

    def decrementar_dosis(self):
        if self.var_dosis.get() > 1:
            self.var_dosis.set(self.var_dosis.get() - 1)

    def crear_frame_intervalo(self, frame):
        frame_superior = tk.Frame(frame, bg='#EF9480')
        frame_superior.pack(side=tk.TOP, pady=10, anchor='w')

        label_intervalo = tk.Label(frame_superior,text="Intervalo/Hora: ",font=("Helvetica", 14),bg='#EF9480',fg="black")
        label_intervalo.pack(side=tk.LEFT, padx=20)

        self.var_intervalo = tk.IntVar(value=1)

        boton_menos_intervalo = tk.Button(frame_superior,text="-",font=("Helvetica", 12),command=self.decrementar_intervalo,bg="#FF6F61",fg="white",bd=5)
        boton_menos_intervalo.pack(side=tk.LEFT, padx=22)

        self.label_intervalo = tk.Label(frame_superior,textvariable=self.var_intervalo,font=("Helvetica", 14),bg='#EF9480',fg="black")
        self.label_intervalo.pack(side=tk.LEFT, padx=19)

        boton_mas_intervalo = tk.Button(frame_superior,text="+",font=("Helvetica", 12),command=self.incrementar_intervalo,bg="#FF6F61",fg="white",bd=5)
        boton_mas_intervalo.pack(side=tk.LEFT, padx=20)

    def incrementar_intervalo(self):
        if self.var_intervalo.get() < 5:
            self.var_intervalo.set(self.var_intervalo.get() + 1)

    def decrementar_intervalo(self):
        if self.var_intervalo.get() > 1:
            self.var_intervalo.set(self.var_intervalo.get() - 1)

    def crear_checkbox_agua(self):
        frame_superior_agua = tk.Frame(self.frame_agua, bg="#EF9480")
        frame_superior_agua.pack(side=tk.TOP, pady=10, anchor='w')

        label_agua = tk.Label(frame_superior_agua,text="Agregar/Agua:",font=("Helvetica", 14),bg="#EF9480",fg="black")
        label_agua.pack(side=tk.LEFT, padx=0)

        self.var_agua = tk.IntVar()
        self.check_agua = tk.Checkbutton(frame_superior_agua,variable=self.var_agua,bg="#EF9480",font=("Helvetica", 26),highlightthickness=0,bd=0,selectcolor="#EF9480",relief="flat",activebackground="#EF9480")
        self.check_agua.pack(side=tk.LEFT, padx=111)

    def cerrar_ventana(self):
        self.grab_release()
        self.destroy()
        self.callback_volver()

    def mostrar_mensaje(self, titulo, texto, tipo="error", callback=None):
        import util.util_mensaje
        util.util_mensaje.mostrar_mensaje(self, titulo, texto, tipo, callback)

    def calcular_crc16(self, data_str):
        """Calcula el CRC-16 Modbus (polinomio 0xA001) para una cadena de texto."""
        crc = 0xFFFF
        for byte in data_str.encode('utf-8'):
            crc ^= byte
            for _ in range(8):
                if crc & 1:
                    crc = (crc >> 1) ^ 0xA001
                else:
                    crc >>= 1
        return crc

    def enviar_y_esperar_ok(self, mensaje_str, reintentos=3, timeout_segundos=1.5):
        """Envía un mensaje por UART y espera la respuesta 'ANIMAL_RECEIVED' u 'OK'."""
        ser = self.uart
        if ser is None:
            print("No hay puerto serie configurado en self.uart")
            # Intento de fallback local si self.uart vino None
            try:
                ser = serial.Serial("/dev/serial0", 9600, timeout=timeout_segundos)
                cierro_local = True
            except Exception as e:
                print("Fallo al abrir puerto serie local: ", e)
                return False
        else:
            cierro_local = False
            original_timeout = ser.timeout
            ser.timeout = timeout_segundos

        exito = False
        import time

        for intento in range(reintentos):
            try:
                ser.reset_input_buffer()
                ser.write(mensaje_str.encode('utf-8'))
                print(f"[UART Dieta] Intento {intento+1}/{reintentos} enviando: {mensaje_str}")

                start_time = time.time()
                while time.time() - start_time < timeout_segundos:
                    linea = ser.readline()
                    if linea:
                        resp = linea.decode('utf-8', errors='ignore').strip()
                        print(f"[UART Dieta] Respuesta ESP: {resp}")
                        if "ANIMAL_RECEIVED" in resp or "OK_RECEIVED" in resp or "OK" in resp:
                            exito = True
                            break
            except Exception as e:
                print(f"[UART Dieta] Error en el envío/recepción: {e}")

            if exito:
                break
            
            time.sleep(0.5)

        if cierro_local:
            ser.close()
        else:
            ser.timeout = original_timeout
            
        return exito

    def guardar_y_volver(self):
        try:
            if not self.datos_seleccionados:
                self.mostrar_mensaje("Error", "No hay animales seleccionados.", "error")
                return

            tipo_curva_str = self.selector_curva.get()
            # Mapeo de la curva a valores enteros 0..3
            mapa_curvas = {'Ascendente': 0, 'Constante': 1, 'Descendente': 2, 'Forma V': 3}
            curva_int = mapa_curvas.get(tipo_curva_str, 1)

            peso_float = float(self.slider_peso.get())      # kg
            peso = int(peso_float * 10)                     # décimas de kg
            dosis = self.var_dosis.get()
            intervalo = self.var_intervalo.get()
            agua = self.var_agua.get()

            # Validaciones mínimas
            if peso <= 0:
                self.mostrar_mensaje("Error", "El peso diario debe ser mayor que 0.", "error")
                return
            if dosis < 1:
                self.mostrar_mensaje("Error", "La cantidad de dosis debe ser al menos 1.", "error")
                return

            # Para no romper base local dejaremos indice predeterminado ya que se quitó del UI
            indice_corporal = "Normal"
            descripcion = f"{tipo_curva_str} - {indice_corporal}"

            corral_val = self.num_corral

            # Armar arreglo de caravanas
            lista_caravanas = []
            for caravana, inseminacion in self.datos_seleccionados:
                lista_caravanas.append(caravana)

            # 1. Componer el JSON general tarea 20
            data_json = {
                "tarea": 20,
                "corral": corral_val,
                "curva": curva_int,
                "peso": peso,
                "dosis": dosis,
                "intervalo": intervalo,
                "agua": agua,
                "animales": lista_caravanas
            }

            json_str = json.dumps(data_json)
            crc_val = self.calcular_crc16(json_str)
            mensaje_json = f"<<<{json_str}>>>|CRC:{crc_val:04X}"

            # 2. Enviar y esperar OK (3 reintentos)
            exito_uart = self.enviar_y_esperar_ok(mensaje_json, reintentos=3, timeout_segundos=1.5)

            if not exito_uart:
                self.mostrar_mensaje(
                    "Error de Comunicación", 
                    "Error de comunicacion. Los datos de la dieta no fueron almacenados.", 
                    "error"
                )
                return

            # 3. Si llega el OK, procesar guardado SQLite local
            id_dieta = db_local.insertarDietaConfig(
                descripcion=descripcion,
                pesoTotal=peso,
                cantidadDosis=dosis,
                intervalo=intervalo,
                tirarAgua=agua
            )

            for caravana, inseminacion in self.datos_seleccionados:
                db_local.actualizarDietaPorCaravanaYFecha(
                    caravana=caravana,
                    fechaInseminacion=inseminacion,
                    idDieta=id_dieta
                )

            self.mostrar_mensaje("Guardado", "La dieta se guardó en SQLite y se envió al equipo.", "info", callback=self.cerrar_ventana)

        except Exception as e:
            print(f"Error al guardar y volver: {e}")
            self.grab_release()
            self.mostrar_mensaje("Error", f"Ocurrió un error al guardar los cambios, se rompio aca: {e}", "error")
            #self.destroy()
            self.callback_volver()
