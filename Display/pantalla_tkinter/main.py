import serial
import subprocess
from forms.form_master import MasterPanel
import re
import datetime
from datetime import datetime
import json
import os
import time

#def enviar_json(archivo_json):
#    with open(archivo_json, "r") as archivo:
#        contenido = archivo.read()
#    ser.write(contenido.encode())
#    ser.write(b'\n')
#    time.sleep(1)
def parcear_json_config(parsear):
        configuracion= json.loads(parsear)
        calibraciones=configuracion["calibraciones"]
        caravanas_libres=configuracion["caravanas_libres"]
        indice_corporal=configuracion["indice_corporal"]
        curvas_alimentacion=configuracion["curvas_alimentacion"]
         
        config_data = {
            "calibraciones": {
                "motor": calibraciones["motor"],
                "agua": calibraciones["agua"],
                "peso": calibraciones["peso"]
            },
            "caravanas_libres": caravanas_libres,
            "indice_corporal": {
                "tipo": indice_corporal["tipo"],
                "porcentaje": indice_corporal["porcentaje"]
            }
        }
        return(config_data)
        
def parcear_json_gestion(parsear):
        gestion= json.loads(parsear)
        
        
        corral1=gestion["Corral 1"]
    
        #corral2=gestion["Corral 2"]
        #corral3=gestion["Corral 3"]
        #corral4=gestion["Corral 4"]
        #corral5=gestion["Corral 5"]
        #corral6=gestion["Corral 6"]
        #corral7=gestion["Corral 7"]
        #corral8=gestion["Corral 8"]
        #corral9=gestion["Corral 9"]
        #corral10=gestion["Corral 10"]
        corral=[]
        if (len(corral1)==0) :
            animal={
            "caravana" : "",
            "inseminacion" : "",
            "agua": "",
            "curva":"",
            "indice":"",
            "peso": "",
            "dosis":"",
            "intervalo":""                   
            }
            corral.append(animal)
        else:
            for i in  range(len(corral1)):
                animal={
                "caravana" : corral1[i][0],
                "inseminacion" : int(datetime.strptime(corral1[i][2], "%Y-%m-%d").timestamp()),
                "agua": corral1[i][3],
                "curva":corral1[i][4],
                "indice":corral1[i][5],
                "peso": corral1[i][6],
                "dosis":corral1[i][7],
                "intervalo":corral1[i][8]                   
                }
                corral.append(animal)        
            
        return(corral)
        
def enviar_json_config(archivo_json):
    with open(archivo_json, "r") as archivo:
        contenido = archivo.read()
        time.sleep(2)
        configuracion=parcear_json_config(contenido)
        time.sleep(2)
        mensaje = '<<<' + json.dumps(configuracion) + '>>>'
        ser.write(mensaje.encode('utf-8'))
        time.sleep(1)

        respuesta = ser.readline().decode('utf-8').strip()
        print('ESP32 respondio:', respuesta)


def enviar_json_gestion(archivo_json):
    with open(archivo_json, "r") as archivo:
        contenido = archivo.read()
        time.sleep(2)
        gestion=parcear_json_gestion(contenido)
        print(gestion)
        mensaje = '<<<' + json.dumps(gestion) + '>>>'
        ser.write(mensaje.encode('utf-8'))
        time.sleep(1)
        respuesta = ser.readline().decode('utf-8').strip()
        print('ESP32 respondio:', respuesta)
    
    
print("Iniciando script..")
ser = serial.Serial("/dev/serial0", 9600, timeout=None)
print("Puerto serial abierto")

timestamp = ""
recibiendo = False
print("Esperando inicio de timestamp...")

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

#lo nuevo
print ("jueves")
enviar_json_config("config/configuracion_sistema.json")
#enviar_json("config/curvas.json")
print("llego la confi")
#enviar_json("datos_reales.json")
enviar_json_gestion("datos_animales.json")
print("llegaron los animales")
time.sleep(1)
print("paseGestion")
print("Confirmacion 'OK' enviada al ESP32")
print("Hora del sistema ahora:", datetime.now())
ser.reset_input_buffer()
msjOK={
    "OK":1
}
mensaje = '<<<' + json.dumps(msjOK) + '>>>'
ser.write(mensaje.encode('utf-8'))
#ser.write(b"OK")

App = MasterPanel()
App.mainloop()
