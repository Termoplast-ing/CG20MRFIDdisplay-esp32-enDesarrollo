import serial
import subprocess
from forms.form_master import MasterPanel
import re
import datetime
from datetime import datetime
import json
import os
import time
import fcntl
import sys
import sqlite3 as sql
from util import sqlite as db_local
import tkinter as tk
import traceback
import tkinter as tk


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
        curvas_list = db_local.cargarCurvas()
        
        # Selección modificables (filtrando los nombres por defecto de las fijas)
        nombres_fijas = ["curva1", "curva2", "curva3"]
        modificables = [
            c for c in curvas_list
            if c.get("nombre", "").strip().lower() not in nombres_fijas
        ]

        # Primero cargamos hasta dos curvas modificables si existen
        for i in range(min(2, len(modificables))):
            curvas_final[i] = {
                "nombre": modificables[i]["nombre"],
                "segmentos": modificables[i]["segmentos"]
            }
    except Exception as e:
        print("Warning: error cargando curvas desde SQLite:", e)

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
        ser.reset_input_buffer() # Limpiar cualquier timestamp residual
        ser.write(mensaje.encode('utf-8'))
        time.sleep(1.5) # Aumentar un poco el margen para configs grandes
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
                t_fin = time.time() + 2.0 # Más tiempo para la respuesta
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
_lock_fd = None

