import json, os, socket


'''
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
'''


def InfoCliente():
	id_uss = input("Ingrese el id del cliente: ")
	nombre_carpeta = input("Ingrese el nombre de la capeta: ")
	return [id_uss, nombre_carpeta]

def ListarCarpeta(nombre_carpeta):
	ficheros = os.listdir(nombre_carpeta)
	return ficheros


def leer_fichero(nombre_carpeta,nombre_fichero):
	fd =  open (nombre_carpeta+"/"+nombre_fichero,'r')
	contenido = fd.read()
	return contenido


'''
{
  "peticion":"POST",
  "tipo": "creacion_c",
  "id_cliente": "123",
  "ficheros": ["fichero_1","fichero_2","fichero_3"]
}
'''
#PETICIONES DE SALIDA CLIENTE
def armar_HTTP(id_cliente, data, peticion, tipo):
    if peticion == "POST":
        if tipo == "ver_f":
            nombre_fichero = data[0]
            contenido = data[1]
            mensaje =  {
               "peticion":peticion,
               "tipo": tipo,
               "id_cliente":id_cliente,
               "nombre_fichero": nombre_fichero,
               "contenido":contenido
             }
        if tipo == "creacion_c":
            ficheros = data
            mensaje =  {
               "peticion":peticion,
               "tipo": tipo,
               "id_cliente":id_cliente,
               "ficheros": ficheros
             }




    JSON = json.dumps(mensaje)
    return JSON


def HTTP_entrantes(HTTP):
    try:
        HTTP = eval(HTTP)
        if HTTP['peticion'] == "POST":
            if HTTP['tipo'] == "notificacion_OK":#SE REVISA SI EL CLIENTE YA EXISTE
                contenido = HTTP['contenido']
                print("Respuesta del servidor: {}".format(contenido))
            if HTTP['tipo'] == "notificacion_FAIL":#SE REVISA SI EL CLIENTE YA EXISTE
                contenido = HTTP['contenido']
                print("Respuesta del servidor: {}".format(contenido))
        else:
            print("PETICION NO ENCONTRADA: {}". HTTP)
    except SyntaxError as e:
        print(e)




if __name__ == '__main__':
    data_cli = InfoCliente()
    ficheros = ListarCarpeta(data_cli[1])
    contenido = leer_fichero(data_cli[1],"prueba_2.txt")
    data = ["prueba_2.txt", contenido]
    res = armar_HTTP(data_cli[0],ficheros, "POST", "creacion_c")


    mi_socket = socket.socket()
    mi_socket.connect( ('localhost', 8001) )

    mi_socket.send(res.encode("ascii"))
    pet = mi_socket.recv(1024)
    pet = pet.decode("ascii")
    HTTP_entrantes(pet)
    mi_socket.close()


    # print("El id del cliente es: {}; Y sus ficheros son: {}".format(data_cli[0], ficheros))
