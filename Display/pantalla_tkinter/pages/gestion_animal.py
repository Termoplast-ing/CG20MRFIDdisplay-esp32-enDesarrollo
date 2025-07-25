import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog
from tkcalendar import DateEntry
from util.util_teclado import TecladoNumerico
from pages.ir_dieta import ir_dietaWindow
from util.util_json import cargar_datos, guardar_datos
from util.util_calendario import seleccionar_fecha
import util.util_ventana as util_ventana
import serial
from util.util_mensaje import mostrar_mensaje

class GestionAnimalWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)        
        self.overrideredirect(True)
        self.geometry("480x800")
        self.config(bg="#EF9480")
        self.resizable(False, False)
        # Centrar la ventana de login
        util_ventana.centrar_ventana(self, 480, 800)
        self.mensaje_actual = None
        # Cargar datos desde el archivo JSON
        self.animales_por_corral = cargar_datos()
        self.uart = serial.Serial(port="/dev/serial0", baudrate=9600, timeout=1, write_timeout=1)
        # Variables para almacenar el N° Caravana y la fecha de inseminación
        self.numero_caravana = tk.StringVar()
        self.numero_interno = tk.StringVar()
        self.fecha_inseminacion = tk.StringVar()
        

        # Crear un frame para el logo en la parte superior
        self.frame_logo = tk.Frame(self, bg='#EF9480', height=100)
        self.frame_logo.pack(side=tk.TOP, fill="x",pady=22)        
        # Crear el logo en la ventana secundaria
        self.crear_logo(self.frame_logo)

        # Crear un frame para el selector de corral debajo del logo
        self.frame_selector = tk.Frame(self, bg='#EF9480', height=50)
        self.frame_selector.pack(side=tk.TOP, fill="x", pady=5)
        self.crear_selector_corral(self.frame_selector)

        # Frame donde se dibujará el Canvas
        self.frame_canvas = tk.Frame(self, bg="#EF9480")
        self.frame_canvas.pack(side=tk.TOP, fill="both", expand=True)
        self.canvas = tk.Canvas(self.frame_canvas, bg="#ffffff", scrollregion=(0, 0, 400, 1000))
        self.canvas.pack(side=tk.LEFT, fill="both", expand=True)

        self.scrollbar = tk.Scrollbar(self.frame_canvas, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill="y")
        self.canvas.config(yscrollcommand=self.scrollbar.set)

        self.frame_interior = tk.Frame(self.canvas, bg="#ffffff")
        self.canvas.create_window((0, 0), window=self.frame_interior, anchor="nw")

        self.frame_interior.bind("<Configure>",lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.checkbuttons = []  # Lista de checkbuttons para gestionar eliminación

        # Botones (+) y (-)
        self.frame_botones_superiores = tk.Frame(self, bg='#EF9480', height=60)
        self.frame_botones_superiores.pack(side=tk.TOP, fill="x", pady=10)

        boton_agregar = tk.Button(self.frame_botones_superiores, text="+", font=("Helvetica", 16),command=self.agregar_fila, bg="red", fg="#ffffff", bd=7)
        boton_agregar.pack(side=tk.LEFT, padx=40, pady=10)

        boton_eliminar = tk.Button(self.frame_botones_superiores, text="-", font=("Helvetica", 16),command=self.eliminar_fila, bg="red", fg="#ffffff", bd=7)
        boton_eliminar.pack(side=tk.RIGHT, padx=40, pady=10)

        # Botones para N° Caravana y Inseminación
        self.frame_botones_inferiores = tk.Frame(self, bg='#EF9480', height=60)
        self.frame_botones_inferiores.pack(side=tk.TOP, fill="x", pady=10)

        boton_caravana = tk.Button(self.frame_botones_inferiores, text="N° Caravana", font=("Helvetica", 16),command=self.abrir_teclado_numerico, bg="red", fg="#ffffff", bd=7)
        boton_caravana.pack(side=tk.LEFT, padx=6, pady=10)

        boton_interno = tk.Button(self.frame_botones_inferiores, text="N° Interno", font=("Helvetica", 16),command=self.abrir_teclado_numerico_interno, bg="red", fg="#ffffff", bd=7)
        boton_interno.pack(side=tk.LEFT, padx=6, pady=10)

        boton_inseminacion = tk.Button(self.frame_botones_inferiores, text="Inseminación", font=("Helvetica", 16),command=self.seleccionar_fecha, bg="red", fg="#ffffff", bd=7)
        boton_inseminacion.pack(side=tk.RIGHT, padx=6, pady=10)

        # Botón para volver a la ventana principal
        self.frame_boton_atras = tk.Frame(self, bg="#EF9480", height=60)
        self.frame_boton_atras.pack(side=tk.BOTTOM, fill="x")
        boton_atras = tk.Button(self, text="<< Atrás", font=("Helvetica", 16), command=self.cerrar_ventana, bg="red", fg="#ffffff", bd=7)
        boton_atras.pack(side=tk.LEFT, padx=10, pady=10)

        boton_Dieta = tk.Button(self, text="Ir a Dieta >>", font=("Helvetica", 16), command=self.ir_dieta, bg="red", fg="#ffffff", bd=7)
        boton_Dieta.pack(side=tk.RIGHT,padx=10, pady=10)

        self.crear_encabezados()
        # Cargar datos guardados al iniciar la ventana
        self.cargar_animales(self.selector_corral.get())

    def crear_logo(self, frame):
        """Función para crear y ubicar el logo en un frame dado"""
        label = tk.Label(frame, image=self.master.logo, bg='#EF9480')
        label.place(relx=0.5, rely=0.5, anchor="center")

    def crear_selector_corral(self, frame):
        """Función para crear el selector de corral"""
        corrales = [f'Corral {i}' for i in range(1, 21)]
        label_corral = tk.Label(frame, text="Seleccionar Corral:", font=("Helvetica", 14), bg='#EF9480', fg="black")
        label_corral.pack(side=tk.LEFT, padx=10)

        self.selector_corral = ttk.Combobox(frame, values=corrales, font=("Helvetica", 12), state="readonly")
        self.selector_corral.set(corrales[0])
        self.selector_corral.pack(side=tk.LEFT, padx=10)

        # Asignar evento al selector de corral para cargar los datos
        self.selector_corral.bind("<<ComboboxSelected>>", self.cargar_animales_al_seleccionar)

    def cargar_animales_al_seleccionar(self, event):
        """Cargar los animales del corral seleccionado al cambiar de corral"""
        corral = self.selector_corral.get()
        self.cargar_animales(corral)

    def crear_encabezados(self):
        """Función para crear los encabezados de la tabla"""
        tk.Label(self.frame_interior, text="Seleccionar", font=("Helvetica", 12, "bold")).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        tk.Label(self.frame_interior, text="N° Caravana", font=("Helvetica", 12, "bold")).grid(row=0, column=1, padx=10, pady=5, sticky="w")
        tk.Label(self.frame_interior, text="N° Interno", font=("Helvetica", 12, "bold")).grid(row=0, column=2, padx=10, pady=5, sticky="w")
        tk.Label(self.frame_interior, text="Inseminación", font=("Helvetica", 12, "bold")).grid(row=0, column=3, padx=10, pady=5, sticky="w")

    def abrir_teclado_numerico(self):
        """Abre el teclado numérico para ingresar el N° Caravana"""
        self.teclado = TecladoNumerico(self, self.numero_caravana)

    def abrir_teclado_numerico_interno(self):
        """Abre el teclado numérico para ingresar el N° Interno"""
        self.teclado = TecladoNumerico(self, self.numero_interno)

    def seleccionar_fecha(self):
        """Abre un selector de fecha para la inseminación"""
        seleccionar_fecha(self, self.fecha_inseminacion)

    def guardar_fecha(self, fecha, fecha_window):
        """Guarda la fecha seleccionada y cierra la ventana"""
        self.fecha_inseminacion.set(fecha)
        fecha_window.grab_release()
        fecha_window.destroy()
        self.focus_force() 

    def agregar_fila(self):
        """Agrega una fila al Canvas si ambos campos están completos"""
        corral = self.selector_corral.get()
        caravana = self.numero_caravana.get()
        interno = self.numero_interno.get()
        inseminacion = self.fecha_inseminacion.get()

        if len(self.animales_por_corral[corral]) >= 20:
            self.mostrar_mensaje("Error", f"No puedes agregar más de 20 animales en el {corral}.")
            return

        if not caravana:
            self.mostrar_mensaje("Error", "Debes ingresar el N° Caravana.")
            return

        if len(caravana) != 15:
            self.mostrar_mensaje("Error", "El N° Caravana debe tener 15 dígitos.")
            return

        if not inseminacion:
            self.mostrar_mensaje("Error", "Debes seleccionar una fecha de inseminación.")
            return
        # Si el N° Interno no se ingresa, se guarda como una cadena vacía
        if not interno:
            interno = ""

        # Crear una nueva fila con los datos (9 valores)
        nuevo_animal = [
            caravana,        # N° Caravana
            interno,         # N° Interno
            inseminacion,    # Fecha de inseminación
            0,               # Agua (0 o 1)
            "",              # Tipo de curva
            "",              # Índice corporal
            0.0,             # Peso
            1,               # Cantidad/Dosis
            1                # Intervalo
        ]
        self.animales_por_corral[corral].append(nuevo_animal)

        # Guardar los datos en el archivo JSON
        guardar_datos(self.animales_por_corral)
        print("Datos guardados:", self.animales_por_corral)  # Depuración: Ver datos guardados
        self.actualizar_interfaz(corral)
        self.enviar_uart(f"AGREGAR,{caravana},{interno},{inseminacion}")

        # Limpiar los campos después de agregar
        self.numero_caravana.set("")
        self.numero_interno.set("")
        self.fecha_inseminacion.set("")

    def eliminar_fila(self):
        """Elimina las filas seleccionadas"""
        corral = self.selector_corral.get()
        animales = self.animales_por_corral[corral]
        # Crear una lista con los índices de las filas seleccionadas
        indices_a_eliminar = [
            self.checkbuttons.index(checkbox)
            for checkbox in self.checkbuttons
            if checkbox.var.get()
        ]
        # Eliminar las filas seleccionadas (en orden inverso para evitar problemas de índices)
        for index in sorted(indices_a_eliminar, reverse=True):
            animales.pop(index)

        # Guardar los datos en el archivo JSON
        guardar_datos(self.animales_por_corral)
        # Actualizar la interfaz
        self.actualizar_interfaz(corral)
   
    def cargar_animales(self, corral):
        """Carga los animales del corral seleccionado en el Canvas"""
        print(f"Cargando animales del corral: {corral}")  # Depuración: Ver corral seleccionado

        # Limpiar el Canvas antes de cargar nuevos datos
        for widget in self.frame_interior.winfo_children():
            widget.destroy()

        self.checkbuttons = []  # Reiniciar la lista de checkbuttons
        # Añadir encabezados
        self.crear_encabezados()
        # Obtener los animales del corral seleccionado
        animales = self.animales_por_corral.get(corral, [])

        # Agregar filas para cada animal
        for i, animal in enumerate(animales, start=1):
            # Asegurarse de que el animal tenga 5 valores
            if len(animal) < 9:
                animal.extend([""] * (9 - len(animal)))  # Agregar valores predeterminados si faltan
            caravana, interno, inseminacion, agua, curva, indice_corporal, peso, dosis, intervalo = animal
            self.agregar_fila_canvas(caravana, interno, inseminacion, agua, i)

        # Actualizar la región de desplazamiento del Canvas
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def agregar_fila_canvas(self, caravana,interno, inseminacion,agua,row):
        """Agrega una fila al Canvas"""
        var = tk.BooleanVar()
        checkbox = tk.Checkbutton(self.frame_interior, text="Select", variable=var)
        checkbox.grid(row=row, column=0, padx=10, pady=5, sticky="w")

        checkbox.var = var
        
        label_caravana = tk.Label(self.frame_interior, text=caravana, font=("Helvetica", 12))
        label_caravana.grid(row=row, column=1, padx=10, pady=5,sticky="w")

        label_interno = tk.Label(self.frame_interior, text=interno if interno else "", font=("Helvetica", 12))
        label_interno.grid(row=row, column=2, padx=10, pady=5,sticky="w")

        label_inseminacion = tk.Label(self.frame_interior, text=inseminacion, font=("Helvetica", 12))
        label_inseminacion.grid(row=row, column=3, padx=10, pady=5,sticky="w")

        # Guardar el checkbox en la lista
        self.checkbuttons.append(checkbox)

        # Configuración para que las columnas se ajusten automáticamente
        self.frame_interior.grid_columnconfigure(0, weight=1)
        self.frame_interior.grid_columnconfigure(1, weight=1)
        self.frame_interior.grid_columnconfigure(2, weight=1)
        self.frame_interior.grid_columnconfigure(3, weight=1)

    def cerrar_ventana(self):
        """Cerrar la ventana de gestión de animales y guardar los datos."""
        guardar_datos(self.animales_por_corral)
        self.destroy()

    def ir_dieta(self):
        """Verifica si hay al menos una fila seleccionada antes de ir a la ventana de dieta"""
        if not any(checkbox.var.get() for checkbox in self.checkbuttons):
            self.mostrar_mensaje("Error", "Selecciona al menos una fila para ir a la dieta.")
            return
    
        # Obtener los datos seleccionados
        datos_seleccionados = []
        for checkbox in self.checkbuttons:
            if checkbox.var.get():  # Si el checkbox está seleccionado
            # Obtener los datos de la fila correspondiente
                indice = self.checkbuttons.index(checkbox)
                caravana = self.animales_por_corral[self.selector_corral.get()][indice][0]  # N° Caravana
                inseminacion = self.animales_por_corral[self.selector_corral.get()][indice][2]  # Fecha de inseminación
                datos_seleccionados.append((caravana, inseminacion))
        self.withdraw()
        # Abrir la ventana de dieta y pasar los datos seleccionados
        self.dieta_window = ir_dietaWindow(self.master, datos_seleccionados,self.volver_a_gestion_animal,self.uart)

    def volver_a_gestion_animal(self):
        """Volver a la ventana de gestión de animales desde la ventana de dieta"""
        self.animales_por_corral = cargar_datos()       
        self.actualizar_interfaz(self.selector_corral.get())
        # Asegurarse de que la ventana esté activa
        self.deiconify()  # Mostrar la ventana si estaba oculta
        self.focus_force()  # Forzar el foco en la ventana

    def actualizar_interfaz(self, corral):
        """Actualiza la interfaz después de agregar o eliminar filas"""
        print(f"Actualizando interfaz para el corral: {corral}")  # Depuración
        for widget in self.frame_interior.winfo_children():
            widget.destroy()  # Limpiar la vista actual

        self.checkbuttons = []  # Reiniciar la lista de checkbuttons

        self.crear_encabezados()  # Añadir encabezados

        animales = self.animales_por_corral.get(corral, [])

        # Agregar filas para cada animal
        for i, animal in enumerate(animales, start=1):
            # Asegurarse de que el animal tenga 5 valores
            if len(animal) < 9:
                animal.extend([""] * (9 - len(animal)))  # Agregar valores predeterminados si faltan
            caravana, interno, inseminacion, agua, curva, indice_corporal, peso, dosis, intervalo = animal
            self.agregar_fila_canvas(caravana, interno, inseminacion, agua, i)

        # Actualizar la región de desplazamiento del Canvas
        self.canvas.update_idletasks()  # Actualizar el Canvas
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def mostrar_mensaje(self,titulo, texto, tipo="error"):
        """Muestra mensajes con borde negro grueso y estilo mejorado"""
        mostrar_mensaje(self, titulo, texto, tipo)

    

    
