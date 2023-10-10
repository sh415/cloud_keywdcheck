import time
import requests
from random import *
from flask import Flask, request
from flask_cors import CORS
from flask_restful import Api
from flasgger import Swagger, swag_from
from bs4 import BeautifulSoup

app = Flask(__name__)
api = Api(app)
CORS(app)

swagger_config = {
    "headers": [],
    "specs": [
        {
            "version": "1.0.0",
            "title": "Your API",
            "endpoint": "apispec",
            "route": "/apispec.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs"
}
swagger = Swagger(app, config=swagger_config)

def scrap_keywdcheck(keywd):
    try:
        url = f'https://m.search.naver.com/search.naver?sm=mtp_hty.top&where=m&query={keywd}'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134'
        }
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        svp = soup.select_one('._svp_list')
        posts = []
        for post in svp.select('.api_txt_lines.total_tit'):
            href = post.get('href')
            posts.append({'href': href})
        
        return posts

    except Exception as e:
        print('scrap_keywdcheck error', e)
        return False

@app.route('/')
def index():
    return 'cloud_keywdcheck_server'

@app.route('/responses', methods=['POST'])
@swag_from({
    'responses': {
        200: {
            'description': 'Successful response',
            'examples': {
                'application/json': {'message': True}
            }
        },
        500: {
            'description': 'Error response',
            'examples': {
                'application/json': {'message': False, 'error': 'Error message'}
            }
        }
    }
})
def server_responses():
    try:
        # res = request.json
        # url = res.get('url')
        # print(url)
        return { 'message': True }, 200
    
    except Exception as e:
        return { 'message': False, 'error': str(e) }, 500

@app.route("/keywdcheck", methods=["POST"])
@swag_from({
    'tags': ['Keywd Check'],
    'description': 'Scrap keywords from Naver',
    'parameters': [
        {
            'name': 'keywds',
            'description': 'Input keywords such as { "col": "인천", "row": "치과" }',
            'in': 'body',
            'type': 'string',
            'required': 'true',
        }
    ],
    'responses': {
        200: {
            'description': 'Successful response',
            'examples': {
                'application/json': [{'href': 'example_url_1'}, {'href': 'example_url_2'}]
            }
        },
        500: {
            'description': 'Error response',
            'examples': {
                'application/json': {'message': False, 'error': 'Error message'}
            }
        }
    }
})
def keywdcheck():
    try:
        col = request.json.get('col')
        row = request.json.get('row')

        keywd = f'{col}+{row}'
        posts1 = scrap_keywdcheck(keywd)

        # time.sleep(uniform(0.5, 1.0))

        keywd = f'{col}{row}'
        posts2 = scrap_keywdcheck(keywd)
        marge_posts = posts1 + posts2

        return { 'message': True, 'posts': marge_posts }, 200

    except Exception as e:
        return { 'message': False, 'error': str(e) }, 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)