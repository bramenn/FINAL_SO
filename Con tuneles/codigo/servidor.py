import json, socket
import threading
from threading import Thread
from time import sleep
from typing import Optional
from pyngrok import ngrok
from datetime import datetime
import time
import logging
def registrar_cliente(lista_clientes):
    f = open("clientes.txt", "w")
    for cliente in lista_clientes:
        f.write("-" + cliente)
    f.close()


def cargar_clientes():
    f = open("clientes.txt", "r+")
    clientes = f.read()
    lista_clientes = []
    if len(clientes) > 0:
        clientes.replace("\n", "")
        clientes = clientes.split("-")
        clientes = clientes[1:]
        lista_clientes = clientes
    return lista_clientes
    f.close()


def listar_ficheros(id_cliente):
    f = open(str(id_cliente) + ".txt", "r")
    data = f.read()
    data = json.loads(data)
    f.close()
    ficheros = []
    for fichero in data["ficheros"]:
        for key in fichero.keys():
            ficheros.append(key)

    return ficheros


def ver_f(id_cliente, nombre_fichero):
    f = open(str(id_cliente) + ".txt", "r")
    data = f.read()
    data = json.loads(data)
    f.close()
    for fichero in data["ficheros"]:
        for key in fichero.keys():
            if key == nombre_fichero:
                return fichero[key]
    return

    # return ficheros

def actualizar_ficheros(id_cliente: Optional[str], ficheros: Optional[list]):
        f = open(id_cliente+".txt", "w") 
        cliente = {"id_cliente": id_cliente, "ficheros": ficheros}
        cliente = json.dumps(cliente)
        f.write(cliente)
        f.close()


  
def eliminar_fichero(id_cliente_el, fichero):
    f = open(str(id_cliente_el) + ".txt", "r+")
    data_fichero = f.read()
    f.close()
    data_fichero = json.loads(data_fichero)
    contador = 0
    for fichero_ in data_fichero["ficheros"]:
        for key in fichero_.keys():
            if key == fichero + ".txt":
                data_fichero["ficheros"].pop(contador)
                id_cliente_f = id_cliente_el + ".txt"
                f = open(id_cliente_f, "w")
                cliente = {"id_cliente": id_cliente_el, "ficheros": data_fichero["ficheros"]}
                CLI = json.dumps(cliente)
                f.write(CLI)
                return f"El archivo {fichero} se elimino correctamente en la carpeta de  {id_cliente_el}"
            else:
                contador += 1
    return f"El archivo {fichero} no se encontro en la carpeta del cliente {id_cliente_el} y no se elimino"


# PETICIONES DE SALIDA
def HTTP_salientes(id_cliente, peticion, tipo, contenido):
    mensaje = ""
    if peticion == "POST":
        if tipo == "notificacion_OK":
            mensaje = {"peticion": peticion, "tipo": tipo, "contenido": contenido}
        if tipo == "notificacion_FAIL":
            mensaje = {"peticion": peticion, "tipo": tipo, "contenido": contenido}
        if tipo == "notificacion_LISTAR_F":
            mensaje = listar_ficheros(id_cliente)
        if tipo == "eliminar_ficheros":            
            mensaje = {"peticion": peticion, "tipo": tipo, "contenido": contenido, "id_cliente":id_cliente}
    elif peticion == "GET":
        if tipo == "notificacion_LISTAR_FICHs":
            mensaje = {"peticion": peticion, "tipo": tipo, "contenido": contenido}

    JSON = json.dumps(mensaje)
    return JSON


