import bs4
import requests
import pika

def extract_product_urls(url, maxNumPage=None, startPage=1):
    arr = []

    if maxNumPage is not None and startPage > maxNumPage:
        return arr
    
    response = requests.get(url.format(startPage))

    if response.status_code == 200:
        soup = bs4.BeautifulSoup(response.text, "html.parser")
        links = soup.select(".block-items__item__title")

        for link in links:
            if "/booster/" not in link.get("href"):
                arr.append("https://999.md" + link.get("href"))

        arr.extend(extract_product_urls(url, maxNumPage, startPage + 1))
        
    else:
        print(f"Failed to retrieve the web page. Status code: {response.status_code}")

    return arr

def send_to_rabbitmq(url_list):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='product_urls')

    for url in url_list:
        channel.basic_publish(exchange='',
                              routing_key='product_urls',
                              body=url)

    connection.close()

if __name__ == "__main__":
    url_list = extract_product_urls("https://m.999.md/ro/list/computers-and-office-equipment/laptops?hide_duplicates=no&buy_online=yes={}", maxNumPage=2)
    send_to_rabbitmq(url_list)