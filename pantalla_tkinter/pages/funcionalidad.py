import tkinter as tk
from tkinter import ttk
from util.util_mensaje import mostrar_mensaje
import pages.curva_alimentacion as curva_alimentacion
import util.util_ventana as util_ventana
from util.util_teclado3 import TecladoFuncionalidadWindow
from util.teclado import TecladoWindow
from pages.curva_alimentacion import obtener_lista_curvas
from util.util_teclado4 import TecladoNumerico4
from util import sqlite as db_local
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
    curvas_fijas = [
        {"nombre": "mod1", "segmentos": [{"dia": 1, "indice": "100%"}]},
        {"nombre": "mod2", "segmentos": [{"dia": 1, "indice": "100%"}]},
        {"nombre": "curva1", "segmentos": [{"dia": 1, "indice": "50%"}]},
        {"nombre": "curva2", "segmentos": [{"dia": 1, "indice": "50%"}, {"dia": 113, "indice": "100%"}]},
        {"nombre": "curva3", "segmentos": [{"dia": 1, "indice": "100%"}, {"dia": 113, "indice": "50%"}]}
    ]
    for curva in curvas_fijas:
        try:
            if not db_local.existeCurva(curva["nombre"]):
                ok, err = db_local.guardarCurva(curva["nombre"], curva["segmentos"])
                if not ok:
                    print(f"[WARN] No se pudo crear curva fija {curva['nombre']}: {err}")
        except Exception as e:
            print(f"[ERROR] inicializando curva fija {curva['nombre']}: {e}")


