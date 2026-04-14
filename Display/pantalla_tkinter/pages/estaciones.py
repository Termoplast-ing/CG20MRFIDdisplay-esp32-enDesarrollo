import tkinter as tk
from tkinter import ttk
import json
import os
import serial
import threading
import time
from datetime import datetime
from util import sqlite as db_local 

def log_bloqueo(mensaje):
    # Usar ruta dinámica relativa al archivo estaciones.py
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    # Subimos un nivel si estamos en la carpeta 'pages'
    PROYECTO_DIR = os.path.dirname(BASE_DIR)
    ruta_fija = os.path.join(PROYECTO_DIR, "log_bloqueos.txt")
    try:
        with open(ruta_fija, "a") as f:
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {mensaje}\n")
            f.flush()
            os.fsync(f.fileno())
    except:
        pass

class Estaciones:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.fecha_vista = None # None significa "Hoy" (Tiempo Real)
        self.timer_retorno = None
        self.estados_colores = {
            'alerta': 'red',    
            'normal': 'green',  
            'completo': 'blue'  
        }      

        self.frame_tabla = tk.Frame(self.parent_frame, bg="#EF9480")
        self.frame_tabla.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # Indicador de qué fecha se está mostrando
        self.label_fecha_vista = tk.Label(
            self.frame_tabla, 
            text="Datos de Hoy", 
            font=("Helvetica", 14, "bold"),
            bg="#EF9480",
            fg="white"
        )
        self.label_fecha_vista.grid(row=0, column=0, sticky="w", padx=10, pady=5)
        
        self.frame_tabla.config(height=400)
        self.frame_tabla.grid_rowconfigure(1, weight=1)
        self.frame_tabla.grid_columnconfigure(0, weight=1)

        self.crear_tabla_estaciones()
        self.actualizar_tabla()
        self.iniciar_recepcion_uart()

    def crear_tabla_estaciones(self):
        scroll_frame = tk.Frame(self.frame_tabla, bg="#EF9480")
        scroll_frame.grid(row=1, column=0, sticky="nsew")
        scroll_frame.config(height=400)
        scroll_frame.grid_rowconfigure(0, weight=1)
        scroll_frame.grid_columnconfigure(0, weight=1)

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
            columns=("Corral", "Peso Acu", "N°Caravana", "Hora"),
            show="headings",
            height=10
        )
        self.treeview.heading("Corral", text="Corral", command=self.ordenar_corral)
        self.treeview.heading("Peso Acu", text="Peso Acu")
        self.treeview.heading("N°Caravana", text="N°Caravana")
        self.treeview.heading("Hora", text="Hora")

        self.treeview.column("Corral", width=65, anchor="center")
        self.treeview.column("Peso Acu", width=110, anchor="center")
        self.treeview.column("N°Caravana", width=210, anchor="w")
        self.treeview.column("Hora", width=70, anchor="center")
        self.treeview.grid(row=0, column=0, sticky="nsew")

        scrollbar_y = tk.Scrollbar(scroll_frame, orient="vertical", command=self.treeview.yview)
        scrollbar_x = tk.Scrollbar(scroll_frame, orient="horizontal", command=self.treeview.xview)
        self.treeview.config(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        scrollbar_y.grid(row=0, column=1, sticky="ns")
        scrollbar_x.grid(row=1, column=0, columnspan=2, sticky="ew")

        self.treeview.bind("<ButtonRelease-1>", self.cambiar_color_fila)
        self.ordenacion_estado = {"Corral": True}

    def actualizar_tabla(self):
        """Refresca la tabla con el resumen por corral de la fecha seleccionada."""
        try:
            # Usar fecha_vista si existe (histórico), si no None (hoy)
            filas = db_local.obtenerResumenPorCorralDiario(self.fecha_vista)
        except Exception as e:
            print(f"Error cargando resumen por corral: {e}")
            return

        for item in self.treeview.get_children():
            self.treeview.delete(item)

        for f in filas:
            corral_id, peso_total, last_caravana, last_ts = f
            
            # Formatear la hora desde el timestamp o string
            hora_str = ""
            if last_ts:
                try:
                    dt = None
                    if str(last_ts).isdigit():
                        dt = datetime.fromtimestamp(int(last_ts))
                    else:
                        # Fallback por si la fecha está guardada como string YYYY-MM-DD HH:MM:SS
                        dt = datetime.strptime(str(last_ts), "%Y-%m-%d %H:%M:%S")
                    
                    # Si estamos viendo HOY, comparamos con la fecha actual del sistema
                    # Si estamos viendo un HISTÓRICO, comparamos con esa fecha
                    ref_date = self.fecha_vista.date() if self.fecha_vista else datetime.now().date()
                    
                    if dt.date() == ref_date:
                        hora_str = dt.strftime("%H:%M")
                    else:
                        hora_str = dt.strftime("%d/%m %H:%M")
                except:
                    hora_str = "-"
            
            # Formatear el peso
            peso_fmt = f"{peso_total:.2f} kg" if peso_total is not None else "0.00 kg"
            
            self.treeview.insert("", "end", values=(
                f"{corral_id}",
                peso_fmt,
                last_caravana if last_caravana else "-",
                hora_str
            ))

    def filtrar_por_fecha(self, fecha_str):
        """Muestra los datos de una fecha específica y programa el retorno a hoy."""
        try:
            # fecha_str viene del calendario (ej: "01/04/2026")
            fecha_dt = datetime.strptime(fecha_str, "%d/%m/%Y")
            self.fecha_vista = fecha_dt
            self.label_fecha_vista.config(text=f"Calendario: {fecha_str} (Histórico)")
            self.actualizar_tabla()
            
            # Cancelar timer anterior si existe
            if self.timer_retorno:
                self.parent_frame.after_cancel(self.timer_retorno)
            
            # Programar retorno en 1 minuto (60000 ms)
            self.timer_retorno = self.parent_frame.after(60000, self.volver_a_hoy)
            print(f"Vista cambiada a {fecha_str}. Volverá a hoy en 60s.")
        except Exception as e:
            print(f"Error al filtrar por fecha: {e}")

    def volver_a_hoy(self):
        """Retorna la vista a los datos del día actual."""
        self.fecha_vista = None
        self.label_fecha_vista.config(text="Datos de Hoy")
        self.actualizar_tabla()
        self.timer_retorno = None
        print("Vista retornada a tiempo real (Hoy).")

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
        try:
            values.sort(key=lambda x: int(x[0][0]), reverse=not ascending)
        except:
            pass
        for item in self.treeview.get_children():
            self.treeview.delete(item)
        for value, row, tag in values:
            self.treeview.insert("", "end", values=value, tags=tag)
        self.ordenacion_estado["Corral"] = not ascending

    def leer_uart_y_guardar_json(self):
        del_i, del_f = "<<<", ">>>"
        buffer = ""
        while True:
            try:
                # Usar el objeto serial compartido desde el frame padre (MasterPanel)
                ser = getattr(self.parent_frame, 'ser', None)
                
                if ser and ser.is_open:
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
                    else:
                        # OPTIMIZACIÓN CRÍTICA: Liberar CPU si no hay datos
                        time.sleep(0.1)
                else:
                    # Si el serial no está listo, esperamos un poco
                    time.sleep(1)
            except Exception as e:
                print(f"Error en hilo UART: {e}")
                time.sleep(5) # Esperar antes de reintentar si falla algo

    def guardar_en_archivo(self, datos_recibidos):
        ahora_ts = int(datetime.now().timestamp())
        
        for animal in datos_recibidos:
            caravana = str(animal.get("caravana", "")).strip()
            corral_num = animal.get("corral", None)
            peso = animal.get("peso", "")
            if not caravana or corral_num is None:
                continue
                
            # 1. Obtenemos datos de la dieta
            dieta = db_local.obtener_dieta_por_caravana(caravana)
            if not dieta: continue

            # 2. VALIDAMOS EL INTERVALO (COMENTADO PARA LECTURA CONTINUA)
            # res_db = db_local.obtener_intervalo_y_ultima_lectura(caravana)
            # if res_db:
            #     intervalo_horas, ultima_fecha_ts = res_db
            #     if ultima_fecha_ts:
            #         intervalo_segundos = int(intervalo_horas) * 3600
            #         if (ahora_ts - int(ultima_fecha_ts)) < intervalo_segundos:
            #             continue 

            # 3. VALIDAMOS LAS DOSIS (COMENTADO: NO HAY LÍMITE DIARIO)
            # inicio_dia_ts = int(datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).timestamp())
            # dosis_hoy = db_local.obtenerConteoDosisDiaria(caravana, inicio_dia_ts)
            #         
            # if dosis_hoy >= int(dieta["cantidadDosis"]):
            #     log_bloqueo(f"Bloqueo Dosis: Carav {caravana}. Dosis: {dosis_hoy} >= {dieta['cantidadDosis']}")
            #     print(f"Animal {caravana} ya cumplio sus dosis de hoy ({dosis_hoy})")
            #     continue 

            # 4. GUARDAR EN SQLITE
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

            # Actualizar contadores en UI si corresponde
            if caravana:
                def act_cont(c=caravana):
                    if not hasattr(self.parent_frame, "datos_reales"):
                        self.parent_frame.datos_reales = {}
                    if c not in self.parent_frame.datos_reales:
                        self.parent_frame.datos_reales[c] = {"dosis_recibidas": 0}
                    self.parent_frame.datos_reales[c]["dosis_recibidas"] += 1
                    # Refrescar tabla inmediatamente tras recibir dato
                    self.actualizar_tabla()
                self.parent_frame.after(0, act_cont)

    def iniciar_recepcion_uart(self):
        # Evitar múltiples hilos si ya está corriendo
        if hasattr(self, "_hilo_corriendo") and self._hilo_corriendo:
            return
        self._hilo_corriendo = True
        threading.Thread(target=self.leer_uart_y_guardar_json, daemon=True).start()
