import json
import os

# Ruta del archivo JSON
ARCHIVO_JSON = "datos_animales.json"

def cargar_datos():
    """Carga los datos desde el archivo JSON."""
    if os.path.exists(ARCHIVO_JSON):
        with open(ARCHIVO_JSON, "r") as archivo:
            datos = json.load(archivo)
            # Asegurarse de que cada animal tenga 5 valores
            for corral, animales in datos.items():
                for i, animal in enumerate(animales):
                    if len(animal) < 9:  # Si faltan un valores
                        animal.extend([""] * (9 - len(animal)))  # Agrega cadenas vacías o valores predeterminados
            return datos
    return {
        'Corral 1': [],
        'Corral 2': [],
        'Corral 3': [],
        'Corral 4': [],
        'Corral 5': [],
        'Corral 6': [],
        'Corral 7': [],
        'Corral 8': [],
        'Corral 9': [],
        'Corral 10': []
    }

def guardar_datos(datos):
    """Guarda los datos en el archivo JSON."""
    print(f"Guardando datos: {datos}")  # Verifica los datos que se están guardando
    with open(ARCHIVO_JSON, "w") as archivo:
        json.dump(datos, archivo, indent=4)