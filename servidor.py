import json, socket
import threading

from pyngrok import ngrok


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
    ficheros = []
    for fichero in data["ficheros"]:
        for key in fichero.keys():
            if key == nombre_fichero:
                return fichero[key]
    return

    # return ficheros


# PETICIONES DE SALIDA
def HTTP_salientes(id_cliente, peticion, tipo, contenido):
    if peticion == "POST":
        if tipo == "notificacion_OK":
            mensaje = {"peticion": peticion, "tipo": tipo, "contenido": contenido}
        if tipo == "notificacion_FAIL":
            mensaje = {"peticion": peticion, "tipo": tipo, "contenido": contenido}
        if tipo == "notificacion_LISTAR_F":
            ficheros = listar_ficheros(id_cliente)

    JSON = json.dumps(mensaje)
    return JSON


def HTTP_entrantes(HTTP, lista_clientes, contenido):
    HTTP = eval(HTTP)
    if HTTP["peticion"] == "POST":
        if HTTP["tipo"] == "creacion_c" and not HTTP["id_cliente"] in lista_clientes:
            id_cliente_f = HTTP["id_cliente"] + ".txt"
            f = open(id_cliente_f, "w")
            lista_clientes.append(HTTP["id_cliente"])
            registrar_cliente(lista_clientes)
            cliente = {"id_cliente": HTTP["id_cliente"], "ficheros": HTTP["ficheros"]}
            CLI = json.dumps(cliente)
            f.write(CLI)
            f.close()
            contenido = "Se creo el cliente correctamente {}".format(HTTP["id_cliente"])
            return HTTP_salientes(HTTP["id_cliente"], "POST", "notificacion_OK", contenido)
        else:
            id_cliente_f = HTTP["id_cliente"] + ".txt"
            f = open(id_cliente_f, "w")
            cliente = {"id_cliente": HTTP["id_cliente"], "ficheros": HTTP["ficheros"]}
            CLI = json.dumps(cliente)
            f.write(CLI)
            f.close()
            contenido = "Se actualizo correctamente {}".format(HTTP["id_cliente"])
            return HTTP_salientes(HTTP["id_cliente"], "POST", "notificacion_OK", contenido)

    elif HTTP["peticion"] == "GET":
        print(lista_clientes)
        if HTTP["tipo"] == "notificacion_LISTAR_F" and HTTP["id_cliente"] in lista_clientes:
            ficheros = listar_ficheros(HTTP["id_cliente"])
            contenido = "Los ficheros del cliente {} son: ".format(HTTP["id_cliente"])
            for fichero in ficheros:
                contenido += "\n" + fichero
            return HTTP_salientes(HTTP["id_cliente"], "POST", "notificacion_OK", contenido)
        elif HTTP["tipo"] == "ver_f" and HTTP["id_cliente"] in lista_clientes:
            nombre_fichero = HTTP["nombre_fichero"]
            res = ver_f(HTTP["id_cliente"], nombre_fichero + ".txt")
            if res:
                contenido = "El contenido del fichero {} es:\n{}".format(nombre_fichero, res)
                return HTTP_salientes(HTTP["id_cliente"], "POST", "notificacion_OK", contenido)
            else:
                contenido = "NO se encontro el fichero {} en el cliente {}".format(
                    nombre_fichero, HTTP["id_cliente"]
                )
        elif HTTP["tipo"] == "ver_clientes":
            contenido = cargar_clientes()
            return HTTP_salientes(HTTP["id_cliente"], "POST", "notificacion_OK", contenido)
        else:
            contenido = "NO se encontro el cliente {}".format(HTTP["id_cliente"])
        return HTTP_salientes("", "POST", "notificacion_FAIL", contenido)
    else:
        contenido = "NO se reconocio la peticion {}".format(HTTP)
        return HTTP_salientes("", "POST", "notificacion_FAIL", contenido)


def crear_hilo_c(conexion, addr):
    pet = conexion.recv(2048)
    if pet != "NoneType":
        pet = pet.decode("ascii")
        print(pet)
        lista_clientes = cargar_clientes()
        res = HTTP_entrantes(HTTP=pet, lista_clientes=lista_clientes, contenido="")
    else:
        contenido = "La peticion NO se ejecuto correctamente no se envio informacio en la data"
        res = HTTP_salientes("", "POST", "notificacion_FAIL", contenido)
    conexion.send(res.encode("ascii"))
    conexion.close()


# if __name__ == "__main__":

#     mi_socket = socket.socket()
#     mi_socket.bind(("localhost", 8000))
#     mi_socket.listen(5)

#     while True:
#         conexion, addr = mi_socket.accept()
#         print("Nueva conexion establecida", addr)
#         if addr and conexion:
#             hilo = threading.Thread(
#                 target=crear_hilo_c,
#                 args=(
#                     conexion,
#                     addr,
#                 ),
#             )
#             hilo.start()


if __name__ == "__main__":

    host = "localhost"
    port = 8000

    # Create a TCP socket
    mi_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind a local socket to the port
    server_address = ("", port)

    mi_socket.bind(server_address)
    mi_socket.listen(5)

    public_url = ngrok.connect(port, "tcp", options={"remote_addr": "{}:{}".format(host, port)})
    print('ngrok tunnel "{}" -> "tcp://127.0.0.1:{}/"'.format(public_url, port))
    while True:
        connection = None
        try:
            conexion, addr = mi_socket.accept()
            print("Nueva conexion establecida", addr)
            if addr and conexion:
                hilo = threading.Thread(
                    target=crear_hilo_c,
                    args=(
                        conexion,
                        addr,
                    ),
                )
                hilo.start()
        except KeyboardInterrupt:
            print(" Shutting down server.")

            if connection:
                connection.close()
            break

    mi_socket.close()
