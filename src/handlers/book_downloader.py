import os
import re
import shutil
import time

import requests
from requests.exceptions import HTTPError, RequestException

from handlers.authentication import Authentication
from handlers.pdf_convert import SVGtoPDFConverter


class Download():
    def __init__(self, session) -> None:
        self.session: requests.Session = session

    def main(self, data: list):
        starttime = time.time()
        down_dir = os.path.join('download', data[0])
        os.makedirs(down_dir, exist_ok=True)

        print("Getting tokens" + ' '*50, end="\r")
        url, self.session = Authentication(self.session).get_token(data)

        print("Downloading SVG files" + ' '*50, end="\r")
        svg_success = self.download_svg(down_dir, url)
        if not svg_success:
            print("Failed to download SVG files.\n")
            return

        print("Downloading images" + ' '*50, end="\r")
        img_success = self.download_images(down_dir, url)
        if not img_success:
            print("Failed to download images.\n")
            return

        print("Converting to PDF" + ' '*50, end="\r")
        svg_success, error_code = SVGtoPDFConverter().convert_all_svgs_to_pdf(down_dir, data[2])
        if not svg_success:
            print(f"Error Converting to pdf: {error_code}")
            return

        shutil.rmtree(down_dir)
        print(f"Process completed in {time.time() - starttime} seconds \n")

    def download_svg(self, down_dir, url):
        special_book_url: bool = False

        response = self.session.get(f"{url}/1.svg", timeout=5)
        if response.status_code != 404:
            file_url = f"{url}/{{}}.svg"
        else:
            response = self.session.get(f"{url}/1/1.svg", timeout=5)
            if response.status_code != 404:
                file_url = f"{url}/{{}}/{{}}.svg"
                special_book_url = True
            else:
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

            svg_text = response.text

            if special_book_url:
                svg_text = self.modify_svg_text(svg_text, counter)

            with open(f"{down_dir}/{counter}.svg", "w+", encoding="utf8") as svg_file:
                svg_file.write(svg_text)

            counter += 1
        return True

    def modify_svg_text(self, svg_text:str, counter):
        pattern = r'<image\s.*?xlink:href="([^"]*)".*?>'
        matches = re.findall(pattern, svg_text)

        if matches:
            for xlink_href in matches:
                new_url = f"{counter}/{xlink_href}"
                svg_text = svg_text.replace(xlink_href, new_url, 1)
        return svg_text

    def download_images(self, svg_dir, url):
        svg_files = os.listdir(svg_dir)

        for file in svg_files:
            with open(f"{svg_dir}/{file}", "rb") as svg_file:
                svg_contents = svg_file.read().decode('utf-8')

            # use a regular expression to extract all xlink:href attribute values from the image tags
            pattern = r'<image\s.*?xlink:href="([^"]*)".*?>'
            matches = re.findall(pattern, svg_contents)

            if matches:
                for xlink_href in matches:
                    image_url = f"{url}/{xlink_href}"
                    response = self.session.get(image_url, timeout=5)
                    dirname = f"{svg_dir}/{os.path.dirname(xlink_href)}"
                    os.makedirs(dirname, exist_ok=True)

                    if response.status_code == 200:
                        with open(os.path.join(dirname, os.path.basename(xlink_href)), "wb") as img_file:
                            img_file.write(response.content)
                    else:
                        return False
        return True
