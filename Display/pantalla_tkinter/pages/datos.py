import tkinter as tk
from tkinter import Scrollbar, ttk
from datetime import datetime, date, timedelta
import util.util_ventana as util_ventana
from util import sqlite as db_local

def ts_to_date(fecha_l):
    try:
        ts = int(fecha_l)
        if ts > 10_000_000_000: ts = ts / 1000
        return datetime.fromtimestamp(ts).date()
    except: return None

class DatosWindow(tk.Toplevel):
    def __init__(self, master, logo=None):
        super().__init__(master)
        self.overrideredirect(True)
        self.geometry("480x800")
        self.config(bg="#EF9480")
        self.resizable(False, False)

        self.frame_logo = tk.Frame(self, bg='#EF9480', height=100)
        self.frame_logo.pack(side=tk.TOP, fill="x", pady=10)
        self.crear_logo(self.frame_logo)

        self.frame_selector = tk.Frame(self, bg="#EF9480", height=40)
        self.frame_selector.pack(side=tk.TOP, fill="x", pady=(0, 5))

        tk.Label(self.frame_selector, text="Seleccionar Corral:", bg="#EF9480", font=("Helvetica", 16, "bold")).pack(side=tk.LEFT, padx=10)
        self.combo_corral = ttk.Combobox(self.frame_selector, values=[f"Corral {i}" for i in range(1, 21)])
        self.combo_corral.current(0)
        self.combo_corral.pack(side=tk.LEFT, padx=5)
        self.combo_corral.bind("<<ComboboxSelected>>", self.actualizar_datos)

        self.frame_canvas = tk.Frame(self, bg="#EF9480", height=500)
        self.frame_canvas.pack(side=tk.TOP, fill="x", padx=10, pady=(0, 5))
        self.frame_canvas.pack_propagate(False)

        self.canvas = tk.Canvas(self.frame_canvas, bg="white")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.v_scroll = Scrollbar(self.frame_canvas, orient="vertical", command=self.canvas.yview)
        self.v_scroll.pack(side="right", fill="y")

        self.h_scroll = Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        self.h_scroll.place(in_=self.frame_canvas, relx=0, rely=1.0, relwidth=1.0, anchor="sw")
        self.canvas.configure(yscrollcommand=self.v_scroll.set, xscrollcommand=self.h_scroll.set)

        self.dibujar_tabla()

        self.frame_botones = tk.Frame(self, bg="#EF9480", height=60)
        self.frame_botones.pack(side=tk.TOP, fill="x")

        tk.Button(self.frame_botones, text="<< Atrás", font=("Helvetica", 16), command=self.destroy, bg="red", fg="white", bd=7).pack(side=tk.LEFT, padx=10, pady=14)
        tk.Button(self.frame_botones, text="Actualizar", font=("Helvetica", 16), command=self.dibujar_tabla, bg="red", fg="white", bd=7).pack(side=tk.RIGHT, padx=10, pady=14)

        util_ventana.centrar_ventana(self, 480, 800)
        self.grab_set()

    def crear_logo(self, frame):
        img = self.master.logo
        label = tk.Label(frame, image=img, bg='#EF9480')
        label.place(relx=0.5, rely=0.5, anchor="center")

    def actualizar_datos(self, event=None):
        self.dibujar_tabla()

    def dibujar_tabla(self):
        headers = ["N° Caravana", "N° Interno", "Día Ciclo", "Peso Acumulado", "Proceso Peso", "Ant", "Ant -1", "Ant -2"]
        col_widths = [120, 120, 70, 120, 200, 50, 50, 50]
        row_height = 40
        self.canvas.delete("all")

        x = 0
        for i, h in enumerate(headers):
            w = col_widths[i]
            self.canvas.create_rectangle(x, 0, x + w, row_height, fill="#f0ad4e", width=3)
            self.canvas.create_text(x + w / 2, row_height / 2, text=h, font=("Helvetica", 10, "bold"))
            x += w

        animales = []
        try:
            corral_str = self.combo_corral.get()
            id_corral = int(corral_str.split()[-1])
            # Usar obtenerAnimalesParaDatos para tener todas las columnas de la dieta
            animales = db_local.obtenerAnimalesParaDatos(id_corral)
        except: animales = []

        self.canvas.config(scrollregion=(0, 0, sum(col_widths), row_height * (len(animales) + 2)))

        ahora = datetime.now()
        hoy_inicio = ahora.replace(hour=0, minute=0, second=0, microsecond=0)
        hoy_inicio_ts = int(hoy_inicio.timestamp())
        
        # Rangos para el histórico (Ant, Ant-1, Ant-2)
        ayer_i, ayer_f = hoy_inicio_ts - 86400, hoy_inicio_ts
        ant1_i, ant1_f = ayer_i - 86400, ayer_i
        ant2_i, ant2_f = ant1_i - 86400, ant1_i

        for fila_idx, animal in enumerate(animales):
            y = row_height * (fila_idx + 1)
            x = 0
            # animal = (caravana, interno, f_insem, pesoT, cantD)
            caravana, interno, f_insem = str(animal[0]), str(animal[1]), animal[2]
            peso_max_dia = float(animal[3] or 0) / 10.0
            cant_dosis_target = int(animal[4] or 1)
            
            delta_dias = "-"
            f_ins_dt = None
            if f_insem:
                try:
                    if str(f_insem).replace(".","").isdigit():
                        f_ins_dt = datetime.fromtimestamp(int(float(str(f_insem))))
                    else:
                        f_ins_dt = datetime.strptime(str(f_insem).split()[0], "%Y-%m-%d")
                    diff_dias = (ahora.date() - f_ins_dt.date()).days + 1
                    if diff_dias < 1:
                        delta_dias = "-"
                    else:
                        delta_dias = max(1, min(113, diff_dias))
                except: delta_dias = "-"

            # d_hoy: cantidad de dosis con peso != 0; ultimo_peso: peso de la última lectura hoy
            d_hoy, ultimo_peso = db_local.obtenerInfoDosisHoy(caravana, id_corral, hoy_inicio_ts)
            
            # Histórico para semáforos
            c_ant = db_local.obtenerConteoDosisEnRango(caravana, id_corral, ayer_i, ayer_f)
            c_ant1 = db_local.obtenerConteoDosisEnRango(caravana, id_corral, ant1_i, ant1_f)
            c_ant2 = db_local.obtenerConteoDosisEnRango(caravana, id_corral, ant2_i, ant2_f)

            def f_color(c, target):
                if c >= target: return "#27ae60" # Verde
                if c > 0: return "#f1c40f"       # Amarillo
                return "#e74c3c"                # Rojo

            colores_hist = {5: f_color(c_ant, cant_dosis_target), 
                            6: f_color(c_ant1, cant_dosis_target), 
                            7: f_color(c_ant2, cant_dosis_target)}

            # Peso Acu = último peso recibido * cantidad de dosis comidas
            peso_acu = ultimo_peso * d_hoy
            fila = [caravana, interno, delta_dias, f"{peso_acu:.1f} kg", "", 0, 0, 0]

            for col_idx, valor in enumerate(fila):
                w = col_widths[col_idx]
                self.canvas.create_rectangle(x, y, x + w, y + row_height, fill="#cacaca", width=2)
                if col_idx == 4:
                    tx, ty = x + 10, y + row_height / 3
                    self.canvas.create_text(tx, ty, text="Dosis:", anchor="w", font=("Helvetica", 9))
                    # Mostrar el peso de la última lectura debajo de "Dosis:"
                    self.canvas.create_text(tx, ty + 16, text=f"{ultimo_peso:.1f} kg", anchor="w", font=("Helvetica", 9))
                    for i in range(d_hoy):
                        cx, cy = tx + 60 + i * 22, ty + 5
                        self.canvas.create_oval(cx-8, cy-8, cx+8, cy+8, fill="#27ae60", outline="black")
                elif col_idx in (5, 6, 7):
                    cx, cy = x + w / 2, y + row_height / 2
                    color = colores_hist.get(col_idx, "#e74c3c")
                    self.canvas.create_oval(cx-10, cy-10, cx+10, cy+10, fill=color, outline="black")
                else:
                    self.canvas.create_text(x + w / 2, y + row_height / 2, text=valor, font=("Helvetica", 10))
                x += w
