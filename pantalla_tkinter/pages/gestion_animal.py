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
from util import sqlite as db_local
import serial


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

        self.frame_botones_superiores = tk.Frame(self, bg='#EF9480', height=60)
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
        boton_agregar.pack(side=tk.LEFT, padx=40, pady=10)

        boton_eliminar = tk.Button(
            self.frame_botones_superiores,
            text="-",
            font=("Helvetica", 16),
            command=self.eliminar_fila,
            bg="red",
            fg="#ffffff",
            bd=7
        )
        boton_eliminar.pack(side=tk.RIGHT, padx=40, pady=10)

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
        seleccionar_fecha(self, self.fecha_inseminacion)

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
            fecha_dt = datetime.strptime(inseminacion_ui, "%d/%m/%Y")
            fecha_sql= int(fecha_dt.timestamp())
            #fecha_sql = datetime.strptime(inseminacion_ui,"%d/%m/%Y").strftime("%Y-%m-%d")
        except Exception:
            fecha_sql = int(datetime.now().timestamp())

        # Interno puede ir como None si está vacío
        numero_interno = interno if interno != "" else None

        # Alta en SQLite
        try:
            db_local.insertarAnimal(
                caravana=caravana,
                numeroInterno=numero_interno,
                fechaInseminacion=fecha_sql,
                corral=num_corral
            )
        except Exception as e:
            self.mostrar_mensaje("Error", f"Error al insertar el animal en SQLite: {e}")
            return

        # Refrescar la tabla desde la DB
        self.cargar_animales(self.selector_corral.get())

        # Limpiar campos
        self.numero_caravana.set("")
        self.numero_interno.set("")
        self.fecha_inseminacion.set("")

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
        self.dieta_window = ir_dietaWindow(
            self.master,
            datos_seleccionados,
            self.volver_a_gestion_animal,
            getattr(self, "uart", None)
        )

    def volver_a_gestion_animal(self):
        self.cargar_animales(self.selector_corral.get())
        self.deiconify()
        self.focus_force()

    def actualizar_interfaz(self, corral):
        self.cargar_animales(corral)

    def mostrar_mensaje(self, titulo, texto, tipo="error"):
        mostrar_mensaje(self, titulo, texto, tipo)