def HTTP_entrantes(HTTP, lista_clientes, contenido):
    if HTTP["peticion"] == "POST":
        if HTTP["tipo"] == "creacion_c" and not HTTP["id_cliente"] in lista_clientes:
            lista_clientes.append(HTTP["id_cliente"])
            registrar_cliente(lista_clientes)
            ficheros = HTTP["ficheros"]
            actualizar_ficheros(id_cliente=HTTP["id_cliente"], ficheros=ficheros)
            contenido = "Se creo el cliente correctamente {}".format(HTTP["id_cliente"])
            return HTTP_salientes(HTTP["id_cliente"], "POST", "notificacion_OK", contenido)
        elif (
            HTTP["tipo"] == "eliminar_f"
            and HTTP["id_cliente"] in lista_clientes
            and HTTP["id_cliente_el"] in lista_clientes
        ):
            contenido = eliminar_fichero(HTTP["id_cliente_el"], HTTP["fichero"])
            return HTTP_salientes(HTTP["id_cliente"], "POST", "notificacion_OK", contenido)
        elif HTTP["tipo"] == "sincro" and HTTP["id_cliente"] in lista_clientes:
            contenido = eliminar_fichero(HTTP["id_cliente_el"], HTTP["fichero"])
            return HTTP_salientes(HTTP["id_cliente"], "POST", "notificacion_OK", contenido)
        elif HTTP["tipo"] == "notificacion_OK" and HTTP["id_cliente"] in lista_clientes:
            contenido = eliminar_fichero(HTTP["id_cliente_el"], HTTP["fichero"])
            return HTTP_salientes(HTTP["id_cliente"], "POST", "notificacion_OK", contenido)
        else:
            actualizar_ficheros(id_cliente=HTTP["id_cliente"], ficheros=HTTP["ficheros"])
            contenido = "Se actualizo correctamente {}".format(HTTP["id_cliente"])
            return HTTP_salientes(HTTP["id_cliente"], "POST", "notificacion_OK", contenido)

    elif HTTP["peticion"] == "GET":
        hora =  time.strftime("%H:%M:%S")
        print(f"{hora} lista_clientes")
        if (
            HTTP["tipo"] == "notificacion_LISTAR_F"
            and HTTP["id_cliente"] in lista_clientes
            and HTTP["id_cliente_ver"] in lista_clientes
        ):
            ficheros = listar_ficheros(HTTP["id_cliente_ver"])
            contenido = "Los ficheros del cliente {} son: ".format(HTTP["id_cliente_ver"])
            for fichero in ficheros:
                contenido += "\n" + fichero
            return HTTP_salientes(HTTP["id_cliente"], "POST", "notificacion_OK", contenido)
        elif (
            HTTP["tipo"] == "ver_f"
            and HTTP["id_cliente"] in lista_clientes
            and HTTP["id_cliente_ver"] in lista_clientes
        ):
            nombre_fichero = HTTP["nombre_fichero"]
            res = ver_f(HTTP["id_cliente_ver"], nombre_fichero + ".txt")
            if res:
                contenido = "El contenido del fichero {} es:\n{}".format(nombre_fichero, res)
                return HTTP_salientes(HTTP["id_cliente_ver"], "POST", "notificacion_OK", contenido)
            else:
                contenido = "NO se encontro el fichero {} en el cliente {}".format(
                    nombre_fichero, HTTP["id_cliente_ver"]
                )
        elif HTTP["tipo"] == "ver_clientes":
            contenido = cargar_clientes()
            return HTTP_salientes("", "POST", "notificacion_OK", contenido)
        else:
            contenido = "NO se encontro el cliente {}".format(HTTP["id_cliente"])
        return HTTP_salientes("", "POST", "notificacion_FAIL", contenido)
    else:
        contenido = "NO se reconocio la peticion {}".format(HTTP)
        return HTTP_salientes("", "POST", "notificacion_FAIL", contenido)


FICHEROS = []


def diff_list(list1, list2):
    return list(
        set(list1).symmetric_difference(set(list2))
    )  # or return list(set(list1) ^ set(list2))


