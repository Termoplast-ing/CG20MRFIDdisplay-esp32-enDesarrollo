"""
import tkinter as tk
from tkinter import ttk
import json
import os
import serial
from tkcalendar import DateEntry
import threading
from datetime import datetime
from util.util_calendario import seleccionar_fecha
from util import sqlite as db_local 

class Estaciones:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.fecha_mostrada = datetime.now().strftime("%d/%m/%Y")  # <- Fecha actual 
        self.estados_colores = {
            'alerta': 'red',    
            'normal': 'green',  
            'completo': 'blue'  
        }     

        self.frame_tabla = tk.Frame(self.parent_frame, bg="#EF9480")
        self.frame_tabla.grid(row=1, column=0, sticky="nsew", padx=5, pady=20)
        self.frame_tabla.config(height=400)
        self.frame_tabla.grid_rowconfigure(1, weight=1)
        self.frame_tabla.grid_columnconfigure(0, weight=1)

        self.crear_tabla_estaciones()
        self.actualizar_tabla()
        self.iniciar_recepcion_uart()

    def crear_tabla_estaciones(self):
        columnas = ["Corral", "N° Caravana", "Peso Acu", "Fecha"]

        scroll_frame = tk.Frame(self.frame_tabla, bg="#EF9480")
        scroll_frame.grid(row=1, column=0, sticky="nsew")
        scroll_frame.config(height=400)
        scroll_frame.grid_rowconfigure(0, weight=1)
        scroll_frame.grid_columnconfigure(0, weight=1)
        scroll_frame.grid_columnconfigure(1, weight=0)

        style = ttk.Style()
        style.configure("Treeview.Heading",
                        font=("Helvetica", 16, "bold"),
                        background="#f0ad4e",
                        foreground="black")
        style.configure("Treeview",
                        font=("Helvetica", 18),
                        rowheight=40,
                        background="#cacaca",
                        fieldbackground="#cacaca",
                        foreground="black",
                        relief="solid",
                        borderwidth=2)

        self.treeview = ttk.Treeview(
            scroll_frame,
            columns=("Corral", "N°Caravana", "Peso Acu", "Fecha"),
            show="headings",
            height=10
        )
        self.treeview.heading("Corral", text="Corral", command=self.ordenar_corral)
        self.treeview.heading("N°Caravana", text="N°Caravana")
        self.treeview.heading("Peso Acu", text="Peso Acu")
        self.treeview.heading("Fecha", text="Fecha")

        self.treeview.column("Corral", width=65, anchor="center")
        self.treeview.column("N°Caravana", width=205, anchor="w")
        self.treeview.column("Peso Acu", width=100, anchor="center")
        self.treeview.column("Fecha", width=130, anchor="center")
        self.treeview.grid(row=0, column=0, sticky="nsew")

        scrollbar_y = tk.Scrollbar(scroll_frame, orient="vertical", command=self.treeview.yview)
        scrollbar_x = tk.Scrollbar(scroll_frame, orient="horizontal", command=self.treeview.xview)
        self.treeview.config(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        scrollbar_y.grid(row=0, column=1, sticky="ns")
        scrollbar_x.grid(row=1, column=0, columnspan=2, sticky="ew")

        self.treeview.bind("<ButtonRelease-1>", self.cambiar_color_fila)
        self.ordenacion_estado = {"Corral": True}

    def cargar_fechas_inseminacion(self):
        try:
            return db_local.obtenerFechasInseminacion()
        except Exception as e:
            print("Error cargando fechas de inseminación desde SQLite:", e)
            return {}

    def cargar_datos_db(self):
        try:
            filas = db_local.obtenerLecturas()  # (corral, caravana, fecha, peso)
        except Exception as e:
            print("Error cargando lecturas desde SQLite:", e)
            return []

        fechas_insem = self.cargar_fechas_inseminacion()

        acumulados = {}
        for corral, caravana, fecha_pesaje, peso in filas:
            corral_num = str(corral)
            try:
                peso_val = float(peso)
            except Exception:
                peso_val = 0.0

            # Clave agrupando por día (recortando la hora para la tabla)
            fecha_dia = str(fecha_pesaje).split()[0]
            corral_str = f"Corral {corral_num}"
            clave = (corral_str, caravana, fecha_dia)
            if clave not in acumulados:
                acumulados[clave] = 0.0
            acumulados[clave] += peso_val

        try:
            ordenado = sorted(
                acumulados.items(),
                key=lambda x: datetime.strptime(x[0][2], "%Y-%m-%d")
            )
        except Exception:
            ordenado = list(acumulados.items())

        resultado = []
        for (corral_str, caravana, fecha_pesaje), peso_total in ordenado:
            if any(r[1] == caravana for r in resultado):
                continue

            dia_ciclo = ""
            if caravana in fechas_insem:
                try:
                    fecha_insem_dt = datetime.strptime(str(fechas_insem[caravana]).split()[0], "%Y-%m-%d")
                    fecha_pesaje_dt = datetime.strptime(fecha_pesaje, "%Y-%m-%d")
                    delta = (fecha_pesaje_dt - fecha_insem_dt).days + 1
                    dia_ciclo = str(delta) if delta >= 1 else "-"
                except Exception:
                    pass

            resultado.append(
                (corral_str.split()[-1], caravana, f"{peso_total:.2f} kg", dia_ciclo)
            )

        return resultado

    def actualizar_tabla(self):
        datos = self.cargar_datos_db()
        datos_filtrados = [item for item in datos if item[-1]]
        datos_filtrados.sort(key=lambda x: int(x[-1]) if str(x[-1]).isdigit() else 9999)
        datos_filtrados = datos_filtrados[:21]

        for item in self.treeview.get_children():
            self.treeview.delete(item)

        for item in datos_filtrados:
            self.treeview.insert("", "end", values=item)

        self.parent_frame.after(15000, self.actualizar_tabla)

    def filtrar_por_fecha(self, fecha):
        try:
            fecha_convertida = datetime.strptime(fecha, "%Y-%m-%d").strftime("%Y-%m-%d")
        except ValueError:
            fecha_convertida = fecha

        datos = self.cargar_datos_db()
        filtrados = [item for item in datos if item[-1] and fecha_convertida in item]

        for item in self.treeview.get_children():
            self.treeview.delete(item)

        if not filtrados:
            print(f"No hay datos para la fecha: {fecha_convertida}")
            return

        for item in filtrados[:20]:
            self.treeview.insert("", "end", values=item)

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
                        try:
                            datos = json.loads(json_str)
                            self.guardar_en_archivo(datos)

                            if hasattr(self.parent_frame, "modal_animal") and datos:
                                caravana = datos[0].get("caravana", "")
                                if caravana:
                                    self.parent_frame.after(
                                        0,
                                        lambda c=caravana: self.parent_frame.modal_animal(c)
                                    )
                        except json.JSONDecodeError:
                            print("Error al decodificar JSON:", json_str)

    def _normalizar_fecha_sql(self, fecha_raw):
        # Retornamos ahora con HORA para que el intervalo funcione
        return datetime.now().strftime("%Y-%m-%d %H:%M")

    def guardar_en_archivo(self, datos_recibidos):
        archivo = "datos_reales.json"
        ahora = datetime.now()

        if os.path.exists(archivo):
            with open(archivo, "r", encoding="utf-8") as f:
                try:
                    datos_existentes = json.load(f)
                except:
                    datos_existentes = {}
        else:
            datos_existentes = {}

        for animal in datos_recibidos:
            caravana = str(animal.get("caravana", "")).strip()
            fecha = animal.get("fecha", "")
            peso = animal.get("peso", "")
            corral_num = animal.get("corral", None)

            if not caravana or corral_num is None:
                continue

            # --- VALIDACIÓN DE INTERVALO ---
            res_db = db_local.obtener_intervalo_y_ultima_lectura(caravana)
            permitir_guardado = True
            
            if res_db:
                intervalo_min, ultima_fecha_str = res_db
                if ultima_fecha_str:
                    try:
                        f_ult = datetime.strptime(ultima_fecha_str, "%Y-%m-%d %H:%M")
                        diff = (ahora - f_ult).total_seconds() / 60
                        if diff < float(intervalo_min):
                            permitir_guardado = False
                    except:
                        pass

            if permitir_guardado:
                # Lógica original de JSON
                dia = ahora.strftime("%Y-%m-%d")
                corral = f"Corral {corral_num}"

                if dia not in datos_existentes:
                    datos_existentes[dia] = {}
                if corral not in datos_existentes[dia]:
                    datos_existentes[dia][corral] = []
                
                datos_existentes[dia][corral].append({
                    "caravana": caravana,
                    "timestamp": ahora.strftime("%Y-%m-%d %H:%M"),
                    "peso": str(peso)
                })

                # Inserción en SQLite
                fecha_sql = self._normalizar_fecha_sql(None)
                try:
                    peso_val = float(str(peso).replace(",", ".")) / 10.0
                    db_local.insertarLectura(
                        caravana=caravana,
                        corral=int(corral_num),
                        fecha=fecha_sql,
                        peso=peso_val
                    )
                except Exception as e:
                    print(f"Error insertando en SQLite: {e}")

                # Contador en memoria
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
        hilo_uart = threading.Thread(target=self.leer_uart_y_guardar_json, daemon=True)
        hilo_uart.start()
"""

