import os
import re
import shutil

import requests
from bs4 import BeautifulSoup as bs
from PyPDF2 import PdfMerger
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from requests.exceptions import HTTPError, RequestException
from svglib.svglib import svg2rlg

from handlers.config_handler import Config


class Digi4school:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
        })
        self.login_url = "https://digi4school.at/br/xhr/login"
        self.books_list_url = "https://digi4school.at/ebooks"
        self.book_display_url = "https://a.digi4school.at/ebook/"
        self.token_url = "https://a.digi4school.at/lti"

        self.image_url_only = None

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
            data_code = a_tag['data-code']
            h1_text = a_tag.find('h1').text
            books.append((data_id, data_code, h1_text, href))

        return books

    def download_book(self, data):
        url = self.book_display_url + data[0]
        down_dir = f'download/{data[0]}'
        os.makedirs(down_dir, exist_ok=True)

        self.get_token(data)
        self.pdf_merge(down_dir)
        if self.get_svg(down_dir, url):
            if self.get_images(down_dir, url):
                self.pdf_merge(down_dir)

        else:
            print("Failed to download SVG files.")

    def get_token(self, data):
        # right now firstly the list-files has to be executed to get the cookies, i will change that in the future i am just
        # trying to implement the feature right now, the request with the id needs the digi4s cookie from the home page
        payload = {}
        book_code_url = "https://digi4school.at/ebook/" + data[1]
        lti_ad_session_url = "https://kat.digi4school.at/lti"
        lti_cookie_url = "https://a.digi4school.at/lti"

        book_code_req = self.session.get(book_code_url)

        book_code_response = book_code_req.content.decode()
        # gets all the data from the first lti response using regular expressions
        for match in re.findall(r"<input name='(\w+)' value='(.*?)'>", book_code_response):
            payload[match[0]] = match[1]

        # this request takes the cookie and the response data from the book id request to get a new ad_session_id token
        first_lti_req = self.session.post(lti_ad_session_url, data=payload)

        first_lti_response = first_lti_req.content.decode()
        payload.clear()

        # gets all the data from the first lti response using regular expressions
        for match in re.findall(r"<input name='(\w+)' value='(.*?)'>", first_lti_response):
            payload[match[0]] = match[1]

        # this request gets the cookies which are needed for reading out book data using the data from the first lti response
        self.session.post(lti_cookie_url, data=payload)

    def get_svg(self, down_dir, url):
        response = self.session.get(f"{url}/1.svg", timeout=5)
        if response.status_code != 404:
            file_url = f"{url}/{{}}.svg"
            self.image_url_only = True
        else:
            response = self.session.get(f"{url}1/1.svg", timeout=5)
            if response.status_code != 404:
                file_url = f"{url}/{{}}/{{}}.svg"
                self.image_url_only = False
            else:
                print("failed to get url")
                return False


        counter = 1
        while True:
            file_url_with_counter = file_url.format(counter, counter)
            try:
                response = self.session.get(file_url_with_counter, timeout=5)
                if response.status_code == 404:
                    if counter == 1:
                        return False
                    break

                response.raise_for_status()
            except (RequestException, HTTPError):
                print(f"Error downloading {file_url_with_counter}")
                return False

            with open(f"{down_dir}/{counter}.svg", "w+", encoding="utf8") as svg_file:
                svg_file.write(response.text)

            counter += 1
        return True


    def get_images(self, svg_dir, url):
        svg_files = os.listdir(svg_dir)

        for file in svg_files:
            with open(f"{svg_dir}/{file}", "rb") as svg_file:
                svg_contents = svg_file.read().decode('utf-8')

            # use a regular expression to extract all xlink:href attribute values from the image tags
            pattern = r'<image\s.*?xlink:href="([^"]*)".*?>'
            matches = re.findall(pattern, svg_contents)

            # print the extracted xlink:href values
            if matches:
                for xlink_href in matches:
                    if self.image_url_only:
                        image_url = f"{url}/{xlink_href}"
                    else:
                        image_url = f"{url}/{os.path.basename(file)}/{xlink_href}"
                    response = self.session.get(image_url, timeout=5)
                    dirname = f"{svg_dir}/{os.path.dirname(xlink_href)}"
                    os.makedirs(dirname, exist_ok=True)

                    if response.status_code == 200:
                        with open(os.path.join(dirname, os.path.basename(xlink_href)), "wb") as img_file:
                            img_file.write(response.content)
                    else:
                        return False
        return True

    def pdf_merge(self, svg_path):
        svg_files = [os.path.join(svg_path, f) for f in os.listdir(svg_path) if f.endswith('.svg')]
        svg_files.sort(key=lambda x: int(os.path.splitext(os.path.basename(x))[0]))


        output_pdf = 'output.pdf'
        merger = PdfMerger()
        os.makedirs(os.path.join(svg_path, "temp_pdf"), exist_ok=True)
        # Convert each SVG file to PDF and add it to the merger
        for svg_file in svg_files:
            drawing = svg2rlg(svg_file)
            pdf_filename = os.path.splitext(os.path.basename(svg_file))[0] + '.pdf'
            pdf_file = os.path.join(svg_path, 'temp_pdf', pdf_filename)
            canvas_obj = canvas.Canvas(pdf_file, pagesize=A4)
            page_width, page_height = A4
            drawing_width, drawing_height = drawing.minWidth(), drawing.height
            scale_factor = min(page_width / drawing_width, page_height / drawing_height)
            drawing.width, drawing.height = drawing_width * scale_factor, drawing_height * scale_factor
            drawing.scale(scale_factor, scale_factor)
            drawing.drawOn(canvas_obj, x=0, y=0)
            canvas_obj.save()
            merger.append(pdf_file)

        # Write the merged PDF file to disk
        merger.write(output_pdf)

        # Delete the output folder
        # folder_to_delete = 'output_folder'
        # shutil.rmtree(folder_to_delete)
