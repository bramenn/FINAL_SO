# HOST="1.tcp.ngrok.io" PORT=12345 python server.py

import os
import socket

from pyngrok import ngrok

host = "localhost"
port = 12345

# Create a TCP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind a local socket to the port
server_address = ("", port)
sock.bind(server_address)
sock.listen(1)

# Open a ngrok tunnel to the socket
public_url = ngrok.connect(port, "tcp", options={"remote_addr": "{}:{}".format(host, port)})
print("ngrok tunnel \"{}\" -> \"tcp://127.0.0.1:{}/\"".format(public_url, port))

while True:
    connection = None
    try:
        # Wait for a connection
        print("\nWaiting for a connection ...")
        connection, client_address = sock.accept()

        print("... connection established from {}".format(client_address))

        # Receive the message, send a response
        while True:
            data = connection.recv(1024)
            if data:
                print("Received: {}".format(data.decode("utf-8")))

                message = "pong"
                print("Sending: {}".format(message))
                connection.sendall(message.encode("utf-8"))
            else:
                break
    except KeyboardInterrupt:
        print(" Shutting down server.")

        if connection:
            connection.close()
        break

sock.close()