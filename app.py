import platform
import time
import requests
from random import *
from flask import Flask, request
from flask_cors import CORS
from flask_restful import Api
from flasgger import Swagger, swag_from
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

class WebDriverManager:
    def __init__(self):
        self.drivers = []

    def count_drivers(self):
        return len(self.drivers)

    def create_driver(self):
        driver = driverInit()
        self.drivers.append(driver)

        return driver

    def close_driver(self, driver):
        driver.quit()
        self.drivers.remove(driver)

manager = WebDriverManager() 

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

# def scrap_keywdcheck(keywd):
#     try:
#         url = f'https://m.search.naver.com/search.naver?sm=mtp_hty.top&where=m&query={keywd}'
#         headers = {
#             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edg/118.0.2088.46'
#         }
#         response = requests.get(url, headers=headers)
#         soup = BeautifulSoup(response.text, 'html.parser')

#         svp = soup.select_one('._svp_list')
#         posts = []
#         for post in svp.select('.api_txt_lines.total_tit'):
#             href = post.get('href')
#             posts.append({'href': href})
        
#         return posts

#     except Exception as e:
#         print('scrap_keywdcheck error', e)
#         return False

def driverInitTest():
    try:
        options = webdriver.ChromeOptions()
        # options.add_argument('headless')
        # options.add_argument("no-sandbox")
        # options.add_argument('window-size=1920x1080')
        # options.add_argument("disable-gpu")
        # options.add_experimental_option('excludeSwitches', ['enable-logging'])
        operaitor = platform.system()
        if (operaitor == 'Windows'):
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        elif (operaitor == 'Linux'):
            driver = webdriver.Chrome(options=options)

        return driver

    except Exception as e:
        print('driverInit error', e)
        return False

def driverInit():
    try:
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument("no-sandbox")
        # options.add_argument('window-size=1920x1080')
        # options.add_argument("disable-gpu")
        # options.add_experimental_option('excludeSwitches', ['enable-logging'])
        operaitor = platform.system()
        if (operaitor == 'Windows'):
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        elif (operaitor == 'Linux'):
            driver = webdriver.Chrome(options=options)

        return driver

    except Exception as e:
        print('driverInit error', e)
        return False

def scrap_keywdcheck_v2(driver, keywd):
    try:
        driver.get(f'https://m.search.naver.com/search.naver?sm=mtp_hty.top&where=m&query={keywd}')
        time.sleep(uniform(1.0, 2.0))

        posts = []

        # VIEW 영역 수집
        try:
            list = driver.find_element(By.CSS_SELECTOR, '.lst_view')
            for post in list.find_elements(By.CSS_SELECTOR, '.title_link'):
                href = post.get_attribute('href')
                posts.append({'href': href})

        except Exception as e:
            print('VIEW 영역 수집 실패', e)

        # 스마트블록 영역 수집
        try:
            print('스마트블록 영역을 탐색한다.')
            smart_blocks = driver.find_elements(By.CSS_SELECTOR, '.fds-ugc-block-mod')
            for smart_block in smart_blocks:
                try:
                    container = smart_block.find_element(By.CSS_SELECTOR, '.fds-comps-right-image')
                    link = container.find_element(By.CSS_SELECTOR, 'a')
                    href = link.get_attribute('href')
                    posts.append({'href': href})
                except Exception as e:
                    None
        except Exception as e:
            print('스마트블록 영역 수집 실패', e)

        return posts

    except Exception as e:
        print('scrap_keywdcheck error', e)
        return []

def scrap_keywdcheck_local(driver, keywd):
    try:
        posts = []
        
        # VIEW 전체보기 상위노출 영역 수집
        try:
            print('VIEW 전체보기 영역을 탐색한다.')
            driver.get(f'https://m.search.naver.com/search.naver?where=m_view&sm=mtb_jum&query={keywd}')
            time.sleep(uniform(1.0, 2.0))

            list = driver.find_element(By.CSS_SELECTOR, '.lst_view')
            for post in list.find_elements(By.CSS_SELECTOR, '.title_link'):
                href = post.get_attribute('href')
                posts.append({'href': href})

        except Exception as e:
            print('VIEW 전체보기 영역 수집 실패', e)

        return posts

    except Exception as e:
        print('scrap_keywdcheck error', e)
        return []

