import concurrent.futures
import copy
import os
import shutil
import time
import requests
from pathlib import Path

from bs4 import BeautifulSoup
from tqdm import tqdm

from .authentication import AuthAndTokenHandler
from .book_downloader import BookContentDownloader
from .pdf_convert import SVGtoPDFConverter


class BookDataRetriever:
    def __init__(self):
        self.books_list_url = "https://digi4school.at/ebooks"

        self.image_url_only = None
        self.conv = SVGtoPDFConverter()

        os.makedirs('download', exist_ok=True)

    def get_book_list(self, session: requests.Session):
        books = []
        if session is None or ('ad_session_id' not in session.cookies and 'digi4s' not in session.cookies):
            raise RuntimeError("Session is not initialized or user is not authenticated.")

        response = session.get(self.books_list_url, timeout=5)

        soup = BeautifulSoup(response.content, 'html.parser')
        shelf_div = soup.find(id='shelf')
        a_tags = shelf_div.find_all('a')

        for a_tag in a_tags:
            data_id = a_tag.get('data-id')
            data_code = a_tag.get('data-code')
            book_title = a_tag.find('h1').text
            href = a_tag.get('href')
            books.append((data_id, data_code, book_title, href))

        return books

    def download_page(self, data, session: requests.Session, start_page=None, end_page=None):
        if session is None or ('ad_session_id' not in session.cookies and 'digi4s' not in session.cookies):
            raise RuntimeError("Session is not initialized or user is not authenticated.")

        download = BookContentDownloader(session)
        starttime = time.perf_counter()
        down_dir = Path('download') / data[0]
        os.makedirs(down_dir, exist_ok=True)

        print("Authenticating" + ' '*50, end="\r")
        url = AuthAndTokenHandler().token_processing(data, session)

        svg_success = download.download_pages(down_dir, url, start_page, end_page, show_progress=True)
        if not svg_success:
            print("Failed to download SVG files.\n")
            shutil.rmtree(down_dir)
            return

        """img_success = download.download_images(down_dir, url, show_progress=True)
        if not img_success:
            print("Failed to download images.\n")
            shutil.rmtree(down_dir)
            return

        svg_success, error_code = self.conv.convert_all_svgs_to_pdf(down_dir, data[2], show_progress=True)

        if svg_success:
            if error_code == "missingsize":
                print("The size parameter is missing in the SVG, which could potentially lead to incorrect scaling in the PDF.", end="\r")
                print("\n")

            time_taken = time.perf_counter() - starttime
            minutes, seconds = divmod(time_taken, 60)
            print(f"Downloaded '{data[2]}' in {int(minutes)} minutes and {seconds:.2f} seconds.\n")
        else:
            print(f"Error Converting to pdf: {error_code}")
            shutil.rmtree(down_dir)
            return
        shutil.rmtree(down_dir)"""

    def download_single_book(self, data, session: requests.Session):
        if session is None or ('ad_session_id' not in session.cookies and 'digi4s' not in session.cookies):
            raise RuntimeError("Session is not initialized or user is not authenticated.")

        download = BookContentDownloader(session)
        starttime = time.perf_counter()
        down_dir = Path('download') / data[0]
        os.makedirs(down_dir, exist_ok=True)

        print("Authenticating" + ' '*50, end="\r")
        url = AuthAndTokenHandler().token_processing(data, session)

        svg_success = download.download_svgs(down_dir, url, show_progress=True)
        if not svg_success:
            print("Failed to download SVG files.\n")
            shutil.rmtree(down_dir)
            return

        img_success = download.download_images(down_dir, url, show_progress=True)
        if not img_success:
            print("Failed to download images.\n")
            shutil.rmtree(down_dir)
            return

        svg_success, error_code = self.conv.convert_all_svgs_to_pdf(down_dir, data[2], show_progress=True)

        if svg_success:
            if error_code == "missingsize":
                print("The size parameter is missing in the SVG, which could potentially lead to incorrect scaling in the PDF.", end="\r")
                print("\n")

            time_taken = time.perf_counter() - starttime
            minutes, seconds = divmod(time_taken, 60)
            print(f"Downloaded '{data[2]}' in {int(minutes)} minutes and {seconds:.2f} seconds.\n")
        else:
            print(f"Error Converting to pdf: {error_code}")
            shutil.rmtree(down_dir)
            return
        shutil.rmtree(down_dir)

    def download_all_books(self, data, session: requests.Session):
        if session is None or ('ad_session_id' not in session.cookies and 'digi4s' not in session.cookies):
            raise RuntimeError("Session is not initialized or user is not authenticated.")

        def download_book(book):
            down_dir = Path('download') / book[0]
            os.makedirs(down_dir, exist_ok=True)
            
            url = AuthAndTokenHandler().token_processing(book, session)

            temp_session = copy.deepcopy(session)
            download = BookContentDownloader(temp_session)

            svg_success = download.download_svgs(down_dir, url)
            if not svg_success:
                shutil.rmtree(down_dir)
                return f"Failed to download SVG files for book {book[0]}"

            img_success = download.download_images(down_dir, url)
            if not img_success:
                shutil.rmtree(down_dir)
                return f"Failed to download images for book {book[0]}"

            return None

        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = list(tqdm(executor.map(download_book, data), total=len(data), desc="Downloading", unit="book"))

        failed_books = [book[2] for book, result in zip(data, results) if result is not None]
        if failed_books:
            print(f"Failed to download the following books: {', '.join(failed_books)}")

        dir_book_dict = {str(book[0]): book[2] for book in data}

        books = [(Path('download') / dir_path, dir_book_dict[dir_path])
                for dir_path in os.listdir("download")
                if os.path.isdir(Path('download') / Path(dir_path))]

        pbar = tqdm(books, desc="Converting to pdf", unit="pdf")
        failed_books = []
        missing_size_books = False
        for book in pbar:
            svg_success, error_code = self.conv.convert_all_svgs_to_pdf(book[0], book[1])

            if svg_success:
                if error_code == "missingsize":
                    missing_size_books = True
                    failed_books.append(book[1])
            else:
                failed_books.append(book[1])
                shutil.rmtree(book[0])
                continue

            shutil.rmtree(book[0])

        if missing_size_books:
            print(f"Incorect scaling for PDFs of the following books: {', '.join(failed_books)}")
        elif failed_books and missing_size_books:
            print(f"Failed to convert to PDF or incorect scaling for PDF for the following books: {', '.join(failed_books)}")
        elif failed_books:
            print(f"Failed to convert to PDF for the following books: {', '.join(failed_books)}")
