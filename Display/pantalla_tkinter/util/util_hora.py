import tkinter as tk
from tkinter import ttk
import util.util_ventana as util_ventana

def seleccionar_hora(parent, variable_hora):
    """Función para abrir una ventana emergente y seleccionar la hora"""
    # Crear una ventana emergente para seleccionar la hora
    hora_window = tk.Toplevel(parent)
    hora_window.title("Seleccionar Hora")
    hora_window.geometry("480x350+200+200")  # Tamaño ajustado para la ventana
    hora_window.config(bg="#706f6f", bd=4, relief="solid")
    hora_window.overrideredirect(True)

    # Centrar la ventana en la pantalla
    util_ventana.centrar_ventana(hora_window, 480, 250)
    hora_window.grab_set()

    # Frame para los selectores de hora y minutos
    frame_selectores = tk.Frame(hora_window, bg='#bdb9b9')
    frame_selectores.pack(side=tk.TOP, fill="x", pady=20)

    # Crear un Label para "Hora:"
    label_hora = tk.Label(frame_selectores, text="Hora:", font=("Helvetica", 14), bg='#bdb9b9', fg="white")
    label_hora.pack(side=tk.LEFT, padx=10, pady=10)

    # Crear un Combobox para las horas (0-23)
    combo_horas = ttk.Combobox(frame_selectores, values=[f"{i:02d}" for i in range(24)], font=("Helvetica", 14), state="readonly")
    combo_horas.set("00")  # Valor predeterminado
    combo_horas.pack(side=tk.LEFT, padx=30, pady=10)

    # Crear un Frame separado para los minutos
    frame_minutos = tk.Frame(hora_window, bg='#bdb9b9')
    frame_minutos.pack(side=tk.TOP, fill="x", pady=10)

    # Crear un Label para "Minutos:"
    label_minutos = tk.Label(frame_minutos, text="Minutos:", font=("Helvetica", 14), bg='#bdb9b9', fg="white")
    label_minutos.pack(side=tk.LEFT, padx=10, pady=10)

    # Crear un Combobox para los minutos (0-59)
    combo_minutos = ttk.Combobox(frame_minutos, values=[f"{i:02d}" for i in range(60)], font=("Helvetica", 14), state="readonly")
    combo_minutos.set("00")  # Valor predeterminado
    combo_minutos.pack(side=tk.LEFT, padx=5, pady=10)

    # Botón para confirmar la selección de la hora
    boton_confirmar = tk.Button(hora_window, text="Guardar", font=("Helvetica", 14),
                                command=lambda: guardar_hora(hora_window, combo_horas, combo_minutos, variable_hora), bg="red", fg="#ffffff", bd=7)
    boton_confirmar.pack(side=tk.BOTTOM, padx=10, pady=20)

def guardar_hora(ventana, combo_horas, combo_minutos, variable_hora):
    """Función para guardar la hora seleccionada y cerrar la ventana"""
    hora = combo_horas.get()
    minutos = combo_minutos.get()
    variable_hora.set(f"{hora}:{minutos}")  # Actualizar la variable con la hora seleccionada
    ventana.destroy()  # Cerrar la ventana