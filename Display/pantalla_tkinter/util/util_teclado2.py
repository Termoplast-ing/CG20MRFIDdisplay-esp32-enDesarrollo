import tkinter as tk
from util.util_mensaje import mostrar_mensaje

class TecladoNumerico(tk.Toplevel):
    def __init__(self, master, entry, es_indice=False):
        super().__init__(master)
        self.overrideredirect(True)
        ancho_teclado = 480
        alto_teclado = 400
        ancho_pantalla = self.winfo_screenwidth()
        alto_pantalla = self.winfo_screenheight()
        x_pos = (ancho_pantalla - ancho_teclado) // 2
        y_pos = alto_pantalla - alto_teclado - 40
        self.geometry(f"{ancho_teclado}x{alto_teclado}+{x_pos}+{y_pos}")
        self.config(bg="grey")

        # Crear un frame principal que ocupe todo el espacio
        self.frame_principal = tk.Frame(self, bg="#EF9480")
        self.frame_principal.pack(fill="both", expand=True)
        self.entry = entry
        self.es_indice = es_indice 
        # Campo de texto para mostrar el número ingresado
        self.entry_display = tk.Entry(self.frame_principal, font=("Helvetica", 14), textvariable=self.entry, state="readonly",bg="black", fg="#000000", width=20)
        self.entry_display.grid(row=0, column=0, columnspan=3, padx=140, pady=10, sticky="ew")

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
                button = tk.Button(self.frame_botones, text=boton, font=("Helvetica", 14), width=5, height=2,command=lambda b=boton: self.agregar_caracter(b),bg="#837e7e", fg="#000000")  # Fondo blanco, texto negro
                button.grid(row=i, column=j, padx=5, pady=5, sticky="nsew")

        # Asegurar que todas las filas y columnas tengan el mismo tamaño
        for i in range(len(botones)):
            self.frame_botones.grid_rowconfigure(i, weight=1, uniform="row")  # Mismo tamaño para todas las filas
        for j in range(len(botones[0])):
            self.frame_botones.grid_columnconfigure(j, weight=1, uniform="col")  # Mismo tamaño para todas las columnas

        boton_enter = tk.Button(self.frame_principal, text="Confirmar", font=("Helvetica", 14), width=10, height=2,command=self.guardar,bg="red", fg="#FFFFFF", bd=7)
        boton_enter.grid(row=2, column=0, columnspan=3, pady=(10, 20))

        # Configurar el peso de las filas y columnas para centrar los botones
        self.frame_principal.grid_rowconfigure(1, weight=1)  # Centrar verticalmente
        self.frame_principal.grid_columnconfigure(0, weight=1)  # Centrar horizontalmente

    def agregar_caracter(self, caracter):
        """Agrega el caracter al campo de texto"""
        current_text = self.entry.get()
        
        if caracter == 'Borrar':
            self.entry.delete(0, tk.END)  # Elimina todo el texto
        else:
            # Si el caracter es '%' y estamos en un campo "Día", no lo permitimos
            if caracter == '%' and not self.es_indice:
                return  # No permitir el '%' en el campo Día
            if len(current_text) < 15:  # Limitar a 15 caracteres
                self.entry.insert(tk.END, caracter)  # Inserta el nuevo texto al final

    def guardar(self):
        """Forzar la adición de '%' en el campo Índice si no está presente"""
        current_text = self.entry.get()

        # Verificar que el campo no esté vacío
        if current_text:
            # Si es el campo "Índice" y no tiene el símbolo '%', lo agregamos
            if self.es_indice and not current_text.endswith('%'):
                current_text += '%'  # Forzamos la adición del '%'

            # Ahora podemos insertar el valor (con o sin % según corresponda)
            self.entry.delete(0, tk.END)  # Limpiar el texto actual
            self.entry.insert(0, current_text)  # Insertar el valor con el '%' si es necesario

            mostrar_mensaje(self, "Resultado", f"Valor guardado: {self.entry.get()}", tipo="info")
        else:
            mostrar_mensaje(self, "Error", "El valor está vacío.", tipo="error")

        self.destroy()  # Cerrar el teclado después de guardar

    def cerrar_teclado(self):
        """Cerrar el teclado"""
        self.destroy()