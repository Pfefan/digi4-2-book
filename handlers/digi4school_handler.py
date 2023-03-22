import requests
from requests_html import HTMLSession
from handlers.config_handler import Config
from bs4 import BeautifulSoup as bs
import os

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
        counter = 1

        os.makedirs(down_dir)

        session = HTMLSession()
        response = session.get(url)

        while True:
            file_url = f"{url}/{counter}.svg"
            response = session.get(file_url, cookies=self.session.cookies)

            # Save the SVG file
            with open(f"{down_dir}/{counter}.svg", "wb") as f:
                f.write(response.content)

            # Exit loop if the file doesn't exist
            if "404 - Not Found" in response.text:
                break

            counter += 1


        print(f"All SVG files for book {book_id} have been downloaded to {down_dir}.")
