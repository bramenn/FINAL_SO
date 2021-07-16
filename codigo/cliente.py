from time import sleep
from pyngrok import ngrok
import json, os, socket
from threading import Thread
CARPETA = ""
ID_CLIENTE = ""
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
    global ID_CLIENTE, CARPETA
    if ID_CLIENTE == "":
        id_uss = input("Ingrese el id del cliente: ")
        ID_CLIENTE = id_uss
    else:
        id_uss = ID_CLIENTE
    if CARPETA == "":
        nombre_carpeta = input("Ingrese el nombre de la capeta: ")
        CARPETA = nombre_carpeta
    else:
        nombre_carpeta = CARPETA
    return [id_uss, nombre_carpeta]


def ListarCarpeta():
    ficheros = os.listdir(CARPETA)
    return ficheros


def leer_fichero(nombre_carpeta, nombre_fichero):
    fd = open(nombre_carpeta + "/" + nombre_fichero, "r")
    contenido = fd.read()
    return contenido

def eliminar_ficheros(ficheros):
    for fichero in ficheros:
        os.remove(CARPETA+"/"+fichero)
    return f"FICHERO ELIMINADO CORRECTAMENTE DEL USUARIO {ID_CLIENTE}"
    
"""
{
  "peticion":"GET",
  "tipo": "creacion_c",
  "id_cliente": "123",
  "ficheros": ["fichero_1","fichero_2","fichero_3"]
}
"""
# PETICIONES DE SALIDA CLIENTE
def HTTP_salientes(id_cliente, data, peticion, tipo, id_cliente_el):
    mensaje = {}
    if peticion == "POST":
        if tipo == "creacion_c":
            ficheros = data
            mensaje = {
                "peticion": peticion,
                "tipo": tipo,
                "id_cliente": id_cliente,
                "ficheros": ficheros,
            }
        if tipo == "eliminar_f":
            fichero = data
            mensaje = {
                "peticion": peticion,
                "tipo": tipo,
                "id_cliente": id_cliente,
                "id_cliente_el": id_cliente_el,
                "fichero": fichero,
            }
        if tipo == "sincro":
            fichero = data
            mensaje = {
                "peticion": peticion,
                "tipo": tipo,
                "id_cliente": ID_CLIENTE,
                "id_cliente_el": id_cliente_el,
                "ficheros": fichero,
            }
    if peticion == "GET":
        if tipo == "ver_f":
            nombre_fichero = data
            mensaje = {
                "peticion": peticion,
                "tipo": tipo,
                "id_cliente": id_cliente,
                "nombre_fichero": nombre_fichero,
                "id_cliente_ver": id_cliente_el,
            }
        if tipo == "ver_clientes":
            mensaje = {
                "peticion": peticion,
                "tipo": tipo,
                "id_cliente": id_cliente,
            }
        if tipo == "notificacion_LISTAR_F":
            ficheros = data
            mensaje = {
                "peticion": peticion,
                "tipo": tipo,
                "id_cliente": id_cliente,
                "id_cliente_ver": id_cliente_el,
            }

    JSON = json.dumps(mensaje)
    return JSON


def HTTP_entrantes(HTTP):
    global CARPETA
    try:
        if HTTP["peticion"] == "POST":
            if HTTP["tipo"] == "notificacion_OK":  # SE REVISA SI EL CLIENTE YA EXISTE
                contenido = HTTP["contenido"]
                print("Respuesta del servidor: {}".format(contenido))
            if HTTP["tipo"] == "notificacion_FAIL":  # SE REVISA SI EL CLIENTE YA EXISTE
                contenido = HTTP["contenido"]
                print("Respuesta del servidor: {}".format(contenido))
            if HTTP["tipo"] == "eliminar_ficheros":  # SE REVISA SI EL CLIENTE YA EXISTE
                contenido = HTTP["contenido"]
                contenido = eliminar_ficheros(contenido)
                print("Respuesta del servidor: {}".format(contenido))
        elif HTTP["peticion"] == "GET":
            if HTTP["tipo"] == "notificacion_LISTAR_FICHs":
                contenido = ListarCarpeta()
                return HTTP_salientes(id_cliente="", data=contenido, peticion="POST", tipo="sincro", id_cliente_el="")
        else:
            print(f"PETICION NO ENCONTRADA: {HTTP}")
    except SyntaxError as e:
        print(e, "ESTE ERROR FUE RECIBIENDO UNA HTTP")


