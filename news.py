import requests
from flask import request, jsonify

from app import app

# @app.route('/news', methods=['POST'])
# def new_list():
#     query = request.json.get('query')
#     print(f'Searching {query}')
#     link = f'https://newsapi.org/v2/everything?q=tesla&from=2025-03-22&sortBy=publishedAt&apiKey=7504f0032ba542b883d1513ec91a9770'
#     response = requests.get(link)
#     data = response.json()
#     return jsonify(data)


@app.route('/news', methods=['POST'])
def new_list():
    query = request.json.get('query')
    print(f'Searching {query}')
    link = f'https://newsapi.org/v2/everything?q={query}&sortBy=publishedAt&apiKey=7504f0032ba542b883d1513ec91a9770'
    response = requests.get(link)
    data = response.json()
    return jsonify(data)