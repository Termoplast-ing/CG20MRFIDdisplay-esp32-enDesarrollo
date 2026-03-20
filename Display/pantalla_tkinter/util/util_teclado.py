import tkinter as tk

class TecladoNumerico(tk.Toplevel):
    def __init__(self, master, entry):
        super().__init__(master)
        self.overrideredirect(True)  # Eliminar la barra de título
        ancho_teclado = 480
        alto_teclado = 400
        ancho_pantalla = self.winfo_screenwidth()
        alto_pantalla = self.winfo_screenheight()
        x_pos = (ancho_pantalla - ancho_teclado) // 2
        y_pos = alto_pantalla - alto_teclado - 40
        self.geometry(f"{ancho_teclado}x{alto_teclado}+{x_pos}+{y_pos}")
        self.config(bg="grey")  # Fondo gris

        # Crear un frame principal que ocupe todo el espacio
        self.frame_principal = tk.Frame(self, bg="#EF9480")
        self.frame_principal.pack(fill="both", expand=True)
        self.entry = entry

        # Campo de texto para mostrar el número ingresado
        self.entry_display = tk.Entry(self.frame_principal, font=("Helvetica", 14), textvariable=self.entry, state="readonly",
                                      bg="black", fg="#000000", width=20)  # Fondo blanco, texto negro
        self.entry_display.grid(row=0, column=0, columnspan=3, padx=140, pady=10, sticky="ew")

        # Crear botones numéricos
        botones = [
            ['7', '8', '9'],
            ['4', '5', '6'],
            ['1', '2', '3'],
            ['0', '.', 'Borrar']
        ]

        # Frame para contener los botones y centrarlos
        self.frame_botones = tk.Frame(self.frame_principal, bg="black")
        self.frame_botones.grid(row=1, column=0, columnspan=3, pady=10)

        for i, fila in enumerate(botones):
            for j, boton in enumerate(fila):
                button = tk.Button(self.frame_botones, text=boton, font=("Helvetica", 14), width=5, height=2,
                                   command=lambda b=boton: self.agregar_caracter(b),
                                   bg="#837e7e", fg="#000000")  # Fondo blanco, texto negro
                button.grid(row=i, column=j, padx=5, pady=5, sticky="nsew")

        # Asegurar que todas las filas y columnas tengan el mismo tamaño
        for i in range(len(botones)):
            self.frame_botones.grid_rowconfigure(i, weight=1, uniform="row")  # Mismo tamaño para todas las filas
        for j in range(len(botones[0])):
            self.frame_botones.grid_columnconfigure(j, weight=1, uniform="col")  # Mismo tamaño para todas las columnas

        # Botón Enter
        boton_enter = tk.Button(self.frame_principal, text="Confirmar", font=("Helvetica", 14), width=10, height=2,
                                command=self.cerrar_teclado,
                                bg="red", fg="#FFFFFF", bd=7)  # Fondo naranja, texto blanco
        boton_enter.grid(row=2, column=0, columnspan=3, pady=(10, 20))

        # Configurar el peso de las filas y columnas para centrar los botones
        self.frame_principal.grid_rowconfigure(1, weight=1)  # Centrar verticalmente
        self.frame_principal.grid_columnconfigure(0, weight=1)  # Centrar horizontalmente

    def agregar_caracter(self, caracter):
        """Agrega el caracter al campo de texto"""
        current_text = self.entry.get()
        if caracter == 'Borrar':
            self.entry.set(current_text[:-1])
        else:
            if len(current_text) < 15:  # Limitar a 15 caracteres
                self.entry.set(current_text + caracter)

    def cerrar_teclado(self):
        """Cierra el teclado numérico"""
        self.destroy()