class FuncionalidadWindow(tk.Toplevel):
    def __init__(self, master, logo):
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

        valor_motor, valor_agua, valor_caravana = self.cargar_calibraciones()

        self.frame_calibracion_motor = tk.Frame(self, bg='#EF9480', height=40)
        self.frame_calibracion_motor.pack(side=tk.TOP, fill="x", pady=5)
        self.crear_calibracion_motor(self.frame_calibracion_motor, valor_inicial=valor_motor)

        self.frame_calibracion_agua = tk.Frame(self, bg='#EF9480', height=40)
        self.frame_calibracion_agua.pack(side=tk.TOP, fill="x", pady=5)
        self.crear_calibracion_agua(self.frame_calibracion_agua, valor_inicial=valor_agua)

        self.frame_caravana_desconocida = tk.Frame(self, bg='#EF9480', height=40)
        self.frame_caravana_desconocida.pack(side=tk.TOP, fill="x", pady=5)
        self.crear_slider_caravana(self.frame_caravana_desconocida, valor_inicial=valor_caravana)

        self.frame_caravanas_libres = tk.Frame(self, bg='#EF9480', height=40)
        self.frame_caravanas_libres.pack(side=tk.TOP, fill="x", pady=5)
        self.crear_caravanas_libres(self.frame_caravanas_libres)

        self.frame_indice_corporal = tk.Frame(self, bg='#EF9480', height=40)
        self.frame_indice_corporal.pack(side=tk.TOP, fill="x", pady=5)
        self.crear_indice_corporal(self.frame_indice_corporal)

        #self.frame_curva_alimentacion = tk.Frame(self, bg='#EF9480', height=40)
        #self.frame_curva_alimentacion.pack(side=tk.TOP, fill="x", pady=5)
        #self.crear_curva_alimentacion(self.frame_curva_alimentacion)

        self.frame_botones_finales = tk.Frame(self, bg='#EF9480')
        self.frame_botones_finales.pack(side=tk.BOTTOM, fill="x", pady=70)

        boton_atras = tk.Button(
            self.frame_botones_finales,
            text="<< Atrás",
            font=("Helvetica", 16),
            command=self.cerrar_ventana,
            bg="red",
            fg="#ffffff",
            bd=7
        )
        boton_atras.pack(side=tk.LEFT, padx=10)

        boton_guardar = tk.Button(
            self.frame_botones_finales,
            text="Guardar",
            font=("Helvetica", 16),
            command=self.guardar,
            bg="red",
            fg="#ffffff",
            bd=7
        )
        boton_guardar.pack(side=tk.RIGHT, padx=10)

    def cargar_calibraciones(self):
        try:
            motor, agua, caravana, caravanas_libres = db_local.obtenerConfiguracion()
            self.lista_caravanas_libres = caravanas_libres if caravanas_libres else ['']
            return motor or 0, agua or 0, float(caravana or 0.0)
        except Exception as e:
            print("Error al cargar calibraciones desde SQLite:", e)
            self.lista_caravanas_libres = ['']
            return 0, 0, 0.0

    def crear_logo(self):
        self.frame_logo = tk.Frame(self, bg='#EF9480', height=100)
        self.frame_logo.pack(side=tk.TOP, fill="x", pady=22)
        label = tk.Label(self.frame_logo, image=self.master.logo, bg='#EF9480')
        label.place(relx=0.5, rely=0.5, anchor="center")

    def crear_calibracion_motor(self, frame, valor_inicial=0):
        frame_superior_motor = tk.Frame(frame, bg='#EF9480')
        frame_superior_motor.pack(side=tk.TOP, pady=10, anchor='w')

        label_motor = tk.Label(
            frame_superior_motor,
            text="Calibración Motor:",
            font=("Helvetica", 14),
            bg='#EF9480',
            fg="black"
        )
        label_motor.pack(side=tk.LEFT, padx=20)

        self.var_calibracion_motor = tk.IntVar(value=valor_inicial)

        frame_botones_motor = tk.Frame(frame_superior_motor, bg='#EF9480')
        frame_botones_motor.pack(side=tk.LEFT)

        boton_disminuir_motor = tk.Button(
            frame_botones_motor,
            text="-",
            font=("Helvetica", 16),
            command=lambda: self.modificar_calibracion(self.var_calibracion_motor, -1),
            bg="#F2B1A1",
            fg="black",
            bd=5
        )
        boton_disminuir_motor.pack(side=tk.LEFT)

        self.label_motor = tk.Label(
            frame_botones_motor,
            textvariable=self.var_calibracion_motor,
            font=("Helvetica", 14),
            bg='#EF9480',
            fg="black"
        )
        self.label_motor.pack(side=tk.LEFT, padx=20)

        boton_aumentar_motor = tk.Button(
            frame_botones_motor,
            text="+",
            font=("Helvetica", 16),
            command=lambda: self.modificar_calibracion(self.var_calibracion_motor, 1),
            bg="#F2B1A1",
            fg="black",
            bd=5
        )
        boton_aumentar_motor.pack(side=tk.LEFT)

    def crear_calibracion_agua(self, frame, valor_inicial=0):
        frame_superior_agua = tk.Frame(frame, bg='#EF9480')
        frame_superior_agua.pack(side=tk.TOP, pady=6, anchor='w')

        label_agua = tk.Label(
            frame_superior_agua,
            text="Calibración Agua:",
            font=("Helvetica", 14),
            bg='#EF9480',
            fg="black"
        )
        label_agua.pack(side=tk.LEFT, padx=22)

        self.var_calibracion_agua = tk.IntVar(value=valor_inicial)

        frame_botones_agua = tk.Frame(frame_superior_agua, bg='#EF9480')
        frame_botones_agua.pack(side=tk.LEFT)

        boton_disminuir_agua = tk.Button(
            frame_botones_agua,
            text="-",
            font=("Helvetica", 16),
            command=lambda: self.modificar_calibracion(self.var_calibracion_agua, -1),
            bg="#F2B1A1",
            fg="black",
            bd=5
        )
        boton_disminuir_agua.pack(side=tk.LEFT)

        self.label_agua = tk.Label(
            frame_botones_agua,
            textvariable=self.var_calibracion_agua,
            font=("Helvetica", 14),
            bg='#EF9480',
            fg="black"
        )
        self.label_agua.pack(side=tk.LEFT, padx=20)

        boton_aumentar_agua = tk.Button(
            frame_botones_agua,
            text="+",
            font=("Helvetica", 16),
            command=lambda: self.modificar_calibracion(self.var_calibracion_agua, 1),
            bg="#F2B1A1",
            fg="black",
            bd=5
        )
        boton_aumentar_agua.pack(side=tk.LEFT)

    def crear_slider_caravana(self, frame, valor_inicial):
        frame_slider_caravana = tk.Frame(frame, bg='#EF9480')
        frame_slider_caravana.pack(side=tk.TOP, pady=10, anchor="w")

        label_caravana = tk.Label(
            frame_slider_caravana,
            text="Caravana/Desc:",
            font=("Helvetica", 14),
            bg='#EF9480',
            fg="black"
        )
        label_caravana.pack(side=tk.LEFT, padx=20)

        self.var_caravana_desconocida = tk.DoubleVar(value=valor_inicial)

        self.slider_caravana = tk.Scale(
            frame_slider_caravana,
            from_=0,
            to=5,
            orient="horizontal",
            variable=self.var_caravana_desconocida,
            resolution=0.1,
            length=200,
            sliderlength=20,
            troughcolor="grey",
            bg='#c7baba',
            activebackground='#F2B1A1',
            font=("Helvetica", 12),
            highlightbackground='#000000',
            highlightthickness=2
        )
        self.slider_caravana.pack(side=tk.LEFT, padx=0)

    def crear_caravanas_libres(self, frame):
        if not hasattr(self, "lista_caravanas_libres"):
            self.lista_caravanas_libres = ['']

        frame_selectores = tk.Frame(frame, bg='#EF9480')
        frame_selectores.pack(side=tk.TOP, fill="x", pady=10)

        label_caravanas = tk.Label(
            frame_selectores,
            text="Caravana Libre:",
            font=("Helvetica", 14),
            bg='#EF9480',
            fg="black"
        )
        label_caravanas.pack(side=tk.LEFT, padx=21)

        self.selector_caravana_libre = ttk.Combobox(
            frame_selectores,
            values=self.lista_caravanas_libres,
            font=("Helvetica", 12),
            state="normal",
            width=15
        )
        self.selector_caravana_libre.set('')
        self.selector_caravana_libre.pack(side=tk.LEFT, padx=3)
        self.selector_caravana_libre.bind('<Button-1>', self.manejar_clic_combobox)
        self.selector_caravana_libre.bind('<FocusIn>', self.manejar_foco_combobox)

        frame_botones = tk.Frame(frame_selectores, bg='#EF9480')
        frame_botones.pack(side=tk.LEFT, padx=26)

        boton_agregar = tk.Button(
            frame_botones,
            text="+",
            font=("Helvetica", 12),
            command=self.agregar_caravana,
            bg="#F2B1A1",
            fg="black",
            bd=3
        )
        boton_agregar.pack(side=tk.LEFT, padx=5)

        boton_eliminar = tk.Button(
            frame_botones,
            text="-",
            font=("Helvetica", 12),
            command=self.eliminar_caravana,
            bg="#F2B1A1",
            fg="black",
            bd=3
        )
        boton_eliminar.pack(side=tk.LEFT, padx=5)

    def agregar_caravana(self):
        nueva_caravana = self.selector_caravana_libre.get().strip()
        print(f"DEBUG: Nueva caravana ingresada: {nueva_caravana}")

        if not nueva_caravana:
            mostrar_mensaje(self, "Error", "El campo de caravana está vacío", "error")
            return

        if len(nueva_caravana) != 15 or not nueva_caravana.isdigit():
            mostrar_mensaje(self, "Error", "La caravana debe tener exactamente 15 dígitos", "error")
            return

        if len(self.lista_caravanas_libres) >= 5:
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
        caravana_seleccionada = self.selector_caravana_libre.get()
        if caravana_seleccionada in self.lista_caravanas_libres:
            self.lista_caravanas_libres.remove(caravana_seleccionada)
            self.selector_caravana_libre['values'] = self.lista_caravanas_libres
            self.selector_caravana_libre.set('')
            mostrar_mensaje(self, "Eliminado", f"Se eliminó la caravana: {caravana_seleccionada}", "info")
        else:
            mostrar_mensaje(self, "Advertencia", "Seleccione una caravana válida para eliminar.", "warning")

    def _cargar_indices_desde_db(self):
        self.opciones_indice = []
        self.mapa_indice_texto_id = {}
        try:
            filas = db_local.obtenerIndicesCorporales()
            for id_ind, desc, corporal in filas:
                texto = f"{desc} {corporal}%"
                self.opciones_indice.append(texto)
                self.mapa_indice_texto_id[texto] = id_ind
            if not self.opciones_indice:
                self.opciones_indice = ['']
        except Exception as e:
            print("Error cargando índices corporales:", e)
            self.opciones_indice = ['']
            self.mapa_indice_texto_id = {}

    def crear_indice_corporal(self, frame):
        self._cargar_indices_desde_db()

        frame_selectores = tk.Frame(frame, bg='#EF9480')
        frame_selectores.pack(side=tk.TOP, fill="x", pady=10)

        label_indice = tk.Label(
            frame_selectores,
            text="Indice Corporal:",
            font=("Helvetica", 14),
            bg='#EF9480',
            fg="black"
        )
        label_indice.pack(side=tk.LEFT, padx=20)

        self.selector_indice = ttk.Combobox(
            frame_selectores,
            values=self.opciones_indice,
            font=("Helvetica", 12),
            state="normal",
            width=12
        )
        self.selector_indice.set('')
        self.selector_indice.pack(side=tk.LEFT, padx=0)
        self.selector_indice.bind('<Button-1>', self.manejar_clic_combobox)
        self.selector_indice.bind('<FocusIn>', self.manejar_foco_combobox)

        label_porcentaje = tk.Label(
            frame_selectores,
            font=("Helvetica", 14),
            bg='#EF9480',
            fg="black"
        )
        label_porcentaje.pack(side=tk.LEFT, padx=5)

        self.var_porcentaje = tk.StringVar()
        self.selector_porcentaje = tk.Entry(
            frame_selectores,
            font=("Helvetica", 12),
            width=5,
            textvariable=self.var_porcentaje,
            fg="black",
            bg="white"
        )
        self.var_porcentaje.set("")
        self.selector_porcentaje.pack(side=tk.LEFT, padx=4)
        self.var_porcentaje.trace_add("write", self.validar_entrada_porcentaje)
        self.selector_porcentaje.bind("<Button-1>", self.mostrar_teclado_porcentaje)
        self.selector_porcentaje.bind("<FocusOut>", self.formatear_porcentaje)

        frame_botones = tk.Frame(frame_selectores, bg='#EF9480')
        frame_botones.pack(side=tk.LEFT)

        boton_agregar = tk.Button(
            frame_botones,
            text="+",
            font=("Helvetica", 12),
            command=self.agregar_opcion,
            bg="#F2B1A1",
            fg="black",
            bd=3
        )
        boton_agregar.pack(side=tk.LEFT, padx=5)

        boton_eliminar = tk.Button(
            frame_botones,
            text="-",
            font=("Helvetica", 12),
            command=self.eliminar_opcion,
            bg="#F2B1A1",
            fg="black",
            bd=3
        )
        boton_eliminar.pack(side=tk.LEFT, padx=5)

    def mostrar_teclado_porcentaje(self, event):
        self.selector_porcentaje.focus_set()
        teclado = TecladoNumerico4(self, self.selector_porcentaje, es_indice=True)
        teclado.update()
        teclado.grab_set()
        self.wait_window(teclado)
        self.formatear_porcentaje(None)

    def validar_entrada_porcentaje(self, *args):
        nuevo_valor = self.var_porcentaje.get().replace('%', '')
        if nuevo_valor == "":
            return True
        try:
            valor = int(nuevo_valor)
            return 0 <= valor <= 200
        except ValueError:
            return False

    def formatear_porcentaje(self, event):
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
        if not self.selector_indice.get():
            TecladoWindow(
                master=self.master,
                target_entry=self.selector_indice
            )

    def agregar_opcion(self):
        texto = self.selector_indice.get().strip()
        if not texto:
            mostrar_mensaje(self, "Error", "Ingrese una descripción para el índice corporal.", "error")
            return

        porcentaje_str = self.var_porcentaje.get().replace('%', '').strip()
        if not porcentaje_str:
            mostrar_mensaje(self, "Error", "Ingrese un porcentaje para el índice corporal.", "error")
            return
        try:
            porcentaje_val = int(porcentaje_str)
        except ValueError:
            mostrar_mensaje(self, "Error", "Porcentaje inválido.", "error")
            return

        if not (0 <= porcentaje_val <= 200):
            mostrar_mensaje(self, "Error", "El porcentaje debe estar entre 0 y 200.", "error")
            return

        try:
            db_local.insertarIndiceCorporal(descripcion=texto, corporal=porcentaje_val)
            mostrar_mensaje(self, "Agregado", f"Se agregó el índice: {texto} {porcentaje_val}%", "info")
            self._cargar_indices_desde_db()
            self.selector_indice['values'] = self.opciones_indice
            self.selector_indice.set(f"{texto} {porcentaje_val}%")
        except Exception as e:
            mostrar_mensaje(self, "Error", f"No se pudo guardar en SQLite: {e}", "error")

    def eliminar_opcion(self):
        seleccionado = self.selector_indice.get().strip()
        if not seleccionado:
            mostrar_mensaje(self, "Advertencia", "Seleccione un índice para eliminar.", "warning")
            return

        id_indice = self.mapa_indice_texto_id.get(seleccionado)
        if not id_indice:
            mostrar_mensaje(self, "Error", "No se encontró el índice seleccionado en la base de datos.", "error")
            return

        try:
            db_local.eliminarIndiceCorporal(id_indice)
            mostrar_mensaje(self, "Eliminado", f"Se eliminó el índice: {seleccionado}", "info")
            self._cargar_indices_desde_db()
            self.selector_indice['values'] = self.opciones_indice
            self.selector_indice.set('')
            self.var_porcentaje.set('')
        except Exception as e:
            mostrar_mensaje(self, "Error", f"No se pudo eliminar de SQLite: {e}", "error")

    def crear_curva_alimentacion(self, frame):
        self.lista_curva_alimentacion = obtener_lista_curvas()

        frame_selectores = tk.Frame(frame, bg='#EF9480')
        frame_selectores.pack(side=tk.TOP, fill="x", pady=10)

        label_curva = tk.Label(
            frame_selectores,
            text="Curva Alimentación:",
            font=("Helvetica", 14),
            bg='#EF9480',
            fg="black"
        )
        label_curva.pack(side=tk.LEFT, padx=20)

        self.selector_curva_alimentacion = ttk.Combobox(
            frame_selectores,
            values=self.lista_curva_alimentacion,
            font=("Helvetica", 12),
            state="normal",
            width=10
        )
        self.selector_curva_alimentacion.set('')
        self.selector_curva_alimentacion.pack(side=tk.LEFT, padx=22)

        frame_botones = tk.Frame(frame_selectores, bg='#EF9480')
        frame_botones.pack(side=tk.LEFT)

        boton_agregar = tk.Button(
            frame_botones,
            text="+",
            font=("Helvetica", 12),
            command=self.abrir_curva_alimentacion,
            bg="#F2B1A1",
            fg="black",
            bd=3
        )
        boton_agregar.pack(side=tk.LEFT, padx=5)

        boton_eliminar = tk.Button(
            frame_botones,
            text="-",
            font=("Helvetica", 12),
            command=self.eliminar_curva,
            bg="#F2B1A1",
            fg="black",
            bd=3
        )
        boton_eliminar.pack(side=tk.LEFT, padx=5)

    def actualizar_combo_curva(self):
        self.lista_curva_alimentacion = obtener_lista_curvas()
        self.selector_curva_alimentacion['values'] = self.lista_curva_alimentacion

        actual = self.selector_curva_alimentacion.get()
        if actual not in self.lista_curva_alimentacion:
            self.selector_curva_alimentacion.set('')

    def abrir_curva_alimentacion(self):
        curva_seleccionada = self.selector_curva_alimentacion.get().strip().lower().replace(" ", "")
        curvas_fijas = ["curva1", "curva2", "curva3"]

        if curva_seleccionada in curvas_fijas:
            mostrar_mensaje(
                self,
                "Accion no permitida",
                f"{curva_seleccionada.title()} es una curva fija y no puede modificarse.",
                "warning"
            )
            return

        if hasattr(self, 'logo') and self.logo:
            ventana = curva_alimentacion.CurvaAlimentacionWindow(self, self.logo)
        else:
            ventana = curva_alimentacion.CurvaAlimentacionWindow(self, None)
            ventana.grab_set()

    def eliminar_curva(self):
        texto_ui = self.selector_curva_alimentacion.get().strip()
        curva_seleccionada = texto_ui.lower().replace(" ", "")
        curvas_fijas = ["curva1", "curva2", "curva3"]

        if not curva_seleccionada:
            mostrar_mensaje(self, "Advertencia", "Seleccione una curva valida para eliminar.", "warning")
            return

        if curva_seleccionada in curvas_fijas:
            mostrar_mensaje(
                self,
                "Accion no permitida",
                f"{curva_seleccionada.title()} es una curva fija y no puede eliminarse.",
                "warning"
            )
            return

        try:
            eliminada = db_local.eliminarCurva(texto_ui)
        except Exception as e:
            mostrar_mensaje(self, "Error", f"No se pudo eliminar la curva en SQLite: {e}", "error")
            return

        if not eliminada:
            mostrar_mensaje(
                self,
                "Error",
                "No se encontró la curva seleccionada en la base de datos.",
                "error"
            )
            return

        self.actualizar_combo_curva()
        self.selector_curva_alimentacion.set('')
        mostrar_mensaje(self, "Eliminado", f"Se eliminó la curva: {texto_ui}", "info")

    def manejar_clic_combobox(self, event):
        combobox = event.widget
        x = event.x
        width = combobox.winfo_width()
        arrow_width = 30
        if x < (width - arrow_width) and not combobox.get():
            if combobox == self.selector_caravana_libre:
                teclado = TecladoFuncionalidadWindow(self, combobox)
            else:
                teclado = TecladoWindow(self, combobox)
            teclado.grab_set()
            self.wait_window(teclado)
            return "break"

    def manejar_foco_combobox(self, event):
        combobox = event.widget
        if not combobox.get() and not combobox.focus_get() == combobox:
            self.mostrar_teclado(combobox)

    def mostrar_teclado(self, combobox):
        if combobox == self.selector_caravana_libre:
            TecladoFuncionalidadWindow(master=self.master, combobox=combobox)
        else:
            TecladoWindow(master=self.master, target_entry=combobox)

    def modificar_calibracion(self, variable, incremento):
        nuevo_valor = variable.get() + incremento
        if nuevo_valor >= 0:
            variable.set(nuevo_valor)

    def cerrar_ventana(self):
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

        try:
            db_local.guardarConfiguracion(
                cal_motor=self.var_calibracion_motor.get(),
                cal_agua=self.var_calibracion_agua.get(),
                caravana_desc=float(self.var_caravana_desconocida.get()),
                caravanas_libres=self.lista_caravanas_libres
            )
        except Exception as e:
            mostrar_mensaje(self, "Error", f"Error al guardar en SQLite: {e}", "error")
            return

        try:
            curvas_guardadas = curva_alimentacion.cargar_todas_curvas()
        except Exception as e:
            curvas_guardadas = []
            print(f"Error al cargar curvas para enviar: {e}")

        curvas_final = [
            {"nombre": "", "segmentos": [{"dia": 0, "indice": "0%"} for _ in range(16)]}
            for _ in range(5)
        ]

        curvas_fijas = {
            "curva1": {"nombre": "curva1", "segmentos": [{"dia": 1, "indice": "50%"}]},
            "curva2": {"nombre": "curva2", "segmentos": [{"dia": 1, "indice": "50%"}, {"dia": 113, "indice": "100%"}]},
            "curva3": {"nombre": "curva3", "segmentos": [{"dia": 1, "indice": "100%"}, {"dia": 113, "indice": "50%"}]}
        }

        modificables = [
            c for c in curvas_guardadas
            if c["nombre"].strip().lower() not in ["curva1", "curva2", "curva3"]
        ]
        for i in range(min(2, len(modificables))):
            curvas_final[i] = modificables[i]

        curvas_final[2] = curvas_fijas["curva1"]
        curvas_final[3] = curvas_fijas["curva2"]
        curvas_final[4] = curvas_fijas["curva3"]

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
            },
            "curvas_alimentacion": curvas_final
        }

        threading.Thread(
            target=enviar_por_uart,
            args=(config_data, '/dev/serial0', 9600),
            daemon=True
        ).start()

        mostrar_mensaje(self, "Guardado", "Configuración guardada en SQLite y enviada", "info")
