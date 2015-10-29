#!/usr/bin/env python3
from flask import Flask, jsonify, request, g
from werkzeug.contrib.cache import SimpleCache
from bs4 import BeautifulSoup
import requests, os, time, json

# Static things
todays_dinner_url = 'https://beta.sio.no/mat-og-drikke/_window/mat+og+drikke+-+dagens+middag?s={}'
cafeteria_ids = {}
api_url = 'http://api.desperate.solutions/dagens/'
api_urls = {}
cache = SimpleCache()

app = Flask(__name__)

def get_menu(cafeteria):
    menu = cache.get(cafeteria)
    if menu is None:
        print("{} is not cached, getting from web.".format(cafeteria))
        menu = get_todays_dinner_from_web(cafeteria)
        if len(menu) == 0:
            return menu

        for category in menu:
            for dish in category['dishes']:
                if "dagens meny legges ut" in dish.lower():
                    return menu


        cache.set(cafeteria, menu, timeout=6*60*60)

    return menu

def make_urls():
    return {cafeteria: '{}/{}'.format(api_url[:api_url.rfind('/')], cafeteria) for cafeteria in cafeteria_ids.keys()}

def get_todays_dinner_from_web(cafeteria):
    todays_dinner_html = requests.get(todays_dinner_url.format(cafeteria_ids[cafeteria])).text
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

@app.route('/todays_dinner/<cafeteria>/flush', methods=['GET'])
def flush_cache(cafeteria=None):
    if not cafeteria:
        return jsonify({error: "Invalid or no cafeteria specified"})
    else:
        cache.delete(cafeteria)
        return get_todays_dinner(cafeteria)

@app.route('/todays_dinner/', methods=['GET'])
@app.route('/todays_dinner/<cafeteria>', methods=['GET'])
def get_todays_dinner(cafeteria=None):
    cafeterias = {}

    if cafeteria in cafeteria_ids.keys():
        return jsonify({'cafeteria': get_menu(cafeteria)})
    else:
        return jsonify(api_urls)

if __name__ == '__main__':
    with open('cafeterias.json') as f:
        cafeteria_ids = json.load(f)
    api_urls = make_urls()
    app.run(host='0.0.0.0', port=5000, debug=True)
