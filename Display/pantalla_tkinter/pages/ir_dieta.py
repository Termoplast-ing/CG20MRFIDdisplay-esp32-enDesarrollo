import tkinter as tk
from tkinter import ttk
from util.util_json import cargar_datos, guardar_datos
from util.util_ventana import centrar_ventana 
from util.util_mensaje import mostrar_mensaje 
import util.util_ventana as util_ventana
import json
from datetime import datetime

class ir_dietaWindow(tk.Toplevel):
    def __init__(self, master, datos_seleccionados,callback_volver,uart):
        super().__init__(master)
        self.overrideredirect(True)
        self.uart= uart
        self.geometry("480x800")
        self.config(bg="#EF9480")
        self.resizable(False, False)
        centrar_ventana(self, 480, 800)
        self.mensaje_actual = None
        self.grab_set()

        # Guardar los datos seleccionados
        self.datos_seleccionados = datos_seleccionados
        self.callback_volver = callback_volver
        

        # Cargar datos desde el archivo JSON
        datos = cargar_datos()

        # Verificar si los datos seleccionados ya tienen un estado de "Agua"
        self.var_agua = tk.IntVar()
        for caravana, inseminacion in datos_seleccionados:
            for corral, animales in datos.items():
                for animal in animales:
                    if animal[0] == caravana and animal[1] == inseminacion:
                        if len(animal) > 2:  # Si ya tiene un estado de "Agua"
                            self.var_agua.set(animal[2])
                        break

        # Crear un frame para el logo en la parte superior
        self.frame_logo = tk.Frame(self, bg='#EF9480', height=100)
        self.frame_logo.pack(side=tk.TOP, fill="x",pady=22)
        self.crear_logo(self.frame_logo)

        # Crear un frame para el selector de tipo de curva
        self.frame_selector = tk.Frame(self, bg='#EF9480', height=50)
        self.frame_selector.pack(side=tk.TOP, fill="x", pady=5)
        self.crear_selector_curva(self.frame_selector)

        # Crear un frame para el selector de indice corporal
        self.frame_indice = tk.Frame(self, bg='#EF9480', height=50)
        self.frame_indice.pack(side=tk.TOP, fill="x", pady=5)
        self.crear_indice_corporal(self.frame_indice)

        # Crear un frame para el slider de peso
        self.frame_peso = tk.Frame(self, bg='#EF9480', height=50)
        self.frame_peso.pack(side=tk.TOP, fill="x", pady=20)
        self.crear_slider_peso(self.frame_peso)

        # Crear un frame para la cantidad de dosis
        self.frame_dosis = tk.Frame(self, bg='#EF9480', height=50)
        self.frame_dosis.pack(side=tk.TOP, fill="x", pady=10)
        self.crear_frame_dosis(self.frame_dosis)  

        # Crear un frame para el intervalo de dosis
        self.frame_intervalo = tk.Frame(self, bg='#EF9480', height=50)
        self.frame_intervalo.pack(side=tk.TOP, fill="x", pady=10)
        self.crear_frame_intervalo(self.frame_intervalo)  

        # Crear un frame para el checkbox del agua
        self.frame_agua = tk.Frame(self, bg="#EF9480")
        self.frame_agua.pack(fill="both", padx=20, pady=20)
        self.crear_checkbox_agua()

        # Crear un frame para los botones de abajo
        self.frame_botones = tk.Frame(self, bg="#EF9480", height=120)
        self.frame_botones.pack(side=tk.BOTTOM, fill="x",pady=20,expand=True)
        
        # Botón para volver a la ventana de gestión animal
        boton_atras = tk.Button(self.frame_botones, text="<< Atrás", font=("Helvetica", 16), command=self.cerrar_ventana, bg="red", fg="#ffffff", bd=7)
        boton_atras.pack(side=tk.LEFT, padx=10, pady=10)

        # Botón para guardar los cambios y volver a la ventana principal
        boton_guardar = tk.Button(self.frame_botones, text="Guardar", font=("Helvetica", 16), command=self.guardar_y_volver, bg="red", fg="#ffffff", bd=7)
        boton_guardar.pack(side=tk.RIGHT, padx=10, pady=10)

    def crear_logo(self, frame):
        """Función para crear y ubicar el logo en un frame dado"""
        label = tk.Label(frame, image=self.master.logo, bg='#EF9480')
        label.place(relx=0.5, rely=0.5, anchor="center")

    def crear_selector_curva(self, frame):
        """Función para crear y ubicar el selector de tipo de curva en un frame dado"""
        tipos_curva = ['Gorda', 'Flaca', 'Mediana', 'Enferma']  # Los tipos de curvas disponibles
        label_curva = tk.Label(frame, text="Tipo de Curva:", font=("Helvetica", 14), bg='#EF9480', fg="black")
        label_curva.pack(side=tk.LEFT, padx=20)

        # Crear el selector de tipo de curva
        self.selector_curva = ttk.Combobox(frame, values=tipos_curva, font=("Helvetica", 12), state="readonly")
        self.selector_curva.set(tipos_curva[0])  # Establecer valor predeterminado
        self.selector_curva.pack(side=tk.LEFT, padx=17)

    def crear_indice_corporal(self, frame):
        """Función para crear y ubicar el selector de índice corporal en un frame dado"""
        indice_corporal = ['Bajo (50%)', 'Normal (100%)', 'Alto (200%)']  # Los índices corporales disponibles
        label_indice = tk.Label(frame, text="Índice Corporal:", font=("Helvetica", 14), bg='#EF9480', fg="black")
        label_indice.pack(side=tk.LEFT, padx=21)

        # Crear el selector de índice corporal
        self.selector_indice = ttk.Combobox(frame, values=indice_corporal, font=("Helvetica", 12), state="readonly")
        self.selector_indice.set(indice_corporal[1])  # Establecer valor predeterminado
        self.selector_indice.pack(side=tk.LEFT, padx=5)

    def crear_slider_peso(self, frame):
        """Función para crear y ubicar el slider de peso en un frame dado"""
        # Crear un frame para el texto "Peso (Kg)" y el slider
        frame_superior = tk.Frame(frame, bg='#EF9480')
        frame_superior.pack(side=tk.TOP, pady=10, anchor='w')  # Colocar el frame superior en el frame principal

        # Crear el texto "Peso (Kg)" a la izquierda
        label_peso = tk.Label(frame_superior,text="Peso diario:",font=("Helvetica", 14),bg='#EF9480',fg="black")
        label_peso.pack(side=tk.LEFT, padx=21)  # Colocar el texto a la izquierda

        # Crear el slider de peso
        self.slider_peso = tk.Scale(frame_superior,from_=0,to=5,resolution=0.1,orient=tk.HORIZONTAL,bg='#c7baba',fg="black",troughcolor="grey",sliderrelief=tk.RAISED,highlightthickness=2,highlightbackground='#000000',font=("Helvetica", 12),length=240,command=self.actualizar_etiqueta_peso)
        self.slider_peso.pack(side=tk.LEFT, padx=10)  # Colocar el slider a la derecha del texto

        # Crear un frame para la etiqueta del valor
        frame_inferior = tk.Frame(frame, bg='#EF9480')
        frame_inferior.pack(side=tk.TOP, pady=5)  # Colocar el frame inferior en el frame principal

        # Crear una etiqueta para mostrar el valor con unidades
        self.label_peso = tk.Label(frame_inferior,text="0.0 Kg",font=("Helvetica", 14),bg='#EF9480',fg="black")
        self.label_peso.pack(side=tk.TOP)  # Colocar la etiqueta debajo del slider

    def actualizar_etiqueta_peso(self, valor):
        """Función para actualizar la etiqueta de peso en función del valor del slider"""
        self.label_peso.config(text=f"{float(valor):.1f} kg")

    def crear_frame_dosis(self, frame):
        """Función para crear y ubicar los botones para la cantidad de dosis"""
        # Crear un frame superior para mostrar el texto "Cant/Dosis"
        frame_superior = tk.Frame(frame, bg='#EF9480')
        frame_superior.pack(side=tk.TOP, pady=10, anchor='w')

        # Etiqueta de "Cant/Dosis"
        label_dosis = tk.Label(frame_superior,text="Cantidad/Dosis: ",font=("Helvetica", 14),bg='#EF9480',fg="black")
        label_dosis.pack(side=tk.LEFT, padx=20)

        # Variable para manejar la cantidad de dosis
        self.var_dosis = tk.IntVar(value=1)  # Valor inicial de dosis en 1

        # Botón para decrementar la cantidad de dosis
        boton_menos = tk.Button(frame_superior,text="-",font=("Helvetica", 12),command=self.decrementar_dosis,bg="#FF6F61",fg="white",bd=5)
        boton_menos.pack(side=tk.LEFT, padx=10)

        # Etiqueta para mostrar la cantidad de dosis
        self.label_dosis = tk.Label(frame_superior,textvariable=self.var_dosis,font=("Helvetica", 14),bg='#EF9480',fg="black")
        self.label_dosis.pack(side=tk.LEFT, padx=30)

        # Botón para incrementar la cantidad de dosis
        boton_mas = tk.Button(frame_superior,text="+",font=("Helvetica", 12),command=self.incrementar_dosis,bg="#FF6F61",fg="white",bd=5)
        boton_mas.pack(side=tk.LEFT, padx=10)

    def incrementar_dosis(self):
        """Función para incrementar la cantidad de dosis (1 a 5)"""
        if self.var_dosis.get() < 5:
            self.var_dosis.set(self.var_dosis.get() + 1)

    def decrementar_dosis(self):
        """Función para decrementar la cantidad de dosis (1 a 5)"""
        if self.var_dosis.get() > 1:
            self.var_dosis.set(self.var_dosis.get() - 1)

    def crear_frame_intervalo(self, frame):
        """Función para crear y ubicar los botones para el intervalo de dosis por hora"""
        # Crear un frame superior para mostrar el texto "Intervalo (+,-) por hora"
        frame_superior = tk.Frame(frame, bg='#EF9480')
        frame_superior.pack(side=tk.TOP, pady=10, anchor='w')

        # Etiqueta de "Intervalo (+,-) por hora"
        label_intervalo = tk.Label(frame_superior,text="Intervalo/Hora: ",font=("Helvetica", 14),bg='#EF9480',fg="black")
        label_intervalo.pack(side=tk.LEFT, padx=20)

        # Variable para manejar el intervalo de dosis
        self.var_intervalo = tk.IntVar(value=1)  # Valor inicial del intervalo en 1

        # Botón para decrementar el intervalo de dosis
        boton_menos_intervalo = tk.Button(frame_superior,text="-",font=("Helvetica", 12),command=self.decrementar_intervalo, bg="#FF6F61", fg="white",bd=5)
        boton_menos_intervalo.pack(side=tk.LEFT, padx=22)

        # Etiqueta para mostrar el intervalo de dosis
        self.label_intervalo = tk.Label(frame_superior,textvariable=self.var_intervalo,font=("Helvetica", 14),bg='#EF9480',fg="black")
        self.label_intervalo.pack(side=tk.LEFT, padx=19)

        # Botón para incrementar el intervalo de dosis
        boton_mas_intervalo = tk.Button(frame_superior,text="+",font=("Helvetica", 12),command=self.incrementar_intervalo, bg="#FF6F61", fg="white",bd=5)
        boton_mas_intervalo.pack(side=tk.LEFT, padx=20)

    def incrementar_intervalo(self):
        """Función para incrementar el intervalo de dosis (1 a 5)"""
        if self.var_intervalo.get() < 5:
            self.var_intervalo.set(self.var_intervalo.get() + 1)

    def decrementar_intervalo(self):
        """Función para decrementar el intervalo de dosis (1 a 5)"""
        if self.var_intervalo.get() > 1:
            self.var_intervalo.set(self.var_intervalo.get() - 1)

    def crear_checkbox_agua(self):
        """Función para crear el checkbox de 'Agua'"""
        # Crear un frame para contener los elementos
        frame_superior_agua = tk.Frame(self.frame_agua, bg="#EF9480")
        frame_superior_agua.pack(side=tk.TOP, pady=10, anchor='w')
        # Etiqueta con la palabra "Agregar/Agua"
        label_agua = tk.Label(frame_superior_agua, text="Agregar/Agua:", font=("Helvetica", 14), bg="#EF9480", fg="black")
        label_agua.pack(side=tk.LEFT, padx=0)

        # Crear el checkbox "Agua"
        self.var_agua = tk.IntVar()  # Variable para almacenar el estado del checkbox (0 o 1)
        self.check_agua = tk.Checkbutton(frame_superior_agua, variable=self.var_agua,bg="#EF9480",font=("Helvetica",26),highlightthickness=0,bd=0,selectcolor="#EF9480",relief="flat",activebackground="#EF9480")
        self.check_agua.pack(side=tk.LEFT, padx=111)

    def cerrar_ventana(self):
        """Cerrar la ventana de dieta"""
        self.grab_release()
        self.destroy()
        self.callback_volver()

    def mostrar_mensaje(self, titulo, texto, tipo="error"):
        """Muestra mensajes con el mismo estilo que en gestion_animal"""
        mostrar_mensaje(self, titulo, texto, tipo)
        # Esperar hasta que se presione OK
        self.wait_window(self.mensaje_actual)
      
    def guardar_y_volver(self):
        try:
            datos = cargar_datos()

            tipo_curva = self.selector_curva.get()
            indice_corporal = self.selector_indice.get()
            peso_float = float(self.slider_peso.get())
            peso = int(peso_float * 10)
            dosis = self.var_dosis.get()
            intervalo = self.var_intervalo.get()
            agua = self.var_agua.get()

            peso_por_dosis = peso
            if dosis > 1:
                peso_por_dosis = peso / dosis

            lista_animales = []

            for caravana, inseminacion in self.datos_seleccionados:
                for corral, animales in datos.items():
                    for i, animal in enumerate(animales):
                        if animal[0] == caravana and animal[2] == inseminacion:
                            datos[corral][i] = [
                                caravana,
                                animal[1],
                                inseminacion,
                                agua,
                                tipo_curva,
                                indice_corporal,
                                peso,
                                dosis,
                                intervalo
                            ]

                            animal_actualizado = datos[corral][i]
                            animal_json = {
                                "caravana": animal_actualizado[0],
                                #"interno": animal_actualizado[1],
                                "inseminacion": int(datetime.strptime(animal_actualizado[2], "%Y-%m-%d").timestamp()),
                                "agua": animal_actualizado[3],
                                "curva": animal_actualizado[4],
                                "indice": animal_actualizado[5],
                                "peso": animal_actualizado[6],
                                "dosis": animal_actualizado[7],
                                "intervalo": animal_actualizado[8]
                                }
                            lista_animales.append(animal_json)
                            break

            mensaje_json = json.dumps(lista_animales)
            try:
                self.uart.write((f"<<<{mensaje_json}>>>").encode('utf-8'))
                print("JSON enviado:", mensaje_json)
            except Exception as e:
                print("Error al enviar por UART:", e)

            guardar_datos(datos)
            self.mostrar_mensaje("Guardado", "Los cambios se han guardado correctamente!", "info")
            self.grab_release()
            self.destroy()
            self.callback_volver()

        except Exception as e:
            print(f"Error al guardar y volver: {e}")
            self.grab_release()
            self.mostrar_mensaje("Error", f"Ocurrió un error al guardar los cambios: {e}")
            self.destroy()
            self.callback_volver()