def agregar_contenido_fichero(ficheros):
    global CARPETA
    fichs = []
    for fichero in ficheros:
        f = open(CARPETA + "/" + fichero, "r")
        contenido = f.read()
        fichs.append({fichero: contenido})
    return fichs


########################################################################
def actu_regis():
    data_cli = InfoCliente()
    ficheros = ListarCarpeta()
    ficheros = agregar_contenido_fichero(ficheros)

    return [data_cli[0], ficheros]


def listar_ficheros():
    id_cli_search = input("Ingrese el ID del cliente: ")

    return [id_cli_search, ""]


def solitud_ver_f():

    id_cliente_ver = input("Ingrese el ID del cliente al que le quiere listar los ficheros: ")
    fichero = input("Ingrese archivo que quiere visualizar: ")

    return [id_cliente_ver, fichero]


def eliminar_f():
    id_cliente_el = input("Ingrese el ID del cliente al cual le quiere eliminar un archivo: ")
    fichero_el = input("Ingrese archivo que quiere eliminar: ")
    return [id_cliente_el, fichero_el]


def menu():
    print("------------------------------")
    print("------------ MENU ------------")
    print("1- Registrarse o actulizarse")
    print("2- Listar ficheros de algun cliente")
    print("3- Ver contenido de un fichero")
    print("4- Eliminar un fichero")
    print("5- Listar a todos los clientes")
    print("0- Salir")
    op = input("Ingrese la opcion: ")
    lista = []
    if op == "1":
        lista = actu_regis()
        if lista:
            lista.append("POST")
            lista.append("creacion_c")
    elif op == "2":
        id_cliente = input("Ingrese su id: ")
        lista_aux = listar_ficheros()
        lista.append(id_cliente)
        lista.append(lista_aux[1])
        lista.append("GET")
        lista.append("notificacion_LISTAR_F")
        lista.append(lista_aux[0])
    elif op == "3":
        id_cliente = input("Ingrese su id: ")
        lista_aux = solitud_ver_f()
        lista.append(id_cliente)
        lista.append(lista_aux[1])
        lista.append("GET")
        lista.append("ver_f")
        lista.append(lista_aux[0])
    elif op == "4":
        id_cliente = input("Ingrese su id: ")
        lista_aux = eliminar_f()
        lista.append(id_cliente)
        lista.append(lista_aux[1])
        lista.append("POST")
        lista.append("eliminar_f")
        lista.append(lista_aux[0])
    elif op == "5":
        lista = ["", ""]
        lista.append("GET")
        lista.append("ver_clientes")
    elif op == "0":
        pass
    else:
        print("Opcion incorrecta {}".format(op))
        return
    return lista


# if __name__ == "__main__":

#     while True:
#         mi_socket = socket.socket()
#         mi_socket.connect(host, port)

#         data = menu()
#         if data:
#             res = HTTP_salientes(data[0], data[1], data[2], data[3])

#         mi_socket.send(res.encode("ascii"))
#         pet = mi_socket.recv(2048)
#         pet = pet.decode("ascii")
#         HTTP_entrantes(pet)
#         mi_socket.close()

def recibir(mi_socket):
    while True:
        pet = mi_socket.recv(100000)
        pet = pet.decode("ascii")
        pet = eval(pet)
        HTTP_entrantes(pet)
        if pet["tipo"]=="notificacion_LISTAR_FICHs":
            a = HTTP_entrantes(pet)
            mi_socket.send(a.encode("ascii"))
            # print(a)
        
        
def enviar(mi_socket, contenido):
        mi_socket.send(res.encode("ascii"))

    
if __name__ == "__main__":
    host = "localhost"
    port = 8000
    mi_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (host, port)
    mi_socket.connect(server_address)
    hilo = Thread(target=recibir, args=[mi_socket])
    hilo.start()
    while True:
        # Create a TCP socket

        # Connect to the server with the socket via our ngrok tunnel
        data = menu()
        if data:
            if len(data) > 4:
                id_cliente_el = data[4]
            else:
                id_cliente_el = ""
            res = HTTP_salientes(
                id_cliente=data[0],
                data=data[1],
                peticion=data[2],
                tipo=data[3],
                id_cliente_el=id_cliente_el,
            )
            enviar(mi_socket=mi_socket, contenido= res)
        else:
            print("ERRORRRRRRR")

