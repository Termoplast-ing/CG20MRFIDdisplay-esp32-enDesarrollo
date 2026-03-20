import tkinter as tk
from tkinter import ttk
import util.util_ventana as util_ventana
from util import sqlite as db_local

class AlarmaWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.overrideredirect(True)
        self.geometry("480x800")
        self.config(bg="#EF9480")
        self.resizable(True, True)  # Permitir que la ventana sea redimensionable
      
        # Crear un frame para el logo en la parte superior
        self.frame_logo = tk.Frame(self, bg='#EF9480', height=100)
        self.frame_logo.pack(side=tk.TOP, fill="x", pady=22)

        # Crear el logo en la ventana secundaria
        self.crear_logo(self.frame_logo)

        # Crear un frame para el Treeview (tabla) y las barras de desplazamiento
        self.frame_treeview = tk.Frame(self, bg='#EF9480', height=400)
        self.frame_treeview.pack(side=tk.TOP, fill="both", expand=True, padx=15, pady=20)

        # Crear el Treeview (tabla) con los encabezados
        self.treeview = ttk.Treeview(
            self.frame_treeview,
            columns=("Fecha y Hora", "Descripción", "Corral", "N° interno", "N° caravana"),
            show="headings"
        )

        # Definir los encabezados de las columnas
        self.treeview.heading("Fecha y Hora", text="Fecha/Hora", anchor="w")
        self.treeview.heading("Descripción", text="Descripción", anchor="w")
        self.treeview.heading("Corral", text="Corral", anchor="w")
        self.treeview.heading("N° interno", text="N° interno", anchor="w")
        self.treeview.heading("N° caravana", text="N° caravana", anchor="w")

        # Configurar el tamaño de las columnas
        self.treeview.column("Fecha y Hora", width=140, anchor="w", stretch=False)
        self.treeview.column("Descripción", width=180, anchor="w", stretch=False)
        self.treeview.column("Corral", width=75, anchor="center", stretch=False)
        self.treeview.column("N° interno", width=110, anchor="w", stretch=False)
        self.treeview.column("N° caravana", width=130, anchor="w", stretch=False)

        # Crear las barras de desplazamiento
        self.scroll_vertical = tk.Scrollbar(self.frame_treeview, orient="vertical", command=self.treeview.yview)
        self.scroll_horizontal = tk.Scrollbar(self.frame_treeview, orient="horizontal", command=self.treeview.xview)

        # Asociar las barras de desplazamiento al Treeview
        self.treeview.configure(
            yscrollcommand=self.scroll_vertical.set,
            xscrollcommand=self.scroll_horizontal.set
        )

        # Colocar el Treeview y las barras de desplazamiento en el frame
        self.treeview.grid(row=0, column=0, sticky="nsew")
        self.scroll_vertical.grid(row=0, column=1, sticky="ns")
        self.scroll_horizontal.grid(row=1, column=0, sticky="ew")

        # Configurar expansión en el grid
        self.frame_treeview.grid_rowconfigure(0, weight=1)
        self.frame_treeview.grid_columnconfigure(0, weight=1)

        # --- Cargar historial real desde SQLite ---
        self.cargar_historial()

        # Crear un frame inferior para el botón "Atrás"
        self.frame_boton_atras = tk.Frame(self, bg="#EF9480", height=60)
        self.frame_boton_atras.pack(side=tk.BOTTOM, fill="x")

        # Botón para volver a la ventana principal
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

        # Botón "Borrar Historial" debajo del Treeview
        boton_borrar_historial = tk.Button(
            self,
            text="Borrar Historial",
            font=("Helvetica", 16),
            command=self.borrar_historial,
            bg="red",
            fg="#ffffff",
            bd=7
        )
        boton_borrar_historial.pack(side=tk.BOTTOM, pady=10)

        # Centrar la ventana
        util_ventana.centrar_ventana(self, 480, 800)

    def crear_logo(self, frame):
        """Función para crear y ubicar el logo en un frame dado"""
        label = tk.Label(frame, image=self.master.logo, bg='#EF9480')
        label.place(relx=0.5, rely=0.5, anchor="center")

    def cargar_historial(self):
        """Lee las alarmas desde SQLite y las carga en el Treeview."""
        # Limpiar el treeview por si ya tenía datos
        for item in self.treeview.get_children():
            self.treeview.delete(item)

        # obtenerAlarmas devuelve: (idAlarma, fechaHora, descripcion, corral, numeroInterno, caravana)
        registros = db_local.obtenerAlarmas()
        for (id_alarma, fechaHora, descripcion, corral, numeroInterno, caravana) in registros:
            # Ojo con el orden de columnas: Fecha/Hora, Descripción, Corral, N° interno, N° caravana
            self.treeview.insert(
                "",
                "end",
                iid=id_alarma,
                values=(fechaHora, descripcion, corral, numeroInterno, caravana)
            )

    def borrar_historial(self):
        """Eliminar todas las filas (en la DB y en el Treeview)."""
        db_local.borrarAlarmas()
        for item in self.treeview.get_children():
            self.treeview.delete(item)

    def cerrar_ventana(self):
        self.destroy()
