import tkinter as tk
from util.util_mensaje import mostrar_mensaje

class TecladoFuncionalidadWindow(tk.Toplevel):
    def __init__(self, master, combobox):
        super().__init__(master)
        self.overrideredirect(True)
        self.combobox = combobox
        ancho_teclado = 480
        alto_teclado = 400
        ancho_pantalla = self.winfo_screenwidth()
        alto_pantalla = self.winfo_screenheight()
        x_pos = (ancho_pantalla - ancho_teclado) // 2
        y_pos = alto_pantalla - alto_teclado - 40
        self.geometry(f"{ancho_teclado}x{alto_teclado}+{x_pos}+{y_pos}")
        self.configure(bg="#EF9480")
        self.attributes('-topmost', True)
        self.update_idletasks()
        self.grab_set()

        self.frame_principal = tk.Frame(self, bg="#EF9480")
        self.frame_principal.pack(fill="both", expand=True)

        self.entry_display = tk.Entry(self.frame_principal, font=("Helvetica", 14),state="readonly", bg="white", fg="black", width=20)
        self.entry_display.grid(row=0, column=0, columnspan=3, padx=140, pady=10, sticky="ew")
        self.actualizar_display()

        botones = [
            ['7', '8', '9'],
            ['4', '5', '6'],
            ['1', '2', '3'],
            ['0', '.', 'Borrar']
        ]

        # Frame de botones con misma configuración que TecladoNumerico
        self.frame_botones = tk.Frame(self.frame_principal, bg="black")
        self.frame_botones.grid(row=1, column=0, columnspan=3, pady=10)

        for i, fila in enumerate(botones):
            for j, boton in enumerate(fila):
                button = tk.Button(self.frame_botones, text=boton, font=("Helvetica", 14), width=5, height=2,command=lambda b=boton: self.agregar_caracter(b),bg="#837e7e", fg="#000000")
                button.grid(row=i, column=j, padx=5, pady=5, sticky="nsew")

        # Configuración uniforme de filas/columnas como en TecladoNumerico
        for i in range(len(botones)):
            self.frame_botones.grid_rowconfigure(i, weight=1, uniform="row")
        for j in range(len(botones[0])):
            self.frame_botones.grid_columnconfigure(j, weight=1, uniform="col")

        boton_enter = tk.Button(self.frame_principal, text="Confirmar", font=("Helvetica", 14),width=10, height=2, command=self.cerrar_teclado,bg="red", fg="#FFFFFF", bd=7)
        boton_enter.grid(row=2, column=0, columnspan=3, pady=(10, 20))

        # Centrado como en TecladoNumerico
        self.frame_principal.grid_rowconfigure(1, weight=1)
        self.frame_principal.grid_columnconfigure(0, weight=1)

    def actualizar_display(self):
        texto = self.combobox.get()
        self.entry_display.config(state='normal')
        self.entry_display.delete(0, tk.END)
        self.entry_display.insert(0, texto)
        self.entry_display.config(state='readonly')

    def agregar_caracter(self, caracter):
        current = self.combobox.get()
        if caracter == 'Borrar':
            new_text = current[:-1]
        else:
            new_text = current + caracter if len(current) < 15 else current
        
        self.combobox.set(new_text)
        self.actualizar_display()
        self.combobox.event_generate('<<ComboboxSelected>>')

    def cerrar_teclado(self):
        """Cierra el teclado permitiendo reapertura"""
        try:
            # Liberar recursos
            if self.grab_status():
                self.grab_release()
            self.attributes('-topmost', False)
            # Transferir foco de forma segura
            if self.master.winfo_exists():
                self.master.focus_set()
            if self.combobox.winfo_exists():
                self.combobox.focus_set()
            # Actualizar combobox
            self.combobox.event_generate('<<ComboboxSelected>>')
            # Cerrar ventana
            self.destroy()
        except Exception as e:
            self.destroy()