"""
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
        self.fecha_mostrada = datetime.now().strftime("%d/%m/%Y")
        self.estados_colores = {
            'alerta': 'red',    
            'normal': 'green',  
            'completo': 'blue'  
        }     

        self.frame_tabla = tk.Frame(self.parent_frame, bg="#EF9480")
        self.frame_tabla.grid(row=1, column=0, sticky="nsew", padx=5, pady=20)
        self.frame_tabla.config(height=400)
        self.frame_tabla.grid_rowconfigure(1, weight=1)
        self.frame_tabla.grid_columnconfigure(0, weight=1)

        self.crear_tabla_estaciones()
        self.actualizar_tabla()
        self.iniciar_recepcion_uart()

    def crear_tabla_estaciones(self):
        columnas = ["Corral", "N° Caravana", "Peso Acu", "Fecha"]

        scroll_frame = tk.Frame(self.frame_tabla, bg="#EF9480")
        scroll_frame.grid(row=1, column=0, sticky="nsew")
        scroll_frame.config(height=400)
        scroll_frame.grid_rowconfigure(0, weight=1)
        scroll_frame.grid_columnconfigure(0, weight=1)
        scroll_frame.grid_columnconfigure(1, weight=0)

        style = ttk.Style()
        style.configure("Treeview.Heading",
                        font=("Helvetica", 16, "bold"),
                        background="#f0ad4e",
                        foreground="black")
        style.configure("Treeview",
                        font=("Helvetica", 18),
                        rowheight=40,
                        background="#cacaca",
                        fieldbackground="#cacaca",
                        foreground="black",
                        relief="solid",
                        borderwidth=2)

        self.treeview = ttk.Treeview(
            scroll_frame,
            columns=("Corral", "N°Caravana", "Peso Acu", "Fecha"),
            show="headings",
            height=10
        )
        self.treeview.heading("Corral", text="Corral", command=self.ordenar_corral)
        self.treeview.heading("N°Caravana", text="N°Caravana")
        self.treeview.heading("Peso Acu", text="Peso Acu")
        self.treeview.heading("Fecha", text="Fecha")

        self.treeview.column("Corral", width=65, anchor="center")
        self.treeview.column("N°Caravana", width=205, anchor="w")
        self.treeview.column("Peso Acu", width=100, anchor="center")
        self.treeview.column("Fecha", width=130, anchor="center")
        self.treeview.grid(row=0, column=0, sticky="nsew")

        scrollbar_y = tk.Scrollbar(scroll_frame, orient="vertical", command=self.treeview.yview)
        scrollbar_x = tk.Scrollbar(scroll_frame, orient="horizontal", command=self.treeview.xview)
        self.treeview.config(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        scrollbar_y.grid(row=0, column=1, sticky="ns")
        scrollbar_x.grid(row=1, column=0, columnspan=2, sticky="ew")

        self.treeview.bind("<ButtonRelease-1>", self.cambiar_color_fila)
        self.ordenacion_estado = {"Corral": True}

    def cargar_fechas_inseminacion(self):
        try:
            return db_local.obtenerFechasInseminacion()
        except Exception:
            return {}

    def cargar_datos_db(self):
        try:
            filas = db_local.obtenerLecturas() 
        except Exception:
            return []

        fechas_insem = self.cargar_fechas_inseminacion()
        acumulados = {}

        for corral, caravana, fecha_pesaje, peso in filas:
            corral_num = str(corral)
            try:
                peso_val = float(peso)
            except Exception:
                peso_val = 0.0

            # USAMOS SPLIT PARA EVITAR QUE LA HORA ROMPA EL AGRUPAMIENTO
            fecha_dia = str(fecha_pesaje).split()[0]
            corral_str = f"Corral {corral_num}"
            clave = (corral_str, caravana, fecha_dia)
            if clave not in acumulados:
                acumulados[clave] = 0.0
            acumulados[clave] += peso_val

        try:
            # SPLIT AQUÍ TAMBIÉN PARA EL PARSEO DE FECHA
            ordenado = sorted(
                acumulados.items(),
                key=lambda x: datetime.strptime(str(x[0][2]).split()[0], "%Y-%m-%d")
            )
        except Exception:
            ordenado = list(acumulados.items())

        resultado = []
        for (corral_str, caravana, fecha_pesaje), peso_total in ordenado:
            if any(r[1] == caravana for r in resultado):
                continue

            dia_ciclo = ""
            if caravana in fechas_insem:
                try:
                    # NORMALIZAMOS AMBAS FECHAS (QUITAMOS HORA SI EXISTE)
                    f_ins_str = str(fechas_insem[caravana]).split()[0]
                    f_pes_str = str(fecha_pesaje).split()[0]
                    
                    fecha_insem_dt = datetime.strptime(f_ins_str, "%Y-%m-%d")
                    fecha_pesaje_dt = datetime.strptime(f_pes_str, "%Y-%m-%d")
                    delta = (fecha_pesaje_dt - fecha_insem_dt).days + 1
                    dia_ciclo = str(delta) if delta >= 1 else "-"
                except Exception:
                    pass

            resultado.append((corral_str.split()[-1], caravana, f"{peso_total:.2f} kg", dia_ciclo))
        return resultado

    def actualizar_tabla(self):
        datos = self.cargar_datos_db()
        datos_filtrados = [item for item in datos if item[-1]]
        datos_filtrados.sort(key=lambda x: int(x[-1]) if str(x[-1]).isdigit() else 9999)
        datos_filtrados = datos_filtrados[:21]

        for item in self.treeview.get_children():
            self.treeview.delete(item)

        for item in datos_filtrados:
            self.treeview.insert("", "end", values=item)

        self.parent_frame.after(15000, self.actualizar_tabla)

    def cambiar_color_fila(self, event):
        item = self.treeview.focus()
        if not item: return
        colores = ["red", "green", "blue"]
        current_tags = self.treeview.item(item)["tags"]
        current_tag = current_tags[0] if current_tags else None
        next_color = colores[(colores.index(current_tag) + 1) % len(colores)] if current_tag in colores else colores[0]
        self.treeview.item(item, tags=(next_color,))
        self.treeview.tag_configure(next_color, background=next_color)

    def ordenar_corral(self):
        rows = list(self.treeview.get_children())
        values = [(self.treeview.item(row)["values"], row, self.treeview.item(row)["tags"]) for row in rows]
        ascending = self.ordenacion_estado["Corral"]
        values.sort(key=lambda x: int(x[0][0]), reverse=not ascending)
        for item in self.treeview.get_children(): self.treeview.delete(item)
        for value, row, tag in values: self.treeview.insert("", "end", values=value, tags=tag)
        self.ordenacion_estado["Corral"] = not ascending

    def leer_uart_y_guardar_json(self):
        puerto, baudrate = "/dev/serial0", 9600
        del_i, del_f = "<<<", ">>>"
        buffer = ""
        try:
            ser = serial.Serial(puerto, baudrate, timeout=1)
            while True:
                if ser.in_waiting:
                    data = ser.read(ser.in_waiting).decode("utf-8", errors="ignore")
                    buffer += data
                    while del_i in buffer and del_f in buffer:
                        inicio = buffer.find(del_i) + len(del_i)
                        fin = buffer.find(del_f)
                        json_str = buffer[inicio:fin]
                        buffer = buffer[fin + len(del_f):]
                        try:
                            datos = json.loads(json_str)
                            self.guardar_en_archivo(datos)
                            if hasattr(self.parent_frame, "modal_animal") and datos:
                                c = datos[0].get("caravana", "")
                                if c: self.parent_frame.after(0, lambda: self.parent_frame.modal_animal(c))
                        except: pass
        except: pass

    def _normalizar_fecha_sql(self, fecha_raw):
        return datetime.now().strftime("%Y-%m-%d %H:%M")

    def guardar_en_archivo(self, datos_recibidos):
        archivo = "datos_reales.json"
        ahora = datetime.now()
        if os.path.exists(archivo):
            with open(archivo, "r", encoding="utf-8") as f:
                try: datos_existentes = json.load(f)
                except: datos_existentes = {}
        else: datos_existentes = {}

        for animal in datos_recibidos:
            caravana = str(animal.get("caravana", "")).strip()
            corral_num = animal.get("corral", None)
            peso = animal.get("peso", "")
            if not caravana or corral_num is None: continue

            # Lógica de intervalo incorporada en tu flujo original
            res_db = db_local.obtener_intervalo_y_ultima_lectura(caravana)
            if res_db:
                intervalo_min, ultima_fecha_str = res_db
                if ultima_fecha_str:
                    try:
                        f_ult = datetime.strptime(ultima_fecha_str, "%Y-%m-%d %H:%M")
                        if (ahora - f_ult).total_seconds() / 60 < float(intervalo_min): continue
                    except: pass

            dia = ahora.strftime("%Y-%m-%d")
            corral = f"Corral {corral_num}"
            if dia not in datos_existentes: datos_existentes[dia] = {}
            if corral not in datos_existentes[dia]: datos_existentes[dia][corral] = []
            
            datos_existentes[dia][corral].append({
                "caravana": caravana, "timestamp": ahora.strftime("%Y-%m-%d %H:%M"), "peso": str(peso)
            })

            try:
                peso_val = float(str(peso).replace(",", ".")) / 10.0
                db_local.insertarLectura(caravana=caravana, corral=int(corral_num), fecha=ahora.strftime("%Y-%m-%d %H:%M"), peso=peso_val)
            except: pass

            if caravana:
                def act_cont(c=caravana):
                    if not hasattr(self.parent_frame, "datos_reales"): self.parent_frame.datos_reales = {}
                    if c not in self.parent_frame.datos_reales: self.parent_frame.datos_reales[c] = {"dosis_recibidas": 0}
                    self.parent_frame.datos_reales[c]["dosis_recibidas"] += 1
                    if hasattr(self.parent_frame, "actualizar_tabla"): self.parent_frame.actualizar_tabla()
                self.parent_frame.after(0, act_cont)

        with open(archivo, "w", encoding="utf-8") as f: json.dump(datos_existentes, f, indent=4)

    def iniciar_recepcion_uart(self):
        threading.Thread(target=self.leer_uart_y_guardar_json, daemon=True).start()
"""
"""
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
        self.fecha_mostrada = datetime.now().strftime("%d/%m/%Y")
        self.estados_colores = {
            'alerta': 'red',    
            'normal': 'green',  
            'completo': 'blue'  
        }     

        self.frame_tabla = tk.Frame(self.parent_frame, bg="#EF9480")
        self.frame_tabla.grid(row=1, column=0, sticky="nsew", padx=5, pady=20)
        self.frame_tabla.config(height=400)
        self.frame_tabla.grid_rowconfigure(1, weight=1)
        self.frame_tabla.grid_columnconfigure(0, weight=1)

        self.crear_tabla_estaciones()
        self.actualizar_tabla()
        self.iniciar_recepcion_uart()

    def crear_tabla_estaciones(self):
        columnas = ["Corral", "N° Caravana", "Peso Acu", "Fecha"]

        scroll_frame = tk.Frame(self.frame_tabla, bg="#EF9480")
        scroll_frame.grid(row=1, column=0, sticky="nsew")
        scroll_frame.config(height=400)
        scroll_frame.grid_rowconfigure(0, weight=1)
        scroll_frame.grid_columnconfigure(0, weight=1)
        scroll_frame.grid_columnconfigure(1, weight=0)

        style = ttk.Style()
        style.configure("Treeview.Heading",
                        font=("Helvetica", 16, "bold"),
                        background="#f0ad4e",
                        foreground="black")
        style.configure("Treeview",
                        font=("Helvetica", 18),
                        rowheight=40,
                        background="#cacaca",
                        fieldbackground="#cacaca",
                        foreground="black",
                        relief="solid",
                        borderwidth=2)

        self.treeview = ttk.Treeview(
            scroll_frame,
            columns=("Corral", "N°Caravana", "Peso Acu", "Fecha"),
            show="headings",
            height=10
        )
        self.treeview.heading("Corral", text="Corral", command=self.ordenar_corral)
        self.treeview.heading("N°Caravana", text="N°Caravana")
        self.treeview.heading("Peso Acu", text="Peso Acu")
        self.treeview.heading("Fecha", text="Fecha")

        self.treeview.column("Corral", width=65, anchor="center")
        self.treeview.column("N°Caravana", width=205, anchor="w")
        self.treeview.column("Peso Acu", width=100, anchor="center")
        self.treeview.column("Fecha", width=130, anchor="center")
        self.treeview.grid(row=0, column=0, sticky="nsew")

        scrollbar_y = tk.Scrollbar(scroll_frame, orient="vertical", command=self.treeview.yview)
        scrollbar_x = tk.Scrollbar(scroll_frame, orient="horizontal", command=self.treeview.xview)
        self.treeview.config(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        scrollbar_y.grid(row=0, column=1, sticky="ns")
        scrollbar_x.grid(row=1, column=0, columnspan=2, sticky="ew")

        self.treeview.bind("<ButtonRelease-1>", self.cambiar_color_fila)
        self.ordenacion_estado = {"Corral": True}

    def cargar_fechas_inseminacion(self):
        try:
            return db_local.obtenerFechasInseminacion()
        except Exception:
            return {}

    def cargar_datos_db(self):
        try:
            filas = db_local.obtenerLecturas() 
        except Exception:
            return []

        fechas_insem = self.cargar_fechas_inseminacion()
        acumulados = {}

        for corral, caravana, fecha_pesaje, peso in filas:
            corral_num = str(corral)
            try:
                peso_val = float(peso)
            except Exception:
                peso_val = 0.0

            try:
                fecha_dt = datetime.fromtimestamp(int(fecha_pesaje))
                fecha_dia = fecha_dt.date()
            except Exception:
                continue

            corral_str = f"Corral {corral_num}"
            clave = (corral_str, caravana, fecha_dia)
            if clave not in acumulados:
                acumulados[clave] = 0.0
            acumulados[clave] += peso_val

        ordenado = sorted(acumulados.items(), key=lambda x: x[0][2])

        resultado = []
        for (corral_str, caravana, fecha_dia), peso_total in ordenado:
            if any(r[1] == caravana for r in resultado):
                continue

            dia_ciclo = ""
            if caravana in fechas_insem:
                try:
                    ts_insem = int(fechas_insem[caravana])
                    f_ins =datetime.fromtimestamp(ts_insem).date()
                    #f_ins = datetime.fromtimestamp(str(fechas_insem[caravana]), "%Y-%m-%d").date()
                    delta = (fecha_dia - f_ins).days + 1
                    dia_ciclo = str(delta) if delta >= 1 else "-"
                except Exception:
                    dia_ciclo = "-"

            resultado.append(
                (corral_str.split()[-1], caravana, f"{peso_total:.2f} kg", fecha_dia.strftime("%d/%m/%Y"))
                #(corral_str.split()[-1], caravana, f"{peso_total:.2f} kg", dia_ciclo)
            )

        return resultado

    def actualizar_tabla(self):
        datos = self.cargar_datos_db()
        datos_filtrados = [item for item in datos if item[-1]]
        datos_filtrados.sort(key=lambda x: int(x[-1]) if str(x[-1]).isdigit() else 9999)
        datos_filtrados = datos_filtrados[:21]

        for item in self.treeview.get_children():
            self.treeview.delete(item)

        for item in datos_filtrados:
            self.treeview.insert("", "end", values=item)

        self.parent_frame.after(15000, self.actualizar_tabla)

    def cambiar_color_fila(self, event):
        item = self.treeview.focus()
        if not item: 
            return
        colores = ["red", "green", "blue"]
        current_tags = self.treeview.item(item)["tags"]
        current_tag = current_tags[0] if current_tags else None
        next_color = colores[(colores.index(current_tag) + 1) % len(colores)] if current_tag in colores else colores[0]
        self.treeview.item(item, tags=(next_color,))
        self.treeview.tag_configure(next_color, background=next_color)

    def ordenar_corral(self):
        rows = list(self.treeview.get_children())
        values = [(self.treeview.item(row)["values"], row, self.treeview.item(row)["tags"]) for row in rows]
        ascending = self.ordenacion_estado["Corral"]
        values.sort(key=lambda x: int(x[0][0]), reverse=not ascending)
        for item in self.treeview.get_children():
            self.treeview.delete(item)
        for value, row, tag in values:
            self.treeview.insert("", "end", values=value, tags=tag)
        self.ordenacion_estado["Corral"] = not ascending

    def leer_uart_y_guardar_json(self):
        puerto, baudrate = "/dev/serial0", 9600
        del_i, del_f = "<<<", ">>>"
        buffer = ""
        try:
            ser = serial.Serial(puerto, baudrate, timeout=1)
            while True:
                if ser.in_waiting:
                    data = ser.read(ser.in_waiting).decode("utf-8", errors="ignore")
                    buffer += data
                    while del_i in buffer and del_f in buffer:
                        inicio = buffer.find(del_i) + len(del_i)
                        fin = buffer.find(del_f)
                        json_str = buffer[inicio:fin]
                        buffer = buffer[fin + len(del_f):]
                        try:
                            datos = json.loads(json_str)
                            self.guardar_en_archivo(datos)
                            if hasattr(self.parent_frame, "modal_animal") and datos:
                                c = datos[0].get("caravana", "")
                                if c:
                                    self.parent_frame.after(0, lambda: self.parent_frame.modal_animal(c))
                        except:
                            pass
        except:
            pass

    def guardar_en_archivo(self, datos_recibidos):
        archivo = "datos_reales.json"
        ahora_ts = int(datetime.now().timestamp())

        if os.path.exists(archivo):
            with open(archivo, "r", encoding="utf-8") as f:
                try:
                    datos_existentes = json.load(f)
                except:
                    datos_existentes = {}
        else:
            datos_existentes = {}

        for animal in datos_recibidos:
            caravana = str(animal.get("caravana", "")).strip()
            corral_num = animal.get("corral", None)
            peso = animal.get("peso", "")
            if not caravana or corral_num is None:
                continue
                
            #lo nuevo 12_02 3 lineas de codigo
            dieta = db_local.obtener_dieta_por_caravana(caravana)
            if not dieta:
                continue

            res_db = db_local.obtener_intervalo_y_ultima_lectura(caravana)
            if res_db:
                intervalo_horas, ultima_fecha_ts = res_db
                try:
                    if ultima_fecha_ts:
                        intervalo_segundos = int(intervalo_horas) * 3600
                        #delta_min = (ahora_ts - int(ultima_fecha_ts)) / 60
                        #if delta_min < float(intervalo_min):
                        diferencia_segundos = ahora_ts - int(ultima_fecha_ts)
                        if diferencia_segundos < intervalo_en_segundos:
                        #if (ahora_ts - int(ultima_fecha_ts)) < intervalo_segundos:
                            continue
                except:
                    pass
                    
            #lo nuevo 12_02 bloque completo desca aca
            
            #hoy_str = datetime.fromtimestamp(ahora_ts).strftime("%Y-%m-%d")
            inicio_dia_ts = int(datetime.fromtimestamp(ahora_ts).replace(hour=0, minute=0, microsecond=0).timestamp())
            lecturas_db = db_local.obtenerLecturas()
            dosis_hoy = 0
            for _, l_car, l_fecha, _ in lecturas_db:
                try:
                    #f_solo = datetime.fromtimestamp(int(l_fecha)).strftime("%Y-%m-%d")
                    fecha_lectura_ts = int(float(l_fecha))
                    #if str(l_car) == caravana and f_solo == hoy_str:
                    if str(l_car).strip() == caravana and fecha_lectura_ts >= inicio_dia_ts:
                        dosis_hoy += 1
                except:
                    continue
                    
            if dosis_hoy >= int(dieta["cantidadDosis"]):
                print(f"Animal {caravana} ya cumplio sus dosis de hoy ({dosis_hoy})")
                continue
            #hasta aca

            dia = datetime.fromtimestamp(ahora_ts).strftime("%Y-%m-%d")
            corral = f"Corral {corral_num}"
            if dia not in datos_existentes:
                datos_existentes[dia] = {}
            if corral not in datos_existentes[dia]:
                datos_existentes[dia][corral] = []

            datos_existentes[dia][corral].append({
                "caravana": caravana,
                "timestamp": str(ahora_ts),
                "peso": str(peso)
            })

            try:                
                peso_val= float(peso) / 10
                #peso_val= (float(dieta["pesoTotal"]) / 10.0) /int(dieta["cantidadDosis"])
                #peso_val = float(str(peso).replace(",", ".")) / 10.0
                db_local.insertarLectura(
                    caravana=caravana,
                    corral=int(corral_num),
                    fecha=str(ahora_ts),
                    peso=peso_val
                )
            except:
                pass

            if caravana:
                def act_cont(c=caravana):
                    if not hasattr(self.parent_frame, "datos_reales"):
                        self.parent_frame.datos_reales = {}
                    if c not in self.parent_frame.datos_reales:
                        self.parent_frame.datos_reales[c] = {"dosis_recibidas": 0}
                    self.parent_frame.datos_reales[c]["dosis_recibidas"] += 1
                    if hasattr(self.parent_frame, "actualizar_tabla"):
                        self.parent_frame.actualizar_tabla()
                self.parent_frame.after(0, act_cont)

        #with open(archivo, "w", encoding="utf-8") as f:
        #    json.dump(datos_existentes, f, indent=4)


    def iniciar_recepcion_uart(self):
        threading.Thread(target=self.leer_uart_y_guardar_json, daemon=True).start()
"""