def asegurar_instancia_unica():
    """Usa fcntl para asegurar que solo una instancia del programa corra a la vez."""
    global _lock_fd
    lock_file = "/tmp/comederos_app.lock"
    try:
        _lock_fd = open(lock_file, "w")
        fcntl.lockf(_lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except (IOError, OSError):
        print("ALERTA: Ya existe una instancia en ejecución. Saliendo automáticamente para evitar conflictos.")
        sys.exit(0)

if __name__ == "__main__":
    # Ruta absoluta para almacenamiento de logs en Raspberry Pi
    LOG_FILE = "/home/cg20mrfid/Desktop/pantalla_tkinter/error_inicio.log"
    try:
        asegurar_instancia_unica()
        splash = SplashScreen()
        splash.set_progress(10, "Abriendo puerto serial...")

        ser = None
        try:
            ser = serial.Serial("/dev/serial0", 9600, timeout=1) 
            if ser:
                ser.reset_input_buffer() 
                print("Puerto serial abierto y buffer limpiado")
        except Exception as e:
            print(f"Error abriendo serial: {e}")
            ser = None
            
        splash.set_progress(20, "Esperando respuesta del equipo (Timestamp)...")

        timestamp = ""
        recibiendo = False
        start_wait = time.time()
        
        # Variables para depuración de basura
        buffer_debug = []
        
        while True:
            try:
                splash.update()
            except tk.TclError:
                sys.exit(0)
            
            # Leer bloques grandes para vaciar rápido el serial
            if ser and ser.in_waiting:
                try:
                    bloque = ser.read(ser.in_waiting).decode(errors="ignore")
                    if len(buffer_debug) < 1000:
                        buffer_debug.append(bloque)
                        
                    for char in bloque:
                        if char == "<":
                            timestamp = ""
                            recibiendo = True
                        elif char == ">" and recibiendo:
                            ts_v = timestamp.strip()
                            # Regex más flexible por si hay algún espacio extra
                            if re.match(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", ts_v):
                                print(f"¡Timestamp válido recibido!: {ts_v}")
                                break
                            else:
                                print(f"Ignorando mensaje malformado entre <>: {ts_v}")
                                recibiendo = False
                                timestamp = ""
                        elif recibiendo:
                            timestamp += char
                    else:
                        # No encontramos el '>' en este bloque, seguimos
                        continue
                    # Si el break del for se activó, salimos del while
                    break
                except Exception as e:
                    print(f"Error procesando bloque serial: {e}")
            else:
                time.sleep(0.05)
            
            if time.time() - start_wait > 30 or ser is None:
                if ser is None:
                    error_msg = "ERROR CRÍTICO: Sin conexión (Puerto Serie). Revise y Reinicie."
                else:
                    error_msg = "ERROR CRÍTICO: Controlador no responde. Revise y Reinicie."
                    log_dump = "".join(buffer_debug)
                    if not log_dump:
                        log_dump = "[SILENCIO TOTAL - No se recibió ni un solo byte]"
                    
                    print(f"DEBUG: Grabando dump de diagnóstico ({len(log_dump)} bytes)...")
                    try:
                        with open(LOG_FILE, "a") as f:
                            f.write(f"\n--- DIAGNÓSTICO DE INICIO ({datetime.now()}) ---\n")
                            f.write(f"Estado del puerto: {ser.is_open if ser else 'CERRADO'}\n")
                            f.write(f"Datos capturados: {log_dump}\n")
                            f.write(f"--- FIN DIAGNÓSTICO ---\n")
                        print("DEBUG: Log de diagnóstico escrito.")
                    except Exception as le:
                        print(f"ERROR: No se pudo escribir el log: {le}")
                
                splash.set_progress(100, error_msg)
                while True:
                    try:
                        splash.update()
                        time.sleep(0.1)
                    except tk.TclError:
                        sys.exit(0)

        splash.set_progress(40, "Sincronizando reloj del sistema...")
        timestamp = timestamp.strip().replace("\0", "")
        if timestamp and re.match(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$", timestamp):
            try:
                subprocess.run(["sudo", "date", "-s", timestamp], check=True)
                print(f"Reloj sincronizado con ESP32: {timestamp}")
            except subprocess.CalledProcessError:
                print("No se pudo cambiar la fecha del sistema.")
        else:
            print("Sincronización de reloj omitida o formato inválido.")

        splash.set_progress(50, "Enviando configuración inicial...")
        enviar_config_desde_sqlite_por_ser(ser)

        splash.set_progress(65, "Confirmando conexión con el equipo...")
        ser.reset_input_buffer()
        msjOK = {"OK": 1}
        mensaje_ok = '<<<' + json.dumps(msjOK) + '>>>'
        
        confirmado = False
        for intento in range(5):
            try:
                ser.write(mensaje_ok.encode('utf-8'))
                t_fin = time.time() + 2.0
                while time.time() < t_fin:
                    if ser.in_waiting:
                        linea = ser.readline().decode('utf-8', errors='ignore').strip()
                        if "OK_RECEIVED" in linea:
                            confirmado = True
                            break
                    time.sleep(0.1)
                if confirmado: break
            except: pass
        
        if not confirmado:
            print("ADVERTENCIA: No se recibió confirmación final del ESP32.")

        splash.set_progress(75, "Sincronizando animales (Tarea 30)...")
        sincronizar_animales_todos_los_corrales(ser, splash=splash)

        splash.set_progress(95, "Iniciando interfaz gráfica...")
        db_local.crearTablas()
        
        splash.destroy()
        
        App = MasterPanel(ser=ser)
        App.mainloop()

    except Exception as e:
        # LOG DE ERROR CRÍTICO PARA EL USUARIO
        error_info = f"\nFECHA: {datetime.now()}\nERROR: {str(e)}\n{traceback.format_exc()}\n"
        with open(LOG_FILE, "a") as f:
            f.write(error_info)
        print(f"ERROR CRITICO EN EL MAIN: {e}")
        
        # Intentar mostrar el error en el Splash si sigue vivo
        try:
            if 'splash' in locals() and splash.winfo_exists():
                error_msg_ui = f"ERROR DETECTADO:\n{str(e)[:100]}...\nRevise error_inicio.log"
                splash.set_progress(100, error_msg_ui)
                while True:
                    splash.update()
                    time.sleep(0.1)
        except:
            pass
        sys.exit(1)
