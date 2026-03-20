import sqlite3 as sqlite
import os
from typing import Optional

DB_PATH = os.path.join(os.path.dirname(__file__), 'comederos.db')


def get_connection():
    return sqlite.connect(DB_PATH, timeout=10)


def crearTablas():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS animal(
            idAnimal INTEGER PRIMARY KEY AUTOINCREMENT,
            caravana TEXT,
            numeroInterno INTEGER,
            fechaInseminacion TEXT,
            idCorral INTEGER,
            idDieta INTEGER,
            FOREIGN KEY(idCorral) REFERENCES corral(idCorral),
            FOREIGN KEY(idDieta) REFERENCES dieta(idDieta)
            )"""
    )

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS corral(
            idCorral INTEGER PRIMARY KEY AUTOINCREMENT,
            descripcion TEXT,
            direccion INTEGER)"""
    )

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS alarma(
            idAlarma INTEGER PRIMARY KEY AUTOINCREMENT,
            fechaHora TEXT,
            numeroInterno INTEGER,
            caravana TEXT,
            idCorral INTEGER,
            idTipoAlarma INTEGER,
            FOREIGN KEY(idCorral) REFERENCES corral(idCorral),
            FOREIGN KEY(idTipoAlarma) REFERENCES tipo_alarma(idTipoAlarma)
            )"""
    )

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS tipo_alarma(
            idTipoAlarma INTEGER PRIMARY KEY AUTOINCREMENT,
            descripcion TEXT
            )"""
    )

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS dieta(
            idDieta INTEGER PRIMARY KEY AUTOINCREMENT,
            descripcion TEXT,
            intervalo INTEGER,
            pesoTotal REAL,
            cantidadDosis INTEGER,
            tirarAgua BLOB,
            idIndiceCorporal INTEGER,
            idTipoCurva INTEGER,
            FOREIGN KEY(idIndiceCorporal) REFERENCES indice_corporal(idIndiceCorporal),
            FOREIGN KEY(idTipoCurva) REFERENCES tipo_curva(idTipoCurva)
            )"""
    )

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS indice_corporal(
            idIndiceCorporal INTEGER PRIMARY KEY AUTOINCREMENT,
            descripcion TEXT,
            corporal INTEGER
            )"""
    )

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS tipo_curva(
            idTipoCurva INTEGER PRIMARY KEY AUTOINCREMENT,
            descripcion TEXT
            )"""
    )

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS datos_curva(
            idDatosCurva INTEGER PRIMARY KEY AUTOINCREMENT,
            dia INTEGER,
            indice INTEGER,
            idTipoCurva INTEGER,
            FOREIGN KEY(idTipoCurva) REFERENCES tipo_curva(idTipoCurva)
            )"""
    )

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS configuracion(
            idConfiguracion INTEGER PRIMARY KEY AUTOINCREMENT,
            calibracionMotor INTEGER,
            calibracionAgua INTEGER,
            caravanaDesconocida REAL,
            caravanaLibre1 TEXT,
            caravanaLibre2 TEXT,
            caravanaLibre3 TEXT,
            caravanaLibre4 TEXT,
            caravanaLibre5 TEXT
            )"""
    )

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS usuario(
            idUsuario INTEGER PRIMARY KEY AUTOINCREMENT,
            nombreUsuario TEXT,
            contrasenia TEXT,
            nombreWifi TEXT,
            contraseniaWifi TEXT
            )"""
    )

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS lectura(
            idLectura INTEGER PRIMARY KEY AUTOINCREMENT,
            caravana TEXT,
            corral INTEGER,
            fecha TEXT,
            peso REAL
            )"""
    )       
    conn.commit()
    conn.close()


def obtenerConfiguracion():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """SELECT calibracionMotor,
                  calibracionAgua,
                  caravanaDesconocida,
                  caravanaLibre1,
                  caravanaLibre2,
                  caravanaLibre3,
                  caravanaLibre4,
                  caravanaLibre5
           FROM configuracion
           ORDER BY idConfiguracion DESC
           LIMIT 1"""
    )
    fila = cur.fetchone()
    conn.close()

    if fila is None:
        return 0, 0, 0.0, []

    cal_motor, cal_agua, car_desc, c1, c2, c3, c4, c5 = fila
    caravanas = [c for c in (c1, c2, c3, c4, c5) if c]
    return cal_motor or 0, cal_agua or 0, float(car_desc or 0.0), caravanas


def guardarConfiguracion(cal_motor: int,
                         cal_agua: int,
                         caravana_desc: float,
                         caravanas_libres: list[str]):
    conn = get_connection()
    cur = conn.cursor()

    car_list = list(caravanas_libres[:5]) + [None] * 5
    c1, c2, c3, c4, c5 = car_list[:5]

    cur.execute(
        "SELECT idConfiguracion FROM configuracion ORDER BY idConfiguracion DESC LIMIT 1"
    )
    fila = cur.fetchone()

    if fila:
        id_conf = fila[0]
        cur.execute(
            """UPDATE configuracion
               SET calibracionMotor = ?,
                   calibracionAgua = ?,
                   caravanaDesconocida = ?,
                   caravanaLibre1 = ?,
                   caravanaLibre2 = ?,
                   caravanaLibre3 = ?,
                   caravanaLibre4 = ?,
                   caravanaLibre5 = ?
               WHERE idConfiguracion = ?""",
            (cal_motor, cal_agua, caravana_desc,
             c1, c2, c3, c4, c5, id_conf)
        )
    else:
        cur.execute(
            """INSERT INTO configuracion
               (calibracionMotor, calibracionAgua, caravanaDesconocida,
                caravanaLibre1, caravanaLibre2, caravanaLibre3, caravanaLibre4, caravanaLibre5)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (cal_motor, cal_agua, caravana_desc,
             c1, c2, c3, c4, c5)
        )

    conn.commit()
    conn.close()


