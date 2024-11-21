import socket  # noqa: F401
import threading as t
import time
import argparse

store: dict = {}
config: dict = {}


def wrap(data):
    if isinstance(data, list):
        return f"*{len(data)}\r\n" + "".join([wrap(d) for d in data])
    if data == "nil":
        return "$-1\r\n"
    return f"${len(data)}\r\n{data}\r\n"


def current_milli_time():
    return round(time.time() * 1000)


def process_data(data):
    cmd = data[2]
    print(f"command: {cmd}")
    if cmd == "echo":
        return data[4]
    if cmd == "ping":
        return "PONG"
    if cmd == "set":
        if len(data) > 8 and data[8] == "px":
            store[data[4]] = (data[6], current_milli_time() + int(data[10]))
        else:
            store[data[4]] = (data[6], -1)
        return "OK"
    if cmd == "get":
        value = store.get(data[4], "nil")
        if value != "nil" and value[1] != -1 and value[1] < current_milli_time():
            store.pop(data[4])
            return "nil"
        return value[0]
    if cmd == "config" and data[4] == "get":
        if data[6] == "dbfilename":
            return ["dbfilename", config.get("dbfilename", "nil")]
        if data[6] == "dir":
            return ["dir", config.get("dir", "nil")]
    return "unknown command"


def handle_request(connection):
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


def main():
    server_socket = socket.create_server(("localhost", 6379), reuse_port=True)
    print("Server started at port 6379")
    try:
        while True:
            connection, _ = server_socket.accept()
            t.Thread(target=handle_request, args=(connection,)).start()
    finally:
        server_socket.close()


if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument("--dir", type=str)
    args.add_argument("--dbfilename", type=str)
    args = args.parse_args()
    config = args.__dict__
    main()
