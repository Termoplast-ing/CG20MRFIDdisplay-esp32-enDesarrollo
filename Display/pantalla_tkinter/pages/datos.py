"""
import tkinter as tk
from tkinter import Scrollbar, ttk
from datetime import datetime
import util.util_ventana as util_ventana
from util import sqlite as db_local

class DatosWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.overrideredirect(True)
        self.geometry("480x800")
        self.config(bg="#EF9480")
        self.resizable(False, False)

        # Frame superior para logo
        self.frame_logo = tk.Frame(self, bg='#EF9480', height=100)
        self.frame_logo.pack(side=tk.TOP, fill="x", pady=10)
        self.crear_logo(self.frame_logo)

        self.frame_selector = tk.Frame(self, bg="#EF9480", height=40)
        self.frame_selector.pack(side=tk.TOP, fill="x", pady=(0, 5))

        label_corral = tk.Label(self.frame_selector,text="Seleccionar Corral:",bg="#EF9480",font=("Helvetica", 16, "bold"))
        label_corral.pack(side=tk.LEFT, padx=10)

        self.combo_corral = ttk.Combobox(self.frame_selector,values=[f"Corral {i}" for i in range(1, 21)])
        self.combo_corral.current(0)
        self.combo_corral.pack(side=tk.LEFT, padx=5)
        self.combo_corral.bind("<<ComboboxSelected>>", self.actualizar_datos)

        # ===== Frame que contendrá canvas + scrollbars =====
        self.frame_canvas = tk.Frame(self, bg="#EF9480")
        self.frame_canvas.pack(side=tk.TOP, fill="both",expand=True, padx=10, pady=(0, 5))
        

        # Canvas y scroll vertical
        self.canvas = tk.Canvas(self.frame_canvas, bg="white", height=500)
        self.canvas.pack(side="left", fill="both", expand=True)

        self.v_scroll = Scrollbar(self.frame_canvas, orient="vertical", command=self.canvas.yview)
        self.v_scroll.pack(side="right", fill="y")
        
        total_filas = 20
        altura_fila = 40
        alto_canvas = altura_fila * (1 + total_filas)
        ancho_canvas = 845

        # Config inicial de scroll
        self.canvas.configure(scrollregion=(0, 0, ancho_canvas, alto_canvas), height=500, yscrollcommand=self.v_scroll.set)

        # Scroll horizontal flotante
        self.h_scroll = Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        self.h_scroll.place(in_=self.frame_canvas, relx=0, rely=1.0, relwidth=1.0, anchor="sw")
        self.canvas.configure(xscrollcommand=self.h_scroll.set)

        # Dibujar tabla inicial
        self.dibujar_tabla()

        # Frame botones abajo
        self.frame_botones = tk.Frame(self, bg="#EF9480", height=100)
        self.frame_botones.pack(side=tk.BOTTOM, fill="x")

        boton_atras = tk.Button(self.frame_botones,text="<< Atrás",font=("Helvetica", 16),command=self.cerrar_ventana,bg="red",fg="#ffffff",bd=7)
        boton_atras.pack(side=tk.LEFT, padx=10, pady=14)

        btn_actualizar = tk.Button(self.frame_botones,text="Actualizar",font=("Helvetica", 16),command=self.actualizar_tabla,bg="red",fg="white",bd=7)
        btn_actualizar.pack(side=tk.RIGHT, padx=10, pady=14)

        util_ventana.centrar_ventana(self, 480, 800)

    def crear_logo(self, frame):
        label = tk.Label(frame, image=self.master.logo, bg='#EF9480')
        label.place(relx=0.5, rely=0.5, anchor="center")

    def actualizar_datos(self, event=None):
        self.dibujar_tabla()

    def dibujar_tabla(self):
        headers = [
            "N° Caravana",
            "N° Interno",
            "Día Ciclo",
            "Peso Acumulado",
            "Proceso Peso",
            "Ant",
            "Ant -1",
            "Ant -2"
        ]
        num_cols = len(headers)
        col_widths = [120, 120, 70, 120, 200, 50, 50, 50]
        row_height = 40
        start_x = 0
        start_y = 0

        # Limpiar canvas
        self.canvas.delete("all")

        x = start_x
        for idx, header in enumerate(headers):
            w = col_widths[idx]
            self.canvas.create_rectangle(
                x, start_y, x + w, start_y + row_height,
                fill="#f0ad4e", width=3
            )
            self.canvas.create_text(
                x + w / 2,
                start_y + row_height / 2,
                text=header,
                anchor="center",
                font=("Helvetica", 10, "bold")
            )
            x += w

        corral_seleccionado = self.combo_corral.get()  # "Corral 3"
        try:
            num_corral = int(corral_seleccionado.split()[-1])
        except Exception:
            num_corral = 1


        animales = db_local.obtenerAnimalesPorCorral(num_corral)

        # Ajustar scrollregion
        alto_canvas = row_height * (1 + len(animales)) + 20
        #ancho_canvas = sum(col_widths)
        #alto_canvas = 40 * (1 + len(animales)) + 20
        ancho_canvas = 845
        self.canvas.config(scrollregion=(0, 0, ancho_canvas, alto_canvas))

        for fila_idx, animal in enumerate(animales):
            # animal = (caravana, numeroInterno, fechaInseminacion, pesoTotal, cantidadDosis, intervalo)
            caravana = animal[0]
            interno = animal[1]
            fecha_inseminacion = animal[2]
            peso_total = animal[3] or 0.0
            cantidad_dosis = animal[4] or 1


            y = start_y + row_height * (fila_idx + 1)
            x = start_x

            try:
                fecha_ins = datetime.strptime(str(fecha_inseminacion), "%Y-%m-%d")
                hoy = datetime.now()
                delta_dias = (hoy - fecha_ins).days + 1
                if delta_dias < 1:
                    delta_dias = 1
                elif delta_dias > 113:
                    delta_dias = 113
            except Exception:
                delta_dias = ""
            peso_total_kg = peso_total / 10.0
            peso_por_dosis = peso_total_kg / cantidad_dosis if cantidad_dosis else 0

            dosis_real = cantidad_dosis
            peso_acumulado = peso_por_dosis * dosis_real

            datos = [
                caravana,
                interno,
                delta_dias,
                f"{peso_acumulado:.1f} kg",
                "",   # Proceso Peso (círculos)
                0,    # Ant
                0,    # Ant -1
                0     # Ant -2
            ]

            for col_idx, valor in enumerate(datos):
                w = col_widths[col_idx]
                # celda
                self.canvas.create_rectangle(
                    x, y, x + w, y + row_height,
                    fill="#cacaca", width=3
                )

                if col_idx == 4:
                    # Texto "Dosis:"
                    texto_x = x + 10
                    texto_y = y + row_height / 3
                    self.canvas.create_text(
                        texto_x,
                        texto_y,
                        text="Dosis:",
                        anchor="w",
                        font=("Helvetica", 10)
                    )

                    
                    circle_radius = 10
                    espacio = 25
                    circle_start_x = texto_x + 70
                    circle_y = texto_y + 7
                    for i in range(dosis_real):
                        self.canvas.create_oval(
                            circle_start_x + i * espacio - circle_radius,
                            circle_y - circle_radius,
                            circle_start_x + i * espacio + circle_radius,
                            circle_y + circle_radius,
                            fill="#27ae60",
                            outline="black"
                        )

                    self.canvas.create_text(
                        texto_x,
                        texto_y + 15,
                        text=f"{peso_por_dosis:.2f} kg",
                        anchor="w",
                        font=("Helvetica", 10)
                    )

                elif col_idx in [5, 6, 7]:
                    # Semáforo (por ahora fijo en rojo)
                    estado = 0  # 0=rojo, 1=amarillo, 2=verde
                    color = "#e74c3c" if estado == 0 else "#f1c40f" if estado == 1 else "#27ae60"
                    circle_radius = 10
                    circle_x = x + w / 2
                    circle_y = y + row_height / 2
                    self.canvas.create_oval(
                        circle_x - circle_radius + 2,
                        circle_y - circle_radius + 2,
                        circle_x + circle_radius + 2,
                        circle_y + circle_radius + 2,
                        fill=color,
                        outline="black",
                        width=1
                    )
                else:
                    # Texto normal
                    self.canvas.create_text(
                        x + w / 2,
                        y + row_height / 2,
                        text=valor,
                        anchor="center",
                        font=("Helvetica", 10)
                    )

                x += w

    def actualizar_tabla(self):
        self.dibujar_tabla()

    def cerrar_ventana(self):
        self.destroy()
"""
"""
import tkinter as tk
from tkinter import Scrollbar, ttk
from datetime import datetime, date, timedelta
import util.util_ventana as util_ventana
from util import sqlite as db_local 

def calcular_semaforo(caravana, cantidad_dosis, lecturas):
    hoy = date.today()
    dias_interes = {
        (hoy - timedelta(days=1)).strftime("%Y-%m-%d"): 0,
        (hoy - timedelta(days=2)).strftime("%Y-%m-%d"): 0,
        (hoy - timedelta(days=3)).strftime("%Y-%m-%d"): 0
    }
    for _, car, fecha_l, _ in lecturas:
        # Usamos split para manejar fechas con o sin hora
        f_solo = str(fecha_l).split()[0]
        if str(car) == str(caravana) and f_solo in dias_interes:
            dias_interes[f_solo] += 1
            
    def estado(d):
        if d == 0: return 0
        if d < cantidad_dosis: return 1
        return 2

    return (
        estado(dias_interes[(hoy - timedelta(days=1)).strftime("%Y-%m-%d")]),
        estado(dias_interes[(hoy - timedelta(days=2)).strftime("%Y-%m-%d")]),
        estado(dias_interes[(hoy - timedelta(days=3)).strftime("%Y-%m-%d")])
    )

class DatosWindow(tk.Toplevel):
    def __init__(self, master):
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

        self.datos_animales = self.cargar_datos_animales()
        self.lecturas = db_local.obtenerLecturas()
        self.dibujar_tabla()

        self.frame_botones = tk.Frame(self, bg="#EF9480", height=60)
        self.frame_botones.pack(side=tk.TOP, fill="x")

        tk.Button(self.frame_botones, text="<< Atrás", font=("Helvetica", 16), command=self.cerrar_ventana, bg="red", fg="#ffffff", bd=7).pack(side=tk.LEFT, padx=10, pady=14)
        tk.Button(self.frame_botones, text="Actualizar", font=("Helvetica", 16), command=self.actualizar_tabla, bg="red", fg="white", bd=7).pack(side=tk.RIGHT, padx=10, pady=14)

        util_ventana.centrar_ventana(self, 480, 800)

    def crear_logo(self, frame):
        label = tk.Label(frame, image=self.master.logo, bg='#EF9480')
        label.place(relx=0.5, rely=0.5, anchor="center")

    def cargar_datos_animales(self):
        datos = {}
        try:
            for n in range(1, 21):
                filas = db_local.obtenerAnimalesPorCorral(n)
                datos[f"Corral {n}"] = [list(f) for f in filas] if filas else []
            return datos
        except: return {}

    def actualizar_datos(self, event=None):
        self.dibujar_tabla()

    def dibujar_tabla(self):
        headers = ["N° Caravana", "N° Interno", "Día Ciclo", "Peso Acumulado", "Proceso Peso", "Ant", "Ant -1", "Ant -2"]
        col_widths = [120, 120, 70, 120, 200, 50, 50, 50]
        row_height = 40
        start_x = 0
        start_y = 0

        self.canvas.delete("all")

        x = start_x
        for idx, header in enumerate(headers):
            w = col_widths[idx]
            self.canvas.create_rectangle(x, start_y, x + w, start_y + row_height, fill="#f0ad4e", width=3)
            self.canvas.create_text(x + w/2, start_y + row_height/2, text=header, anchor="center", font=("Helvetica", 10, "bold"))
            x += w
        
        animales = self.datos_animales.get(self.combo_corral.get(), [])
        self.canvas.config(scrollregion=(0, 0, sum(col_widths), row_height * (len(animales) + 2)))

        for fila_idx, animal in enumerate(animales):
            y = start_y + row_height * (fila_idx + 1)
            x = start_x
            
            # --- Tus variables originales ---
            caravana = animal[0]
            interno = animal[1]
            fecha_inseminacion = animal[2]
            
            from util.sqlite import get_connection
            with get_connection() as conn:
                cur = conn.cursor()
                cur.execute("SELECT d.pesoTotal, d.cantidadDosis FROM animal a JOIN dieta d ON a.idDieta = d.idDieta WHERE TRIM(CAST(a.caravana AS TEXT)) = TRIM(CAST(? AS TEXT))", (str(caravana),))
                res = cur.fetchone()
                peso_total, cantidad_dosis = (res[0], res[1]) if res else (0.0, 1)

            try:
                f_ins = datetime.strptime(str(fecha_inseminacion), "%Y-%m-%d")
                delta_dias = (datetime.now() - f_ins).days + 1
                delta_dias = max(1, min(113, delta_dias))
            except:
                delta_dias = ""; f_ins = None

            peso_por_dosis = (float(peso_total) / 10) / int(cantidad_dosis) if cantidad_dosis > 0 else 0
            
            # Conteo para dosis_real (hoy) y acumulado histórico
            d_hoy = 0
            d_hist = 0
            hoy_actual = date.today()
            for _, car_l, fecha_l, _ in self.lecturas:
                if str(car_l) != str(caravana): continue
                try:
                    f_lec_date = datetime.strptime(str(fecha_l).split()[0], "%Y-%m-%d").date()
                    if f_lec_date == hoy_actual: d_hoy += 1
                    if f_ins and f_ins.date() <= f_lec_date <= hoy_actual: d_hist += 1
                except: continue

            # --- Tus variables de cálculo ---
            dosis_real = d_hoy 
            peso_acumulado = peso_por_dosis * d_hist
            sem = calcular_semaforo(caravana, cantidad_dosis, self.lecturas)

            datos = [caravana, interno, delta_dias, f"{peso_acumulado:.1f} kg", "", sem[0], sem[1], sem[2]]

            for col_idx, valor in enumerate(datos):
                w = col_widths[col_idx]
                self.canvas.create_rectangle(x, y, x + w, y + row_height, fill="#cacaca", width=3)

                if col_idx == 4: # Proceso Peso
                    texto_x = x + 10
                    texto_y = y + row_height / 3
                    self.canvas.create_text(texto_x, texto_y, text="Dosis:", anchor="w", font=("Helvetica", 10))
                    circle_radius = 10
                    espacio = 25
                    circle_start_x = texto_x + 70
                    circle_y = texto_y + 7
                    # Dibujar círculos según dosis_real (hoy)
                    for i in range(dosis_real):
                        self.canvas.create_oval(circle_start_x + i * espacio - circle_radius, circle_y - circle_radius, circle_start_x + i * espacio + circle_radius, circle_y + circle_radius, fill="#27ae60", outline="black")
                    self.canvas.create_text(texto_x, texto_y + 15, text=f"{peso_por_dosis:.2f} kg", anchor="w", font=("Helvetica", 10))
                elif col_idx in [5, 6, 7]:
                    color = "#e74c3c" if valor == 0 else "#f1c40f" if valor == 1 else "#27ae60"
                    cr = 10
                    cx, cy = x + w / 2, y + row_height / 2
                    self.canvas.create_oval(cx - cr + 2, cy - cr + 2, cx + cr + 2, cy + cr + 2, fill=color, outline="black")
                else:
                    self.canvas.create_text(x + w/2, y + row_height/2, text=valor, anchor="center", font=("Helvetica", 10))
                x += w

    def actualizar_tabla(self):
        corral_str = self.combo_corral.get()
        try:
            n_corral = int(corral_str.split()[-1])
            filas = db_local.obtenerAnimalesPorCorral(n_corral)
            self.datos_animales[corral_str] = [list(f) for f in filas] if filas else []
        except: pass
        self.lecturas = db_local.obtenerLecturas()
        self.dibujar_tabla()

    def cerrar_ventana(self): 
        self.destroy()
"""