# Esto es la nueva consulta 02_02_2026:
def obtener_intervalo_y_ultima_lectura(caravana):
    conn = get_connection()
    cur = conn.cursor()
    # Buscamos el intervalo de la dieta del animal y su última lectura registrada
    query = """
        SELECT d.intervalo, 
               (SELECT MAX(CAST(l.fecha AS INT)) FROM lectura l WHERE l.caravana = a.caravana) as ultima_fecha
        FROM animal a
        JOIN dieta d ON a.idDieta = d.idDieta
        WHERE a.caravana = ?
    """
    cur.execute(query, (str(caravana),))
    res = cur.fetchone()
    conn.close()
    return res # Retorna (intervalo_horas, ultima_fecha_str)

def obtenerIndicesCorporales():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """SELECT idIndiceCorporal, descripcion, corporal
           FROM indice_corporal
           ORDER BY idIndiceCorporal"""
    )
    filas = cur.fetchall()
    conn.close()
    return filas


def insertarIndiceCorporal(descripcion: str, corporal: int) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO indice_corporal (descripcion, corporal) VALUES (?, ?)",
        (descripcion, corporal)
    )
    nuevo_id = cur.lastrowid
    conn.commit()
    conn.close()
    return nuevo_id


def eliminarIndiceCorporal(id_indice: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM indice_corporal WHERE idIndiceCorporal = ?",
        (id_indice,)
    )
    conn.commit()
    conn.close()


