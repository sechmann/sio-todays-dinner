#!/usr/bin/env python3
from flask import Flask, jsonify, request
from werkzeug.contrib.cache import SimpleCache
from bs4 import BeautifulSoup
import requests, os, time

todays_dinner_url = 'https://beta.sio.no/mat-og-drikke/_window/mat+og+drikke+-+dagens+middag?s={}'

# Static things
cafeteria_ids = {
        'informatikk': 284,
        'frederikke': 122,
        'kutt': 310
        }
api_url = 'http://api.desperate.solutions/dagens/'
cache = SimpleCache()

app = Flask(__name__)

def get_dishes(cafeteria):
    dishes = cache.get(cafeteria)
    if dishes is None:
        print("{} is not cached, getting from web.".format(cafeteria))
        dishes = get_todays_dinner_from_web(cafeteria)
        cache.set(cafeteria, dishes, timeout=6*60*60)

    return dishes

def make_urls():
    return {cafeteria: '{}/{}'.format(api_url[:api_url.rfind('/')], cafeteria) for cafeteria in cafeteria_ids.keys()}

def get_todays_dinner_from_web(cafeteria):
    todays_dinner_html = requests.get(todays_dinner_url.format(cafeteria_ids[cafeteria])).text
    soup = BeautifulSoup(todays_dinner_html, 'html.parser')
    headers = soup.find_all('h3')
    paragraphs = soup.find_all('p')
    dishes = []

    if len(headers) != len(paragraphs):
        return jsonify({
            error: "Invalid response from beta.sio.no",
            more_info: "Number of headers does not correspond to the number of paragraphs"
            })

    for h, p in zip(headers, paragraphs):
        dishes.append({
            "category": h.contents[0].lower(),
            "dishes": [span.contents[0] for span in p.find_all('span')]})

    return dishes

@app.route('/todays_dinner/', methods=['GET'])
@app.route('/todays_dinner/<cafeteria>', methods=['GET'])
def get_todays_dinner(cafeteria=None):
    cafeterias = {}

    if cafeteria in cafeteria_ids.keys():
        return jsonify({'cafeteria': get_dishes(cafeteria)})
    else:
        return jsonify(make_urls())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
