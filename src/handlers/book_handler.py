from pathlib import Path
from lxml import etree
from tqdm import tqdm

import os
import shutil
import time
import concurrent.futures

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
        regal_div = html_tree.find('.//div[@id="regal"]')
        shelf_div = regal_div.find('.//div[@id="shelf"]')
        a_tags = shelf_div.findall('.//a')

        for a_tag in a_tags:
            data_id = a_tag.get('data-id')
            data_code = a_tag.get('data-code')
            book_title = a_tag.find('.//h1').text
            href = a_tag.get('href')
            books.append((data_id, data_code, book_title, href))

        return books

    def download_book(self, data, session):
        if session is None:
            raise ValueError("Session is not initialized.")

        download = Download(session)
        starttime = time.perf_counter()
        down_dir = Path('download') / data[0]
        os.makedirs(down_dir, exist_ok=True)
        print(data)

        print("Getting tokens" + ' '*50, end="\r")
        url = Authentication().get_token(data, session)

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
    
    def download_all(self, data, session):
        if session is None:
            raise ValueError("Session is not initialized.")

        def download_book(book):
            down_dir = Path('download') / book[0]
            os.makedirs(down_dir, exist_ok=True)

            download = Download(session)
            url = Authentication().get_token(book, session)

            svg_success = download.download_svg(down_dir, url)
            if not svg_success:
                return f"Failed to download SVG files for book {book[0]}"

            img_success = download.download_images(down_dir, url)
            if not img_success:
                return f"Failed to download images for book {book[0]}"

            return None

        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = list(tqdm(executor.map(download_book, data), total=len(data), desc="Downloading", unit="book"))

        failed_books = [book[2] for book, result in zip(data, results) if result is not None]
        if failed_books:
            print(f"Failed to download the following books: {', '.join(failed_books)}")

        dir_book_dict = {str(Path('download') / book[0]): book[2] for book in data}

        books = [(dir_path, dir_book_dict[dir_path]) 
                for dir_path in os.listdir("download") 
                if os.path.isdir(Path('download') / Path(dir_path))]

        pbar = tqdm(books, desc="Converting to pdf", unit="pdf")
        failed_books = []
        for book in pbar:
            svg_success, error_code = self.conv.convert_all_svgs_to_pdf(book[0], book[1])

            if svg_success:
                if error_code == "missingsize":
                    failed_books.append(book[2])
            else:
                failed_books.append(book[2])
                shutil.rmtree(book[0])
                continue

            shutil.rmtree(book[0])

        if failed_books:
            print(f"Failed to convert to PDF for the following books: {', '.join(failed_books)}")

        shutil.rmtree('download')