def _get_or_create_tipo_alarma(descripcion: str) -> int:
    """Devuelve idTipoAlarma para esa descripción; si no existe, lo crea."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT idTipoAlarma FROM tipo_alarma WHERE descripcion = ?",
        (descripcion,)
    )
    fila = cur.fetchone()

    if fila is not None:
        id_tipo = fila[0]
    else:
        cur.execute(
            "INSERT INTO tipo_alarma (descripcion) VALUES (?)",
            (descripcion,)
        )
        id_tipo = cur.lastrowid

    conn.commit()
    conn.close()
    return id_tipo


def insertarAlarma(fechaHora: str, descripcion: str, corral: int,
                   numeroInterno: int, caravana: str):
    tipoAlarma = _get_or_create_tipo_alarma(descripcion)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO alarma (fechaHora, numeroInterno, caravana, idCorral, idTipoAlarma)
        VALUES (?, ?, ?, ?, ?)
        """,
        (fechaHora, numeroInterno, caravana, corral, tipoAlarma),
    )
    conn.commit()
    conn.close()


def obtenerAlarmas():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT a.idAlarma,
                  a.fechaHora,
                  t.descripcion,
                  a.idCorral,
                  a.numeroInterno,
                  a.caravana
           FROM alarma a
           JOIN tipo_alarma t ON a.idTipoAlarma = t.idTipoAlarma
           ORDER BY a.idAlarma DESC
        """
    )
    filas = cursor.fetchall()
    conn.close()
    return filas



def borrarAlarmas():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM alarma")
    conn.commit()
    conn.close()


def cargarCurvas():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """SELECT tc.idTipoCurva,
               tc.descripcion,
               dc.dia,
               dc.indice
        FROM tipo_curva AS tc
        LEFT JOIN datos_curva AS dc
            ON dc.idTipoCurva = tc.idTipoCurva
        ORDER BY tc.idTipoCurva, dc.dia
        """
    )
    filas = cur.fetchall()
    conn.close()

    curvas = {}
    for id_tipo, nombre, dia, indice in filas:
        if id_tipo not in curvas:
            curvas[id_tipo] = {
                "id": id_tipo,
                "nombre": nombre,
                "segmentos": []
            }
        if dia is not None:
            curvas[id_tipo]["segmentos"].append({
                "dia": dia,
                "indice": indice
            })

    return list(curvas.values())


def obtenerCurvas():
    curvas_guardadas = cargarCurvas()
    nombres_defecto = ["ascendente", "constante", "descendente", "forma v"]

    curvas_nuevas = [
        c["nombre"]
        for c in curvas_guardadas
        if c["nombre"]
        and c["nombre"].strip().lower() not in nombres_defecto
    ]

    lista_final = ['']
    lista_final.extend(curvas_nuevas)
    lista_final.extend(["Ascendente", "Constante", "Descendente", "Forma V"])
    return lista_final


def existeCurva(nombre: str) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """SELECT 1
        FROM tipo_curva
        WHERE LOWER(descripcion) = LOWER(?)
        LIMIT 1
        """,
        (nombre.strip(),)
    )
    existe = cur.fetchone() is not None
    conn.close()
    return existe


def guardarCurva(nombre: str, segmentos: list):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT idTipoCurva FROM tipo_curva WHERE LOWER(descripcion) = LOWER(?)",
            (nombre.strip(),)
        )
        fila = cur.fetchone()

        if fila:
            id_tipo_curva = fila[0]
            # Borramos segmentos anteriores
            cur.execute(
                "DELETE FROM datos_curva WHERE idTipoCurva = ?",
                (id_tipo_curva,)
            )
        else:
            # Creamos nueva curva
            cur.execute(
                "INSERT INTO tipo_curva (descripcion) VALUES (?)",
                (nombre.strip(),)
            )
            id_tipo_curva = cur.lastrowid

        # Insertar segmentos
        for seg in segmentos:
            dia = seg["dia"]
            indice_str = str(seg["indice"]).replace('%', '').strip()
            indice_val = int(indice_str) if indice_str else 0

            cur.execute(
                """ INSERT INTO datos_curva (dia, indice, idTipoCurva)
                VALUES (?, ?, ?)""",
                (dia, indice_val, id_tipo_curva)
            )

        conn.commit()
        return True, None

    except Exception as e:
        conn.rollback()
        return False, f"Error al guardar curva en SQLite: {e}"

    finally:
        conn.close()

def obtenerAnimalesPorCorral(corral: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT caravana, numeroInterno, fechaInseminacion
        FROM animal
        WHERE idCorral = ?
        ORDER BY fechaInseminacion
    """,(corral,))
    filas = cur.fetchall()
    conn.close()
    return filas
              
