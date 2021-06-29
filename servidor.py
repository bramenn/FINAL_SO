import json, socket

def registrar_cliente(lista_clientes):
    f = open("clientes.txt", "w")
    for cliente in lista_clientes:
        f.write("-"+cliente)
    f.close()


def cargar_clientes():
    f = open("clientes.txt", "r+")
    clientes = f.read()
    print(clientes)
    lista_clientes = []
    if len(clientes) > 0:
        clientes.replace("\n", "")
        clientes = clientes.split("-")
        clientes = clientes[1:]
        lista_clientes = clientes
    return lista_clientes
    f.close()



'''
NOTIFICACION
{
  "servidor":"POST",
  "tipo": "notificacion",
  "contenido":"ñlkhadshfkjasdhfh"
}
'''
#PETICIONES DE SALIDA
def armar_HTTP(id_cliente, peticion, tipo, contenido):
    if peticion == "POST":
        if tipo == "notificacion_OK":
            mensaje =  {
               "peticion":peticion,
               "tipo": tipo,
               "contenido":contenido
             }
        if tipo == "notificacion_FAIL":
            mensaje =  {
               "peticion":peticion,
               "tipo": tipo,
               "contenido":contenido
             }
    JSON = json.dumps(mensaje)
    return JSON

def HTTP_entrantes(HTTP, lista_clientes, contenido):
    HTTP = eval(HTTP)
    if HTTP['peticion'] == "POST":
        if HTTP['tipo'] == "creacion_c" and not HTTP['id_cliente'] in lista_clientes:#SE REVISA SI EL CLIENTE YA EXISTE
            id_cliente_f = HTTP['id_cliente'] + ".txt"
            f = open(id_cliente_f,"w")
            lista_clientes.append(HTTP['id_cliente'])
            registrar_cliente(lista_clientes)
            cliente = {
                "id_cliente":HTTP['id_cliente'],
                "ficheros": HTTP['ficheros']
            }
            CLI = json.dumps(cliente)
            f.write(CLI)
            f.close()
            contenido = "La peticion para crear un cliente se ejecuto correctamente {}".format(id_cliente)
            return armar_HTTP( HTTP['id_cliente'], "POST", "notificacion_OK", contenido)
        else:
            id_cliente_f = HTTP['id_cliente'] + ".txt"
            f = open(id_cliente_f,"w")
            cliente = {
                "id_cliente":HTTP['id_cliente'],
                "ficheros": HTTP['ficheros']
            }
            CLI = json.dumps(cliente)
            f.write(CLI)
            f.close()
            contenido = "La peticion para actualizar al cliente se ejecuto correctamente {}".format(id_cliente)
            return armar_HTTP( HTTP['id_cliente'], "POST", "notificacion_OK", contenido)

        contenido = "La peticion NO se ejecuto correctamente no se reconocio la peticion {}".format(HTTP)
        return armar_HTTP("","POST","notificacion_FAIL", contenido)


if __name__ == '__main__':


    mi_socket = socket.socket()
    mi_socket.bind( ('localhost', 8001) )
    mi_socket.listen(5)

    while True:
        conexion, addr = mi_socket.accept()
        print("Nueva conexion establecida", addr)

        pet = conexion.recv(1024)
        if pet != "NoneType":
            pet = pet.decode("ascii")
            print(pet)
            lista_clientes = cargar_clientes()
            res = HTTP_entrantes(pet, lista_clientes, "")
        else:
            contenido = "La peticion NO se ejecuto correctamente no se envio informacio en la data"
            res = armar_HTTP("","POST","notificacion_FAIL", contenido)
        conexion.send(res.encode("ascii"))

        conexion.close()
