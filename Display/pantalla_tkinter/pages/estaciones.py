import tkinter as tk
from tkinter import ttk
import json
import os
import serial
from tkcalendar import DateEntry
import threading
from datetime import datetime
from util.util_calendario import seleccionar_fecha

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
        self.frame_tabla.grid_rowconfigure(1, weight=1)  # IMPORTANTE para que scroll funcione bien
        self.frame_tabla.grid_columnconfigure(0, weight=1)

        self.crear_tabla_estaciones()
        self.actualizar_tabla()
        self.iniciar_recepcion_uart()

    def crear_tabla_estaciones(self):
        columnas = ["Corral", "N° Caravana","Peso Acu","Fecha"]
        scroll_frame = tk.Frame(self.frame_tabla,bg="#EF9480")
        scroll_frame.grid(row=1, column=0, sticky="nsew")
        scroll_frame.config(height=400)
        scroll_frame.grid_rowconfigure(0, weight=1)
        scroll_frame.grid_columnconfigure(0, weight=1)
        scroll_frame.grid_columnconfigure(1, weight=0)

        style = ttk.Style()                
        style.configure("Treeview.Heading", font=("Helvetica", 16, "bold"),  background="#f0ad4e",  foreground="black")         
        style.configure("Treeview",font=("Helvetica", 18),rowheight=40,background="#cacaca", fieldbackground="#cacaca", foreground="black",relief="solid",borderwidth=2) 

        self.treeview = ttk.Treeview(scroll_frame, columns=("Corral", "N°Caravana", "Peso Acu","Fecha"), show="headings",height=10)
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

    def parsear_fecha(self, fecha_str):
        try:
            if "/" in fecha_str:
                try:
                    return datetime.strptime(fecha_str, "%d/%m/%Y")
                except ValueError:
                    return datetime.strptime(fecha_str, "%d/%m/%y")
            else:
                if len(fecha_str) == 6:
                    f = fecha_str[:2] + "/" + fecha_str[2:4] + "/" + fecha_str[4:]
                    return datetime.strptime(f, "%d/%m/%y")
                else:
                    return None
        except Exception:
            return None
            
    def cargar_fechas_inseminacion(self):
        archivo = os.path.join(os.getcwd(), "datos_animales.json")
        fechas_insem = {}
        try:
            with open(archivo, "r", encoding="utf-8") as f:
                datos = json.load(f)
                for corral, animales in datos.items():
                    for animal in animales:
                        if len(animal) >= 3:
                            caravana = animal[0]
                            fecha_insem = animal[2]  # formato: '2025-09-18'
                            fechas_insem[caravana] = fecha_insem
        except Exception as e:
            print("Error cargando fechas de inseminación:", e)
        return fechas_insem
    
    def cargar_datos_json(self):
        ruta_json = os.path.join(os.getcwd(), "datos_reales.json")
        fechas_insem = self.cargar_fechas_inseminacion()
        try:
            with open(ruta_json, "r", encoding="utf-8") as f:
                datos = json.load(f)
        except Exception:
            return {}

        acumulados = {}
        for dia, corrales in datos.items():
            for corral, registros in corrales.items():
                for registro in registros:
                    caravana = registro.get("caravana")
                    timestamp = registro.get("timestamp")
                    peso = registro.get("peso")

                    fecha_legible = None
                    if isinstance(timestamp, int) or (isinstance(timestamp, str) and timestamp.isdigit()):
                        try:
                            fecha_legible = datetime.fromtimestamp(int(timestamp)).strftime("%Y-%m-%d")
                        except:
                            fecha_legible = None
                    else:
                        try:
                            fecha_legible = str(timestamp).split("T")[0]
                        except:
                            fecha_legible = None

                    if fecha_legible is None:
                        continue

                    try:
                        peso_val = float(str(peso).replace(",", ".")) / 10.0
                    except:
                        peso_val = 0.0

                    clave = (corral, caravana, fecha_legible)
                    if clave not in acumulados:
                        acumulados[clave] = 0.0
                    acumulados[clave] += peso_val

        ordenado = sorted(acumulados.items(), key=lambda x: datetime.strptime(x[0][2], "%Y-%m-%d"))

        resultado = []
        for (corral, caravana, fecha_pesaje), peso in ordenado:
            #verificar si la caravana ya esta en resultado
            if any(r[1] == caravana for r in resultado):
                continue
            corral_num = corral.split()[-1]
            dia_ciclo = ""
            if caravana in fechas_insem:
                try:
                    fecha_insem_dt = datetime.strptime(fechas_insem[caravana], "%Y-%m-%d")
                    fecha_pesaje_dt = datetime.strptime(fecha_pesaje, "%Y-%m-%d")
                    delta = (fecha_pesaje_dt - fecha_insem_dt).days + 1  # Día 1 es el día de inseminación
                    if delta < 1:
                        delta= "-"
                    dia_ciclo = str(delta)
                except:
                    pass
            resultado.append((corral_num, caravana, f"{peso:.2f} kg", dia_ciclo))
        return resultado


    #def cargar_datos_json(self):
    #    ruta_json = os.path.join(os.getcwd(), "datos_reales.json")
    #    fechas_insem = self.cargar_fechas_inseminacion()
    #    try:
    #        with open(ruta_json, "r", encoding="utf-8") as f:
    #            datos = json.load(f)
    #    except Exception:
    #        return {}

    #    acumulados = {}
    #    for dia, corrales in datos.items():
    #        for corral, registros in corrales.items():
    #            for registro in registros:
    #                caravana = registro.get("caravana")
    #                timestamp = registro.get("timestamp")
    #                peso = registro.get("peso")

    #                fecha_legible = None
    #                if isinstance(timestamp, int) or (isinstance(timestamp, str) and timestamp.isdigit()):
    #                    try:
    #                        fecha_legible = datetime.fromtimestamp(int(timestamp)).strftime("%d/%m/%Y")
    #                    except:
    #                        fecha_legible = None
    #                else:
    #                    fecha_legible = self.parsear_fecha(str(timestamp).split("T")[0])

    #                if fecha_legible is None:
    #                    continue

    #                try:
    #                    peso_val = float(str(peso).replace(",", ".")) / 10.0
    #                except:
    #                    peso_val = 0.0

    #                clave = (corral, caravana, fecha_legible)
    #                if clave not in acumulados:
    #                    acumulados[clave] = 0.0
    #                acumulados[clave] += peso_val

    #    ordenado = sorted(acumulados.items(), key=lambda x: datetime.strptime(x[0][2], "%d/%m/%Y"))

    #    resultado = []
    #    for (corral, caravana, fecha), peso in ordenado:
    #        resultado.append((corral.split()[-1], caravana, f"{peso:.2f} kg", fecha))
    #    return resultado

    def actualizar_tabla(self):
        datos = self.cargar_datos_json()

        # Filtrar solo los que tienen día de ciclo no vacío
        datos_filtrados = [item for item in datos if item[-1]]

        # Ordenar por día de ciclo numéricamente (de menor a mayor)
        datos_filtrados.sort(key=lambda x: int(x[-1]) if str(x[-1]).isdigit() else 9999)

        # Limitar a 20 registros máximo
        datos_filtrados = datos_filtrados[:21]

        # Limpiar la tabla
        for item in self.treeview.get_children():
            self.treeview.delete(item)

        # Insertar los datos
        for item in datos_filtrados:
            self.treeview.insert("", "end", values=item)

        # Actualizar cada 2 minutos
        self.parent_frame.after(15000, self.actualizar_tabla)

    #def actualizar_tabla(self):
    #    datos = self.cargar_datos_json()
    
        # Obtener fecha actual en formato dd/mm/yyyy
    #    fecha_actual = datetime.now().strftime("%d/%m/%Y")
    
        # Filtrar solo los datos que corresponden a la fecha actual
    #    datos_filtrados = [item for item in datos if item[-1] == fecha_actual]
    
        # Limitar a 20 registros máximo
    #    datos_filtrados = datos_filtrados[:20]
    
        # Limpiar la tabla
    #    for item in self.treeview.get_children():
    #        self.treeview.delete(item)
    
        # Insertar solo los datos filtrados
    #    for item in datos_filtrados:
    #        self.treeview.insert("", "end", values=item)
    
        # Actualizar cada 2 minutos
    #    self.parent_frame.after(150000, self.actualizar_tabla)
    
    from datetime import datetime

    def filtrar_por_fecha(self, fecha):
        try:
            # Convertir de 'YYYY-MM-DD' a 'DD/MM/YYYY'
            fecha_convertida = datetime.strptime(fecha, "%Y-%m-%d").strftime("%d/%m/%Y")
        except ValueError:
            fecha_convertida = fecha  # Si falla, usar la original (por si ya viene formateada)

        datos = self.cargar_datos_json()

        # Comparar contra las fechas ya formateadas en cargar_datos_json
        filtrados = [item for item in datos if item[-1] == fecha_convertida]

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
        current_tag = self.treeview.item(item)["tags"][0] if self.treeview.item(item)["tags"] else None
        if current_tag in colores:
            next_color = colores[(colores.index(current_tag) + 1) % len(colores)]
        else:
            next_color = colores[0]
        self.treeview.item(item, tags=(next_color,))
        self.treeview.tag_configure(next_color, background=next_color)

    def ordenar_corral(self):
        rows = list(self.treeview.get_children())
        values = [(self.treeview.item(row)["values"], row, self.treeview.item(row)["tags"]) for row in rows]
        ascending = self.ordenacion_estado["Corral"]
        values.sort(key=lambda x: int(x[0]), reverse=not ascending)
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
                        print("Mensaje recibido en Raspberry:", json_str)
                        try:
                            datos = json.loads(json_str)
                            self.guardar_en_archivo(datos)
                            if hasattr(self.parent_frame, "modal_animal") and datos:
                                caravana = datos[0].get("caravana","")
                                if caravana:
                                    self.parent_frame.after(0, lambda c=caravana: self.parent_frame.modal_animal(c))
                            print("JSON recibido y modal ejecutando")
                        except json.JSONDecodeError:
                            print("Error al decodificar JSON:", json_str)

    def guardar_en_archivo(self, datos_recibidos):
        archivo = "datos_reales.json"
        if os.path.exists(archivo):
            with open(archivo, "r", encoding="utf-8") as f:
                try:
                    datos_existentes = json.load(f)
                except:
                    datos_existentes = {}
        else:
            datos_existentes = {}

        for animal in datos_recibidos:
            caravana = animal.get("caravana", "")
            fecha = animal.get("fecha", "")
            peso = animal.get("peso", "")
            corral_num = animal.get("corral", None)
            #if hasattr(self.parent_frame, "modal_animal"):
            #    self.parent_frame.after(0, lambda c=caravana: self.parent.modal_animal(c))
            if not fecha or not caravana or corral_num is None:
                continue
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
            #pruebo esto nuevo:
            if caravana:
                #if caravana not in self.parent_frame.datos_reales:
                #    self.parent_frame.datos_reales[caravana] = {"dosis_recibidas": 0}
                #self.parent_frame.datos_reales[caravana]["dosis_recibidas"] += 1
                #self.parent_frame.actualizar_tabla()
                def actualizar_contador(c=caravana):
                    if c not in self.parent_frame.datos_reales:
                        self.parent_frame.datos_reales[c] = {"dosis_recibidas": 0}
                    self.parent_frame.datos_reales[c]["dosis_recibidas"] += 1
                    self.parent_frame.actualizar_tabla()
                self.parent_frame.after(0, actualizar_contador)
                
        with open(archivo, "w", encoding="utf-8") as f:
            json.dump(datos_existentes, f, indent=4)
        

    
    def iniciar_recepcion_uart(self):
        hilo_uart = threading.Thread(target=self.leer_uart_y_guardar_json, daemon=True)
        hilo_uart.start()
