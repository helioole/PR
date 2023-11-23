import pika
import threading
import bs4
import requests
from tinydb import TinyDB

db = TinyDB('scraped_data_db.json', indent=4, ensure_ascii=False)
lock = threading.Lock()

def parse_product_details(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        if response.status_code == 200:
            soup = bs4.BeautifulSoup(response.text, "html.parser")

            title_element = soup.find('header', {"class": "adPage__header"})
            title = title_element.text.strip() if title_element else "Title not available"

            price_element = soup.find('span', {"class": "adPage__content__price-feature__prices__price__value"})
            currency_element = soup.find('span', {"class": "adPage__content__price-feature__prices__price__currency"})

            price = price_element.text.strip() if price_element else "Price not available"
            currency = currency_element.text.strip() if currency_element else ""
            formatted_price = f"{price} {currency}"

            description_element = soup.find('div', {"class": "adPage__content__description grid_18", "itemprop": "description"})
            description = description_element.text.strip() if description_element else "Description not available"

            product_details = {
                "title": title,
                "price": formatted_price,
                "description": description,
            }

            return product_details
        else:
            print(f"Failed to retrieve the web page at {url}. Status code: {response.status_code}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error during request: {e}")
        return None

def save_to_persistence(data, consumer_id):
    try:
        with lock:
            if '_id' in data:
                del data['_id']

            data["consumer_id"] = consumer_id
            db.insert(data)
    except Exception as e:
        print(f"Error saving to persistence: {e}")

def worker(url):
    thread_id = threading.current_thread().ident
    consumer_id = thread_id % 20 + 1
    print(f"Consumer {consumer_id} processing URL: {url}")

    product_details = parse_product_details(url)

    if product_details:
        save_to_persistence(product_details, consumer_id)

def consume_urls(num_threads):
    threads = []

    for _ in range(num_threads):
        thread = threading.Thread(target=consume_worker)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

def consume_worker():
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='product_urls')

        for method_frame, properties, body in channel.consume('product_urls'):
            if method_frame is None:
                break
            url = body.decode('utf-8')
            worker(url)
            channel.basic_ack(method_frame.delivery_tag)

        channel.close()
        connection.close()
    except Exception as e:
        print(f"Error in consume_worker: {e}")

if __name__ == "__main__":
    num_threads = 20
    consume_urls(num_threads)