import os

from handlers.download import Download
from bs4 import BeautifulSoup as bs


class Digi4school:
    def __init__(self, session):
        self.session = session
        self.books_list_url = "https://digi4school.at/ebooks"
        self.book_display_url = "https://a.digi4school.at/ebook/"
        self.hpthek_book = False

        self.image_url_only = None

        os.makedirs('download', exist_ok=True)

    def get_books(self, session):
        self.session = session
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
            data_code = a_tag['data-code']
            h1_text = a_tag.find('h1').text
            books.append((data_id, data_code, h1_text, href))

        return books

    def download_book(self, data, session):
        self.session = session
        Download(session).main(data)
        