#def obtenerAnimalesPorCorral(corral: int):
#    conn = get_connection()
#    cur = conn.cursor()
#    cur.execute(
#        """SELECT a.caravana,
#                  a.numeroInterno,
#                  a.fechaInseminacion,
#                  d.pesoTotal,
#                  d.cantidadDosis,
#                  
#           FROM animal a
#           LEFT JOIN dieta d ON a.idDieta = d.idDieta
#           WHERE a.idCorral = ?
#           ORDER BY a.fechaInseminacion
#        """,
#        (corral,)
#    )
#    filas = cur.fetchall()
#    conn.close()
#    return filas

#probamos esto 20_01  nueva prueba
#def obtenerAnimalesPorCorral(corral: int):
#    conn = get_connection()
#    cur = conn.cursor()
#    cur.execute("""
#        SELECT a.caravana,
#
#               a.numeroInterno,
#               a.fechaInseminacion,
#               d.pesoTotal,
#               d.cantidadDosis,
#               MAX(CASE WHEN l.fecha = date('now','-1 day') THEN l.peso END) AS ant,
#               MAX(CASE WHEN l.fecha = date('now','-2 day') THEN l.peso END) AS ant_1,
#               MAX(CASE WHEN l.fecha = date('now','-3 day') THEN l.peso END) AS ant_2
#        FROM animal a
#        LEFT JOIN dieta d ON a.idDieta = d.idDieta
#        LEFT JOIN lectura l ON l.caravana = .caravana
#        WHERE a.idCorral = ?
#        ORDER BY a.fechaInseminacion
#        """,
#        (corral,)
#    )
#    filas = cur.fetchall()
#    conn.close()
#    return filas

#esto es lo nuevo 27_01:
 
def obtenerAnimalesParaDatos(corral: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT a.caravana,
               a.numeroInterno,
               a.fechaInseminacion,
               d.pesoTotal,
               d.cantidadDosis
        FROM animal a
        LEFT JOIN dieta d ON a.idDieta = d.idDieta
        WHERE a.idCorral = ?
        ORDER BY a.fechaInseminacion
    """, (corral,))
    filas = cur.fetchall()
    conn.close()
    return filas

def obternerDosisReales():
    """
    Obtiene cuantas dosis ah recibido cada caravana desde la tabla lectura.
    Retorna: {'caravana': {'dosis_recibidas': X},...}
    """
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT caravana, COUNT(*) as dosis_recibidas
            FROM lectura
            GROUP BY caravana
        """)
        resultados = {}
        for row in cur.fetchall():
            caravana, count = row
            resultados[caravana] = {"dosis_recibidas": count}
        return resultados
    except Exception as e:
        print(f"Error en obtenerDosisReales: {e}")
        return {}
    finally:
        conn.close()

def obtenerCorrales():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """SELECT idCorral, descripcion, direccion
           FROM corral
           ORDER BY idCorral"""
    )
    filas = cur.fetchall()
    conn.close()
    return filas


def actualizarDireccionCorral(id_corral: int, direccion: Optional[int]):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE corral SET direccion = ? WHERE idCorral = ?",
        (direccion, id_corral)
    )
    conn.commit()
    conn.close()