import tkinter as tk
from tkinter import ttk
import json
import os
import serial
import threading
from datetime import datetime
from util import sqlite as db_local 

def log_bloqueo(mensaje):
    ruta_fija = "/home/cg20mrfid/Desktop/pantalla_tkinter/log_bloqueos.txt"
    with open(ruta_fija, "a") as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {mensaje}\n")
        f.flush()
        os.fsync(f.fileno())

class Estaciones:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.fecha_mostrada = datetime.now().strftime("%d/%m/%Y")
        self.estados_colores = {
            'alerta': 'red',    
            'normal': 'green',  
            'completo': 'blue'  
        }      

        self.frame_tabla = tk.Frame(self.parent_frame, bg="#EF9480")
        self.frame_tabla.grid(row=1, column=0, sticky="nsew", padx=5, pady=20)
        self.frame_tabla.config(height=400)
        self.frame_tabla.grid_rowconfigure(1, weight=1)
        self.frame_tabla.grid_columnconfigure(0, weight=1)

        self.crear_tabla_estaciones()
        self.actualizar_tabla()
        self.iniciar_recepcion_uart()

    def crear_tabla_estaciones(self):
        columnas = ["Corral", "N° Caravana", "Peso Acu", "Fecha"]

        scroll_frame = tk.Frame(self.frame_tabla, bg="#EF9480")
        scroll_frame.grid(row=1, column=0, sticky="nsew")
        scroll_frame.config(height=400)
        scroll_frame.grid_rowconfigure(0, weight=1)
        scroll_frame.grid_columnconfigure(0, weight=1)
        scroll_frame.grid_columnconfigure(1, weight=0)

        style = ttk.Style()
        style.configure("Treeview.Heading",
                        font=("Helvetica", 16, "bold"),
                        background="#f0ad4e",
                        foreground="black")
        style.configure("Treeview",
                        font=("Helvetica", 18),
                        rowheight=40,
                        background="#cacaca",
                        fieldbackground="#cacaca",
                        foreground="black",
                        relief="solid",
                        borderwidth=2)

        self.treeview = ttk.Treeview(
            scroll_frame,
            columns=("Corral", "N°Caravana", "Peso Acu", "Fecha"),
            show="headings",
            height=10
        )
        self.treeview.heading("Corral", text="Corral", command=self.ordenar_corral)
        self.treeview.heading("N°Caravana", text="N°Caravana")
        self.treeview.heading("Peso Acu", text="Peso Acu")
        self.treeview.heading("Fecha", text="Fecha")

        self.treeview.column("Corral", width=65, anchor="center")
        self.treeview.column("N°Caravana", width=205, anchor="w")
        self.treeview.column("Peso Acu", width=100, anchor="center")
        self.treeview.column("Fecha", width=130, anchor="center")
        self.treeview.grid(row=0, column=0, sticky="nsew")

        scrollbar_y = tk.Scrollbar(scroll_frame, orient="vertical", command=self.treeview.yview)
        scrollbar_x = tk.Scrollbar(scroll_frame, orient="horizontal", command=self.treeview.xview)
        self.treeview.config(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        scrollbar_y.grid(row=0, column=1, sticky="ns")
        scrollbar_x.grid(row=1, column=0, columnspan=2, sticky="ew")

        self.treeview.bind("<ButtonRelease-1>", self.cambiar_color_fila)
        self.ordenacion_estado = {"Corral": True}

    def cargar_fechas_inseminacion(self):
        try:
            return db_local.obtenerFechasInseminacion()
        except Exception:
            return {}

    def cargar_datos_db(self):
        try:
            filas = db_local.obtenerLecturas() 
        except Exception:
            return []

        fechas_insem = self.cargar_fechas_inseminacion()
        acumulados = {}

        for corral, caravana, fecha_pesaje, peso in filas:
            corral_num = str(corral)
            try:
                peso_val = float(peso)
            except Exception:
                peso_val = 0.0

            try:
                fecha_dt = datetime.fromtimestamp(int(fecha_pesaje))
                fecha_dia = fecha_dt.date()
            except Exception:
                continue

            corral_str = f"Corral {corral_num}"
            clave = (corral_str, caravana, fecha_dia)
            if clave not in acumulados:
                acumulados[clave] = 0.0
            acumulados[clave] += peso_val

        ordenado = sorted(acumulados.items(), key=lambda x: x[0][2])

        resultado = []
        for (corral_str, caravana, fecha_dia), peso_total in ordenado:
            if any(r[1] == caravana for r in resultado):
                continue

            dia_ciclo = ""
            if caravana in fechas_insem:
                try:
                    ts_insem = int(fechas_insem[caravana])
                    f_ins =datetime.fromtimestamp(ts_insem).date()
                    delta = (fecha_dia - f_ins).days + 1
                    dia_ciclo = str(delta) if delta >= 1 else "-"
                except Exception:
                    dia_ciclo = "-"

            resultado.append(
                (corral_str.split()[-1], caravana, f"{peso_total:.2f} kg", fecha_dia.strftime("%d/%m/%Y"))
            )

        return resultado

    def actualizar_tabla(self):
        datos = self.cargar_datos_db()
        datos_filtrados = [item for item in datos if item[-1]]
        datos_filtrados.sort(key=lambda x: int(x[-1]) if str(x[-1]).isdigit() else 9999)
        datos_filtrados = datos_filtrados[:21]

        for item in self.treeview.get_children():
            self.treeview.delete(item)

        for item in datos_filtrados:
            self.treeview.insert("", "end", values=item)

        self.parent_frame.after(15000, self.actualizar_tabla)

    def cambiar_color_fila(self, event):
        item = self.treeview.focus()
        if not item: 
            return
        colores = ["red", "green", "blue"]
        current_tags = self.treeview.item(item)["tags"]
        current_tag = current_tags[0] if current_tags else None
        next_color = colores[(colores.index(current_tag) + 1) % len(colores)] if current_tag in colores else colores[0]
        self.treeview.item(item, tags=(next_color,))
        self.treeview.tag_configure(next_color, background=next_color)

    def ordenar_corral(self):
        rows = list(self.treeview.get_children())
        values = [(self.treeview.item(row)["values"], row, self.treeview.item(row)["tags"]) for row in rows]
        ascending = self.ordenacion_estado["Corral"]
        values.sort(key=lambda x: int(x[0][0]), reverse=not ascending)
        for item in self.treeview.get_children():
            self.treeview.delete(item)
        for value, row, tag in values:
            self.treeview.insert("", "end", values=value, tags=tag)
        self.ordenacion_estado["Corral"] = not ascending

    def leer_uart_y_guardar_json(self):
        puerto, baudrate = "/dev/serial0", 9600
        del_i, del_f = "<<<", ">>>"
        buffer = ""
        try:
            ser = serial.Serial(puerto, baudrate, timeout=1)
            while True:
                if ser.in_waiting:
                    data = ser.read(ser.in_waiting).decode("utf-8", errors="ignore")
                    buffer += data
                    while del_i in buffer and del_f in buffer:
                        inicio = buffer.find(del_i) + len(del_i)
                        fin = buffer.find(del_f)
                        json_str = buffer[inicio:fin]
                        buffer = buffer[fin + len(del_f):]
                        try:
                            datos = json.loads(json_str)
                            self.guardar_en_archivo(datos)
                            if hasattr(self.parent_frame, "modal_animal") and datos:
                                c = datos[0].get("caravana", "")
                                if c:
                                    self.parent_frame.after(0, lambda: self.parent_frame.modal_animal(c))
                        except:
                            pass
        except:
            pass

    def guardar_en_archivo(self, datos_recibidos):
        archivo = "datos_reales.json"
        ahora_ts = int(datetime.now().timestamp())

        if os.path.exists(archivo):
            with open(archivo, "r", encoding="utf-8") as f:
                try:
                    datos_existentes = json.load(f)
                except:
                    datos_existentes = {}
        else:
            datos_existentes = {}

        for animal in datos_recibidos:
            caravana = str(animal.get("caravana", "")).strip()
            corral_num = animal.get("corral", None)
            peso = animal.get("peso", "")
            if not caravana or corral_num is None:
                continue
                
            # 1. Obtenemos datos de la dieta
            dieta = db_local.obtener_dieta_por_caravana(caravana)
            if not dieta: continue

            # 2. VALIDAMOS EL INTERVALO (Con tu función existente)
            res_db = db_local.obtener_intervalo_y_ultima_lectura(caravana)
            if res_db:
                intervalo_horas, ultima_fecha_ts = res_db
                if ultima_fecha_ts:
                    intervalo_segundos = int(intervalo_horas) * 3600
                    self.treeview.insert("", 0, values=("DEBUG", caravana,ultima_fecha_ts ,ahora_ts))
                    if (ahora_ts - int(ultima_fecha_ts)) < intervalo_segundos:
                        
                        #log_bloqueo(f"Bloqueo Intervalo: Carav {caravana}. Dif: {ahora_ts - int(ultima_fecha_ts)}s < {intervalo_segundos}s")
                        continue # <--- AQUÍ BLOQUEAS: No pasa de esta línea

            # 3. VALIDAMOS LAS DOSIS (Tu lógica original)
            #probamos esto nuevo con antigravity 09_03_2026 lunes
            inicio_dia_ts = ahora_ts - 86400
            
            #inicio_dia_ts = int(datetime.fromtimestamp(ahora_ts).replace(hour=0, minute=0, microsecond=0).timestamp())
            lecturas_db = db_local.obtenerLecturas()
            dosis_hoy = 0
            for _, l_car, l_fecha, _ in lecturas_db:
                try:
                    fecha_lectura_ts = int(float(l_fecha))
                    if str(l_car).strip() == caravana and fecha_lectura_ts >= inicio_dia_ts:
                        dosis_hoy += 1
                except: continue
                    
            if dosis_hoy >= int(dieta["cantidadDosis"]):
                log_bloqueo(f"Bloqueo Dosis: Carav {caravana}. Dosis: {dosis_hoy} >= {dieta['cantidadDosis']}")
                print(f"Animal {caravana} ya cumplio sus dosis de hoy ({dosis_hoy})")
                continue # <--- AQUÍ BLOQUEAS: No pasa de esta línea

            # 4. SOLO SI LLEGAMOS HASTA AQUÍ, GUARDAMOS (Tu código original intacto)
            dia = datetime.fromtimestamp(ahora_ts).strftime("%Y-%m-%d")
            corral = f"Corral {corral_num}"
            if dia not in datos_existentes: datos_existentes[dia] = {}
            if corral not in datos_existentes[dia]: datos_existentes[dia][corral] = []

            datos_existentes[dia][corral].append({
                "caravana": caravana,
                "timestamp": str(ahora_ts),
                "peso": str(peso)
            })

            try:                
                peso_val = float(peso) / 10
                db_local.insertarLectura(
                    caravana=caravana,
                    corral=int(corral_num),
                    fecha=str(ahora_ts),
                    peso=peso_val
                )
            except:
                pass

            if caravana:
                def act_cont(c=caravana):
                    if not hasattr(self.parent_frame, "datos_reales"):
                        self.parent_frame.datos_reales = {}
                    if c not in self.parent_frame.datos_reales:
                        self.parent_frame.datos_reales[c] = {"dosis_recibidas": 0}
                    self.parent_frame.datos_reales[c]["dosis_recibidas"] += 1
                    if hasattr(self.parent_frame, "actualizar_tabla"):
                        self.parent_frame.actualizar_tabla()
                self.parent_frame.after(0, act_cont)

    def iniciar_recepcion_uart(self):
        threading.Thread(target=self.leer_uart_y_guardar_json, daemon=True).start()
