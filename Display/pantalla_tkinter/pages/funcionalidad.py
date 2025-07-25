import tkinter as tk
from tkinter import ttk
from util.util_mensaje import mostrar_mensaje
import pages.curva_alimentacion as curva_alimentacion
import util.util_ventana as util_ventana
from util.util_teclado3 import TecladoFuncionalidadWindow
from util.teclado import TecladoWindow
from pages.curva_alimentacion import obtener_lista_curvas
from util.util_teclado4 import TecladoNumerico4
import serial
import json
import os
import time
import threading

def enviar_por_uart(config_obj, puerto='/dev/serial0', baud=9600):
    try:
        ser = serial.Serial(port=puerto, baudrate=baud, timeout=1)
        time.sleep(2)
        mensaje = '<<<' + json.dumps(config_obj) + '>>>'
        ser.write(mensaje.encode('utf-8'))
        respuesta = ser.readline().decode('utf-8').strip()
        print('ESP32 respondio:', respuesta)
    except Exception as e:
        print('Error UART:', e)
    finally:
        try:
            ser.close()
        except:
            pass
            
def inicializar_curvas_fijas():
    #import pages.curva_alimentacion import cargar_todas_curvas
    DIR_CONFIG = "config"
    ARCHIVO_CURVAS = "curvas.json"
    curvas_fijas = [
        {"nombre": "mod1", "segmentos": [{"dia": 1, "indice": "100%"}]},
        {"nombre": "mod2", "segmentos": [{"dia": 1, "indice": "100%"}]},
        {"nombre": "curva1", "segmentos": [{"dia": 1, "indice": "50%"}]},
        {"nombre": "curva2", "segmentos": [{"dia": 1, "indice": "50%"}, {"dia": 113, "indice": "100%"}]},
        {"nombre": "curva3", "segmentos": [{"dia": 1, "indice": "100%"}, {"dia": 113, "indice": "50%"}]}
    ]
    try:
        curvas = curvas_alimentacion.cargar_todas_curvas()
        nombres = {c["nombre"].strip().lower().replace(" ", "") for c in curvas}
        for f in curvas_fijas:
            key = f["nombre"].strip().lower().replace(" ", "")
            if key not in nombres:
                curvas.append(f)
        os.makedirs(DIR_CONFIG, exist_ok=True)
        with open(os.path.join(DIR_CONFIG, ARCHIVO_CURVAS), 'w', encoding='utf-8') as w:
            json.dump(curvas, w, indent=4, ensure_ascii=False)
    except Exception as e:
        print("Error inicializando curvas fijas:", e)