def insertarLectura(caravana: str, corral: int, fecha: str, peso: float):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO lectura (caravana, corral, fecha, peso)
        VALUES (?, ?, ?, ?)""",
        (caravana, corral, fecha, peso)
    )
    conn.commit()
    conn.close()


def obtenerLecturas():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT corral, caravana, fecha, peso FROM lectura"
    )
    filas = cur.fetchall()
    conn.close()
    return filas


def obtenerFechasInseminacion():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """SELECT caravana, fechaInseminacion
           FROM animal
           WHERE caravana IS NOT NULL
             AND fechaInseminacion IS NOT NULL"""
    )
    filas = cur.fetchall()
    conn.close()
    return {car: fecha for car, fecha in filas}


def insertarAnimal(caravana: str,
                   numeroInterno: Optional[str],
                   fechaInseminacion: str,
                   corral: int):
    conn = get_connection()
    cur = conn.cursor()
    #try:
        #if numeroInterno is not None and str(numeroInterno).strip() != "":
         #   num_int = int(numeroInterno)
        #else:
        #    num_int = None

    cur.execute(
        """INSERT INTO animal (
                caravana,
                numeroInterno,
                fechaInseminacion,
                idCorral,
                idDieta               
            )
               VALUES (?, ?, ?, ?,1)""",
          (caravana, numeroInterno, fechaInseminacion, corral)
        )

    conn.commit()
    #finally:
    conn.close()



def eliminarAnimalesPorCorralYCaravanas(corral: int, caravanas: list[str]):
    if not caravanas:
        return
    conn = get_connection()
    cur = conn.cursor()
    try:
        for car in caravanas:
            cur.execute(
                "DELETE FROM animal WHERE idCorral = ? AND caravana = ?",
                (corral, car)
            )
        conn.commit()
    finally:
        conn.close()
    
def insertarDietaConfig(descripcion: Optional[str],
                        pesoTotal: float,
                        cantidadDosis: int,
                        intervalo: int,
                        tirarAgua: int) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO dieta (
               descripcion,
               intervalo,
               pesoTotal,
               cantidadDosis,
               tirarAgua,
               idIndiceCorporal,
               idTipoCurva
           )
           VALUES (?, ?, ?, ?, ?, NULL, NULL)""",
        (descripcion, intervalo, pesoTotal, cantidadDosis, tirarAgua)
    )
    nuevo_id = cur.lastrowid
    conn.commit()
    conn.close()
    return nuevo_id


def actualizarDietaPorCaravanaYFecha(caravana: str,
                                     fechaInseminacion: str,
                                     idDieta: int):
    conn = get_connection()
    cur = conn.cursor()
    #fecha_para_sqlite= fechaInseminacion
    #if "/" in fechaInseminacion:
    #    try:
    #        dia, mes, año = fechaInseminacion.split("/")
    #        fecha_para_sqlite = f"{año}-{mes}-{dia}"
    #    except:
    #        pass
    cur.execute(
        """UPDATE animal
           SET idDieta = ?
           WHERE caravana = ? AND fechaInseminacion = ?""",
        (idDieta, caravana, fechaInseminacion)
    )
    conn.commit()
    conn.close()


def actualizarFechaInseminacion(caravana: str, idCorral: int, nueva_fecha):
    """Actualiza la fecha de inseminación de un animal específico en un corral.
    La fecha se almacena como texto en formato YYYY-MM-DD.
    """
    conn = get_connection()
    cur = conn.cursor()
    nueva_str = str(nueva_fecha) if nueva_fecha is not None else None
    cur.execute(
        """UPDATE animal
           SET fechaInseminacion = ?
           WHERE caravana = ? AND idCorral = ?""",
        (nueva_str, caravana, idCorral)
    )
    conn.commit()
    conn.close()
def obtenerUsuarioPorNombre(nombreUsuario: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """SELECT idUsuario, nombreUsuario, contrasenia
           FROM usuario
           WHERE nombreUsuario = ?
           LIMIT 1""",
        (nombreUsuario,)
    )
    fila = cur.fetchone()
    conn.close()
    return fila


def crearUsuarioPorDefecto():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM usuario")
    (cant,) = cur.fetchone()

    if cant == 0:
        cur.execute(
            """INSERT INTO usuario
                   (nombreUsuario, contrasenia, nombreWifi, contraseniaWifi)
               VALUES (?, ?, NULL, NULL)""",
            ("admin", "1234")
        )
        conn.commit()

    conn.close()


