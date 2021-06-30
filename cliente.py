import json, os, socket


"""
CREACION
{
  "peticion":"POST",
  "tipo": "creacion_c",
  "id_cliente": "123",
  "ficheros": ["fichero_1","fichero_2","fichero_3"]
}

LEER ARCHIVOS
{
  "peticion":"GET",
  "tipo": "lectura_f",
  "id_cliente":"123",
  "nombre_fichero": "fichero.txt"
}
{
  "peticion":"POST",
  "tipo": "lectura_f",
  "id_cliente":"123",
  "nombre_fichero": "fichero.txt",
  "contenido":"dkjfgdfgsdkjfgkjasghdf"
}

ELIMINAR ARCHIVO
{
  "peticion":"DELETE",
  "tipo": "eliminar_f",
  "id_cliente":"123",
  "nombre_fichero":"fichero.txt"
}

NOTIFICACION
{
  "servidor":"POST",
  "tipo": "notificacion",
  "contenido":"ñlkhadshfkjasdhfh"
}
"""


def InfoCliente():
    id_uss = input("Ingrese el id del cliente: ")
    nombre_carpeta = input("Ingrese el nombre de la capeta: ")
    return [id_uss, nombre_carpeta]


def ListarCarpeta(nombre_carpeta):
    ficheros = os.listdir(nombre_carpeta)
    return ficheros


def leer_fichero(nombre_carpeta, nombre_fichero):
    fd = open(nombre_carpeta + "/" + nombre_fichero, "r")
    contenido = fd.read()
    return contenido


"""
{
  "peticion":"GET",
  "tipo": "creacion_c",
  "id_cliente": "123",
  "ficheros": ["fichero_1","fichero_2","fichero_3"]
}
"""
# PETICIONES DE SALIDA CLIENTE
def HTTP_salientes(id_cliente, data, peticion, tipo):
    if peticion == "POST":
        if tipo == "creacion_c":
            ficheros = data
            mensaje = {
                "peticion": peticion,
                "tipo": tipo,
                "id_cliente": id_cliente,
                "ficheros": ficheros,
            }
    if peticion == "GET":
        if tipo == "ver_f":
            nombre_fichero = data
            mensaje = {
                "peticion": peticion,
                "tipo": tipo,
                "id_cliente": id_cliente,
                "nombre_fichero": nombre_fichero,
            }
        if tipo == "notificacion_LISTAR_F":
            ficheros = data
            mensaje = {"peticion": peticion, "tipo": tipo, "id_cliente": id_cliente}

    JSON = json.dumps(mensaje)
    return JSON


def HTTP_entrantes(HTTP):
    try:
        HTTP = eval(HTTP)
        if HTTP["peticion"] == "POST":
            if HTTP["tipo"] == "notificacion_OK":  # SE REVISA SI EL CLIENTE YA EXISTE
                contenido = HTTP["contenido"]
                print("Respuesta del servidor: {}".format(contenido))
            if HTTP["tipo"] == "notificacion_FAIL":  # SE REVISA SI EL CLIENTE YA EXISTE
                contenido = HTTP["contenido"]
                print("Respuesta del servidor: {}".format(contenido))
        else:
            print("PETICION NO ENCONTRADA: {}".HTTP)
    except SyntaxError as e:
        print(e)


def agregar_contenido_fichero(ficheros, carpeta):
    fichs = []
    for fichero in ficheros:
        f = open(carpeta + "/" + fichero, "r")
        contenido = f.read()
        fichs.append({fichero: contenido})
    return fichs


########################################################################
def actu_regis():
    data_cli = InfoCliente()
    ficheros = ListarCarpeta(data_cli[1])
    ficheros = agregar_contenido_fichero(ficheros, data_cli[1])

    return [data_cli[0], ficheros]


def listar_ficheros():
    id_cli_search = input("Ingrese el ID del cliente: ")

    return [id_cli_search, ""]


def solitud_ver_f():

    id_cliente = input("Ingrese el ID del cliente: ")
    fichero = input("Ingrese archivo que quiere visualizar: ")

    return [id_cliente, fichero]
    
def eliminar_f():
    id_cliente = input("Ingrese el ID del cliente: ")
    fichero = input("Ingrese archivo que quiere eliminar: ")

def menu():
    print("------------------------------")
    print("------------ MENU ------------")
    print("1- Registrarse o actulizarse")
    print("2- Listar ficheros de algun cliente")
    print("3- Ver contenido de un fichero")
    print("4- Eliminar un fichero")
    print("0- Salir")
    op = input("Ingrese la opcion: ")
    if op == "1":
        lista = actu_regis()
        if lista:
            lista.append("POST")
            lista.append("creacion_c")
    elif op == "2":
        lista = listar_ficheros()
        if lista:
            lista.append("GET")
            lista.append("notificacion_LISTAR_F")
    elif op == "3":
        lista = solitud_ver_f()
        if lista:
            lista.append("GET")
            lista.append("ver_f")
    elif op == "4":
        lista = eliminar_f()
        if lista:
            lista.append("GET")
            lista.append("ver_f")
    elif op == "0":
        pass
    else:
        print("Opcion incorrecta {}".format(op))
        return
    return lista


if __name__ == "__main__":

    while True:
        mi_socket = socket.socket()
        mi_socket.connect(("localhost", 8000))

        data = menu()
        if data:
            res = HTTP_salientes(data[0], data[1], data[2], data[3])

        mi_socket.send(res.encode("ascii"))
        pet = mi_socket.recv(2048)
        pet = pet.decode("ascii")
        HTTP_entrantes(pet)
        mi_socket.close()
