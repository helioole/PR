import socket
import threading
import json
import os

class Server:
    def __init__(self, host, port, media_folder):
        self.host = host
        self.port = port
        self.media_folder = media_folder
        self.clients = []
        self.rooms = {}

    def start(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen()
        print(f'Server is listening on {self.host}:{self.port}')

        while True:
            client_socket, client_address = server_socket.accept()
            self.clients.append(client_socket)
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address))
            client_thread.start()

    def handle_client(self, client_socket, client_address):
        print(f'Accepted connection from {client_address}')

        while True:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break

            data = json.loads(message)
            self.handle_message(client_socket, data)

    def handle_message(self, client_socket, data):
        message_type = data.get('type', '')

        if message_type == 'connect':
            self.handle_connect(client_socket, data)
        elif message_type == 'disconnect':
            self.handle_disconnect(client_socket, data)
        elif message_type == 'upload':
            self.handle_upload(client_socket, data)
        elif message_type == 'download':
            self.handle_download(client_socket, data)
        elif message_type == 'message':
            self.handle_message_broadcast(client_socket, data)
        else:
            print(f'\nInvalid client message received: {data}')

    def handle_connect(self, client_socket, data):
        acknowledge_message = {
            "type": "connect_ack",
            "payload": {
                "message": f"\nYou successfully connected to the room '{data['payload']['room']}'.\
                            \nEnter your message or command"
            }
        }
        server_data = json.dumps(acknowledge_message)
        client_socket.send(bytes(server_data, encoding='utf-8'))

        room = data['payload']['room']
        if room not in self.rooms:
            self.rooms[room] = set()

        self.rooms[room].add(client_socket)

        if len(self.clients) > 1:
            notification_message = {
                "type": "notification",
                "payload": {
                    "message": f"{data['payload']['name']} has joined the room.\n"
                }
            }
            server_data = json.dumps(notification_message)
            self.send_broadcast_message(client_socket, self.clients, self.rooms, bytes(server_data, encoding='utf-8'))

    def handle_disconnect(self, client_socket, data):
        self.clients.remove(client_socket)

        if len(self.clients) != 0:
            notification_message = {
                "type": "notification",
                "payload": {
                    "message": f"{data['payload']['name']} left the room.\n"
                }
            }
            server_data = json.dumps(notification_message)
            self.send_broadcast_message(client_socket, self.clients, self.rooms, bytes(server_data, encoding='utf-8'))

        for room in self.rooms:
            if room == data['payload']['room']:
                self.rooms[room].remove(client_socket)
                break
        return

    def handle_upload(self, client_socket, data):
        if not os.path.isdir(self.media_folder):
            os.mkdir(self.media_folder)
        if not os.path.isdir(f"{self.media_folder}/{data['payload']['room']}"):
            os.mkdir(f"{self.media_folder}/{data['payload']['room']}")

        file_name = data['payload']['file_name']
        file_path = f"{self.media_folder}/{data['payload']['room']}/{file_name}"
        option = 'w'
        if not os.path.exists(file_path):
            option = 'x'

        if data['payload']['file_size'] > 1024:
            with open(file_path, f'{option}b') as received_file:
                index = 0
                while index < data['payload']['file_size']:
                    chunk = client_socket.recv(1024)
                    received_file.write(chunk)
                    index += 1024
        else:
            with open(file_path, f'{option}b') as received_file:
                chunk = client_socket.recv(data['payload']['file_size'])
                received_file.write(chunk)

        notification_message = {
            "type": "notification",
            "payload": {
                "message": f"{data['payload']['name']} uploaded the {file_name} file.\n"
            }
        }

        upload_message = {
            "type": "notification",
            "payload": {
                "message": f"You successfully uploaded the {file_name} file.\n"
            }
        }
        server_data = json.dumps(notification_message)
        self.send_broadcast_message(client_socket, self.clients, self.rooms, bytes(server_data, encoding='utf-8'))

        server_data = json.dumps(upload_message)
        client_socket.sendall(bytes(server_data, encoding='utf-8'))

    def handle_download(self, client_socket, data):
        file_path = f"{self.media_folder}/{data['payload']['room']}/{data['payload']['file_name']}"
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)

            stream_message = {
                "type": "download-ack",
                "payload": {
                    "file_name": data['payload']['file_name'],
                    "file_size": file_size
                }
            }
            server_data = json.dumps(stream_message)
            client_socket.sendall(bytes(server_data, encoding='utf-8'))

            if file_size > 1024:
                with open(file_path, 'rb') as file:
                    while True:
                        chunk = file.read(1024)
                        if not chunk:
                            break
                        client_socket.sendall(chunk)
            else:
                with open(file_path, 'rb') as file:
                    chunk = file.read(file_size)
                    client_socket.sendall(chunk)
        else:
            notification_message = {
                "type": "notification",
                "payload": {
                    "message": f"The file {data['payload']['file_name']} does not exist.\n"
                }
            }
            server_data = json.dumps(notification_message)
            client_socket.sendall(bytes(server_data, encoding='utf-8'))

    def send_broadcast_message(self, client_socket, clients, rooms, data):
        for client in clients:
            if client != client_socket:
                for room in rooms:
                    if (client in rooms[room]) and (client_socket in rooms[room]):
                        client.sendall(data)
                        break

server = Server('127.0.0.1', 8080, 'server_media')
server.start()
