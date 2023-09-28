import bs4
import requests
import json

arr = []

def scrape(url, maxNumPage=None, startPage=1):

    if maxNumPage is not None and startPage > maxNumPage:
        return
    
    response = requests.get(url.format(startPage))

    if response.status_code == 200:

        soup = bs4.BeautifulSoup(response.text, "html.parser")
        links = soup.select(".block-items__item__title")

        for link in links:
            if "/booster/" not in link.get("href"):
                arr.append("https://999.md" + link.get("href"))   

        scrape(url, maxNumPage, startPage + 1)
        
    else:
        print(f"Failed to retrieve the web page. Status code: {response.status_code}")
    
    with open("url.json", "w", encoding="utf-8") as json_file:
        json.dump(arr, json_file, indent=4, ensure_ascii=False)
    
    return arr

if __name__ == "__main__":
    url = scrape("https://m.999.md/ro/list/real-estate/apartments-and-rooms?o_30_241=893&o_33_1=776={}", maxNumPage=2)