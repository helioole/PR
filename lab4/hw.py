import socket
from bs4 import BeautifulSoup
import json

HOST = '127.0.0.1'
PORT = 8080

scraped_links = []
product_data = []

def send_request(link):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))

    request_string = f"GET {link} HTTP/1.1\r\nHost: {HOST}:{PORT}\n"
    client_socket.send(request_string.encode('utf-8'))

    response = b'' 
    while True:
        data = client_socket.recv(4096)
        if not data:
            break
        response += data

    client_socket.close()
    return response.decode('utf-8')  


def parse_product_page(response):
    soup = BeautifulSoup(response, 'html.parser')
    
    product_details = {}

    # Find all 'p' elements and extract information based on their text content
    for p in soup.find_all('p'):
        text = p.text.strip()
        if text.startswith('ID'):
            product_details['id'] = int(text.split(': ')[1])
        elif text.startswith('Name'):
            product_details['name'] = text.split(': ')[1]
        elif text.startswith('Author'):
            product_details['author'] = text.split(': ')[1]
        elif text.startswith('Price'):
            product_details['price'] = float(text.split(': ')[1])
        elif text.startswith('Description'):
            product_details['description'] = text.split(': ')[1]

    product_data.append(product_details)



def parse_page(link):
    response = send_request(link)
    soup = BeautifulSoup(response, 'html.parser')

    if 'product' in link:
        parse_product_page(response)
    else:
        # Save the content of simple pages
        with open(f"{link.replace('/', '_')}.html", "w") as page_file:
            page_file.write(soup.prettify())

    internal_links = [a['href'] for a in soup.find_all('a')]
    for internal_link in internal_links:
        if internal_link not in scraped_links:
            scraped_links.append(internal_link)
            parse_page(internal_link)

def main():
    initial_link = '/'
    scraped_links.append(initial_link)
    parse_page(initial_link)

    with open('product_details.json', 'w') as product_file:
        json.dump(product_data, product_file, indent=4)

if __name__ == '__main__':
    main()