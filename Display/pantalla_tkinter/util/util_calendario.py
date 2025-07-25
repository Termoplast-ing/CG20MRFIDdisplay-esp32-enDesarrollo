import tkinter as tk
from tkcalendar import Calendar
from tkinter import Toplevel

def seleccionar_fecha(parent, variable_fecha):
    """Función para mostrar un calendario y seleccionar una fecha"""
    # Crear una ventana emergente para seleccionar la fecha
    fecha_window = Toplevel(parent)
    fecha_window.title("Seleccionar Fecha")
    fecha_window.geometry("480x480")
    fecha_window.config(bg="#EF9480", bd=4, relief="solid")
    fecha_window.overrideredirect(True)
    
    # Centrar la ventana en la pantalla
    screen_width = parent.winfo_screenwidth()
    screen_height = parent.winfo_screenheight()
    position_top = int(screen_height / 2 - 180)  # Para centrar verticalmente
    position_left = int(screen_width / 2 - 240)  # Para centrar horizontalmente
    fecha_window.geometry(f"480x360+{position_left}+{position_top}")  # Establecer la posición centrada

    fecha_window.config(bg="#EF9480")
    # Crear el calendario en la ventana
    calendar = Calendar(fecha_window, selectmode='day', date_pattern='yyyy-mm-dd',font="Helvetica 16", locale='es_ES')
    calendar.pack(padx=0, pady=0,expand=True)

    def guardar_fecha():
        """Guardar la fecha seleccionada y actualizar la variable StringVar"""
        fecha = calendar.get_date()  # Obtener la fecha seleccionada
        variable_fecha.set(fecha)  # Actualizar la variable StringVar con la fecha seleccionada
        fecha_window.destroy()  

    # Crear un botón de confirmar con las características que mencionaste
    boton_confirmar = tk.Button(fecha_window, text="Confirmar", font=("Helvetica", 16),
                                command=guardar_fecha, bg="red", fg="#ffffff", bd=7)
    boton_confirmar.pack(side=tk.BOTTOM, padx=10, pady=10)

    # Mostrar la ventana para seleccionar la fecha
    fecha_window.grab_set()  # Capturar eventos solo para esta ventana
    
    