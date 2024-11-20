import socket  # noqa: F401
import threading as t
import time

store: dict = {}

def wrap(data):
    if data == "nil":
        return "$-1\r\n"
    return f"${len(data)}\r\n{data}\r\n"

def current_milli_time():
    return round(time.time() * 1000)


def process_data(data):
    cmd = data[2]
    print(f"command: {cmd}")
    if cmd == 'echo':
        return data[4]
    if cmd == 'ping':
        return "PONG"
    if cmd == 'set':
        if len(data) > 8 and data[8] == 'px':
            store[data[4]] = (data[6], current_milli_time() + int(data[10]))
        else:
            store[data[4]] = (data[6], -1)
        return "OK"
    if cmd == 'get':
        value = store.get(data[4], "nil")
        if value != 'nil' and value[1] != -1 and value[1] < current_milli_time():
            store.pop(data[4])
            return "nil"
        return value[0]
    
    return "unknown command"

def handle_request(connection, request_num):
    print(f"Handling request {request_num}")
    crlf = "\r\n"
    while True:
        data = connection.recv(1024).decode("utf-8").strip().lower()
        if not data:
            break
        print(f"Received data: {data}")
        data_processed = process_data(data.split(crlf))
        print(f"processed data: {data_processed}")
        
        response = wrap(data_processed)

        print(f"Response: {response}")
        connection.sendall(bytes(response, "utf-8"))
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
