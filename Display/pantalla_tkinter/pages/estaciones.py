import tkinter as tk
from tkinter import ttk
import json
import os
import serial
import threading
from datetime import datetime
from util import sqlite as db_local 


class Estaciones:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.fecha_mostrada = datetime.now().strftime("%d/%m/%Y")  # Fecha actual 
        self.estados_colores = {
            'alerta': 'red',    
            'normal': 'green',  
            'completo': 'blue'  
        }     

        # ===== Frame de la tabla =====
        self.frame_tabla = tk.Frame(self.parent_frame, bg="#EF9480")
        self.frame_tabla.grid(row=1, column=0, sticky="nsew", padx=5, pady=20)
        self.frame_tabla.config(height=400)
        self.frame_tabla.grid_rowconfigure(1, weight=1)
        self.frame_tabla.grid_columnconfigure(0, weight=1)

        self.crear_tabla_estaciones()
        self.actualizar_tabla()
        self.iniciar_recepcion_uart()

    def crear_tabla_estaciones(self):
        columnas = ["Corral", "N° Caravana", "Peso Acu", "Día Ciclo"]

        scroll_frame = tk.Frame(self.frame_tabla, bg="#EF9480")
        scroll_frame.grid(row=1, column=0, sticky="nsew")
        scroll_frame.config(height=400)
        scroll_frame.grid_rowconfigure(0, weight=1)
        scroll_frame.grid_columnconfigure(0, weight=1)
        scroll_frame.grid_columnconfigure(1, weight=0)

        style = ttk.Style()
        style.configure(
            "Treeview.Heading",
            font=("Helvetica", 16, "bold"),
            background="#f0ad4e",
            foreground="black"
        )
        style.configure(
            "Treeview",
            font=("Helvetica", 18),
            rowheight=40,
            background="#cacaca",
            fieldbackground="#cacaca",
            foreground="black",
            relief="solid",
            borderwidth=2
        )

        self.treeview = ttk.Treeview(
            scroll_frame,
            columns=("Corral", "N°Caravana", "Peso Acu", "Día Ciclo"),
            show="headings",
            height=10
        )
        self.treeview.heading("Corral", text="Corral", command=self.ordenar_corral)
        self.treeview.heading("N°Caravana", text="N°Caravana")
        self.treeview.heading("Peso Acu", text="Peso Acu")
        self.treeview.heading("Día Ciclo", text="Día Ciclo")

        self.treeview.column("Corral", width=65, anchor="center")
        self.treeview.column("N°Caravana", width=205, anchor="w")
        self.treeview.column("Peso Acu", width=100, anchor="center")
        self.treeview.column("Día Ciclo", width=130, anchor="center")
        self.treeview.grid(row=0, column=0, sticky="nsew")

        scrollbar_y = tk.Scrollbar(scroll_frame, orient="vertical", command=self.treeview.yview)
        scrollbar_x = tk.Scrollbar(scroll_frame, orient="horizontal", command=self.treeview.xview)
        self.treeview.config(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        scrollbar_y.grid(row=0, column=1, sticky="ns")
        scrollbar_x.grid(row=1, column=0, columnspan=2, sticky="ew")

        self.treeview.bind("<ButtonRelease-1>", self.cambiar_color_fila)
        self.ordenacion_estado = {"Corral": True}

    # ------------------- SQLITE: fechas de inseminación -------------------

    def cargar_fechas_inseminacion(self):
        """
        Usa tu función db_local.obtenerFechasInseminacion()
        que devuelve {caravana: fechaInseminacion}
        """
        try:
            return db_local.obtenerFechasInseminacion()
        except Exception as e:
            print("Error cargando fechas de inseminación desde SQLite:", e)
            return {}

    def cargar_datos_db(self):
        """
        Lee lecturas desde la tabla 'lectura' y arma:
        [(corral_num, caravana, 'peso kg', dia_ciclo_str), ...]
        """
        try:
            filas = db_local.obtenerLecturas()  # (corral, caravana, fecha, peso)
        except Exception as e:
            print("Error cargando lecturas desde SQLite:", e)
            return []

        fechas_insem = self.cargar_fechas_inseminacion()

        # Acumular peso por (corral, caravana, fecha_pesaje)
        acumulados = {}
        for corral, caravana, fecha_pesaje, peso in filas:
            corral_num = str(corral)
            try:
                peso_val = float(peso)
            except Exception:
                peso_val = 0.0

            corral_str = f"Corral {corral_num}"
            clave = (corral_str, caravana, fecha_pesaje)
            if clave not in acumulados:
                acumulados[clave] = 0.0
            acumulados[clave] += peso_val

        # Ordenar por fecha de pesaje
        try:
            ordenado = sorted(
                acumulados.items(),
                key=lambda x: datetime.strptime(x[0][2], "%Y-%m-%d")
            )
        except Exception:
            ordenado = list(acumulados.items())

        resultado = []
        for (corral_str, caravana, fecha_pesaje), peso_total in ordenado:
            # Si ya mostramos esa caravana, no la repetimos
            if any(r[1] == caravana for r in resultado):
                continue

            dia_ciclo = ""
            if caravana in fechas_insem:
                try:
                    fecha_insem_dt = datetime.strptime(fechas_insem[caravana], "%Y-%m-%d")
                    fecha_pesaje_dt = datetime.strptime(fecha_pesaje, "%Y-%m-%d")
                    delta = (fecha_pesaje_dt - fecha_insem_dt).days + 1
                    if delta < 1:
                        dia_ciclo = "-"
                    else:
                        dia_ciclo = str(delta)  # Día 1, 2, 3, etc.
                except Exception:
                    pass

            resultado.append(
                (corral_str.split()[-1],  # solo número de corral
                 caravana,
                 f"{peso_total:.2f} kg",
                 dia_ciclo)
            )

        return resultado

    # ------------------- ACTUALIZAR TABLA -------------------

    def actualizar_tabla(self):
        datos = self.cargar_datos_db()

        # Sólo los que tienen día de ciclo calculado
        datos_filtrados = [item for item in datos if item[-1]]

        # Ordenar por día de ciclo (numérico)
        datos_filtrados.sort(
            key=lambda x: int(x[-1]) if str(x[-1]).isdigit() else 9999
        )

        # Limitar a 21 registros
        datos_filtrados = datos_filtrados[:21]

        # Limpiar tabla
        for item in self.treeview.get_children():
            self.treeview.delete(item)

        # Insertar filas
        for item in datos_filtrados:
            self.treeview.insert("", "end", values=item)

        # Refrescar cada 15 segundos
        self.parent_frame.after(15000, self.actualizar_tabla)

    # ------------------- (Opcional) filtro por fecha -------------------

    def filtrar_por_fecha(self, fecha):
        try:
            fecha_convertida = datetime.strptime(fecha, "%Y-%m-%d").strftime("%Y-%m-%d")
        except ValueError:
            fecha_convertida = fecha

        datos = self.cargar_datos_db()
        # Ojo: acá podrías querer filtrar por fecha_pesaje si la devolvés también
        filtrados = [item for item in datos if item[-1] and fecha_convertida in item]

        for item in self.treeview.get_children():
            self.treeview.delete(item)

        if not filtrados:
            print(f"No hay datos para la fecha: {fecha_convertida}")
            return

        for item in filtrados[:20]:
            self.treeview.insert("", "end", values=item)

    # ------------------- UI extra: colores, orden -------------------

    def cambiar_color_fila(self, event):
        item = self.treeview.focus()
        if not item:
            return
        colores = ["red", "green", "blue"]
        current_tags = self.treeview.item(item)["tags"]
        current_tag = current_tags[0] if current_tags else None

        if current_tag in colores:
            next_color = colores[(colores.index(current_tag) + 1) % len(colores)]
        else:
            next_color = colores[0]

        self.treeview.item(item, tags=(next_color,))
        self.treeview.tag_configure(next_color, background=next_color)

    def ordenar_corral(self):
        rows = list(self.treeview.get_children())
        values = [
            (self.treeview.item(row)["values"], row, self.treeview.item(row)["tags"])
            for row in rows
        ]
        ascending = self.ordenacion_estado["Corral"]
        values.sort(key=lambda x: int(x[0][0]), reverse=not ascending)

        for item in self.treeview.get_children():
            self.treeview.delete(item)

        for value, row, tag in values:
            self.treeview.insert("", "end", values=value, tags=tag)

        self.ordenacion_estado["Corral"] = not ascending

    # ------------------- UART + persistencia -------------------

    def leer_uart_y_guardar_json(self):
        puerto = "/dev/serial0"
        baudrate = 9600
        delimitador_inicio = "<<<"
        delimitador_fin = ">>>"
        buffer = ""

        try:
            ser = serial.Serial(puerto, baudrate, timeout=1)
        except serial.SerialException as e:
            print("Error al abrir el puerto serial:", e)
            return

        while True:
            if ser.in_waiting:
                data = ser.read(ser.in_waiting).decode("utf-8", errors="ignore")
                buffer += data
                while delimitador_inicio in buffer and delimitador_fin in buffer:
                    inicio = buffer.find(delimitador_inicio) + len(delimitador_inicio)
                    fin = buffer.find(delimitador_fin)
                    if inicio < fin:
                        json_str = buffer[inicio:fin]
                        buffer = buffer[fin + len(delimitador_fin):]
                        print("Mensaje recibido en Raspberry:", json_str)
                        try:
                            datos = json.loads(json_str)
                            # Guarda JSON + inserta en SQLite
                            self.guardar_en_archivo(datos)

                            if hasattr(self.parent_frame, "modal_animal") and datos:
                                caravana = datos[0].get("caravana", "")
                                if caravana:
                                    self.parent_frame.after(
                                        0,
                                        lambda c=caravana: self.parent_frame.modal_animal(c)
                                    )
                            print("JSON recibido y modal ejecutando")
                        except json.JSONDecodeError:
                            print("Error al decodificar JSON:", json_str)

    def _normalizar_fecha_sql(self, fecha_raw):
        # int o string de dígitos → timestamp
        if isinstance(fecha_raw, int) or (isinstance(fecha_raw, str) and fecha_raw.isdigit()):
            try:
                return datetime.fromtimestamp(int(fecha_raw)).strftime("%Y-%m-%d")
            except Exception:
                return datetime.now().strftime("%Y-%m-%d")

        try:
            texto = str(fecha_raw)
            if "T" in texto:
                return texto.split("T")[0]
            if len(texto) == 10 and texto[4] == "-" and texto[7] == "-":
                return texto
        except Exception:
            pass

        return datetime.now().strftime("%Y-%m-%d")

    def guardar_en_archivo(self, datos_recibidos):
        """
        Sigue guardando en datos_reales.json (compatibilidad)
        y también inserta en SQLite (tabla lectura).
        """
        archivo = "datos_reales.json"

        if os.path.exists(archivo):
            with open(archivo, "r", encoding="utf-8") as f:
                try:
                    datos_existentes = json.load(f)
                except Exception:
                    datos_existentes = {}
        else:
            datos_existentes = {}

        for animal in datos_recibidos:
            caravana = animal.get("caravana", "")
            fecha = animal.get("fecha", "")
            peso = animal.get("peso", "")
            corral_num = animal.get("corral", None)

            if not fecha or not caravana or corral_num is None:
                continue

            # Clave para el JSON viejo
            try:
                dia = int(fecha)
            except (ValueError, TypeError):
                try:
                    fecha_str = str(fecha).split("T")[0]
                    fecha_dt = datetime.strptime(fecha_str, "%Y-%m-%d")
                    dia = int(fecha_dt.timestamp())
                except Exception:
                    dia = str(fecha).split("T")[0] if "T" in str(fecha) else str(fecha)

            corral = f"Corral {corral_num}"

            if dia not in datos_existentes:
                datos_existentes[dia] = {}
            if corral not in datos_existentes[dia]:
                datos_existentes[dia][corral] = []
            datos_existentes[dia][corral].append({
                "caravana": caravana,
                "timestamp": fecha,
                "peso": str(peso)
            })

            # Inserción en SQLite
            fecha_sql = self._normalizar_fecha_sql(fecha)
            try:
                peso_val = float(str(peso).replace(",", ".")) / 10.0
            except Exception:
                peso_val = 0.0

            try:
                db_local.insertarLectura(
                    caravana=caravana,
                    corral=int(corral_num),
                    fecha=fecha_sql,
                    peso=peso_val
                )
            except Exception as e:
                print(f"Error insertando lectura en SQLite: {e}")

            # Contador en memoria para DatosWindow (si lo usás)
            if caravana:
                def actualizar_contador(c=caravana):
                    if not hasattr(self.parent_frame, "datos_reales"):
                        self.parent_frame.datos_reales = {}
                    if c not in self.parent_frame.datos_reales:
                        self.parent_frame.datos_reales[c] = {"dosis_recibidas": 0}
                    self.parent_frame.datos_reales[c]["dosis_recibidas"] += 1
                    if hasattr(self.parent_frame, "actualizar_tabla"):
                        self.parent_frame.actualizar_tabla()

                self.parent_frame.after(0, actualizar_contador)

        with open(archivo, "w", encoding="utf-8") as f:
            json.dump(datos_existentes, f, indent=4)

    def iniciar_recepcion_uart(self):
        hilo_uart = threading.Thread(
            target=self.leer_uart_y_guardar_json,
            daemon=True
        )
        hilo_uart.start()
