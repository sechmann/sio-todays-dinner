from bs4 import BeautifulSoup
import requests, os, time, json

TODAYS_DINNER_URL = 'https://beta.sio.no/mat-og-drikke/_window/mat+og+drikke+-+dagens+middag?s={}'

class Menu:
    def __init__(self):
        self.dishes = {}


class TodaysDinner:
    def __init__(self, cache):
        self.cache = cache

        with open('cafeterias.json') as f:
            self.cafeteria_ids = json.load(f)

    def get_menu(self, cafeteria):
        menu = self.cache.get(cafeteria)
        if menu is None:
            print("{} is not cached, getting from web.".format(cafeteria))
            menu = get_todays_dinner_from_web(cafeteria)
            if len(menu) == 0:
                return menu

            for category in menu:
                for dish in category['dishes']:
                    if "dagens meny legges ut" in dish.lower():
                        return menu

            self.cache.set(cafeteria, menu, timeout=6*60*60)

        return menu

    def get_todays_dinner_from_web(self, cafeteria):
        todays_dinner_html = requests.get(TODAYS_DINNER_URL.format(self.cafeteria_ids[cafeteria])).text
        soup = BeautifulSoup(todays_dinner_html, 'html.parser')
        headers = soup.find_all('h3')
        paragraphs = soup.find_all('p')
        menu = []

        if len(headers) != len(paragraphs):
            # Number of headers does not correspond to the number of paragraphs
            return jsonify({error: "Invalid response from beta.sio.no"})

        for h, p in zip(headers, paragraphs):
            dishes = [span.contents[0].strip(' -') for span in p.find_all('span')]

            menu.append({
                "category": h.contents[0].lower(),
                "cacheTimestamp": time.time(),
                "dishes": dishes})

        return menu