class FuncionalidadWindow(tk.Toplevel):
    def __init__(self, master,logo):
        super().__init__(master)
        self.master = master
        self.logo = logo
        self.overrideredirect(True)
        inicializar_curvas_fijas()
        util_ventana.centrar_ventana(self, 480, 800) 
        self.config(bg="#EF9480")
        self.resizable(False, False)
        self.grab_set()        
        self.crear_logo()
        self.bind("<Escape>", lambda e: self.cerrar_ventana())

        # Crear los frames para los elementos de funcionalidad
        self.frame_calibracion_motor = tk.Frame(self, bg='#EF9480', height=40)
        self.frame_calibracion_motor.pack(side=tk.TOP, fill="x", pady=5)
        self.crear_calibracion_motor(self.frame_calibracion_motor)
        self.frame_calibracion_agua = tk.Frame(self, bg='#EF9480', height=40)
        self.frame_calibracion_agua.pack(side=tk.TOP, fill="x", pady=5)
        self.crear_calibracion_agua(self.frame_calibracion_agua)
        # Crear el slider para "Caravana Desconocida"
        self.frame_caravana_desconocida = tk.Frame(self, bg='#EF9480', height=40)
        self.frame_caravana_desconocida.pack(side=tk.TOP, fill="x", pady=5)
        self.crear_slider_caravana(self.frame_caravana_desconocida)
        # Frame para el selector de caravanas
        self.frame_caravanas_libres = tk.Frame(self, bg='#EF9480', height=40)
        self.frame_caravanas_libres.pack(side=tk.TOP, fill="x", pady=5)
        self.crear_caravanas_libres(self.frame_caravanas_libres)
        # Crear el frame para el índice corporal
        self.frame_indice_corporal = tk.Frame(self, bg='#EF9480', height=40)
        self.frame_indice_corporal.pack(side=tk.TOP, fill="x", pady=5)
        self.crear_indice_corporal(self.frame_indice_corporal)
        # Nuevo Frame para el menú desplegable con los botones + y -
        self.frame_curva_alimentacion = tk.Frame(self, bg='#EF9480', height=40)
        self.frame_curva_alimentacion.pack(side=tk.TOP, fill="x", pady=5)
        self.crear_curva_alimentacion(self.frame_curva_alimentacion)
        # Crear un frame para los botones "Guardar" y "Atrás" en la misma línea
        self.frame_botones_finales = tk.Frame(self, bg='#EF9480')
        self.frame_botones_finales.pack(side=tk.BOTTOM, fill="x", pady=70)
        # Botón "Atrás"
        boton_atras = tk.Button(self.frame_botones_finales, text="<< Atrás", font=("Helvetica", 16), command=self.cerrar_ventana, bg="red", fg="#ffffff", bd=7)
        boton_atras.pack(side=tk.LEFT, padx=10)
        # Botón "Guardar"
        boton_guardar = tk.Button(self.frame_botones_finales, text="Guardar", font=("Helvetica", 16), command=self.guardar, bg="red", fg="#ffffff", bd=7)
        boton_guardar.pack(side=tk.RIGHT, padx=10)

    def crear_logo(self):
        """Función para crear y ubicar el logo en un frame dado"""
        self.frame_logo = tk.Frame(self, bg='#EF9480', height=100)
        self.frame_logo.pack(side=tk.TOP, fill="x", pady=22)
        label = tk.Label(self.frame_logo, image=self.master.logo, bg='#EF9480')
        label.place(relx=0.5, rely=0.5, anchor="center")
    
    def crear_calibracion_motor(self, frame):
        """Función para crear los controles de calibración del motor con botones + y -"""
        frame_superior_motor = tk.Frame(frame, bg='#EF9480')
        frame_superior_motor.pack(side=tk.TOP, pady=10, anchor='w')

        # Etiqueta para "Calibración Motor"
        label_motor = tk.Label(frame_superior_motor, text="Calibración Motor:", font=("Helvetica", 14), bg='#EF9480', fg="black")
        label_motor.pack(side=tk.LEFT, padx=20)
        # Variables para manejar el valor de calibración del motor
        self.var_calibracion_motor = tk.IntVar(value=0)  # Valor inicial del motor
        # Crear botones para disminuir y aumentar el valor de calibración
        frame_botones_motor = tk.Frame(frame_superior_motor, bg='#EF9480')
        frame_botones_motor.pack(side=tk.LEFT)
        boton_disminuir_motor = tk.Button(frame_botones_motor, text="-", font=("Helvetica", 16), command=lambda: self.modificar_calibracion(self.var_calibracion_motor, -1), bg="#F2B1A1", fg="black", bd=5)
        boton_disminuir_motor.pack(side=tk.LEFT)
        # Etiqueta para mostrar el valor actual de la calibración del motor
        self.label_motor = tk.Label(frame_botones_motor, textvariable=self.var_calibracion_motor, font=("Helvetica", 14), bg='#EF9480', fg="black")
        self.label_motor.pack(side=tk.LEFT, padx=20)
        boton_aumentar_motor = tk.Button(frame_botones_motor, text="+", font=("Helvetica", 16), command=lambda: self.modificar_calibracion(self.var_calibracion_motor, 1), bg="#F2B1A1", fg="black", bd=5)
        boton_aumentar_motor.pack(side=tk.LEFT)
               
    def crear_calibracion_agua(self, frame):
        """Función para crear los controles de calibración de agua con botones + y -"""
        frame_superior_agua = tk.Frame(frame, bg='#EF9480')
        frame_superior_agua.pack(side=tk.TOP, pady=6, anchor='w')

        # Etiqueta para "Calibración Agua"
        label_agua = tk.Label(frame_superior_agua, text="Calibración Agua:", font=("Helvetica", 14), bg='#EF9480', fg="black")
        label_agua.pack(side=tk.LEFT, padx=22)
        # Variables para manejar el valor de calibración del agua
        self.var_calibracion_agua = tk.IntVar(value=0)

        # Crear botones para disminuir y aumentar el valor de calibración
        frame_botones_agua = tk.Frame(frame_superior_agua, bg='#EF9480')
        frame_botones_agua.pack(side=tk.LEFT)
        boton_disminuir_agua = tk.Button(frame_botones_agua, text="-", font=("Helvetica", 16), command=lambda: self.modificar_calibracion(self.var_calibracion_agua, -1), bg="#F2B1A1", fg="black", bd=5)
        boton_disminuir_agua.pack(side=tk.LEFT)

        # Etiqueta para mostrar el valor actual de la calibración del agua
        self.label_agua = tk.Label(frame_botones_agua, textvariable=self.var_calibracion_agua, font=("Helvetica", 14), bg='#EF9480', fg="black")
        self.label_agua.pack(side=tk.LEFT, padx=20)
        boton_aumentar_agua = tk.Button(frame_botones_agua, text="+", font=("Helvetica", 16), command=lambda: self.modificar_calibracion(self.var_calibracion_agua, 1), bg="#F2B1A1", fg="black", bd=5)
        boton_aumentar_agua.pack(side=tk.LEFT)

    def crear_slider_caravana(self, frame):
        """Función para crear el slider de "Caravana Desconocida" con un estilo similar al slider en ir_dieta.py"""
        frame_slider_caravana = tk.Frame(frame, bg='#EF9480')
        frame_slider_caravana.pack(side=tk.TOP, pady=10, anchor="w")

        # Etiqueta para "Caravana Desconocida"
        label_caravana = tk.Label(frame_slider_caravana, text="Caravana/Desc:", font=("Helvetica", 14), bg='#EF9480', fg="black")
        label_caravana.pack(side=tk.LEFT, padx=20)
        # Variable para manejar el valor del slider
        self.var_caravana_desconocida = tk.DoubleVar(value=0.0)  # Valor inicial del slider

        # Crear el slider con un diseño similar al de ir_dieta.py
        self.slider_caravana = tk.Scale(frame_slider_caravana, from_=0, to=5, orient="horizontal", variable=self.var_caravana_desconocida, resolution=0.1, length=200, sliderlength=20, troughcolor="grey", bg='#c7baba', activebackground='#F2B1A1', font=("Helvetica", 12), highlightbackground='#000000',highlightthickness=2)
        self.slider_caravana.pack(side=tk.LEFT, padx=0)
        # Crear un frame para la etiqueta del valor
        frame_inferior = tk.Frame(frame, bg='#EF9480')
        frame_inferior.pack(side=tk.TOP, pady=5)

        # Crear una etiqueta para mostrar el valor con unidades
        self.label_slider_caravana = tk.Label(frame_inferior, text="0.0 kg", font=("Helvetica", 14), bg='#EF9480', fg="black")
        self.label_slider_caravana.pack(side=tk.TOP)
        # Actualizar el valor mostrado en el label cada vez que se mueva el slider
        self.slider_caravana.bind("<Motion>", self.actualizar_label_caravana)

    def actualizar_label_caravana(self, event):
        """Actualizar el valor del label cuando se mueve el slider"""
        valor = self.var_caravana_desconocida.get()
        self.label_slider_caravana.config(text=f"Valor: {valor:.1f} kg")

    def crear_caravanas_libres(self, frame):
        """Función para crear y ubicar el selector de caravana en un frame dado"""
        # Intentar cargar caravanas existentes del archivo JSON
        try:
            import json
            import os
            config_path = os.path.join("config", "configuracion_sistema.json")
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config_data = json.load(f)
                    self.lista_caravanas_libres = config_data.get("caravanas_libres", [''])
            else:
                self.lista_caravanas_libres = ['']
        except Exception as e:
            self.lista_caravanas_libres = ['']

        # Frame para los selectores y botones
        frame_selectores = tk.Frame(frame, bg='#EF9480')
        frame_selectores.pack(side=tk.TOP, fill="x", pady=10)
        # Etiqueta para el selector de caravana
        label_caravanas = tk.Label(frame_selectores, text="Caravana Libre:", font=("Helvetica", 14), bg='#EF9480', fg="black")
        label_caravanas.pack(side=tk.LEFT, padx=21)

        # Crear el selector de caravana (editable)
        self.selector_caravana_libre = ttk.Combobox(frame_selectores, values=self.lista_caravanas_libres, font=("Helvetica", 12), state="normal", width=15)
        self.selector_caravana_libre.set('') 
        self.selector_caravana_libre.pack(side=tk.LEFT, padx=3)
        self.selector_caravana_libre.bind('<Button-1>', self.manejar_clic_combobox)
        self.selector_caravana_libre.bind('<FocusIn>', self.manejar_foco_combobox)

        # Frame para los botones + y -
        frame_botones = tk.Frame(frame_selectores, bg='#EF9480')
        frame_botones.pack(side=tk.LEFT,padx=26)
        # Botón para agregar una nueva caravana
        boton_agregar = tk.Button(frame_botones, text="+", font=("Helvetica", 12), command=self.agregar_caravana, bg="#F2B1A1", fg="black", bd=3)
        boton_agregar.pack(side=tk.LEFT, padx=5)
        # Botón para eliminar una caravana
        boton_eliminar = tk.Button(frame_botones, text="-", font=("Helvetica", 12), command=self.eliminar_caravana, bg="#F2B1A1", fg="black", bd=3)
        boton_eliminar.pack(side=tk.LEFT, padx=5)

    def agregar_caravana(self):
        """Función para agregar una nueva caravana al menú desplegable"""
        nueva_caravana = self.selector_caravana_libre.get().strip()
        print(f"DEBUG: Nueva caravana ingresada: {nueva_caravana}")

        if not nueva_caravana:
            mostrar_mensaje(self, "Error", "El campo de caravana está vacío", "error")
            return
            
        if len(nueva_caravana) != 15 or not nueva_caravana.isdigit():
            mostrar_mensaje(self, "Error", "La caravana debe tener exactamente 15 dígitos", "error")
            return
            
        if len(self.lista_caravanas_libres) >5:
            mostrar_mensaje(self, "Limite alcanzado", "Solo se pueden ingresar hasta 5 caravanas", "warning")
            return

        if len(self.lista_caravanas_libres) == 1 and self.lista_caravanas_libres[0] == "":
            self.lista_caravanas_libres = []

        if nueva_caravana not in self.lista_caravanas_libres:
            self.lista_caravanas_libres.append(nueva_caravana)            
            self.selector_caravana_libre['values'] = self.lista_caravanas_libres
            self.selector_caravana_libre.set(nueva_caravana)            
            mostrar_mensaje(self, "Éxito", f"Caravana {nueva_caravana} agregada", "info")
        else:
            mostrar_mensaje(self, "Error", "Esta caravana ya existe", "error")

    def eliminar_caravana(self):
        """Función para eliminar una caravana del menú desplegable"""
        caravana_seleccionada = self.selector_caravana_libre.get() 
        if caravana_seleccionada in self.lista_caravanas_libres:
            self.lista_caravanas_libres.remove(caravana_seleccionada) 
            self.selector_caravana_libre['values'] = self.lista_caravanas_libres  
            self.selector_caravana_libre.set('') 
            mostrar_mensaje(self, "Eliminado", f"Se eliminó la caravana: {caravana_seleccionada}", "info")
        else:
            mostrar_mensaje(self, "Advertencia", "Seleccione una caravana válida para eliminar.", "warning")

    def crear_indice_corporal(self, frame):
        """Función para crear y ubicar el selector de índice corporal en un frame dado"""
        # Opciones para el índice corporal y los porcentajes
        self.opciones_indice = ['','gorda', 'flaca', 'mediana', 'enferma']
        self.opciones_porcentajes = [f"{i}%" for i in range(1, 201)]

        # Frame para los selectores y botones
        frame_selectores = tk.Frame(frame, bg='#EF9480')
        frame_selectores.pack(side=tk.TOP, fill="x", pady=10)
        # Etiqueta para el selector de índice corporal
        label_indice = tk.Label(frame_selectores, text="Indice Corporal:", font=("Helvetica", 14), bg='#EF9480', fg="black")
        label_indice.pack(side=tk.LEFT, padx=21)

        # Crear el selector de índice corporal (editable)
        self.selector_indice = ttk.Combobox(frame_selectores, values=self.opciones_indice, font=("Helvetica", 12), state="normal", width=8)
        self.selector_indice.set('')
        self.selector_indice.pack(side=tk.LEFT, padx=0)       
        self.selector_indice.bind('<Button-1>', self.manejar_clic_combobox)
        self.selector_indice.bind('<FocusIn>', self.manejar_foco_combobox)

        # Etiqueta para el selector de porcentaje
        label_porcentaje = tk.Label(frame_selectores, text="", font=("Helvetica", 14), bg='#EF9480', fg="black")
        label_porcentaje.pack(side=tk.LEFT, padx=5)

        # Crear un Entry editable para el porcentaje
        self.var_porcentaje = tk.StringVar()
        self.selector_porcentaje = tk.Entry(frame_selectores, font=("Helvetica", 12), width=5,textvariable=self.var_porcentaje,fg="black", bg="white")
        self.var_porcentaje.set("")
        self.selector_porcentaje.pack(side=tk.LEFT, padx=4)        
        # Configurar validación en tiempo real
        self.var_porcentaje.trace_add("write", self.validar_entrada_porcentaje)        
        # Asociar eventos para mostrar teclado solo al hacer clic
        self.selector_porcentaje.bind("<Button-1>", self.mostrar_teclado_porcentaje)
        self.selector_porcentaje.bind("<FocusOut>", self.formatear_porcentaje)
        # Frame para los botones + y -
        frame_botones = tk.Frame(frame_selectores, bg='#EF9480')
        frame_botones.pack(side=tk.LEFT)
        # Botón para agregar una nueva opción
        boton_agregar = tk.Button(frame_botones, text="+", font=("Helvetica", 12), command=self.agregar_opcion, bg="#F2B1A1", fg="black", bd=3)
        boton_agregar.pack(side=tk.LEFT, padx=5)
        # Botón para eliminar una opción
        boton_eliminar = tk.Button(frame_botones, text="-", font=("Helvetica", 12), command=self.eliminar_opcion,  bg="#F2B1A1", fg="black", bd=3)
        boton_eliminar.pack(side=tk.LEFT, padx=5)

    def mostrar_teclado_porcentaje(self, event):
        """Muestra el teclado numérico para el porcentaje al hacer clic en el Entry"""
        self.selector_porcentaje.focus_set()
        
        # Mostrar teclado con el Entry original
        teclado = TecladoNumerico4(self, self.selector_porcentaje, es_indice=True)
        teclado.update()
        teclado.grab_set()
        self.wait_window(teclado)
        self.formatear_porcentaje(None)

    def validar_entrada_porcentaje(self,  *args):
        """Valida que la entrada sea numérica y esté entre 0-200"""
        nuevo_valor = self.var_porcentaje.get().replace('%', '')
        if nuevo_valor == "":
            return True
        try:
            valor = int(nuevo_valor)
            return 0 <= valor <= 200
        except ValueError:
            return False

    def actualizar_visualizacion(self, *args):
        """Actualiza la visualización del porcentaje mientras se escribe"""
        valor = self.var_porcentaje.get().replace('%', '')
        if valor.isdigit() and 0 <= int(valor) <= 200:
            self.selector_porcentaje.config(fg='black')
        else:
            self.selector_porcentaje.config(fg='red')

    def formatear_porcentaje(self, event):
        """Agrega el símbolo % y valida que esté entre 0 y 200"""
        valor = self.var_porcentaje.get().replace('%', '').strip()
        
        if valor:
            try:
                numero = int(valor)
                if 0 <= numero <= 200:
                    self.var_porcentaje.set(f"{numero}%")
                    self.selector_porcentaje.config(fg='black')
                else:
                    self.var_porcentaje.set("")
                    mostrar_mensaje(self, "Error", "El porcentaje debe estar entre 0 y 200.", "error")
            except ValueError:
                pass
    def mostrar_teclado_indice(self):
        """Muestra el teclado para el índice corporal"""
        if not self.selector_indice.get():
            TecladoWindow(
                master=self.master,
                target_entry=self.selector_indice)

    def agregar_opcion(self):
        """Función para agregar una nueva opción al menú desplegable"""
        nuevo_indice = self.selector_indice.get()  # Obtener el valor del índice corporal
        nuevo_porcentaje = self.selector_porcentaje.get()  # Obtener el valor de porcentaje

        if nuevo_indice and nuevo_porcentaje:
            nueva_opcion = f"{nuevo_indice} ({nuevo_porcentaje})"
            if nueva_opcion not in self.opciones_indice:
                self.opciones_indice.append(nueva_opcion)  # Agregar la nueva opción a la lista
                self.selector_indice['values'] = self.opciones_indice  # Actualizar el combobox
                self.selector_indice.set(nueva_opcion)  # Establecer la nueva opción seleccionada
                mostrar_mensaje(self, "Agregado", f"Se agregó la opción: {nueva_opcion}", "info")
            else:
                mostrar_mensaje(self, "Advertencia", "La opción ya existe.", "warning")
        else:
            mostrar_mensaje(self, "Advertencia", "Complete ambos campos antes de agregar.", "warning")

    def eliminar_opcion(self):
        """Función para eliminar una opción del menú desplegable"""
        opcion_seleccionada = self.selector_indice.get()  # Obtener la opción seleccionada
        if opcion_seleccionada in self.opciones_indice:
            self.opciones_indice.remove(opcion_seleccionada)  # Eliminar la opción seleccionada de la lista
            self.selector_indice['values'] = self.opciones_indice  # Actualizar el combobox
            self.selector_indice.set('')  # Limpiar el campo después de eliminar
            mostrar_mensaje(self, "Eliminado", f"Se eliminó la opción: {opcion_seleccionada}", "info")
        else:
            mostrar_mensaje(self, "Advertencia", "Seleccione una opción válida para eliminar.", "warning")

    def crear_curva_alimentacion(self, frame):
        """Función para crear el selector de curva de alimentación con teclado"""
        self.lista_curva_alimentacion = obtener_lista_curvas()

        frame_selectores = tk.Frame(frame, bg='#EF9480')
        frame_selectores.pack(side=tk.TOP, fill="x", pady=10)

        label_curva = tk.Label(frame_selectores, text="Curva Alimentación:",font=("Helvetica", 14), bg='#EF9480', fg="black")
        label_curva.pack(side=tk.LEFT, padx=20)

        # Combobox editable para la curva
        self.selector_curva_alimentacion = ttk.Combobox(frame_selectores,values=self.lista_curva_alimentacion,font=("Helvetica", 12),state="normal",width=10)
        self.selector_curva_alimentacion.set('')
        self.selector_curva_alimentacion.pack(side=tk.LEFT, padx=22)
        
        # Frame para los botones + y -
        frame_botones = tk.Frame(frame_selectores, bg='#EF9480')
        frame_botones.pack(side=tk.LEFT)
        # Botón para agregar una nueva curva (abrir ventana de curva)
        boton_agregar = tk.Button(frame_botones, text="+", font=("Helvetica", 12), command=self.abrir_curva_alimentacion, bg="#F2B1A1", fg="black", bd=3)
        boton_agregar.pack(side=tk.LEFT, padx=5)
        # Botón para eliminar una curva
        boton_eliminar = tk.Button(frame_botones,  text="-", font=("Helvetica", 12), state="disabled", bg="#F2B1A1", fg="black", bd=3)
        boton_eliminar.pack(side=tk.LEFT, padx=5)
        
    def actualizar_combo_curva(self):
        self.lista_curva_alimentacion = obtener_lista_curvas()
        self.selector_curva_alimentacion['values'] = self.lista_curva_alimentacion
        
        actual = self.selector_curva_alimentacion.get()
        if actual not in self.lista_curva_alimentacion:
            self.selector_curva_alimentacion.set('')

    def manejar_clic_combobox(self, event):
        """Controla si fue clic en campo vacío o en la flecha"""
        combobox = event.widget
        x = event.x
        width = combobox.winfo_width()
        arrow_width = 30         
        if x < (width - arrow_width) and not combobox.get():
            # Cambio clave: Hacer que el teclado sea hijo de ESTA ventana (self) en lugar de master
            if combobox == self.selector_caravana_libre:
                teclado = TecladoFuncionalidadWindow(self, combobox)  # Nota el self en lugar de self.master
            else:
                teclado = TecladoWindow(self, combobox)  # Aquí también
            teclado.grab_set()  # Asegura que el teclado capture los eventos
            self.wait_window(teclado)  # Espera hasta que se cierre el teclado
            return "break"

    def manejar_foco_combobox(self, event):
        """Maneja cuando el combobox recibe foco"""
        combobox = event.widget
        if not combobox.get() and not combobox.focus_get() == combobox:
            self.mostrar_teclado(combobox)

    def mostrar_teclado(self, combobox):
        """Muestra el teclado virtual, usando TecladoFuncionalidadWindow para caravanas libres"""
        if combobox == self.selector_caravana_libre:
            TecladoFuncionalidadWindow(master=self.master, combobox=combobox)
        else:
            TecladoWindow(master=self.master, target_entry=combobox)
    def abrir_curva_alimentacion(self):
        """Función para abrir la ventana de Curva Alimentación"""
        curva_seleccionada = self.selector_curva_alimentacion.get().strip().lower().replace(" ", "")
        curvas_fijas = ["curva1", "curva2", "curva3"]
        
        if curva_seleccionada in curvas_fijas:
            mostrar_mensaje(self, "Accion no permitida", f"{curva.seleccionada.title()} es una curva fija y no puede modificarse.", "warning")
            return
            
        if hasattr(self, 'logo') and self.logo:
            ventana = curva_alimentacion.CurvaAlimentacionWindow(self, self.logo)
        else:
            ventana = curva_alimentacion.CurvaAlimentacionWindow(self, None)
            ventana.grab_set()

    def eliminar_curva(self):
        """Función para eliminar una opción del selector de Curva de Alimentación"""
        curva_seleccionada = self.selector_curva_alimentacion.get().strip().lower().replace(" ", "")
        curvas_fijas = ["curva1", "curva2", "curva3"]
        
        if curva_seleccionada in curvas_fijas:
            mostrar_mensaje(self, "Accion no permitida", f"{curva_seleccionada.title()} es una curva fija y no puede eliminarse.", "warning")
            return
        
        if curva_seleccionada in [c.lower().replace(" ", "") for c in  self.lista_curva_alimentacion]:
            self.lista_curva_alimentacion = [c for c in self.lista_curva_alimentacion if c.lower().replace(" ", "") != curva_seleccionada]
            self.selector_curva_alimentacion['values'] = self.lista_curva_alimentacion
            self.selector_curva_alimentacion.set('') 

            from pages.curva_alimentacion import cargar_todas_curvas
            DIR_CONFIG = "config"
            ARCHIVO_CURVAS = "curvas.json"
            
            try:
                curvas = cargar_todas_curvas()
                curva_vacia = {"nombre": "", "segmentos": [{"dia": 0, "indice": "0%"} for _ in range(16)]}
                for i, curva in enumerate(curvas):
                    if curva["nombre"].strip().lower().replace(" ", "") == curva_seleccionada:
                        curvas[i] = curva_vacia
                        break
                
                with open(os.path.join(DIR_CONFIG, ARCHIVO_CURVAS), 'w', encoding='utf-8') as f:
                    json.dump(curvas, f, indent=4, ensure_ascii=False)
                mostrar_mensaje(self, "Eliminado", f"Se elimino la curva:{curva_seleccionada.title()}", "info")
                    
            except Exception as e:
                mostrar_mensaje(self, "Error", f"No se pudo eliminar la curva del archivo: {e}", "error")
        else:
            mostrar_mensaje(self, "Advertencia", "Seleccione una curva valida para eliminar.", "warning")

    def modificar_calibracion(self, variable, incremento):
        """Función para modificar los valores de calibración (aumentar o disminuir)"""
        nuevo_valor = variable.get() + incremento
        if nuevo_valor >= 0:  # Evitar valores negativos
            variable.set(nuevo_valor)

    def cerrar_ventana(self):
        """Cerrar la ventana de Funcionalidad"""
        self.grab_set()
        self.destroy()
    
    def guardar(self):
        porcentaje = self.var_porcentaje.get().replace('%', '').strip()
        if porcentaje:
            try:
                valor = int(porcentaje)
                if not (0 <= valor <= 200):
                    mostrar_mensaje(self, "Error", "El porcentaje debe estar entre 0 y 200.", "error")
                    return
            except ValueError:
                mostrar_mensaje(self, "Error", "Porcentaje inválido", "error")
                return

        config_data = {
            "calibraciones": {
                "motor": self.var_calibracion_motor.get(),
                "agua": self.var_calibracion_agua.get(),
                "peso": float(self.var_caravana_desconocida.get())
            },
            "caravanas_libres": self.lista_caravanas_libres,
            "indice_corporal": {
                "tipo": self.selector_indice.get(),
                "porcentaje": self.var_porcentaje.get()
            }
        }
        try:
            curvas_guardadas = curva_alimentacion.cargar_todas_curvas()
        except Exception as e:
            curvas_guardadas = []
            print(f"Error al cargar curvas para enviar: {e}")
        curvas_final = [{"nombre": "", "segmentos": [{"dia": 0, "indice": "0%"} for _ in range(16)]} for _ in range(5)]
        
        curvas_fijas = {
            "curva1": {"nombre": "curva1", "segmentos": [{"dia": 1, "indice": "50%"}]},
            "curva2": {"nombre": "curva2", "segmentos": [{"dia": 1, "indice": "50%"}, {"dia": 113, "indice": "100%"}]},
            "curva3": {"nombre": "curva3", "segmentos": [{"dia": 1, "indice": "100%"}, {"dia": 113, "indice": "50%"}]}
        }
        
        modificables = [c for c in curvas_guardadas if c["nombre"].strip().lower() not in ["curva1", "curva2", "curva3"]]
        for i in range(min(2, len(modificables))):
            curvas_final[i] = modificables[i]
            
        curvas_final[2] = curvas_fijas["curva1"]
        curvas_final[3] = curvas_fijas["curva2"]
        curvas_final[4] = curvas_fijas["curva3"]

        config_data["curvas_alimentacion"] = curvas_final
        
        try:
            import os, json
            os.makedirs("config", exist_ok=True)
            config_path = os.path.join("config", "configuracion_sistema.json")
            with open(config_path, 'w') as f:
                json.dump(config_data, f, indent=4)
                f.flush()
                os.fsync(f.fileno())
        except Exception as e:
            mostrar_mensaje(self, "Error", f"Error al guardar archivo: {e}", "error")
            return

        # Envía por UART sin bloquear la GUI
        threading.Thread(
            target=enviar_por_uart,
            args=(config_data, '/dev/serial0', 9600),
            daemon=True
        ).start()

        mostrar_mensaje(self, "Guardado", "Configuración guardada y enviada", "info")
