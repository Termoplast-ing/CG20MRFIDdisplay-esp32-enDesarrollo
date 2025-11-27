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

        # ===== Frame para selector de corral =====
        self.frame_selector = tk.Frame(self, bg="#EF9480", height=40)
        self.frame_selector.pack(side=tk.TOP, fill="x", pady=(0, 5))

        label_corral = tk.Label(
            self.frame_selector,
            text="Seleccionar Corral:",
            bg="#EF9480",
            font=("Helvetica", 16, "bold")
        )
        label_corral.pack(side=tk.LEFT, padx=10)

        self.combo_corral = ttk.Combobox(
            self.frame_selector,
            values=[f"Corral {i}" for i in range(1, 21)]
        )
        self.combo_corral.current(0)
        self.combo_corral.pack(side=tk.LEFT, padx=5)
        self.combo_corral.bind("<<ComboboxSelected>>", self.actualizar_datos)

        # ===== Frame que contendrá canvas + scrollbars =====
        self.frame_canvas = tk.Frame(self, bg="#EF9480", height=500)
        self.frame_canvas.pack(side=tk.TOP, fill="x", padx=10, pady=(0, 5))

        # Canvas y scroll vertical
        self.canvas = tk.Canvas(self.frame_canvas, bg="white")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.v_scroll = Scrollbar(self.frame_canvas, orient="vertical", command=self.canvas.yview)
        self.v_scroll.pack(side="right", fill="y")

        # Config inicial de scroll
        self.canvas.configure(height=500, yscrollcommand=self.v_scroll.set)

        # Scroll horizontal flotante
        self.h_scroll = Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        self.h_scroll.place(in_=self.frame_canvas, relx=0, rely=1.0, relwidth=1.0, anchor="sw")
        self.canvas.configure(xscrollcommand=self.h_scroll.set)

        # Dibujar tabla inicial
        self.dibujar_tabla()

        # Frame botones abajo
        self.frame_botones = tk.Frame(self, bg="#EF9480", height=60)
        self.frame_botones.pack(side=tk.TOP, fill="x")

        boton_atras = tk.Button(
            self.frame_botones,
            text="<< Atrás",
            font=("Helvetica", 16),
            command=self.cerrar_ventana,
            bg="red",
            fg="#ffffff",
            bd=7
        )
        boton_atras.pack(side=tk.LEFT, padx=10, pady=14)

        btn_actualizar = tk.Button(
            self.frame_botones,
            text="Actualizar",
            font=("Helvetica", 16),
            command=self.actualizar_tabla,
            bg="red",
            fg="white",
            bd=7
        )
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

        # ==== Encabezados ====
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

        # Obtener corral seleccionado
        corral_seleccionado = self.combo_corral.get()  # "Corral 3"
        try:
            num_corral = int(corral_seleccionado.split()[-1])
        except Exception:
            num_corral = 1


        animales = db_local.obtenerAnimalesPorCorral(num_corral)

        # Ajustar scrollregion
        alto_canvas = row_height * (1 + len(animales)) + 20
        ancho_canvas = sum(col_widths)
        self.canvas.config(scrollregion=(0, 0, ancho_canvas, alto_canvas))

        # ==== Filas ====
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

                    # mostrar peso por dosis
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
