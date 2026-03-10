import serial
import subprocess
from forms.form_master import MasterPanel
import re
import datetime
from datetime import datetime
import json
import os
import time
import sqlite3 as sql
from util import sqlite as db_local


# ============================================================
#   ARMADO DE CONFIG DESDE SQLITE
# ============================================================
def construir_config_desde_sqlite():
    """
    Construye la configuración que la ESP32 espera,
    leyendo desde tu base SQLite.
    """

    # --- Calibraciones / Caravanas ---
    try:
        motor, agua, caravana, caravanas_libres = db_local.obtenerConfiguracion()
    except Exception as e:
        print("Error leyendo configuración desde SQLite:", e)
        motor, agua, caravana, caravanas_libres = 0, 0, 0.0, ['']

    if not caravanas_libres:
        caravanas_libres = ['']

    indice_corporal = {
        "tipo": "",
        "porcentaje": ""
    }

    # --- Curvas ---
    curvas_final = [
        {"nombre": "", "segmentos": [{"dia": 0, "indice": "0%"} for _ in range(16)]}
        for _ in range(5)
    ]

    try:
        filas = db_local.cargarCurvas()     # puede traer 3 o 4 columnas
        curvas_map = {}

        for fila in filas:

            # Aceptar 3 o 4 columnas sin romper nada
            if len(fila) == 4:
                id_tipo, nombre, dia, indice = fila
            elif len(fila) == 3:
                id_tipo, nombre, dia = fila
                indice = 0
            else:
                continue  # evitamos romper el main

            if id_tipo not in curvas_map:
                curvas_map[id_tipo] = {
                    "id": id_tipo,
                    "nombre": nombre or "",
                    "segmentos": []
                }

            curvas_map[id_tipo]["segmentos"].append({
                "dia": dia,
                "indice": f"{indice}%"
            })

        curvas_list = list(curvas_map.values())

    except Exception as e:
        print("Warning: error cargando curvas desde SQLite:", e)
        curvas_list = []

    # --- Selección modificables ---
    nombres_defecto = ["curva1", "curva2", "curva3"]
    modificables = [
        c for c in curvas_list
        if c["nombre"].strip().lower() not in nombres_defecto
    ]

    # Primero cargamos hasta dos curvas modificables
    for i in range(min(2, len(modificables))):
        curvas_final[i] = {
            "nombre": modificables[i]["nombre"],
            "segmentos": modificables[i]["segmentos"]
        }

    # Luego cargamos las fijas (igual que tu UI)
    curvas_final[2] = {
        "nombre": "curva1",
        "segmentos": [{"dia": 1, "indice": "50%"}]
    }
    curvas_final[3] = {
        "nombre": "curva2",
        "segmentos": [
            {"dia": 1, "indice": "50%"},
            {"dia": 113, "indice": "100%"}
        ]
    }
    curvas_final[4] = {
        "nombre": "curva3",
        "segmentos": [
            {"dia": 1, "indice": "100%"},
            {"dia": 113, "indice": "50%"}
        ]
    }

    # --- JSON final ---
    config_data = {
        "calibraciones": {
            "motor": motor or 0,
            "agua": agua or 0,
            "peso": float(caravana or 0.0)
        },
        "caravanas_libres": caravanas_libres,
        "indice_corporal": indice_corporal,
        "curvas_alimentacion": curvas_final
    }

    return config_data


# ============================================================
#   ENVÍO POR UART
# ============================================================
def enviar_config_desde_sqlite_por_ser(ser):
    config = construir_config_desde_sqlite()
    mensaje = '<<<' + json.dumps(config) + '>>>'

    try:
        ser.write(mensaje.encode('utf-8'))
        time.sleep(1)
        respuesta = ser.readline().decode('utf-8').strip()
        print("ESP32 respondió:", respuesta)
    except Exception as e:
        print("Error enviando configuración por serial:", e)


# ============================================================
#   MAIN
# ============================================================
print("Iniciando script..")

ser = serial.Serial("/dev/serial0", 9600, timeout=None)
print("Puerto serial abierto")

timestamp = ""
recibiendo = False
print("Esperando inicio de timestamp...")


# --- Leer timestamp desde ESP32 ---
while True:
    byte = ser.read(1).decode(errors="ignore")
    print(f"Byte recibido: '{byte}'")
    if byte == "<":
        timestamp = ""
        recibiendo = True
        print("Delimitador inicial '<' recibido")
    elif byte == ">" and recibiendo:
        print("Delimitador final '>' recibido")
        break
    elif recibiendo:
        timestamp += byte
        print(f"Timestamp parcial: '{timestamp}'")


timestamp = timestamp.strip().replace("\0", "")

if re.match(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$", timestamp):
    try:
        subprocess.run(["sudo", "date", "-s", timestamp], check=True)
    except subprocess.CalledProcessError:
        pass


# ============================================================
#   Enviar CONFIG generado desde SQLite
# ============================================================
print("Enviando configuración (origen: SQLite)")
try:
    enviar_config_desde_sqlite_por_ser(ser)
except Exception as e:
    print("Error al enviar config desde SQLite:", e)


# ============================================================
#   Enviar OK al ESP32
# ============================================================
print("Confirmación 'OK' enviada al ESP32 (si procede)")
print("Hora del sistema ahora:", datetime.now())
ser.reset_input_buffer()

msjOK = {"OK": 1}
mensaje_ok = '<<<' + json.dumps(msjOK) + '>>>'

try:
    ser.write(mensaje_ok.encode('utf-8'))
except Exception as e:
    print("Error enviando OK:", e)


# ============================================================
#   Iniciar GUI (TKinter)
# ============================================================
db_local.crearTablas()
#db_local.EliminarTablas()
App = MasterPanel()
App.mainloop()
