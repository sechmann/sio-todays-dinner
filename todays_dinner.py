#!/usr/bin/env python3
from flask import Flask, jsonify, request, g
from werkzeug.contrib.cache import MemcachedCache
from sio import TodaysDinner

api_base_url = 'http://api.desperate.solutions/dagens/'
todays_dinner = TodaysDinner()

api_base_urls = {cafeteria:
'{}/{}'.format(api_base_url[:api_base_url.rfind('/')], cafeteria) for cafeteria in todays_dinner.cafeteria_ids.keys()}

app = Flask(__name__)
@app.route('/dagens/<cafeteria>/flush', methods=['GET'])
def flush_cache(cafeteria=None):
    if not cafeteria:
        return jsonify({error: "Invalid or no cafeteria specified"})
    else:
        todays_dinner.flush_cache(cafeteria)
        return get_todays_dinner(cafeteria)

@app.route('/dagens/', methods=['GET'])
@app.route('/dagens/<cafeteria>', methods=['GET'])
def get_todays_dinner(cafeteria=None):
    cafeterias = {}

    if cafeteria in todays_dinner.cafeteria_ids.keys():
        return jsonify({'cafeteria': todays_dinner.get_menu(cafeteria)})
    else:
        return jsonify(api_base_urls)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
