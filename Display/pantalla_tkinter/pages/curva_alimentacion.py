import tkinter as tk
import os
import json
import serial
import util.util_ventana as util_ventana
from util.util_mensaje import mostrar_mensaje

# Configuración de rutas
DIR_CONFIG = "config"
ARCHIVO_CURVAS = "curvas.json"

def cargar_todas_curvas():
    """Carga todas las curvas desde el archivo principal"""
    if not os.path.exists(os.path.join(DIR_CONFIG, ARCHIVO_CURVAS)):
        return []
        
    try:
        with open(os.path.join(DIR_CONFIG, ARCHIVO_CURVAS), 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        mostrar_mensaje(None, "Error", f"Error al cargar curvas: {str(e)}", "error")
        return []
        
def obtener_lista_curvas():
    curvas_guardadas = cargar_todas_curvas()
    curvas_nuevas = [c["nombre"] for c in curvas_guardadas if c["nombre"].lower() not in ["curva1","curva2","curva3"]]
    lista_final = ['']
    lista_final.extend(curvas_nuevas)
    lista_final.extend(["curva1", "curva2", "curva3"])
    return lista_final

def existe_curva(nombre):
    """Verifica si ya existe una curva con este nombre"""
    curvas = cargar_todas_curvas()
    return any(curva["nombre"].lower() == nombre.lower() for curva in curvas)

def guardar_curva(nombre, segmentos):
    """Guarda o actualiza una curva en el archivo principal"""
    if not os.path.exists(DIR_CONFIG):
        os.makedirs(DIR_CONFIG)
    
    curvas = cargar_todas_curvas()
    
    # Buscar si ya existe la curva
    curva_existente = next((c for c in curvas if c["nombre"].lower() == nombre.lower()), None)
    
    if curva_existente:
        # Actualizar curva existente
        curva_existente["segmentos"] = segmentos
    else:
        # Agregar nueva curva
        curvas.append({
            "nombre": nombre,
            "segmentos": segmentos
        })
    
    try:
        with open(os.path.join(DIR_CONFIG, ARCHIVO_CURVAS), 'w', encoding='utf-8') as f:
            json.dump(curvas, f, indent=4, ensure_ascii=False)
        return True, None
    except Exception as e:
        return False, f"Error al guardar curva: {str(e)}"
from util import util_teclado2
from util.teclado import TecladoWindow

class CurvaAlimentacionWindow(tk.Toplevel):
    def __init__(self, master, logo):
        super().__init__(master)
        self.master = master
        self.logo = logo
        self.overrideredirect(True)
        self.geometry("480x800")
        self.config(bg="#EF9480")
        self.resizable(False, False)
        util_ventana.centrar_ventana(self, 480, 800)
        self.grab_set()

        # Crear un frame para el logo en la parte superior
        self.frame_logo = tk.Frame(self, bg='#EF9480', height=100)
        self.frame_logo.pack(side=tk.TOP, fill="x", pady=22)

        # Crear el logo en la ventana secundaria
        self.crear_logo(self.frame_logo)

        # Crear un frame para el nombre
        self.frame_nombre = tk.Frame(self, bg="#EF9480")
        self.frame_nombre.pack(side=tk.TOP, fill="x", padx=20, pady=5)

        # Label y Entry para nombre
        label_nombre = tk.Label(self.frame_nombre, text="Nombre:", font=("Helvetica", 14), bg="#EF9480", fg="black")
        label_nombre.pack(side=tk.LEFT)

        self.entry_nombre = tk.Entry(self.frame_nombre, font=("Helvetica", 14), bg="white", fg="black")
        self.entry_nombre.pack(side=tk.LEFT, padx=20)
        self.entry_nombre.bind('<Button-1>', lambda e: self.mostrar_teclado_alfanumerico(self.entry_nombre))

        # Frame para la tabla segmentos
        self.frame_segmentos = tk.Frame(self, bg="#EF9480")
        self.frame_segmentos.pack(side=tk.TOP, fill="both", padx=20, pady=5, expand=True)

        # Lista para almacenar las filas de la tabla (segmentos)
        self.segmentos = []
        # Inicializar la tabla con un segmento
        self.iniciar_tabla_segmentos()

        # Frame para los botones de agregar y eliminar segmentos
        self.frame_botonera_segmentos = tk.Frame(self, bg="#EF9480")
        self.frame_botonera_segmentos.pack(side=tk.TOP, fill="x", pady=(10, 0))  # Frame en la parte superior

        boton_agregar_segmento = tk.Button(self.frame_botonera_segmentos, text="+", font=("Helvetica", 16), state="disabled", bg="red", fg="white", bd=7)
        boton_agregar_segmento.pack(side=tk.LEFT, padx=10, pady=5)  # Botón + a la izquierda

        boton_eliminar_segmento = tk.Button(self.frame_botonera_segmentos, text="-", font=("Helvetica", 16), state="disabled", bg="red", fg="white", bd=7)
        boton_eliminar_segmento.pack(side=tk.RIGHT, padx=10, pady=5)  # Botón - a la derecha

        # Frame para los botones de Guardar y Atrás (en el mismo frame)
        self.frame_botonera2 = tk.Frame(self, bg="#EF9480")
        self.frame_botonera2.pack(side=tk.BOTTOM, fill="x", pady=(10, 60))  # Frame en la parte inferior

        boton_guardar = tk.Button(self.frame_botonera2, text="Guardar", font=("Helvetica", 16), state="disabled", bg="red", fg="white", bd=7)
        boton_guardar.pack(side=tk.RIGHT, padx=10, pady=10)  # Botón Guardar a la derecha

        boton_atras = tk.Button(self.frame_botonera2, text="<< Atrás", font=("Helvetica", 16), command=self.cerrar_ventana, bg="red", fg="#ffffff", bd=7)
        boton_atras.pack(side=tk.LEFT, padx=10, pady=10)  # Botón Atrás a la izquierda

    def crear_logo(self, frame):
        """Función para crear y ubicar el logo en un frame dado"""
        if self.logo:  # Verificar que el logo esté definido
            label = tk.Label(frame, image=self.logo, bg='#EF9480')
            label.place(relx=0.5, rely=0.5, anchor="center")
        else:
            print("Error: El logo no está definido en CurvaAlimentacionWindow")

    def iniciar_tabla_segmentos(self):
        """Inicializa la tabla de segmentos (solo un segmento al principio)"""
        # Crear el frame del encabezado (solo una vez)
        frame_encabezado = tk.Frame(self.frame_segmentos, bg="#EF9480")
        frame_encabezado.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        # Crear el primer segmento (solo la primera fila visible con los valores de entrada)
        self.crear_segmento(1)

    def crear_segmento(self, index):
        """Crea un nuevo segmento y lo agrega a la tabla"""
        frame_segmento = tk.Frame(self.frame_segmentos, bg="#EF9480")
        frame_segmento.grid(row=index, column=0, sticky="ew", padx=5, pady=0)

        # Columna vacía
        tk.Label(frame_segmento, text="", font=("Helvetica", 10), bg="#EF9480", fg="black").grid(row=0, column=0)

        # Columna con Día e Índice
        frame_contenido = tk.Frame(frame_segmento, bg="#EF9480")
        frame_contenido.grid(row=0, column=1, padx=20, sticky="ew")

        # Día
        label_dia = tk.Label(frame_contenido, text="Día", font=("Helvetica", 11), bg="#EF9480", fg="black")
        label_dia.grid(row=0, column=0)

        entry_dia = tk.Entry(frame_contenido, font=("Helvetica", 11), bg="white", fg="black", width=5)
        if index == 1:
            entry_dia.insert(0, "1")  # Valor inicial para el primer día
            entry_dia.config(state=tk.DISABLED)
        else:
            entry_dia.insert(0, str(self.calcular_dia()))  # Calcular el siguiente día
        entry_dia.grid(row=0, column=1, padx=72)
        entry_dia.bind('<Button-1>', lambda e: util_teclado2.TecladoNumerico(self, entry_dia, es_indice=False))

        # Índice
        label_indice = tk.Label(frame_contenido, text="Índice", font=("Helvetica", 11), bg="#EF9480", fg="black")
        label_indice.grid(row=0, column=2)

        entry_indice = tk.Entry(frame_contenido, font=("Helvetica", 11), bg="white", fg="black", width=5)
        entry_indice.insert(0, "")  # Valor vacío para el índice
        entry_indice.grid(row=0, column=3, padx=72)

        # Validar Índice
        validate_indice = self.register(self.validar_indice)
        entry_indice.config(validate="key", validatecommand=(validate_indice, "%P"))
        entry_indice.bind('<Button-1>', lambda e: util_teclado2.TecladoNumerico(self, entry_indice, es_indice=True))

        # Guardar referencia a todos los campos juntos
        self.segmentos.append((frame_segmento, entry_dia, entry_indice))

    def calcular_dia(self):
        """Calcula el siguiente día basado en la fila anterior"""
        if not self.segmentos:
            return 1
        try:
            return int(self.segmentos[-1][1].get()) + 1
        except ValueError:
            return 2

    def validar_indice(self, texto):
        """Valida que el índice sea un número entre 0 y 200 (con % opcional)"""
        if texto == "":
            return True
            
        # Permite números con o sin % al final
        if texto.endswith('%'):
            texto = texto[:-1]
            
        return texto.isdigit() and 0 <= int(texto) <= 200

    def mostrar_teclado_alfanumerico(self, entry_widget):
        """Muestra el teclado alfanumérico completo para el nombre"""
        TecladoWindow(self, entry_widget)

    def mostrar_teclado_numerico(self, entry_widget):
        """Muestra el teclado numérico para días/índices"""
        util_teclado2.TecladoNumerico(self, entry_widget)

    def agregar_segmento(self):
        """Función para agregar un segmento (una fila en la tabla)"""
        if len(self.segmentos) < 16:
            self.crear_segmento(len(self.segmentos) + 1)
        else:
            mostrar_mensaje(self, "Límite alcanzado", "Ya no se pueden agregar más segmentos.", "warning")

    def eliminar_segmento(self):
        """Función para eliminar un segmento (una fila en la tabla)"""
        if len(self.segmentos) > 1:
            # Asegurarnos de obtener los 3 elementos del segmento
            frame_segmento, entry_dia, entry_indice = self.segmentos.pop()
            frame_segmento.destroy()
        else:
            mostrar_mensaje(self, "Límite alcanzado", "Debe haber al menos un segmento.", "warning")

    def guardar_configuracion(self):
        config_name = self.entry_nombre.get().strip()
        
        if not config_name:
            mostrar_mensaje(self, "Error", "El nombre de la curva no puede estar vacío", "error")
            return
            
        if existe_curva(config_name):
            mostrar_mensaje(self, "Error", "Ya existe una curva con este nombre", "error")
            return

        segments_data = []
        prev_day = 0
        has_empty_index = False
        
        for _, entry_dia, entry_indice in self.segmentos:
            dia = entry_dia.get()
            indice = entry_indice.get().strip()

            if not dia.isdigit():
                mostrar_mensaje(self, "Error", f"Día inválido: {dia} - debe ser un número", "error")
                return
                
            dia_num = int(dia)
            if dia_num <= prev_day:
                mostrar_mensaje(self, "Error", f"Día {dia_num} no es incremental", "error")
                return
                
            if dia_num > 114:
                mostrar_mensaje(self, "Error", f"Día {dia_num} excede el límite de 114", "error")
                return
                
            prev_day = dia_num

            if not indice:
                has_empty_index = True
                continue
                
            if not self.validar_indice(indice):
                mostrar_mensaje(self, "Error", f"Índice inválido: {indice} - debe ser entre 1 y 200", "error")
                return
                
            if int(indice.replace('%', '')) < 1:
                mostrar_mensaje(self, "Error", "El índice debe ser mayor que 0", "error")
                return

            segments_data.append({
                "dia": dia_num,
                "indice": indice
            })

        if has_empty_index:
            mostrar_mensaje(self, "Error", "Todos los índices deben tener un valor", "error")
            return
            
        curvas_existentes = cargar_todas_curvas()
        
        nombre_bloqueado = config_name.strip().lower() in ["curva 1", "curva 2", "curva 3"]
        if nombre_bloqueado:
            mostrar_mensaje(self, "Error", "no se puede modificar Curva 1,2 o 3", "error")
            return
            
        curva_existente = next((c for c in curvas_existentes if c["nombre"].lower() == config_name.lower()), None)
        curvas_nuevas = [c for c in curvas_existentes if c["nombre"].strip().lower().replace(" ", "") not in ["curva1", "curva2", "curva3"]]
        if not curva_existente and len(curvas_nuevas) >= 2:
            mostrar_mensaje(self, "Error", "Solo se pueden agregar hasta 2 curvas personalizadas.", "error")
            return

        success, message = guardar_curva(config_name, segments_data)
        print(f"DEBUG: guardar_curva() success={success}, message={message}")
        if success:
            try:
                curva_para_enviar = {
                    "segmentos": segments_data
                }
                json_str = json.dumps([curva_para_enviar])
                json_con_marcos = f"<<<{json_str}>>>"
                
                with serial.Serial('/dev/serial0', 9600, timeout=1) as uart:
                    uart.write(json_con_marcos.encode('utf-8'))
                    print("UART.write() ejecutando correctamente")
            except Exception as e:
                print(f"Error al enviar por UART: {e}")

            mostrar_mensaje(self, "Éxito", f"Curva '{config_name}' guardada correctamente\n\nPresione OK para continuar", "info", 
                            callback=lambda: self.cerrar_ventana())
        else:
            mostrar_mensaje(self, "Error", message, "error")

    def cerrar_ventana(self):
        """Cerrar la ventana actual y regresar"""
        self.destroy()