import tkinter as tk
from tkinter import Scrollbar, ttk
from datetime import datetime, date, timedelta
import util.util_ventana as util_ventana
from util import sqlite as db_local
from tkinter import messagebox


def ts_to_date(fecha_l):
    """
    Convierte timestamp TEXT (seg o ms) a date
    """
    try:
        ts = int(fecha_l)
        if ts > 10_000_000_000:  # viene en milisegundos
            ts = ts / 1000
        return datetime.fromtimestamp(ts).date()
    except:
        return None


def calcular_semaforo(caravana, cantidad_dosis, lecturas):
    hoy = date.today()

    dias_interes = {
        hoy - timedelta(days=1): 0,
        hoy - timedelta(days=2): 0,
        hoy - timedelta(days=3): 0
    }

    for _, car, fecha_l, _ in lecturas:
        if str(car) != str(caravana):
            continue

        f_date = ts_to_date(fecha_l)
        if f_date in dias_interes:
            dias_interes[f_date] += 1

    def estado(d):
        if d == 0:
            return 0
        if d < cantidad_dosis:
            return 1
        return 2

    return (
        estado(dias_interes[hoy - timedelta(days=1)]),
        estado(dias_interes[hoy - timedelta(days=2)]),
        estado(dias_interes[hoy - timedelta(days=3)])
    )


