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

def sincronizar_animales_todos_los_corrales(ser, splash=None):
    print("Iniciando sincronización masiva de corrales (TAREA 30)...")
    for corral_id in range(1, 11):
        try:
            filas_animal = db_local.obtenerAnimalesPorCorral(corral_id)
            if not filas_animal:
                continue
            
            lista_am = []
            curva_map = {"Ascendente": 0, "Constante": 1, "Descendente": 2, "Forma V": 3}
            indice_map = {"Gorda": 0, "Normal": 1, "Flaca": 2}

            for a in filas_animal:
                caravana = a[0]
                ins_str = a[2]
                dieta = db_local.obtener_dieta_completa_por_caravana(caravana)
                
                curva_int = 1
                indice_int = 1
                peso_int = 0
                dosis_int = 0
                intervalo_int = 0
                agua_int = 0
                
                if dieta:
                    cur_str = dieta.get("tipo_curva", "Constante")
                    curva_int = curva_map.get(cur_str, 1)
                    ind_str = dieta.get("indice_corporal", "Normal")
                    indice_int = indice_map.get(ind_str, 1)
                    
                    peso_int = int(dieta.get("peso_total", 0) * 10)
                    dosis_int = int(dieta.get("cantidad_dosis", 0))
                    intervalo_int = int(dieta.get("intervalo", 0))
                    agua_int = 1 if dieta.get("agua", False) else 0

                fecha_ts = "946695600"
                if ins_str:
                    try:
                        if str(ins_str).isdigit():
                            fecha_ts = str(ins_str)
                        else:
                            dt = datetime.strptime(str(ins_str), "%Y-%m-%d")
                            fecha_ts = str(int(dt.timestamp()))
                    except:
                        pass
                
                animal_data = {
                    "caravana": caravana,
                    "inseminacion": int(fecha_ts),
                    "agua": agua_int,
                    "peso": peso_int,
                    "dosis": dosis_int,
                    "intervalo": intervalo_int,
                    "curva": curva_int,
                    "indice": indice_int
                }
                lista_am.append(animal_data)
                
            payload = {"tarea": 30, "corral": corral_id, "animales": lista_am}
            jstr = json.dumps(payload)
            crc = 0xFFFF
            for b in jstr.encode('utf-8'):
                crc ^= b
                for _ in range(8):
                    if crc & 1:
                        crc = (crc >> 1) ^ 0xA001
                    else:
                        crc >>= 1
            mensaje = f"<<<{jstr}>>>|CRC:{crc:04X}"
            
            print(f"Enviando Sync Corral {corral_id} ({len(lista_am)} animales)...")
            for reintento in range(3):
                ser.reset_input_buffer()
                ser.write(mensaje.encode('utf-8'))
                t_fin = time.time() + 1.5
                exito = False
                while time.time() < t_fin:
                    if ser.in_waiting:
                        resp = ser.readline().decode('utf-8', errors='ignore').strip()
                        if "OK" in resp or "RECEIVED" in resp:
                            exito = True
                            break
                    time.sleep(0.05)
                if exito:
                    break
            time.sleep(0.2)
            if splash:
                # El porcentaje va de 75% a 95% (un rango de 20%)
                prog = 75 + (corral_id / 10) * 20
                splash.set_progress(prog, f"Sincronizando Corral {corral_id}...")
                splash.update()
        except Exception as e:
            print(f"Error sincronizando corral {corral_id}: {e}")


from forms.form_splash import SplashScreen

# ============================================================
#   MAIN
# ============================================================
if __name__ == "__main__":
    splash = SplashScreen()
    splash.set_progress(10, "Abriendo puerto serial...")

    try:
        ser = serial.Serial("/dev/serial0", 9600, timeout=1)  # Agregamos timeout para no quedar bloqueados forever
        print("Puerto serial abierto")
    except Exception as e:
        print(f"Error abriendo serial: {e}")
        # En caso de error crítico igual intentamos seguir o mostrar error
        
    splash.set_progress(20, "Esperando respuesta del equipo (Timestamp)...")

    timestamp = ""
    recibiendo = False
    start_wait = time.time()
    
    # --- Leer timestamp desde ESP32 ---
    # Ponemos un límite de tiempo por si el ESP32 no manda nada, no quedar colgados
    while True:
        splash.update()
        if ser.in_waiting:
            byte = ser.read(1).decode(errors="ignore")
            if byte == "<":
                timestamp = ""
                recibiendo = True
            elif byte == ">" and recibiendo:
                break
            elif recibiendo:
                timestamp += byte
        
        # Timeout de 60 segundos para el timestamp inicial
        if time.time() - start_wait > 60:
            print("ERROR: No se recibió respuesta del controlador en 60 segundos.")
            splash.show_error("ERROR en controlador.\n\nPor favor reinicie el sistema.")
            # La línea de arriba bloquea con mainloop, así que el código de abajo no se ejecutará mai

    splash.set_progress(40, "Sincronizando reloj del sistema...")
    timestamp = timestamp.strip().replace("\0", "")
    if re.match(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$", timestamp):
        try:
            subprocess.run(["sudo", "date", "-s", timestamp], check=True)
        except subprocess.CalledProcessError:
            pass

    splash.set_progress(50, "Enviando configuración inicial...")
    try:
        enviar_config_desde_sqlite_por_ser(ser)
    except Exception as e:
        print("Error al enviar config desde SQLite:", e)

    splash.set_progress(65, "Confirmando conexión...")
    ser.reset_input_buffer()
    msjOK = {"OK": 1}
    mensaje_ok = '<<<' + json.dumps(msjOK) + '>>>'
    try:
        ser.write(mensaje_ok.encode('utf-8'))
    except Exception as e:
        print("Error enviando OK:", e)

    splash.set_progress(75, "Sincronizando animales (Tarea 30)...")
    try:
        sincronizar_animales_todos_los_corrales(ser, splash=splash)
    except Exception as e:
        print("Fallo critico en sincronización inicial:", e)

    splash.set_progress(95, "Iniciando interfaz gráfica...")
    db_local.crearTablas()
    
    # Cerramos splash y arrancamos App principal
    splash.destroy()
    
    App = MasterPanel(ser=ser)
    App.mainloop()
