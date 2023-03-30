import os

import requests
from bs4 import BeautifulSoup as bs
from requests.utils import cookiejar_from_dict

from handlers.config_handler import Config


class Digi4school:
    def __init__(self):
        self.session = requests.Session()
        self.login_url = "https://digi4school.at/br/xhr/login"
        self.books_list_url = "https://digi4school.at/ebooks"
        self.book_url = "https://a.digi4school.at/ebook/"
        self.token_url = "https://a.digi4school.at/lti/"

        os.makedirs('download', exist_ok=True)


    def login_user(self):
        payload = {
            'email': 'email',
            'password': 'password'
        }
        data = Config().get_config()
        payload["email"] = data["email"]
        payload["password"] = data["password"]
        response = self.session.post(self.login_url, data=payload, timeout=5)
    
        if str(response.content, 'utf-8') == "OK":
            return True
        elif str(response.content, 'utf-8') == "KO":
            return False

    def get_page(self):
        books = []
        if self.session is None:
            raise ValueError("Session is not initialized.")

        response = self.session.get(self.books_list_url, timeout=5)

        soup = bs(response.content, 'html.parser')

        shelf_div = soup.find('div', {'id': 'shelf'})

        a_tags = shelf_div.find_all('a')

        for a_tag in a_tags:
            href = a_tag.get('href')

            data_id = a_tag['data-id']
            h1_text = a_tag.find('h1').text
            books.append((data_id, h1_text, href))

        return books


    def download_book(self, book_id):
        url = self.book_url + book_id
        down_dir = f'download/{book_id}'

        self.session.get(url, timeout=5)

        cookies = self.session.cookies.get_dict()

        print(cookies)

        headers = {
            'Cookie': 'digi4b="{digi4b}"; digi4s="{digi4s}"; ad_session_id={ad_session_id}'.format(digi4b=cookies["digi4b"], digi4s=cookies["digi4s"], ad_session_id=cookies["ad_session_id"]),
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
        }

        counter = 1

        os.makedirs(down_dir)


        while True:
            file_url = f"{url}/{counter}.svg"
            response = self.session.get(file_url, headers=headers, timeout=10)

            if response.status_code == 400:
                break

            with open(f"{down_dir}/{counter}.svg", "w+", encoding="utf8") as f:
                f.write(response.text)

            counter += 1

        print(f"All SVG files for book {book_id} have been downloaded to {down_dir}.")
