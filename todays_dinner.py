#!/usr/bin/env python3
from flask import Flask, jsonify, request
from bs4 import BeautifulSoup
import requests

todays_dinner_url = 'https://beta.sio.no/mat-og-drikke/_window/mat+og+drikke+-+dagens+middag?s={}'
cafeteria_ids = {
        'informatikk': 284,
        'frederikke': 122,
        'kutt': 310
        }

app = Flask(__name__)

def todays_dinner_to_dict(text, own_url):
    soup = BeautifulSoup(text, 'html.parser')
    headers = soup.find_all('h3')
    paragraphs = soup.find_all('p')

    if len(headers) != len(paragraphs):
        return {error: "Number of headers does not correspond to the number of paragraphs."}
    
    todays_dinner = {}
    for h, p in zip(headers, paragraphs):
        todays_dinner[h.contents[0].lower()] = [span.contents[0] for span in p.find_all('span')]

    todays_dinner['cafeterias'] = ['{}/{}'.format(own_url[:own_url.rfind('/')], cafeteria) for cafeteria in cafeteria_ids.keys()]

    return todays_dinner

@app.route('/todays_dinner/', methods=['GET'])
@app.route('/todays_dinner/<cafeteria>', methods=['GET'])
def get_todays_dinner(cafeteria='informatikk'):
    if not cafeteria in cafeteria_ids.keys():
        cafeteria = 'informatikk'

    todays_dinner_html = requests.get(todays_dinner_url.format(cafeteria_ids[cafeteria])).text
    return jsonify(todays_dinner_to_dict(todays_dinner_html, request.base_url))

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)