def driverQuit(driver):
    try:
        driver.quit()
        return True
    except Exception as e:
        print('driverQuit error', e)
        return False

@app.route('/')
def index():
    return 'cloud_keywdcheck_server'

# 응답 api
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

# 테스트 api
@app.route('/test', methods=['POST'])
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
def test_responses():
    try:    
        driver_count = manager.count_drivers()
        if (driver_count == 0):
            print('driver가 생성되지 않아 새로 생성.')
            driver = manager.create_driver()

        else:
            print('driver가 이미 생성됨.')
            driver = manager.drivers[0]
        
        return { 'message': True }, 200
    
    except Exception as e:
        return { 'message': False, 'error': str(e) }, 500

# 키워드 체크 api
@app.route("/keywdcheck", methods=["POST"])
@swag_from({
    'tags': ['Keywd Check'],
    'description': 'Scrap keywords from Naver',
    'parameters': [
        {
            'name': 'keywds',
            'description': 'Input keywords such as { "col": "성남", "row": "치과", "content": {"keywdWorkType": "paste"} }',
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
        driver = driverInit()
        # driver_count = manager.count_drivers()

        # if (driver_count == 0):
        #     print('driver가 생성되지 않으면 새로 생성')
        #     driver = manager.create_driver()
        
        # if (driver == False):
        #     return { 'message': False, 'error': 'driverInit error', 'code': 1 }, 500

        col = request.json.get('col')
        row = request.json.get('row')
        content = request.json.get('content')

        workType = content['keywdWorkType']
        posts1 = []
        posts2 = []
        marge_posts = []

        if (workType is None):
            print('workType is None')
            keywd = f'{col}+{row}'
            posts1 = scrap_keywdcheck_v2(driver, keywd)
            
            time.sleep(uniform(2.0, 3.0))

            keywd = f'{col}{row}'
            posts2 = scrap_keywdcheck_v2(driver, keywd)

        elif (workType == 'space'):
            print('workType is space')
            keywd = f'{col}+{row}'
            posts1 = scrap_keywdcheck_v2(driver, keywd)

        elif (workType == 'paste'):
            print('workType is paste')
            keywd = f'{col}{row}'
            posts2 = scrap_keywdcheck_v2(driver, keywd)

        marge_posts = posts1 + posts2

        quit = driverQuit(driver)
        if (quit == False):
             return { 'message': False, 'error': 'driverQuit error', 'code': 2 }, 500
    
        if (len(marge_posts) == 0):
            return { 'message': True, 'posts': marge_posts, 'code': 3 }, 200
        else:
            return { 'message': True, 'posts': marge_posts, 'code': 4 }, 200

    except Exception as e:
        return { 'message': False, 'error': 'Exception error', 'code': 5 }, 500

# 지역 키워드 체크 api
@app.route("/keywdcheck/local", methods=["POST"])
@swag_from({
    'tags': ['Keywd Check'],
    'description': 'Scrap keywords from Naver',
    'parameters': [
        {
            'name': 'keywds',
            'description': 'Input keywords such as { "col": "동천동 치과" }',
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
def keywdchecklocal():
    try:
        driver = driverInit()

        col = request.json.get('col')
        posts = []
        keywd = f'{col}'
        posts = scrap_keywdcheck_local(driver, keywd)

        quit = driverQuit(driver)
        if (quit == False):
             return { 'message': False, 'error': 'driverQuit error', 'code': 2 }, 500
    
        if (len(posts) == 0):
            return { 'message': True, 'posts': posts, 'code': 3 }, 200
        else:
            return { 'message': True, 'posts': posts, 'code': 4 }, 200

    except Exception as e:
        return { 'message': False, 'error': 'Exception error', 'code': 5 }, 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)