class Sincronizacion(Thread):
    def __init__(self, Client, id_cliente, ficheros):
        # Inicializar clase padre.
        Thread.__init__(self)
        # self._stop_event = threading.Event()
        self.id_cliente = id_cliente
        self.ficheros = ficheros
        self.Client = Client

    def sincro(self):
        f = open(self.id_cliente + ".txt", "r+")
        data_f = f.read()
        f.close()
        data_fichero = json.loads(data_f)
        # print(data_fichero)
        # print(Client.id_cliente)
        aaa = listar_ficheros(self.id_cliente)
        hora =  time.strftime("%H:%M:%S")
        if aaa == self.ficheros:
            print(f"{hora} Cliente {self.id_cliente} sincronizado")
        else:
            print(f"{hora} Cliente {self.id_cliente} no esta sincronizado")
            lista_ficheros_faltantes = diff_list(aaa, self.ficheros)
            actualizar_ficheros(id_cliente=self.id_cliente, ficheros= aaa)
            a = HTTP_salientes(
                id_cliente=self.id_cliente,
                peticion="POST",
                tipo="eliminar_ficheros",
                contenido=lista_ficheros_faltantes,
            )
            Client.responder(self.Client, res=a)

    def pedir_f_cli(self):
        a = HTTP_salientes(
            id_cliente=self.id_cliente,
            peticion="GET",
            tipo="notificacion_LISTAR_FICHs",
            contenido="",
        )
        Client.responder(self.Client, res=a)

    def run(self):
        while True:
            self.pedir_f_cli()
            sleep(5)
            self.sincro()


class Client(Thread):
    """
    Objeto hijo de la libreria Thread
    """

    def __init__(self, conn, addr):
        # Inicializar clase padre.
        Thread.__init__(self)
        self.conn = conn #Conexion
        self.addr = addr #Addres de la conexion
        self.id_cliente = ""
        self.Sincronizacion = None

    def run(self):
        while True:
            try:
                # Recibir datos del cliente.
                self.recibir()
            except SyntaxError:
                print("[%s] Error de lectura." % self.name)
                break

    def recibir(
        self,
    ):
        pet = self.conn.recv(100000)
        if pet != "NoneType":
            pet = pet.decode("ascii") # Decodifica la peticion en ascii
            lista_clientes = cargar_clientes()
            pet = eval(pet)
            hora =  time.strftime("%H:%M:%S")            
            print(f"{hora} LO QUE LLEGA DEL CLIENTE {pet}")
            if self.Sincronizacion and pet["tipo"] == "sincro":
                self.id_cliente = pet["id_cliente"]
                self.Sincronizacion.ficheros = pet["ficheros"]
                # self.Sincronizacion.pedir_f_cli()
            else:
                res = HTTP_entrantes(HTTP=pet, lista_clientes=lista_clientes, contenido="")
                self.responder(res)
            if not self.Sincronizacion and pet["tipo"] == "creacion_c":
                self.Sincronizacion = Sincronizacion(
                    Client=self, id_cliente=pet["id_cliente"], ficheros=pet["ficheros"]
                )
                self.Sincronizacion.start()
        else:
            contenido = "La peticion NO se ejecuto correctamente no se envio informacio en la data"
            res = HTTP_salientes("", "POST", "notificacion_FAIL", contenido)
            self.responder(res)

    def responder(self, res):
        try:
            self.conn.send(res.encode("ascii"))
        except BrokenPipeError:
            pass


def verificar_sesion(hilos, hilo_nuevo):
    for h in hilos:
        if h.id_cliente == hilo_nuevo.id_cliente:
            return True
    return False


if __name__ == "__main__":

    host = "localhost" # Direccion IP
    port = 8000 # Puerto de practica

    # Create a TCP socket
    mi_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind a local socket to the port
    server_address = (host, port)

    mi_socket.bind(server_address)
    mi_socket.listen(5)
    hora =  time.strftime("%H:%M:%S")
    print(f"{hora} Escuchando...")
    # public_url = ngrok.connect(port, "tcp", options={"remote_addr": "{}:{}".format(host, port)})
    # print('ngrok tunnel "{}" -> "tcp://127.0.0.1:{}/"'.format(public_url, port))
    hilos = []  # Se crea una lista de hilos vacia
    while True:
        connection = None
        try:
            conexion, addr = mi_socket.accept()
            hora =  time.strftime("%H:%M:%S")
            print(f"{hora} Nueva conexion establecida", addr)
            c = Client(conn=conexion, addr=addr)
            c.start()
            hilos.append(c)
        except KeyboardInterrupt:
            print(" Shutting down server.")
            connection.close()
            break

    mi_socket.close()
