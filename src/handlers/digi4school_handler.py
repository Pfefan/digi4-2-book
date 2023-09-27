import os

from handlers.download import Download
from bs4 import BeautifulSoup as bs


class Digi4school:
    def __init__(self):
        self.books_list_url = "https://digi4school.at/ebooks"

        self.image_url_only = None

        os.makedirs('download', exist_ok=True)

    def get_books(self, session):
        books = []
        if session is None:
            raise ValueError("Session is not initialized.")

        response = session.get(self.books_list_url, timeout=5)

        soup = bs(response.content, 'html.parser')

        shelf_div = soup.find('div', {'id': 'shelf'})

        a_tags = shelf_div.find_all('a')

        for a_tag in a_tags:
            href = a_tag.get('href')

            data_id = a_tag['data-id']
            data_code = a_tag['data-code']
            h1_text = a_tag.find('h1').text
            books.append((data_id, data_code, h1_text, href))

        return books

    def download_book(self, data, session):
        if session is None:
            raise ValueError("Session is not initialized.")

        Download(session).main(data)
        