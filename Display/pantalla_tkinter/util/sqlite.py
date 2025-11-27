import sqlite3 as sqlite
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'comederos.db')

def get_connection():
    return sqlite.connect(DB_PATH)

def crearTablas():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute (
        """CREATE TABLE IF NOT EXISTS animal(
            idanimal INTEGER PRIMARY KEY AUTOINCREMENT,
            intervalo INTEGER,
            pesoTotal FLOAT,
            cantidadDosis INTEGER,
            tirarAgua BLOB,
            descripcion TEXT,
            caravana TEXT,
            numeroInterno INTEGER,
            fechaInseminacion DATE,
            IdIndiceCorporal INTEGER,
            idTipoCurva INTEGER,
            corral INTEGER,
            FOREIGN KEY (IdIndiceCorporal) REFERENCES indice_corporal(idIndiceCorporal),
            FOREIGN KEY (idTipoCurva) REFERENCES tipo_curva(idTipoCurva)
            )"""
        )
    
    cursor.execute (
         """CREATE TABLE IF NOT EXISTS indice_corporal(
            idIndiceCorporal INTEGER PRIMARY KEY AUTOINCREMENT,
            descripcion TEXT,
            corporal INTEGER
            )"""
        )
    
    cursor.execute (
         """CREATE TABLE IF NOT EXISTS tipo_curva(
            idTipoCurva INTEGER PRIMARY KEY AUTOINCREMENT,
            descripcion TEXT
            )"""
    )

    cursor.execute (
         """CREATE TABLE IF NOT EXISTS datos_curva(
            idDatosCurva INTEGER PRIMARY KEY AUTOINCREMENT,
            dia INTEGER,
            indice INTEGER,
            idTipoCurva INTEGER,
            FOREIGN KEY (idTipoCurva) REFERENCES tipo_curva(idTipoCurva)
            )"""  
    )

    cursor.execute(
         """CREATE TABLE IF NOT EXISTS configuracion(
            idConfiguracion INTEGER PRIMARY KEY AUTOINCREMENT,
            calibracionMotor INTEGER,
            calibracionAgua INTEGER,
            caravanaDesconocida FLOAT,
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
         usuario TEXT,
         contrasenia TEXT,
         nombreWifi TEXT,
         contraseniaWifi TEXT
         )"""
    )

    cursor.execute(
         """CREATE TABLE IF NOT EXISTS estacion(
         idEstacion INTEGER PRIMARY KEY AUTOINCREMENT,
         descripcion TEXT,
         direccion INTEGER DEFAULT 0
         )"""
    )

    # Asegura siempre 10 estaciones (1..10)
    for i in range(1, 11):
        cursor.execute(
            "SELECT 1 FROM estacion WHERE direccion = ? LIMIT 1",
            (i,)
        )
        existe = cursor.fetchone()
        if existe is None:
            cursor.execute(
                "INSERT INTO estacion (descripcion, direccion) VALUES (?, ?)",
                (f"Estacion {i}", i)
            )
    
    # Trigger: máximo 17 segmentos por cada curva (idTipoCurva)
    cursor.execute("""
    CREATE TRIGGER IF NOT EXISTS limitar_segmentos_por_curva
    BEFORE INSERT ON datos_curva
    WHEN (
        SELECT COUNT(*) FROM datos_curva
        WHERE idTipoCurva = NEW.idTipoCurva
    ) >= 17
    BEGIN
        SELECT RAISE(ABORT, 'Maximo 17 segmentos por curva');
    END;
    """)
    
    
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS tipo_alarma(
            idTipoAlarma INTEGER PRIMARY KEY AUTOINCREMENT,
            descripcion TEXT NOT NULL
        )"""
    )

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS alarma(
            idAlarma INTEGER PRIMARY KEY AUTOINCREMENT,
            fechaHora TEXT NOT NULL,
            corral INTEGER,
            numeroInterno INTEGER,
            caravana TEXT,
            idTipoAlarma INTEGER,
            FOREIGN KEY (idTipoAlarma) REFERENCES tipo_alarma(idTipoAlarma)
        )"""
    )

    
    cursor.execute("SELECT COUNT(*) FROM tipo_alarma")
    cant_tipos = cursor.fetchone()[0]
    if cant_tipos == 0:
        cursor.executemany(
            "INSERT INTO tipo_alarma (descripcion) VALUES (?)",
            [
                ("Animal desconocido",),
                ("Dieta no cumplida",),
                ("Falla conexión",),
            ]
        )

    # DATOS DE PRUEBA SOLO SI LA TABLA ALARMA ESTÁ VACÍA
    cursor.execute("SELECT COUNT(*) FROM alarma")
    cantidad = cursor.fetchone()[0]
    if cantidad == 0:
        cursor.executemany(
            """
            INSERT INTO alarma (fechaHora, corral, numeroInterno, caravana, idTipoAlarma)
            VALUES (?, ?, ?, ?, ?)
            """,
            [
                ("19/02/25 10:30", 1, 56, "123456789", 1),
                ("20/02/25 12:00", 2, 6, "345676532", 2),
                ("21/02/25 10:30", 1, 0, "0", 3),
                ("21/02/25 12:00", 2, 2, "345676532", 2),
            ]
        )

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS lectura(
            idLectura INTEGER PRIMARY KEY AUTOINCREMENT,
            caravana TEXT NOT NULL,
            corral INTEGER NOT NULL,
            fecha TEXT NOT NULL,
            peso REAL NOT NULL
        )"""
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


def insertarAlarma(fechaHora: str, descripcion: str, corral: str,
                   numeroInterno: int, caravana: str):
    tipoAlarma = _get_or_create_tipo_alarma(descripcion)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO alarma (fechaHora, corral, numeroInterno, caravana, idTipoAlarma)
        VALUES (?, ?, ?, ?, ?)
        """,
        (fechaHora, corral, numeroInterno, caravana, tipoAlarma),
    )
    conn.commit()
    conn.close()


def obtenerAlarmas():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT a.idAlarma, a.fechaHora, t.descripcion, a.corral, a.numeroInterno, a.caravana
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
                VALUES (?, ?, ?)
                """,
                (dia, indice_val, id_tipo_curva)
            )

        conn.commit()
        return True, None

    except Exception as e:
        conn.rollback()
        return False, f"Error al guardar curva en SQLite: {e}"

    finally:
        conn.close()

def obtenerAnimalesPorCorral(corral: int): #Listado para datos.py
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """SELECT caravana,
             numeroInterno,
             fechaInseminacion,
             pesoTotal,
             cantidadDosis,
             intervalo
        FROM animal
        WHERE corral = ?
        ORDER BY numeroInterno
        """,
        (corral,)
    )
    filas = cur.fetchall()
    conn.close()
    return filas

def obtenerEstaciones():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """SELECT idEstacion, descripcion, direccion
        FROM estacion
        ORDER BY idEstacion"""
    )
    filas = cur.fetchall()
    conn.close()
    return filas


def actualizarDireccionEstacion(id_estacion: int, direccion: int | None):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE estacion SET direccion = ? WHERE idEstacion = ?",
        (direccion, id_estacion)
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
   # Devuelve {caravana: fechaInseminacion} desde la tabla animal. Se usa para calcular el día de ciclo.
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