def obtenerWifi():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """SELECT nombreWifi, contraseniaWifi
           FROM usuario
           ORDER BY idUsuario DESC
           LIMIT 1"""
    )
    fila = cur.fetchone()
    conn.close()

    if fila is None:
        return None, None

    return fila[0], fila[1]


def guardarWifi(nombreWifi: Optional[str], contraseniaWifi: Optional[str]):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT idUsuario FROM usuario ORDER BY idUsuario DESC LIMIT 1")
    fila = cur.fetchone()

    if fila:
        id_usuario = fila[0]
        cur.execute(
            """UPDATE usuario
               SET nombreWifi = ?, contraseniaWifi = ?
               WHERE idUsuario = ?""",
            (nombreWifi, contraseniaWifi, id_usuario)
        )
    else:
        cur.execute(
            """INSERT INTO usuario (nombreUsuario, contrasenia, nombreWifi, contraseniaWifi)
               VALUES (?, ?, ?, ?)""",
            (None, None, nombreWifi, contraseniaWifi)
        )

    conn.commit()
    conn.close()
    
def obtener_dieta_por_caravana(caravana):
    conn = get_connection()
    #conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT d.pesoTotal, d.cantidadDosis, d.intervalo
        FROM animal a
        JOIN dieta d ON a.idDieta = d.idDieta
        WHERE a.caravana = ?         
        LIMIT 1
    """, (caravana,))
    row = cursor.fetchone()
    conn.close()
    if row is None:
        return None
    return { 
        "pesoTotal": row[0],
        "cantidadDosis": row[1],
        "intervalo": row[2]
    }

def obtener_dieta_completa_por_caravana(caravana):
    """Obtiene toda la información de la dieta de un animal por su caravana."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT d.descripcion, d.pesoTotal, d.cantidadDosis, d.intervalo, d.tirarAgua
        FROM animal a
        JOIN dieta d ON a.idDieta = d.idDieta
        WHERE a.caravana = ?
        LIMIT 1
    """, (caravana,))
    row = cursor.fetchone()
    conn.close()
    if row is None:
        return None
    
    # Parsear la descripción para extraer tipo de curva e índice corporal
    descripcion = row[0] or ""
    tipo_curva = ""
    indice_corporal = ""
    
    if " - " in descripcion:
        partes = descripcion.split(" - ")
        if len(partes) >= 2:
            tipo_curva = partes[0]
            indice_corporal = partes[1]
    
    return {
        "descripcion": descripcion,
        "tipo_curva": tipo_curva,
        "indice_corporal": indice_corporal,
        "peso_total": row[1] / 10.0 if row[1] else 0,  # Convertir de décimas a kg
        "cantidad_dosis": row[2] or 0,
        "intervalo": row[3] or 0,
        "agua": bool(row[4]) if row[4] is not None else False
    }

#def EliminarTablas():
#    conn = get_connection()
#    cursor = conn.cursor()
    
#    cursor.execute("DROP TABLE IF EXISTS animal")
#    cursor.execute("DROP TABLE IF EXISTS corral")
#    cursor.execute("DROP TABLE IF EXISTS alarma")
#    cursor.execute("DROP TABLE IF EXISTS tipo_alarma")
#    cursor.execute("DROP TABLE IF EXISTS dieta")
#    cursor.execute("DROP TABLE IF EXISTS indice_corporal")
#    cursor.execute("DROP TABLE IF EXISTS tipo_curva")
#    cursor.execute("DROP TABLE IF EXISTS datos_curva")
#    cursor.execute("DROP TABLE IF EXISTS configuracion")
#    cursor.execute("DROP TABLE IF EXISTS usuario")
#    cursor.execute("DROP TABLE IF EXISTS lectura")
#    cursor.execute("DROP TABLE IF EXISTS estacion")
    
#    conn.commit()
#    conn.close()
