import tkinter as tk
import util.util_ventana as util_ventana
from util.util_teclado import TecladoNumerico
from util import sqlite as db_local

class EstacionesCorralesWindow(tk.Toplevel):
    def __init__(self, master, configuracion_window):
        super().__init__(master)
        self.configuracion_window = configuracion_window
        self.overrideredirect(True)
        self.geometry("480x800")
        self.config(bg="#EF9480")
        self.resizable(False, False)
        self.grab_set()

        self.corrales_info = self._cargar_corrales_desde_db()

        self.frame_logo = tk.Frame(self, bg="#EF9480", height=100)
        self.frame_logo.pack(side=tk.TOP, fill="x", pady=(15, 10))
        self.crear_logo(self.frame_logo)

        self.frame_contenido = tk.Frame(self, bg="#EF9480")
        self.frame_contenido.pack(fill="both", expand=True)

        self.frame_corrales = tk.Frame(self.frame_contenido, bg="#EF9480")
        self.frame_corrales.pack(expand=True)

        self.botones_corrales = {}
        self.crear_botones_corrales()

        self.frame_inferior = tk.Frame(self, bg="#EF9480", height=100)
        self.frame_inferior.pack(side=tk.BOTTOM, fill="x", pady=(10, 25))

        boton_atras = tk.Button(
            self.frame_inferior,
            text="<< Atrás",
            font=("Helvetica", 16),
            command=self.cerrar_ventana,
            bg="red",
            fg="#ffffff",
            bd=7
        )
        boton_atras.pack(side=tk.LEFT, padx=40)

        boton_escanear = tk.Button(
            self.frame_inferior,
            text="Escanear",
            font=("Helvetica", 16),
            bg="green",
            fg="#ffffff",
            bd=7
        )
        boton_escanear.pack(side=tk.RIGHT, padx=40)

        util_ventana.centrar_ventana(self, 480, 800)

    def _cargar_corrales_desde_db(self):
        resultado = {}
        filas = db_local.obtenerCorrales()  # [(idCorral, descripcion, direccion), ...]
        for id_corral, descripcion, direccion in filas:
            num = None
            if descripcion and descripcion.lower().startswith("corral"):
                try:
                    num = int(descripcion.split()[-1])
                except ValueError:
                    num = id_corral
            else:
                num = id_corral

            if 1 <= num <= 10:
                resultado[num] = {
                    "id": id_corral,
                    "direccion": direccion
                }

        for n in range(1, 11):
            resultado.setdefault(
                n,
                {"id": None, "direccion": None}
            )

        return resultado

    def _guardar_direccion_en_db(self, numero_corral: int, direccion: int):
        corral_info = self.corrales_info.get(numero_corral)
        if not corral_info or corral_info["id"] is None:
            print(f"[WARN] No hay idCorral para C{numero_corral}")
            return

        id_corral = corral_info["id"]
        db_local.actualizarDireccionCorral(id_corral, direccion)
        self.corrales_info[numero_corral]["direccion"] = direccion

        boton = self.botones_corrales.get(numero_corral)
        if boton:
            texto = f"C{numero_corral}\n({direccion})"
            boton.config(text=texto)

    def crear_logo(self, frame):
        label = tk.Label(frame, image=self.master.logo, bg="#EF9480")
        label.place(relx=0.5, rely=0.5, anchor="center")

    def crear_botones_corrales(self):
        for i in range(1, 11):
            texto = f"C{i}"
            dir_actual = self.corrales_info.get(i, {}).get("direccion")
            if dir_actual is not None:
                texto = f"C{i}\n({dir_actual})"

            boton = tk.Button(
                self.frame_corrales,
                text=texto,
                font=("Helvetica", 16, "bold"),
                bg="#ABABAB",
                fg="black",
                bd=5,
                relief="raised",
                width=6,
                height=2,
                command=lambda n=i: self.abrir_modal_corral(n)
            )
            self.botones_corrales[i] = boton

        for i in range(5):
            self.botones_corrales[i * 2 + 1].grid(row=i, column=0, padx=35, pady=12)
            self.botones_corrales[i * 2 + 2].grid(row=i, column=1, padx=35, pady=12)

    def abrir_modal_corral(self, numero_corral):
        self.grab_release()
        modal = tk.Toplevel(self)
        modal.overrideredirect(True)
        modal.title(f"Corral C{numero_corral}")
        modal.geometry("380x300")
        modal.config(bg="#FFD966")

        x = self.winfo_x() + (self.winfo_width() - 380) // 2
        y = self.winfo_y() + (self.winfo_height() - 300) // 2
        modal.geometry(f"+{x}+{y}")

        frame_borde = tk.Frame(modal, bg="#FFD966", bd=3, relief="solid")
        frame_borde.pack(fill="both", expand=True, padx=5, pady=5)

        boton_cerrar = tk.Button(
            frame_borde,
            text="X",
            font=("Helvetica", 12, "bold"),
            bg="#DBC0A2",
            fg="white",
            width=3,
            command=lambda: self.cerrar_modal(modal)
        )
        boton_cerrar.place(x=300, y=10)

        etiqueta = tk.Label(
            frame_borde,
            text=f"Ingrese dirección (0 a 255)",
            font=("Helvetica", 14),
            bg="#FFD966"
        )
        etiqueta.pack(pady=20)

        valor_entry = tk.StringVar()

        dir_actual = self.corrales_info.get(numero_corral, {}).get("direccion")
        if dir_actual is not None:
            valor_entry.set(str(dir_actual))

        entrada = tk.Entry(
            frame_borde,
            textvariable=valor_entry,
            font=("Helvetica", 18),
            justify="center",
            width=8
        )
        entrada.pack(pady=10)

        def mostrar_teclado(event):
            teclado = TecladoNumerico(self, valor_entry)
            teclado_ancho = 480
            teclado_alto = 400
            teclado_x = x + (380 - teclado_ancho) // 2
            teclado_y = y - 100
            teclado.geometry(f"+{teclado_x}+{teclado_y}")
            teclado.attributes('-topmost', True)
            teclado.lift()
            teclado.focus_force()

        entrada.bind("<Button-1>", mostrar_teclado)

        boton_aceptar = tk.Button(
            frame_borde,
            text="Ok",
            font=("Helvetica", 14),
            bg="green",
            fg="#ffffff",
            bd=5,
            command=lambda: self.validar_valor(modal, numero_corral, valor_entry.get())
        )
        boton_aceptar.pack(pady=20)

        modal.focus_force()
        modal.lift()

    def validar_valor(self, modal, numero_corral, valor):
        try:
            numero = int(valor)
            if 0 <= numero <= 255:
                self._guardar_direccion_en_db(numero_corral, numero)
                self.cerrar_modal(modal)
            else:
                self.mostrar_error(modal, "La dirección debe estar entre 0 y 255")
        except ValueError:
            self.mostrar_error(modal, "Debe ingresar un número válido")

    def mostrar_error(self, modal, mensaje):
        frame_borde = modal.winfo_children()[0]
        for widget in frame_borde.winfo_children():
            if isinstance(widget, tk.Label) and widget.cget('fg') == 'red':
                widget.destroy()

        etiqueta_error = tk.Label(
            frame_borde,
            text=mensaje,
            font=("Helvetica", 12),
            fg="red",
            bg="#FFD966"
        )
        etiqueta_error.pack(pady=5)

    def cerrar_modal(self, modal):
        modal.destroy()
        self.grab_set()

    def cerrar_ventana(self):
        if self.configuracion_window:
            self.grab_release()
            self.destroy()
            self.configuracion_window.deiconify()
        else:
            print("Error: configuracion_window es None")
