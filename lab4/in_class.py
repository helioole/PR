import socket
import signal
import sys
import threading
import re

HOST = '127.0.0.1'
PORT = 8080

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.bind((HOST, PORT))

server_socket.listen(5)
print(f"Server is listening on {HOST}:{PORT}")

list_of_products = [
    {
        "id": 0,
        "name": "Fluent Python: Clear, Concise, and Effective Programming",
        "author": "Luciano Ramalho",
        "price": 39.95,
        "description": "Don't waste time bending Python to fit patterns you've learned in other languages. Python's simplicity lets you become productive quickly, but often this means you aren't using everything the language has to offer. With the updated edition of this hands-on guide, you'll learn how to write effective, modern Python 3 code by leveraging its best ideas. "
    },
    {
        "id": 1,
        "name": "Introducing Python: Modern Computing in Simple Packages",
        "author": "Bill Lubanovic",
        "price": 27.49,
        "description": "Easy to understand and fun to read, this updated edition of Introducing Python is ideal for beginning programmers as well as those new to the language. Author Bill Lubanovic takes you from the basics to more involved and varied topics, mixing tutorials with cookbook-style code recipes to explain concepts in Python 3. End-of-chapter exercises help you practice what you’ve learned."
    }
]

product_url_pattern = re.compile(r'^/product/(\d+)$')


def handle_request(client_socket):
    request_data = client_socket.recv(1024).decode('utf-8')
    print(f"Received Request:\n{request_data}")

    request_lines = request_data.split('\n')
    request_line = request_lines[0].strip().split()
    method = request_line[0]
    path = request_line[1]

    response_content = ''

    status_code = 200

    if path == '/':
        available_pages = [
            ("/", "Home"),
            ("/about", "About Us"),
            ("/contacts", "Contacts"),
            ("/products", "Products"),
        ]

        response_content = "<h1>Available Pages:</h1>\n<ul>"
        for page_path, page_name in available_pages:
            response_content += f'<li><a href="{page_path}">{page_name}</a></li>'
        response_content += "</ul>"

    elif path == '/about':
        response_content = 'About page.'
    elif path == '/contacts':
        response_content = 'Contacts.'
    elif path == '/products':
        response_content = "<h1>Products:</h1>\n<ul>"
        for product in list_of_products:
            response_content += f"<a href='/product/{product['id']}'> Product: {product['name']} </a><br>"
    else:
        match = product_url_pattern.match(path)
        if match:
            product_id = int(match.group(1))
            if 0 <= product_id < len(list_of_products):
                product = list_of_products[product_id]
                response_content = f"""<p> ID : {product['id']} </p>""" +\
                                f"""<p> Name : {product['name']} </p>""" +\
                                f"""<p> Author : {product['author']} </p>""" +\
                                f"""<p> Price : {product['price']} </p>"""  +\
                                f"""<p> Description : {product['description']} </p>"""
            else:
                response_content = '404 Not Found'
                status_code = 404
        else:
            response_content = '404 Not Found'
            status_code = 404

    response = f'HTTP/1.1 {status_code} OK\nContent-Type: text/html\n\n{response_content} '
    client_socket.send(response.encode('utf-8'))

    client_socket.close()


def signal_handler(sig, frame):
    print("\nShutting down the server...")
    server_socket.close()
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

while True:
    client_socket, client_address = server_socket.accept()
    print(f"Accepted connection from {client_address[0]}:{client_address[1]}")

    client_handler = threading.Thread(target=handle_request, args=(client_socket,))
    client_handler.start()
