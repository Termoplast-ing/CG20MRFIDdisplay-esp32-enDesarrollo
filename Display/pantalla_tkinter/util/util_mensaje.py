import tkinter as tk

def mostrar_mensaje(parent, titulo, texto, tipo="error", callback=None):

    # Configuración de colores (igual que en tu versión)
    color_fondo = "#FFFFFF"  # Fondo blanco
    color_texto = "#000000"  # Texto negro

    if tipo == "error":
        color_boton = "red"
        color_borde = "#FF0000"  # Rojo más intenso para el borde
    elif tipo == "info":
        color_boton = "#4CAF50"  # Verde
        color_borde = "#2E7D32"  # Verde oscuro
    elif tipo == "warning":
        color_boton = "#FF9800"  # Naranja
        color_borde = "#FF6D00"  # Naranja oscuro
    else:
        color_boton = "red"  # Por defecto rojo
        color_borde = "black"

        # Si el parent tiene mensaje_actual, lo destruimos primero
    if hasattr(parent, 'mensaje_actual') and parent.mensaje_actual:
        parent.mensaje_actual.destroy()

    # Crear la ventana de mensaje (inicialmente oculta)
    mensaje_actual = tk.Toplevel(parent)
    mensaje_actual.withdraw()  # Ocultar inicialmente
    mensaje_actual.configure(bg="black")  # Borde negro
    
    # Calcular posición primero
    parent.update_idletasks()
    x = parent.winfo_x() + (parent.winfo_width() - 480) // 2
    y = parent.winfo_y() + (parent.winfo_height() - 300) // 2
    mensaje_actual.geometry(f"480x300+{x}+{y}")
    
    # Ahora aplicar overrideredirect y mostrar
    mensaje_actual.overrideredirect(True)
    mensaje_actual.deiconify()  # Mostrar ventana
    
    # Frame interior con fondo blanco (mismos parámetros que tu versión)
    frame_interior = tk.Frame(mensaje_actual,bg=color_fondo,padx=40,pady=40)
    frame_interior.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)
    
    # Contenido del mensaje (idéntico a tu versión)
    tk.Label(frame_interior,text=texto,padx=20,pady=10,bg=color_fondo,fg=color_texto,font=("Helvetica", 14),wraplength=360).pack(pady=(10, 20))
    
    # Botón OK con mismo estilo
    def cerrar():
        mensaje_actual.destroy()
        if callback:
            callback()
            
    tk.Button(frame_interior,text="   OK   ",command=cerrar,bg="red",fg="#ffffff",font=("Helvetica", 14, "bold"),bd=3).pack(pady=(15, 0))
    
    mensaje_actual.grab_set()

    # Guardar referencia si es necesario
    if hasattr(parent, 'mensaje_actual'):
        parent.mensaje_actual = mensaje_actual
    