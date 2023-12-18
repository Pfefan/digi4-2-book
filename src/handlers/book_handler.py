from pathlib import Path
from lxml import etree
import os
import shutil
import time

from handlers.authentication import Authentication
from handlers.book_downloader import Download
from handlers.pdf_convert import SVGtoPDFConverter


class Digi4school:
    def __init__(self):
        self.books_list_url = "https://digi4school.at/ebooks"

        self.image_url_only = None
        self.conv = SVGtoPDFConverter()

        os.makedirs('download', exist_ok=True)

    def get_books(self, session):
        books = []
        if session is None:
            raise ValueError("Session is not initialized.")

        response = session.get(self.books_list_url, timeout=5)

        html_tree = etree.HTML(response.content)

        shelf_div = html_tree.find('div', {'id': 'shelf'})

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

        download = Download()
        starttime = time.perf_counter()
        down_dir = Path('download') / data[0]
        os.makedirs(down_dir, exist_ok=True)

        print("Getting tokens" + ' '*50, end="\r")
        url, session = Authentication(session).get_token(data)
        download.set_session(session)

        print("Downloading SVG files" + ' '*50, end="\r")
        svg_success = download.download_svg(down_dir, url)
        if not svg_success:
            print("Failed to download SVG files.\n")
            shutil.rmtree(down_dir)
            return

        print("Downloading images" + ' '*50, end="\r")
        img_success = download.download_images(down_dir, url)
        if not img_success:
            print("Failed to download images.\n")
            shutil.rmtree(down_dir)
            return

        print("Converting to PDF" + ' '*50, end="\r")
        svg_success, error_code = self.conv.convert_all_svgs_to_pdf(down_dir, data[2])

        if svg_success:
            if error_code == "missingsize":
                print("The size parameter is missing in the SVG, which could potentially lead to incorrect scaling in the PDF.", end="\r")
            print(f"Downloaded '{data[2]}' in {time.perf_counter() - starttime} seconds \n")
        else:
            print(f"Error Converting to pdf: {error_code}")
            shutil.rmtree(down_dir)
            return
        shutil.rmtree(down_dir)
