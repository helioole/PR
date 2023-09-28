import bs4
import requests
import json 
from in_class import scrape

def crawling(rent_car, num):
    count = 0
    scraped_data = []

    while count < num:
        response = requests.get(rent_car[count])
        if response.status_code == 200:
            soup = bs4.BeautifulSoup(response.text, "html.parser")
            title = soup.find('header', {"class": "adPage__header"}).text
            price = soup.find('span', {"class": "adPage__content__price-feature__prices__price__value"}).text
            currency_element = soup.find('span', {"class": "adPage__content__price-feature__prices__price__currency"})
            description = soup.find('div', {"class": "adPage__content__description grid_18", "itemprop": "description"}).text
            
            if currency_element is not None:
                currency = currency_element.text
                item_data = {
                    "title": title,
                    "price": price + currency,
                    "description": description
                }
                scraped_data.append(item_data)

            else:
                item_data = {
                    "title": title,
                    "price": price,
                    "description": description
                }
                scraped_data.append(item_data)

        else:
            print(f"Failed to retrieve the web page at {rent_car[count]}. Status code: {response.status_code}")
        count += 1

    with open("scraped_data.json", "w", encoding="utf-8") as json_file:
        json.dump(scraped_data, json_file, indent=4, ensure_ascii=False)

    print("Scraped data exported to scraped_data.json")


if __name__ == "__main__":
    url = scrape("https://m.999.md/ro/list/computers-and-office-equipment/laptops?hide_duplicates=no&buy_online=yes={}", maxNumPage=2)
    scrap = crawling(url, 15)