class DatosWindow(tk.Toplevel):
    def __init__(self, master):
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

        tk.Label(
            self.frame_selector,
            text="Seleccionar Corral:",
            bg="#EF9480",
            font=("Helvetica", 16, "bold")
        ).pack(side=tk.LEFT, padx=10)

        self.combo_corral = ttk.Combobox(
            self.frame_selector,
            values=[f"Corral {i}" for i in range(1, 21)]
        )
        self.combo_corral.current(0)
        self.combo_corral.pack(side=tk.LEFT, padx=5)
        self.combo_corral.bind("<<ComboboxSelected>>", self.actualizar_datos)

        self.frame_canvas = tk.Frame(self, bg="#EF9480", height=500)
        self.frame_canvas.pack(side=tk.TOP, fill="x", padx=10, pady=(0, 5))
        self.frame_canvas.pack_propagate(False)

        self.canvas = tk.Canvas(self.frame_canvas, bg="white")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.v_scroll = Scrollbar(
            self.frame_canvas,
            orient="vertical",
            command=self.canvas.yview
        )
        self.v_scroll.pack(side="right", fill="y")

        self.h_scroll = Scrollbar(
            self,
            orient="horizontal",
            command=self.canvas.xview
        )
        self.h_scroll.place(
            in_=self.frame_canvas,
            relx=0,
            rely=1.0,
            relwidth=1.0,
            anchor="sw"
        )

        self.canvas.configure(
            yscrollcommand=self.v_scroll.set,
            xscrollcommand=self.h_scroll.set
        )

        self.datos_animales = self.cargar_datos_animales()
        self.lecturas = db_local.obtenerLecturas()
        self.dibujar_tabla()

        self.frame_botones = tk.Frame(self, bg="#EF9480", height=60)
        self.frame_botones.pack(side=tk.TOP, fill="x")

        tk.Button(
            self.frame_botones,
            text="<< Atrás",
            font=("Helvetica", 16),
            command=self.cerrar_ventana,
            bg="red",
            fg="white",
            bd=7
        ).pack(side=tk.LEFT, padx=10, pady=14)

        tk.Button(
            self.frame_botones,
            text="Actualizar",
            font=("Helvetica", 16),
            command=self.actualizar_tabla,
            bg="red",
            fg="white",
            bd=7
        ).pack(side=tk.RIGHT, padx=10, pady=14)

        util_ventana.centrar_ventana(self, 480, 800)

    def crear_logo(self, frame):
        label = tk.Label(frame, image=self.master.logo, bg='#EF9480')
        label.place(relx=0.5, rely=0.5, anchor="center")

    def cargar_datos_animales(self):
        datos = {}
        try:
            for n in range(1, 21):
                filas = db_local.obtenerAnimalesPorCorral(n)
                datos[f"Corral {n}"] = [list(f) for f in filas] if filas else []
            return datos
        except:
            return {}

    def actualizar_datos(self, event=None):
        self.dibujar_tabla()

    def dibujar_tabla(self):
        headers = [
            "N° Caravana", "N° Interno", "Día Ciclo",
            "Peso Acumulado", "Proceso Peso",
            "Ant", "Ant -1", "Ant -2"
        ]

        col_widths = [120, 120, 70, 120, 200, 50, 50, 50]
        row_height = 40

        self.canvas.delete("all")

        x = 0
        for i, h in enumerate(headers):
            w = col_widths[i]
            self.canvas.create_rectangle(x, 0, x + w, row_height, fill="#f0ad4e", width=3)
            self.canvas.create_text(x + w / 2, row_height / 2, text=h, font=("Helvetica", 10, "bold"))
            x += w

        #from util.sqlite import get_connection
        animales = []
        #id_corral_actual = self.combo_corral.get()
        try:
            corral_str = self.combo_corral.get()
            id_corral_actual = int(corral_str.split()[-1])
            
            from util.sqlite import get_connection
            with get_connection() as conn:
                cur = conn.cursor()
                cur.execute("""
                    SELECT a.caravana,
                           a.numeroInterno,
                           a.fechaInseminacion,
                           d.pesoTotal,
                           d.cantidadDosis
                    FROM animal a
                    LEFT JOIN dieta d ON a.idDieta = d.idDieta
                    WHERE a.idCorral = ?
                """,(id_corral_actual,))
                animales = cur.fetchall()
        except:
            animales = []
        #animales = obtenerAnimalesParaDatos(id_corral_actual)
        #animales = self.datos_animales.get(self.combo_corral.get(), [])
        self.canvas.config(scrollregion=(0, 0, sum(col_widths), row_height * (len(animales) + 2)))

        for fila_idx, animal in enumerate(animales):
            y = row_height * (fila_idx + 1)
            x = 0

            caravana = animal[0]
            interno = animal[1]
            fecha_inseminacion = animal[2]
            peso_total = animal[3] if animal[3] is not None else 0.0
            cantidad_dosis = animal[4] if animal[4] is not None else 1

            #from util.sqlite import get_connection
            #with get_connection() as conn:
            #    cur = conn.cursor()
            #    cur.execute("""
            #        SELECT d.pesoTotal, d.cantidadDosis
            #        FROM animal a
            #        JOIN dieta d ON a.idDieta = d.idDieta
            #        WHERE TRIM(CAST(a.caravana AS TEXT)) = TRIM(CAST(? AS TEXT))
            #    """, (str(caravana),))
            #    res = cur.fetchone()
            #    peso_total, cantidad_dosis = res if res else (0.0, 1)

            f_ins = None
            #delta_dias = str(fecha_inseminacion)
            delta_dias = ""
            if fecha_inseminacion:
                try:
                    ts_valor = int(float(str(fecha_inseminacion)))
                    f_ins_dt = datetime.fromtimestamp(ts_valor)
                    diff = (datetime.now() - f_ins_dt).days + 1
                    delta_dias = max(1, min(113, diff))
                    f_ins = f_ins_dt
                except:
                    #f_ins = None
                    delta_dias = "Error"

            peso_por_dosis = (float(peso_total) / 10) / int(cantidad_dosis) if cantidad_dosis > 0 else 0

            d_hoy = 0
            d_hist = 0
            hoy_actual = date.today()

            for _, car_l, fecha_l, _ in self.lecturas:
                if str(car_l) != str(caravana):
                    continue

                f_lec_date = ts_to_date(fecha_l)
                if not f_lec_date:
                    continue

                if f_lec_date == hoy_actual:
                    d_hoy += 1

                if f_ins and f_ins.date() <= f_lec_date <= hoy_actual:
                    d_hist += 1

            dosis_real = d_hoy
            peso_acumulado = peso_por_dosis * d_hist
            sem = calcular_semaforo(caravana, cantidad_dosis, self.lecturas)

            fila = [
                caravana,
                interno,
                delta_dias,
                f"{peso_acumulado:.1f} kg",
                "",
                sem[0],
                sem[1],
                sem[2]
            ]

            for col_idx, valor in enumerate(fila):
                w = col_widths[col_idx]
                self.canvas.create_rectangle(x, y, x + w, y + row_height, fill="#cacaca", width=3)

                if col_idx == 4:
                    tx = x + 10
                    ty = y + row_height / 3
                    self.canvas.create_text(tx, ty, text="Dosis:", anchor="w", font=("Helvetica", 10))

                    for i in range(dosis_real):
                        cx = tx + 70 + i * 25
                        cy = ty + 7
                        self.canvas.create_oval(cx - 10, cy - 10, cx + 10, cy + 10, fill="#27ae60", outline="black")

                    self.canvas.create_text(tx, ty + 15, text=f"{peso_por_dosis:.2f} kg", anchor="w", font=("Helvetica", 10))

                elif col_idx in (5, 6, 7):
                    color = "#e74c3c" if valor == 0 else "#f1c40f" if valor == 1 else "#27ae60"
                    cx, cy = x + w / 2, y + row_height / 2
                    self.canvas.create_oval(cx - 10, cy - 10, cx + 10, cy + 10, fill=color, outline="black")

                else:
                    self.canvas.create_text(x + w / 2, y + row_height / 2, text=valor, font=("Helvetica", 10))

                x += w

    def actualizar_tabla(self):
        corral = self.combo_corral.get()
        try:
            n = int(corral.split()[-1])
            filas = db_local.obtenerAnimalesPorCorral(n)
            self.datos_animales[corral] = [list(f) for f in filas] if filas else []
        except:
            pass

        self.lecturas = db_local.obtenerLecturas()
        self.dibujar_tabla()

    def cerrar_ventana(self):
        self.destroy()
