import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog
from tkcalendar import DateEntry
from datetime import datetime
from util.util_teclado import TecladoNumerico
from pages.ir_dieta import ir_dietaWindow
from util.util_calendario import seleccionar_fecha
import util.util_ventana as util_ventana
from util.util_mensaje import mostrar_mensaje
import json
from util import sqlite as db_local
import serial
import time


class GestionAnimalWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.overrideredirect(True)
        self.geometry("480x800")
        self.config(bg="#EF9480")
        self.resizable(False, False)
        util_ventana.centrar_ventana(self, 480, 800)

        self.mensaje_actual = None

        # Variables para almacenar el N° Caravana, N° Interno y fecha de inseminación
        self.numero_caravana = tk.StringVar()
        self.numero_interno = tk.StringVar()
        self.fecha_inseminacion = tk.StringVar()

        self.frame_logo = tk.Frame(self, bg='#EF9480', height=100)
        self.frame_logo.pack(side=tk.TOP, fill="x", pady=22)
        self.crear_logo(self.frame_logo)

        # ==== Selector de corral ====
        self.frame_selector = tk.Frame(self, bg='#EF9480', height=50)
        self.frame_selector.pack(side=tk.TOP, fill="x", pady=5)
        self.crear_selector_corral(self.frame_selector)

        # ==== Canvas para la tabla ====
        self.frame_canvas = tk.Frame(self, bg="#EF9480")
        self.frame_canvas.pack(side=tk.TOP, fill="both", expand=True)

        self.canvas = tk.Canvas(
            self.frame_canvas,
            bg="#ffffff",
            scrollregion=(0, 0, 400, 1000)
        )
        self.canvas.pack(side=tk.LEFT, fill="both", expand=True)

        self.scrollbar = tk.Scrollbar(
            self.frame_canvas,
            orient="vertical",
            command=self.canvas.yview
        )
        self.scrollbar.pack(side=tk.RIGHT, fill="y")
        self.canvas.config(yscrollcommand=self.scrollbar.set)

        self.frame_interior = tk.Frame(self.canvas, bg="#ffffff")
        self.canvas.create_window((0, 0), window=self.frame_interior, anchor="nw")
        self.frame_interior.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.checkbuttons = []  # Lista de checkbuttons para gestionar selección/baja

        # botones superiores: alta, ver dieta y baja
        self.frame_botones_superiores = tk.Frame(self, bg='#EF9480', height=60)
        # no dejar que el frame cambie de tamaño cuando los widgets se empaquetan
        self.frame_botones_superiores.pack_propagate(False)
        self.frame_botones_superiores.pack(side=tk.TOP, fill="x", pady=10)

        boton_agregar = tk.Button(
            self.frame_botones_superiores,
            text="+",
            font=("Helvetica", 16),
            command=self.agregar_fila,
            bg="red",
            fg="#ffffff",
            bd=7
        )
        boton_agregar.pack(side=tk.LEFT, padx=10, pady=10)

        boton_ver_dieta = tk.Button(
            self.frame_botones_superiores,
            text="Ver Dieta",
            font=("Helvetica", 16),
            command=self.ver_dieta_modal,
            bg="red",
            fg="#ffffff",
            bd=7
        )
        boton_ver_dieta.pack(side=tk.LEFT, expand=True, padx=10, pady=10)

        boton_eliminar = tk.Button(
            self.frame_botones_superiores,
            text="-",
            font=("Helvetica", 16),
            command=self.eliminar_fila,
            bg="red",
            fg="#ffffff",
            bd=7
        )
        boton_eliminar.pack(side=tk.RIGHT, padx=10, pady=10)

        self.frame_botones_inferiores = tk.Frame(self, bg='#EF9480', height=60)
        self.frame_botones_inferiores.pack(side=tk.TOP, fill="x", pady=10)

        boton_caravana = tk.Button(
            self.frame_botones_inferiores,
            text="N° Caravana",
            font=("Helvetica", 16),
            command=self.abrir_teclado_numerico,
            bg="red",
            fg="#ffffff",
            bd=7
        )
        boton_caravana.pack(side=tk.LEFT, padx=6, pady=10)

        boton_interno = tk.Button(
            self.frame_botones_inferiores,
            text="N° Interno",
            font=("Helvetica", 16),
            command=self.abrir_teclado_numerico_interno,
            bg="red",
            fg="#ffffff",
            bd=7
        )
        boton_interno.pack(side=tk.LEFT, padx=6, pady=10)

        boton_inseminacion = tk.Button(
            self.frame_botones_inferiores,
            text="Inseminación",
            font=("Helvetica", 16),
            command=self.seleccionar_fecha,
            bg="red",
            fg="#ffffff",
            bd=7
        )
        boton_inseminacion.pack(side=tk.RIGHT, padx=6, pady=10)

        self.frame_boton_atras = tk.Frame(self, bg="#EF9480", height=60)
        self.frame_boton_atras.pack(side=tk.BOTTOM, fill="x")

        boton_atras = tk.Button(
            self,
            text="<< Atrás",
            font=("Helvetica", 16),
            command=self.cerrar_ventana,
            bg="red",
            fg="#ffffff",
            bd=7
        )
        boton_atras.pack(side=tk.LEFT, padx=10, pady=10)

        boton_Dieta = tk.Button(
            self,
            text="Ir a Dieta >>",
            font=("Helvetica", 16),
            command=self.ir_dieta,
            bg="red",
            fg="#ffffff",
            bd=7
        )
        boton_Dieta.pack(side=tk.RIGHT, padx=10, pady=10)

        # Encabezados de la tabla
        self.crear_encabezados()
        # Cargar animales desde SQLite para el corral inicial
        self.cargar_animales(self.selector_corral.get())


    def _obtener_num_corral_actual(self) -> int:
        """Devuelve el número de corral (1..20) a partir del combobox."""
        texto = self.selector_corral.get()  # "Corral 3"
        try:
            return int(texto.split()[-1])
        except Exception:
            return 1

    def crear_logo(self, frame):
        label = tk.Label(frame, image=self.master.logo, bg='#EF9480')
        label.place(relx=0.5, rely=0.5, anchor="center")

    def crear_selector_corral(self, frame):
        corrales = [f'Corral {i}' for i in range(1, 21)]
        label_corral = tk.Label(
            frame,
            text="Seleccionar Corral:",
            font=("Helvetica", 14),
            bg='#EF9480',
            fg="black"
        )
        label_corral.pack(side=tk.LEFT, padx=10)

        self.selector_corral = ttk.Combobox(
            frame,
            values=corrales,
            font=("Helvetica", 12),
            state="readonly"
        )
        self.selector_corral.set(corrales[0])
        self.selector_corral.pack(side=tk.LEFT, padx=10)

        self.selector_corral.bind(
            "<<ComboboxSelected>>",
            self.cargar_animales_al_seleccionar
        )

    # ------------------------------------------------------------------
    # Función de utilidad: muestra un modal con la información de dieta
    # de todos los animales seleccionados en la tabla.
    # ------------------------------------------------------------------
    def ver_dieta_modal(self):
        # recolectar caravanas seleccionadas
        seleccionadas = []
        for checkbox in self.checkbuttons:
            if checkbox.var.get():
                car = getattr(checkbox, "caravana", None)
                if car:
                    seleccionadas.append(car)

        if not seleccionadas:
            self.mostrar_mensaje("Error", "Selecciona al menos un animal para ver la dieta.")
            return

        # crear ventana modal
        modal = tk.Toplevel(self)
        modal.overrideredirect(True)
        modal.geometry("340x700")
        # darle un borde visible al propio toplevel
        modal.config(bg="#EF9480", bd=2, relief="solid")
        modal.resizable(False, False)
        util_ventana.centrar_ventana(modal, 340, 700)
        modal.grab_set()

        # scrollable frame
        contenedor = tk.Frame(modal, bg="#EF9480")
        contenedor.pack(fill="both", expand=True, padx=10, pady=10)
        canvas = tk.Canvas(contenedor, bg="#ffffff", width=320)
        scrollbar = tk.Scrollbar(contenedor, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill="y")
        canvas.pack(side=tk.LEFT, fill="both", expand=True)
        interior = tk.Frame(canvas, bg="#ffffff")
        # colocar el interior anclado al norte pero centrado horizontalmente
        # como el canvas tiene ancho fijo 440, usamos x=220
        canvas.create_window((160, 0), window=interior, anchor="n")
        interior.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        # agregar una seccion por cada caravana seleccionada
        for car in seleccionadas:
            dieta = db_local.obtener_dieta_completa_por_caravana(car)
            frame_animal = tk.Frame(interior, bg="#f0f0f0", bd=1, relief="solid", padx=5, pady=5)
            frame_animal.pack(fill="x", pady=5, padx=0)

            # número de caravana en negrita
            tk.Label(frame_animal, text=f"Nro. Caravana: {car}", font=("Helvetica", 12, "bold"), bg="#f0f0f0").pack(anchor="w")

            if dieta is None:
                tk.Label(frame_animal, text="No hay dieta asignada.", font=("Helvetica", 12), fg="red", bg="#f0f0f0").pack(anchor="w", pady=2)
                continue

            # primera línea: tipo de curva y peso
            linea1 = f"Tipo curva: {dieta.get('tipo_curva','')}    peso: {dieta.get('peso_total',0):.1f} kg"
            tk.Label(frame_animal, text=linea1, font=("Helvetica", 12), bg="#f0f0f0").pack(anchor="w", pady=2)

            # segunda línea: agua, intervalo, dosis
            agua_str = "Sí" if dieta.get('agua') else "No"
            linea2 = f"Agua: {agua_str}    Interv.: {dieta.get('intervalo',0)}h    Cant. dosis: {dieta.get('cantidad_dosis',0)}"
            tk.Label(frame_animal, text=linea2, font=("Helvetica", 12), bg="#f0f0f0").pack(anchor="w", pady=2)

        # boton cerrar
        boton_cerrar = tk.Button(modal, text="Cerrar", font=("Helvetica", 14), command=lambda: (modal.grab_release(), modal.destroy()), bg="red", fg="#ffffff", bd=7)
        boton_cerrar.pack(pady=10)

        # forzar enfoque en modal
        modal.focus_force()



    def crear_encabezados(self):
        tk.Label(
            self.frame_interior,
            text="Seleccionar",
            font=("Helvetica", 12, "bold")
        ).grid(row=0, column=0, padx=10, pady=5, sticky="w")

        tk.Label(
            self.frame_interior,
            text="N° Caravana",
            font=("Helvetica", 12, "bold")
        ).grid(row=0, column=1, padx=10, pady=5, sticky="w")

        tk.Label(
            self.frame_interior,
            text="N° Interno",
            font=("Helvetica", 12, "bold")
        ).grid(row=0, column=2, padx=10, pady=5, sticky="w")

        tk.Label(
            self.frame_interior,
            text="Inseminación",
            font=("Helvetica", 12, "bold")
        ).grid(row=0, column=3, padx=10, pady=5, sticky="w")

    def abrir_teclado_numerico(self):
        self.teclado = TecladoNumerico(self, self.numero_caravana)

    def abrir_teclado_numerico_interno(self):
        self.teclado = TecladoNumerico(self, self.numero_interno)


    def seleccionar_fecha(self):
        # Verificar si hay animales seleccionados
        seleccionados = []
        for checkbox in self.checkbuttons:
            if checkbox.var.get():
                car = getattr(checkbox, "caravana", None)
                insem = getattr(checkbox, "fecha_inseminacion", None)
                if car:
                    seleccionados.append((car, insem))
        
        # Si hay seleccionados, abre calendario para actualizar sus fechas
        if seleccionados:
            self.actualizar_fecha_inseminacion_seleccionados(seleccionados)
        else:
            # Comportamiento original: se llena el campo para agregar un nuevo animal
            seleccionar_fecha(self, self.fecha_inseminacion)

    def enviar_y_esperar_ok(self, mensaje_str, reintentos=3, timeout_segundos=1.5):
        """Envía un mensaje por UART y espera la respuesta 'ANIMAL_RECEIVED' u 'OK'.
        Retorna True si fue exitoso, False en caso contrario."""
        ser = getattr(self.master, "ser", None)
        if ser is None:
            print("No hay puerto serie configurado en self.master.ser")
            return False

        original_timeout = ser.timeout
        ser.timeout = timeout_segundos
        exito = False

        for intento in range(reintentos):
            try:
                ser.reset_input_buffer()
                ser.write(mensaje_str.encode('utf-8'))
                print(f"[UART] Intento {intento+1}/{reintentos} enviando: {mensaje_str}")

                # Leer hasta que timeout o recibamos la cadena esperada
                start_time = time.time()
                while time.time() - start_time < timeout_segundos:
                    linea = ser.readline()
                    if linea:
                        resp = linea.decode('utf-8', errors='ignore').strip()
                        print(f"[UART] Respuesta ESP: {resp}")
                        if "ANIMAL_RECEIVED" in resp or "OK_RECEIVED" in resp or "OK" in resp:
                            exito = True
                            break
            except Exception as e:
                print(f"[UART] Error en el envío/recepción: {e}")

            if exito:
                break
            
            time.sleep(0.5) # Pausa antes de reintentar

        ser.timeout = original_timeout
        return exito

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

    def construir_json_animal(self, caravana, ts_inseminacion):
        """Construye el diccionario básico del animal (solo caravana e inseminación)."""
        return {
            "caravana": caravana,
            "inseminacion": int(ts_inseminacion)
        }

    def actualizar_fecha_inseminacion_seleccionados(self, seleccionados):
        """Abre un calendario para actualizar la fecha de inseminación de animales seleccionados."""
        from util.util_calendario import seleccionar_fecha as abrir_calendario
        
        # Variable temporal para capturar la fecha seleccionada
        fecha_temp = tk.StringVar()
        abrir_calendario(self, fecha_temp)
        
        # Esperar a que se seleccione una fecha
        self.wait_variable(fecha_temp)
        
        nueva_fecha_str = fecha_temp.get().strip()
        if not nueva_fecha_str:
            return
        
        # Convertir fecha del calendario (YYYY-MM-DD) a timestamp de 10 dígitos (segundos desde epoch) como string
        try:
            fecha_dt = datetime.strptime(nueva_fecha_str, "%Y-%m-%d")
            fecha_ts = str(int(fecha_dt.timestamp()))
        except Exception as e:
            self.mostrar_mensaje("Error", f"Error al procesar la fecha: {e}")
            return
        
        num_corral = self._obtener_num_corral_actual()
        
        # 1. Armar el JSON (tarea: 10 + CRC)
        lista_animales = []
        for caravana, fecha_vieja in seleccionados:
            animal_data = self.construir_json_animal(caravana, fecha_ts)
            lista_animales.append(animal_data)
        
        data_json = {
            "tarea": 15,
            "corral": num_corral,
            "animales": lista_animales
        }
        json_str = json.dumps(data_json)
        crc_val = self.calcular_crc16(json_str)
        mensaje_json = f"<<<{json_str}>>>|CRC:{crc_val:04X}"

        # 2. Enviar y esperar OK (3 reintentos)
        self.mostrar_mensaje("Enviando", "Enviando datos al equipo...", "info")
        self.update() # Refrescar UI

        exito_uart = self.enviar_y_esperar_ok(mensaje_json, reintentos=3, timeout_segundos=1.5)

        if not exito_uart:
            self.mostrar_mensaje("Error de Comunicación", "Error de comunicacion.los datos no fueron almacenados", "error")
            return

        # 3. Si fue exitoso, guardar en SQLite
        for caravana, fecha_vieja in seleccionados:
            try:
                # Actualizar en SQLite
                db_local.actualizarFechaInseminacion(caravana, num_corral, fecha_ts)
            except Exception as e:
                self.mostrar_mensaje("Error", f"Error al actualizar la BD (caravana {caravana}): {e}")
        
        # Refrescar la tabla
        self.cargar_animales(self.selector_corral.get())
        
        # Ocultar popup de enviando (el próximo msj lo pisa) o mostrar éxito
        self.mostrar_mensaje("Éxito", f"Fecha de inseminación actualizada correctamente para {len(seleccionados)} animal(es). y enviada al equipo.", "info")

    def guardar_fecha(self, fecha, fecha_window):
        self.fecha_inseminacion.set(fecha)
        fecha_window.grab_release()
        fecha_window.destroy()
        self.focus_force()


    def cargar_animales_al_seleccionar(self, event):
        self.cargar_animales(self.selector_corral.get())

    def cargar_animales(self, corral):
        """Carga desde SQLite los animales del corral seleccionado."""
        num_corral = self._obtener_num_corral_actual()

        # Limpiar el frame interior
        for widget in self.frame_interior.winfo_children():
            widget.destroy()

        self.checkbuttons = []
        self.crear_encabezados()

        try:
            # (caravana, numeroInterno, fechaInseminacion, pesoTotal, cantidadDosis, intervalo)
            filas = db_local.obtenerAnimalesPorCorral(num_corral)
        except Exception as e:
            print(f"Error cargando animales de SQLite para corral {num_corral}: {e}")
            filas = []

        for i, fila in enumerate(filas, start=1):
            caravana = fila[0]
            interno = fila[1]
            fecha_ins_db = fila[2]

            # Convertimos de YYYY-MM-DD (DB) a dd/mm/YYYY (UI), si se puede
            fecha_ui = ""
            if fecha_ins_db:
                try:
                    fecha_ui = datetime.strptime(
                        str(fecha_ins_db),
                        "%Y-%m-%d"
                    ).strftime("%d/%m/%Y")
                except Exception:
                    fecha_ui = str(fecha_ins_db)

            self.agregar_fila_canvas(
                caravana=caravana,
                interno=str(interno) if interno is not None else "",
                #inseminacion=fecha_ui,
                inseminacion=fecha_ins_db,
                agua=0,
                row=i
            )

        self.canvas.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def agregar_fila(self):
        """Alta de animal: inserta en SQLite y refresca la tabla."""
        num_corral = self._obtener_num_corral_actual()
        caravana = self.numero_caravana.get().strip()
        interno = self.numero_interno.get().strip()
        inseminacion_ui = self.fecha_inseminacion.get().strip()

        # Validaciones básicas
        try:
            animales_corral = db_local.obtenerAnimalesPorCorral(num_corral)
        except Exception as e:
            print(f"Error leyendo animales para validar en corral {num_corral}: {e}")
            animales_corral = []

        if len(animales_corral) >= 20:
            self.mostrar_mensaje("Error", f"No puedes agregar más de 20 animales en el Corral {num_corral}.")
            return

        if not caravana:
            self.mostrar_mensaje("Error", "Debes ingresar el N° Caravana.")
            return

        if len(caravana) != 15 or not caravana.isdigit():
            self.mostrar_mensaje("Error", "El N° Caravana debe tener exactamente 15 dígitos.")
            return

        if not inseminacion_ui:
            self.mostrar_mensaje("Error", "Debes seleccionar una fecha de inseminación.")
            return

        # Evitar caravana duplicada en el mismo corral
        for fila in animales_corral:
            if fila[0] == caravana:
                self.mostrar_mensaje(
                    "Error",
                    f"Ya existe un animal con N° Caravana {caravana} en este corral."
                )
                return
        #comentamos esto, para prueba de insert:18/02
        #fecha_sql = inseminacion_ui
        try:
            fecha_dt = datetime.strptime(inseminacion_ui, "%Y-%m-%d")
            # Guardar como timestamp de 10 dígitos (segundos desde epoch) como texto
            fecha_sql = str(int(fecha_dt.timestamp()))
        except Exception:
            # En caso de error, usar la fecha actual como timestamp
            fecha_sql = str(int(datetime.now().timestamp()))

        # 1. Construir JSON (tarea: 10 + CRC)
        animal_data = self.construir_json_animal(caravana, fecha_sql)
        data_json = {
            "tarea": 10,
            "corral": num_corral,
            "animales": [animal_data]
        }
        json_str = json.dumps(data_json)
        crc_val = self.calcular_crc16(json_str)
        mensaje_json = f"<<<{json_str}>>>|CRC:{crc_val:04X}"

        # 2. Enviar por UART con reintentos
        self.mostrar_mensaje("Enviando", "Enviando datos al equipo...", "info")
        self.update() # Para que el modal anterior se renderice
        exito_uart = self.enviar_y_esperar_ok(mensaje_json, reintentos=3, timeout_segundos=1.5)

        if not exito_uart:
            self.mostrar_mensaje("Error de Comunicación", "El equipo no respondió tras 3 intentos. El animal NO ha sido guardado.", "error")
            return

        # 3. Si llega el OK, Guardar en SQLite
        try:
            db_local.insertarAnimal(
                caravana=caravana,
                numeroInterno=interno,
                fechaInseminacion=fecha_sql,
                corral=num_corral
            )
        except Exception as e:
            self.mostrar_mensaje("Error", f"Error al insertar el animal en BD: {e}")
            return

        # 4. Asignar Dieta por Defecto (Tarea 20) y actualizar SQLite
        try:
            _, _, peso_desc, _ = db_local.obtenerConfiguracion()
            peso_int = int(float(peso_desc) * 10)  # Convertir a décimas de kg para Modbus

            # Enviar la dieta por Modbus
            data_json_dieta = {
                "tarea": 20,
                "corral": num_corral,
                "curva": 1,        # 1 = Constante
                "peso": peso_int,
                "dosis": 1,
                "intervalo": 1,
                "agua": 1,
                "indice": 1,       # 1 = Normal (100%)
                "animales": [caravana]
            }
            json_str_dieta = json.dumps(data_json_dieta)
            crc_val_dieta = self.calcular_crc16(json_str_dieta)
            mensaje_json_dieta = f"<<<{json_str_dieta}>>>|CRC:{crc_val_dieta:04X}"
            
            self.enviar_y_esperar_ok(mensaje_json_dieta, reintentos=3, timeout_segundos=1.5)

            # Insertar la dieta exacta en SQLite para que Tkinter y ESP32 coincidan
            id_dieta = db_local.insertarDietaConfig(
                descripcion="Constante - Normal", # Curva 1 y Indice 1
                pesoTotal=peso_int,
                cantidadDosis=1,
                intervalo=1,
                tirarAgua=1
            )
            db_local.actualizarDietaPorCaravanaYFecha(
                caravana=caravana,
                fechaInseminacion=fecha_sql,
                idDieta=id_dieta
            )
        except Exception as e:
            print(f"Error sincronizando dieta por defecto: {e}")

        # Refrescar la tabla desde la DB
        self.cargar_animales(self.selector_corral.get())

        # Limpiar campos
        self.numero_caravana.set("")
        self.numero_interno.set("")
        self.fecha_inseminacion.set("")
        
        self.mostrar_mensaje("Guardado Exitoso", "El animal ha sido guardado correctamente y enviado al equipo.", "info")

    def eliminar_fila(self):
        """Baja de animales seleccionados: elimina en SQLite y refresca."""
        num_corral = self._obtener_num_corral_actual()

        caravanas_a_eliminar = []
        for checkbox in self.checkbuttons:
            if checkbox.var.get():
                car = getattr(checkbox, "caravana", None)
                if car:
                    caravanas_a_eliminar.append(car)

        if not caravanas_a_eliminar:
            self.mostrar_mensaje("Error", "Selecciona al menos un animal para eliminar.")
            return

        # 1. Enviar JSON de baja (Tarea 11)
        lista_animales = [{"caravana": car} for car in caravanas_a_eliminar]
        data_json = {"tarea": 11, "corral": num_corral, "animales": lista_animales}
        json_str = json.dumps(data_json)
        crc_val = self.calcular_crc16(json_str)
        mensaje_json = f"<<<{json_str}>>>|CRC:{crc_val:04X}"
        
        self.mostrar_mensaje("Enviando", "Enviando orden de baja al equipo...", "info")
        self.update()
        exito_uart = self.enviar_y_esperar_ok(mensaje_json, reintentos=3, timeout_segundos=1.5)
        
        if not exito_uart:
            self.mostrar_mensaje("Error de Comunicación", "El equipo no respondió. Cancelando baja.", "error")
            return

        # 2. Borrar en SQLite
        try:
            db_local.eliminarAnimalesPorCorralYCaravanas(
                corral=num_corral,
                caravanas=caravanas_a_eliminar
            )
        except Exception as e:
            self.mostrar_mensaje("Error", f"Error al eliminar animales en SQLite: {e}")
            return

        # Refrescar tabla
        self.cargar_animales(self.selector_corral.get())
        
        self.mostrar_mensaje("Éxito", "Animales eliminados del equipo y de base de datos local.", "info")


    def agregar_fila_canvas(self, caravana, interno, inseminacion, agua, row):
        """Agrega una fila visual en el canvas para un animal."""
        var = tk.BooleanVar()
        checkbox = tk.Checkbutton(
            self.frame_interior,
            text="Select",
            variable=var
        )
        checkbox.grid(row=row, column=0, padx=10, pady=5, sticky="w")
        checkbox.var = var
        checkbox.caravana = caravana
        checkbox.fecha_inseminacion = inseminacion
        #checkbox.fecha_inseminacion = fecha_ins_db
        checkbox.numero_interno = interno

        label_caravana = tk.Label(
            self.frame_interior,
            text=caravana,
            font=("Helvetica", 12)
        )
        label_caravana.grid(row=row, column=1, padx=10, pady=5, sticky="w")

        label_interno = tk.Label(
            self.frame_interior,
            text=interno if interno else "",
            font=("Helvetica", 12)
        )
        label_interno.grid(row=row, column=2, padx=10, pady=5, sticky="w")
        
        fecha_para_mostrar = ""
        if inseminacion:
            try :
                fecha_para_mostrar = datetime.fromtimestamp(int(float(inseminacion))).strftime("%d/%m/%Y")
                #fecha_para_mostrar = datetime.strptime(inseminacion, "%Y-%m-%d").strftime("%d/%m/%Y")
            except:
                fecha_para_mostrar = str(inseminacion)

        label_inseminacion = tk.Label(
            self.frame_interior,
            text=fecha_para_mostrar,
            font=("Helvetica", 12)
        )
        label_inseminacion.grid(row=row, column=3, padx=10, pady=5, sticky="w")

        self.checkbuttons.append(checkbox)
        self.frame_interior.grid_columnconfigure(0, weight=1)
        self.frame_interior.grid_columnconfigure(1, weight=1)
        self.frame_interior.grid_columnconfigure(2, weight=1)
        self.frame_interior.grid_columnconfigure(3, weight=1)


    def cerrar_ventana(self):
        self.destroy()

    def ir_dieta(self):
        if not any(checkbox.var.get() for checkbox in self.checkbuttons):
            self.mostrar_mensaje(
                "Error",
                "Selecciona al menos una fila para ir a la dieta."
            )
            return

        datos_seleccionados = []
        for checkbox in self.checkbuttons:
            if checkbox.var.get():
                caravana = getattr(checkbox, "caravana", "")
                inseminacion = getattr(checkbox, "fecha_inseminacion", "")
                
                if caravana:
                    datos_seleccionados.append((caravana, inseminacion))

        self.withdraw()
        num_corral = self._obtener_num_corral_actual()
        self.dieta_window = ir_dietaWindow(
            self.master,
            datos_seleccionados,
            self.volver_a_gestion_animal,
            getattr(self, "uart", None),
            num_corral
        )

    def volver_a_gestion_animal(self):
        self.cargar_animales(self.selector_corral.get())
        self.deiconify()
        self.focus_force()

    def actualizar_interfaz(self, corral):
        self.cargar_animales(corral)

    def mostrar_mensaje(self, titulo, texto, tipo="error"):
        mostrar_mensaje(self, titulo, texto, tipo)
