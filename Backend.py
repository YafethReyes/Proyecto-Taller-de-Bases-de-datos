import mysql.connector
import hashlib
import os
from dotenv import load_dotenv
from datetime import date

# Leemos los datos secretos del archivo .env
load_dotenv()
CLAVE = os.getenv("CLAVE_AES")


def conectar():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"))


def hashear_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def validar_login(username, password):
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT ID_USUARIO, USERNAME, ID_ROL FROM USUARIOS WHERE USERNAME = %s AND PASSWORD_HASH = %s",
                   (username, hashear_password(password)))
    usuario = cursor.fetchone()
    conexion.close()
    return usuario


# ---------- USUARIOS ----------

def obtener_usuarios(id_rol):
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    if id_rol == 1:  # El administrador ve los datos desencriptados
        cursor.execute("""SELECT ID_USUARIO, USERNAME, ID_ROL, NOMBRE, CORREO,
            CAST(AES_DECRYPT(TELEFONO_ENC, %s) AS CHAR) AS TELEFONO,
            CAST(AES_DECRYPT(CURP_ENC, %s) AS CHAR) AS CURP,
            CAST(AES_DECRYPT(DIRECCION_ENC, %s) AS CHAR) AS DIRECCION
            FROM USUARIOS""", (CLAVE, CLAVE, CLAVE))
    else:  # El empleado usa la vista segura
        cursor.execute("SELECT ID_USUARIO, USERNAME, NOMBRE, CORREO, '***' AS TELEFONO, '***' AS CURP, '***' AS DIRECCION FROM VISTA_USUARIOS_EMPLEADO")
    resultados = cursor.fetchall()
    conexion.close()
    return resultados


def agregar_usuario(username, pwd, nombre, correo, telefono, curp, direccion, id_rol):
    puesto = "Administrador" if id_rol == 1 else "Empleado"
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""INSERT INTO USUARIOS
        (USERNAME, PASSWORD_HASH, ID_ROL, NOMBRE, APELLIDO_PATERNO, CORREO, FECHA_NACIMIENTO, GENERO, PUESTO, FECHA_CONTRATACION, TELEFONO_ENC, CURP_ENC, DIRECCION_ENC)
        VALUES (%s, %s, %s, %s, 'Sin Apellido', %s, '2000-01-01', 'O', %s, %s,
        AES_ENCRYPT(%s, %s), AES_ENCRYPT(%s, %s), AES_ENCRYPT(%s, %s))""",
                   (username, hashear_password(pwd), id_rol, nombre, correo, puesto, date.today(),
                    telefono, CLAVE, curp, CLAVE, direccion, CLAVE))
    conexion.commit()
    conexion.close()


def editar_usuario(id_usuario, nombre, correo, telefono, curp, direccion, id_rol, nueva_pwd):
    puesto = "Administrador" if id_rol == 1 else "Empleado"
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""UPDATE USUARIOS SET NOMBRE = %s, CORREO = %s, ID_ROL = %s, PUESTO = %s,
        TELEFONO_ENC = AES_ENCRYPT(%s, %s), CURP_ENC = AES_ENCRYPT(%s, %s), DIRECCION_ENC = AES_ENCRYPT(%s, %s)
        WHERE ID_USUARIO = %s""",
                   (nombre, correo, id_rol, puesto, telefono, CLAVE, curp, CLAVE, direccion, CLAVE, id_usuario))
    # La contraseña solo se cambia si escribieron una nueva
    if nueva_pwd != "":
        cursor.execute("UPDATE USUARIOS SET PASSWORD_HASH = %s WHERE ID_USUARIO = %s",
                       (hashear_password(nueva_pwd), id_usuario))
    conexion.commit()
    conexion.close()


def eliminar_usuario(id_usuario):
    conexion = conectar()
    cursor = conexion.cursor()
    try:
        cursor.execute("DELETE FROM USUARIOS WHERE ID_USUARIO = %s", (id_usuario,))
        conexion.commit()
        resultado = True
    except mysql.connector.IntegrityError:
        resultado = False  # tiene animales publicados
    conexion.close()
    return resultado


# ---------- ANIMALES ----------

def obtener_animales():
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT ID_ANIMAL, NOMBRE, ESPECIE, SEXO, EDAD_MESES, TAMANO, ESTADO, DESCRIPCION FROM ANIMALES")
    resultados = cursor.fetchall()
    conexion.close()
    return resultados


def agregar_animal(nombre, especie, edad, sexo, tamano, descripcion, estado, id_usuario):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""INSERT INTO ANIMALES
        (NOMBRE, ESPECIE, EDAD_MESES, SEXO, TAMANO, DESCRIPCION, ESTADO, FECHA_INGRESO, PUBLICADO_POR)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                   (nombre, especie, int(edad), sexo, tamano, descripcion, estado, date.today(), id_usuario))
    conexion.commit()
    conexion.close()