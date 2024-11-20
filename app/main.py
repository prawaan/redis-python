import socket  # noqa: F401
import threading as t


def handle_request(connection, request_num):
    print(f"Handling request {request_num}")
    while True:
        data = connection.recv(1024)
        if not data:
            break
        connection.sendall(b"+PONG\r\n")
    print(f"Request handled : {request_num}")


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage
    #
    server_socket = socket.create_server(("localhost", 6379), reuse_port=True)
    client_num = 0
    while True:
        connection, _ = server_socket.accept()
        client_num += 1
        thread1 = t.Thread(target=handle_request, args=(connection, client_num))
        thread1.start()

    # server_socket.close()

if __name__ == "__main__":
    main()
