import os

import requests
from bs4 import BeautifulSoup as bs
from requests.utils import cookiejar_from_dict

from handlers.config_handler import Config


class Digi4school:
    def __init__(self):
        self.session = None
        self.login_url = "https://digi4school.at/br/xhr/login"
        self.books_list_url = "https://digi4school.at/ebooks"
        self.book_url = "https://a.digi4school.at/ebook/"

        os.makedirs('download', exist_ok=True)


    def login_user(self):
        payload = {
            'email': 'email',
            'password': 'password'
        }
        data = Config().get_config()
        payload["email"] = data["email"]
        payload["password"] = data["password"]
        response = requests.post(self.login_url, data=payload, timeout=5)
    
        if str(response.content, 'utf-8') == "OK":
            self.session = response
            return True
        elif str(response.content, 'utf-8') == "KO":
            return False

    def get_page(self):
        books = []
        if self.session is None:
            raise ValueError("Session is not initialized.")

        response = requests.get(self.books_list_url, cookies=self.session.cookies, timeout=5)

        soup = bs(response.content, 'html.parser')

        shelf_div = soup.find('div', {'id': 'shelf'})

        a_tags = shelf_div.find_all('a')

        for a_tag in a_tags:
            data_id = a_tag['data-id']
            h1_text = a_tag.find('h1').text
            books.append((data_id, h1_text))

        return books


    def download_book(self, book_id):
        url = self.book_url + book_id
        down_dir = f'download/{book_id}'

        cookies_dict = requests.utils.dict_from_cookiejar(self.session.cookies)
        cookies = requests.utils.cookiejar_from_dict(cookies_dict)

        
        url = "https://a.digi4school.at/ebook/7553/"

        response = requests.get(url, cookies=self.session.cookies ,allow_redirects=True)

        initiator_chain = []

        for redirect in response.history:
            initiator_chain.append(redirect.url)

        initiator_chain.append(response.url)

        print(initiator_chain)

        digi4s = cookies.get("digi4s")
        ad_session_id = cookies.get("ad_session_id")
        print(ad_session_id)
        print(digi4s)

        headers = {
            'Cookie': 'digi4b="2296329404%2c7553%2c22s5bzuagyky%2c252212%20{261%201679642398%20AC09555B659FA11FB163DACED7E711E8A4426B7F}"; ad_session_id="%s"; digi4s="%s"' % (ad_session_id, digi4s),
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
        }
        counter = 1

        os.makedirs(down_dir)


        while True:
            file_url = f"{url}/{counter}.svg"
            response = requests.get(file_url, cookies=self.session.cookies, headers=headers, timeout=10)

            if response.status_code == 400:
                break

            with open(f"{down_dir}/{counter}.svg", "w+", encoding="utf8") as f:
                f.write(response.text)

            counter += 1


        print(f"All SVG files for book {book_id} have been downloaded to {down_dir}.")
