
def centrar_ventana(ventana,aplicacion_ancho, aplicacion_alto):
    pantalla_ancho = ventana.winfo_screenwidth()
    pantalla_alto = ventana.winfo_screenheight()
    x = int ((pantalla_ancho/2) - (aplicacion_ancho/2))
    y = int ((pantalla_alto/2) - (aplicacion_alto/2))
    ventana.geometry(f'{aplicacion_ancho}x{aplicacion_alto}+{x}+{y}')
    ventana.resizable(False, False)  # Evitar que la ventana sea redimensionable