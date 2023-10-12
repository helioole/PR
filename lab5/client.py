import socket
import threading
import json
import re
import os

class Client:
        def __init__(self, host, port, media_folder):
            self.host = host
            self.port = port
            self.media_folder = media_folder

        def connect(self):
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.client_socket.connect((self.host, self.port))
            print(f"Connected to {self.host}:{self.port}")

        def receive_messages(self, name):
            while True:
                server_message = self.client_socket.recv(1024).decode('utf-8')
                if not server_message:
                    break

                self.handle_server_message(server_message, name)

        def handle_server_message(self, server_message, name):
            data = json.loads(server_message)
            message_type = data.get('type', '')

            if message_type == 'connect_ack' or message_type == 'notification':
                print(data['payload']['message'])
            elif message_type == 'download-ack':
                self.download_file(data, name)
            elif message_type == 'message':
                print(f"\nRoom: {data['payload']['room']}, {data['payload']['sender']}: {data['payload']['text']}")
            else:
                print(f'\nInvalid message received: {data}')

        def upload_file(self, message, name, room):
            file_path = message.split(' ')[1]
            tokens = file_path.split('/')
            file_name = tokens[len(tokens) - 1]

            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                file_upload_message = {
                    "type": "upload",
                    "payload": {
                        "file_name": file_name,
                        "file_size": file_size,
                        "name": name,
                        "room": room
                    }
                }
                data = json.dumps(file_upload_message)
                self.client_socket.sendall(bytes(data, encoding='utf-8'))

                if file_size > 1024:
                    with open(file_path, 'rb') as file:
                        while True:
                            chunk = file.read(1024)
                            if not chunk:
                                break
                            self.client_socket.sendall(chunk)
                else:
                    with open(file_path, 'rb') as file:
                        chunk = file.read(file_size)
                        self.client_socket.sendall(chunk)
            else:
                print(f'File {file_name} does not exist!')

        def download_file(self, data, name):
            option = 'w'
            if not os.path.exists(f"{self.media_folder}/{name}/{data['payload']['file_name']}"):
                option = 'x'

            if data['payload']['file_size'] > 1024:
                with open(f"{self.media_folder}/{name}/{data['payload']['file_name']}", f'{option}b') as received_file:
                    index = 0
                    while index < data['payload']['file_size']:
                        chunk = self.client_socket.recv(1024)
                        received_file.write(chunk)
                        index += 1024
            else:
                with open(f"{self.media_folder}/{name}/{data['payload']['file_name']}", f'{option}b') as received_file:
                    chunk = self.client_socket.recv(data['payload']['file_size'])
                    received_file.write(chunk)

            print('File was downloaded successfully')

        def perform_server_connection(self):
            name = input('Enter your name: ')
            room = input('Enter the room: ')
            connection_message = {
                "type": "connect",
                "payload": {
                    "name": name,
                    "room": room
                }
            }

            data = json.dumps(connection_message)
            self.client_socket.sendall(bytes(data, encoding='utf-8'))

            return name, room

        def start(self):
            self.connect()
            name, room = self.perform_server_connection()

            if not os.path.isdir(self.media_folder):
                os.mkdir(self.media_folder)
            if not os.path.isdir(f"{self.media_folder}/{name}"):
                os.mkdir(f"{self.media_folder}/{name}")

            receive_thread = threading.Thread(target=self.receive_messages, args=(name,))
            receive_thread.daemon = True
            receive_thread.start()

            while True:
                message = input()
                if message.lower() == 'exit':
                    disconnect_message = {
                        "type": "disconnect",
                        "payload": {
                            "name": name,
                            "room": room
                        }
                    }
                    data = json.dumps(disconnect_message)
                    self.client_socket.sendall(bytes(data, encoding='utf-8'))
                    break

                if re.match(r'upload ([A-Za-z\./]+)', message):
                    self.upload_file(message, name, room)
                elif re.match(r'download ([A-Za-z\.]+)', message):
                    file_download_message = {
                        "type": "download",
                        "payload": {
                            "file_name": message.split(' ')[1],
                            "name": name,
                            "room": room
                        }
                    }
                    data = json.dumps(file_download_message)
                    self.client_socket.sendall(bytes(data, encoding='utf-8'))
                else:
                    chat_message = {
                        "type": "message",
                        "payload": {
                            "sender": name,
                            "room": room,
                            "text": f'{message}\n'
                        }
                    }

                    data = json.dumps(chat_message)
                    self.client_socket.sendall(bytes(data, encoding='utf-8'))


client = Client('127.0.0.1', 8080, 'client_media')
client.start()

